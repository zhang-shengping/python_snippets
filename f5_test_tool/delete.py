# Copyright 2011 VMware, Inc
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from collections import defaultdict

from neutron_lib.plugins import constants as lib_const
from neutron_lib.plugins import directory
from neutron_lbaas.services.loadbalancer.data_models import LoadBalancer
from oslo_config import cfg
from oslo_log import log as logging
import oslo_messaging
from oslo_service import periodic_task
from oslo_utils import excutils
from osprofiler import profiler
import six

from neutron._i18n import _
from neutron.common import utils
from neutron.plugins.common import constants

from oslo_db import options as db_options
try:
    from neutron.common import config as common_config
    from neutron.common import rpc as n_rpc
    try:
        from neutron.conf.agent import common as config
    except Exception:
        from neutron.agent.common import config
    # for openstack backward compatible
    try:
        # q version
        from neutron.conf.agent.common import INTERFACE_OPTS
    except Exception:
        # m/n/o/p version
        from neutron.agent.linux.interface import OPTS as INTERFACE_OPTS
except ImportError as Error:
    pass
import f5_openstack_agent.lbaasv2.drivers.bigip.agent_manager as manager
from neutron_lib import context as ncontext
import sys

from f5_vpcep_driver.driver import F5Driver


LOG = logging.getLogger(__name__)

CORE_PLUGINS_NAMESPACE = 'neutron.core_plugins'

def load_config():
    db_options.set_defaults(cfg.CONF)
    # cfg.CONF.register_opts(manager.OPTS)
    config.register_agent_state_opts_helper(cfg.CONF)
    config.register_root_helper(cfg.CONF)
    common_config.init(sys.argv[1:])
    # cfg.CONF(sys.argv[1:])

def validate_post_plugin_load():
    """Checks if the configuration variables are valid.

    If the configuration is invalid then the method will return an error
    message. If all is OK then it will return None.
    """
    if ('dhcp_agents_per_network' in cfg.CONF and
        cfg.CONF.dhcp_agents_per_network <= 0):
        msg = _("dhcp_agents_per_network must be >= 1. '%s' "
                "is invalid.") % cfg.CONF.dhcp_agents_per_network
        return msg


def validate_pre_plugin_load():
    """Checks if the configuration variables are valid.

    If the configuration is invalid then the method will return an error
    message. If all is OK then it will return None.
    """
    if cfg.CONF.core_plugin is None:
        msg = _('Neutron core_plugin not configured!')
        return msg


@six.add_metaclass(profiler.TracedMeta)
class NeutronManager(object):
    """Neutron's Manager class.

    Neutron's Manager class is responsible for parsing a config file and
    instantiating the correct plugin that concretely implements
    neutron_plugin_base class.
    """
    # TODO(armax): use of the singleton pattern for this class is vestigial,
    # and it is mainly relied on by the unit tests. It is safer to get rid
    # of it once the entire codebase (neutron + subprojects) has switched
    # entirely to using the plugins directory.
    _instance = None
    __trace_args__ = {"name": "rpc"}

    def __init__(self, options=None, config_file=None):
        # If no options have been provided, create an empty dict
        if not options:
            options = {}

        msg = validate_pre_plugin_load()
        if msg:
            LOG.critical(msg)
            raise Exception(msg)

        # NOTE(jkoelker) Testing for the subclass with the __subclasshook__
        #                breaks tach monitoring. It has been removed
        #                intentionally to allow v2 plugins to be monitored
        #                for performance metrics.
        plugin_provider = cfg.CONF.core_plugin
        LOG.info("Loading core plugin: %s", plugin_provider)
        # NOTE(armax): keep hold of the actual plugin object
        plugin = self._get_plugin_instance(CORE_PLUGINS_NAMESPACE,
                                           plugin_provider)
        directory.add_plugin(lib_const.CORE, plugin)
        msg = validate_post_plugin_load()
        if msg:
            LOG.critical(msg)
            raise Exception(msg)

        # load services from the core plugin first
        self._load_services_from_core_plugin(plugin)
        self._load_service_plugins()
        # Used by pecan WSGI
        # self.resource_plugin_mappings = {}
        # self.resource_controller_mappings = {}
        # self.path_prefix_resource_mappings = defaultdict(list)

    @property
    def core_plugin(self):
        return directory.get_plugin()

    @staticmethod
    def load_class_for_provider(namespace, plugin_provider):
        """Loads plugin using alias or class name

        :param namespace: namespace where alias is defined
        :param plugin_provider: plugin alias or class name
        :returns: plugin that is loaded
        :raises ImportError: if fails to load plugin
        """

        try:
            return utils.load_class_by_alias_or_classname(namespace,
                    plugin_provider)
        except ImportError:
            with excutils.save_and_reraise_exception():
                LOG.error("Plugin '%s' not found.", plugin_provider)

    def _get_plugin_instance(self, namespace, plugin_provider):
        plugin_class = self.load_class_for_provider(namespace, plugin_provider)
        return plugin_class()

    def _load_services_from_core_plugin(self, plugin):
        """Puts core plugin in service_plugins for supported services."""
        LOG.debug("Loading services supported by the core plugin")

        # supported service types are derived from supported extensions
        for ext_alias in getattr(plugin, "supported_extension_aliases", []):
            if ext_alias in constants.EXT_TO_SERVICE_MAPPING:
                service_type = constants.EXT_TO_SERVICE_MAPPING[ext_alias]
                directory.add_plugin(service_type, plugin)
                LOG.info("Service %s is supported by the core plugin",
                         service_type)

    def _get_default_service_plugins(self):
        """Get default service plugins to be loaded."""
        core_plugin = directory.get_plugin()
        if core_plugin.has_native_datastore():
            return constants.DEFAULT_SERVICE_PLUGINS.keys()
        else:
            return []

    def _load_service_plugins(self):
        """Loads service plugins.

        Starts from the core plugin and checks if it supports
        advanced services then loads classes provided in configuration.
        """
        plugin_providers = cfg.CONF.service_plugins
        plugin_providers.extend(self._get_default_service_plugins())
        LOG.debug("Loading service plugins: %s", plugin_providers)
        for provider in plugin_providers:
            if provider == '':
                continue

            LOG.info("Loading Plugin: %s", provider)
            plugin_inst = self._get_plugin_instance('neutron.service_plugins',
                                                    provider)

            # only one implementation of svc_type allowed
            # specifying more than one plugin
            # for the same type is a fatal exception
            # TODO(armax): simplify this by moving the conditional into the
            # directory itself.
            plugin_type = plugin_inst.get_plugin_type()
            if directory.get_plugin(plugin_type):
                raise ValueError(_("Multiple plugins for service "
                                   "%s were configured") % plugin_type)

            directory.add_plugin(plugin_type, plugin_inst)

            # search for possible agent notifiers declared in service plugin
            # (needed by agent management extension)
            plugin = directory.get_plugin()
            if (hasattr(plugin, 'agent_notifiers') and
                    hasattr(plugin_inst, 'agent_notifiers')):
                plugin.agent_notifiers.update(plugin_inst.agent_notifiers)

            LOG.debug("Successfully loaded %(type)s plugin. "
                      "Description: %(desc)s",
                      {"type": plugin_type,
                       "desc": plugin_inst.get_plugin_description()})

    @classmethod
    @utils.synchronized("manager")
    def _create_instance(cls):
        if not cls.has_instance():
            cls._instance = cls()

    @classmethod
    def has_instance(cls):
        return cls._instance is not None

    @classmethod
    def clear_instance(cls):
        cls._instance = None

    @classmethod
    def get_instance(cls):
        # double checked locking
        if not cls.has_instance():
            cls._create_instance()
        return cls._instance

def init():
    """Call to load the plugins (core+services) machinery."""
    if not directory.is_loaded():
        manager = NeutronManager.get_instance()
    return manager


if __name__ == "__main__":
    load_config()
    mage = init()
    plugin = directory.get_plugin("LOADBALANCERV2")
    f5_driver = F5Driver(plugin, "VPCEP")

    # mock scheduler
    def schedule_agent(context, vpcep):
        return {"host": "neutron-server-1.pdsea.f5net.com"}
    f5_driver.vpcep.schedule_agent = schedule_agent

    context = ncontext.get_admin_context()

    vpcep_id = "b7c1a69e88bf4b21a8148f787aef2081"
    network_id = "2e8bb436-aafa-4eee-8d73-c71736b0f45c"
    subnet_id = "0916f471-afcd-48ee-afc5-56bcb0efa963"
    project_id = "346052548d924ee095b3c2a4f05244ac"
    router_id = "4817588d-50e7-455c-b81c-41fdc0f97b16"

    vpcep = {
        "id": vpcep_id,
        "project_id": project_id,
        "tenant_id": project_id,
        "router_id": router_id,
        "subnet_id": subnet_id,
        "vpcep_vip_address": "10.0.0.4",
        "bandwidth": 25,
        "protocol": "tcp",
        "protocol_port": 8000
    }

    vpcep_service_id = "5f126d84-551a-4dcf-bb01-0e9c0df0c793"

    svc_a = {
        "project_id": project_id,
        "tenant_id": project_id,
        "id": "aaaaaaaa-551a-4dcf-bb01-0e9c0df0c793",
        "vpcep_service_address": "172.168.1.16",
        "vpcep_service_port": 80
    }
    svc_b = {
        "project_id": project_id,
        "tenant_id": project_id,
        "id": "bbbbbbbb-551a-4dcf-bb01-0e9c0df0c793",
        "vpcep_service_address": "172.168.1.16",
        "vpcep_service_port": 22
    }

    # vpcep_svc_create = svc_a
    vpcep_svc_create = svc_b

    vpcep_svc_delete = svc_b

    # vpcep_services = [
        # {
            # "project_id": "b7c1a69e88bf4b21a8148f787aef2081",
            # "id": "5f126d84-551a-4dcf-bb01-0e9c0df0c793",
            # " vpcep_service_address ": "10.0.0.7",
            # " vpcep_service_port ": 80
        # }
    # ]

    net = f5_driver.plugin.db._core_plugin.get_network(context, network_id)
    # network = f5_driver.plugin.db._core_plugin.get_network(context, network_id)
    import pdb; pdb.set_trace()
    subnet = f5_driver.plugin.db._core_plugin.get_subnet(context, subnet_id)
    router = {}

    # f5_driver.vpcep.disassociate(context, vpcep, vpcep_svc_delete, network=network, subnet=subnet)
    f5_driver.vpcep.delete(context, vpcep, network=net, subnet=subnet)

