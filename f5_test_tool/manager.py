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

from f5lbaasdriver.v2.bigip.driver_v2 import F5DriverV2


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
            # import pdb; pdb.set_trace()

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

    # @classmethod
    # def set_plugin_for_resource(cls, resource, plugin):
        # cls.get_instance().resource_plugin_mappings[resource] = plugin

    # @classmethod
    # def get_plugin_for_resource(cls, resource):
        # return cls.get_instance().resource_plugin_mappings.get(resource)

    # @classmethod
    # def set_controller_for_resource(cls, resource, controller):
        # cls.get_instance().resource_controller_mappings[resource] = controller

    # @classmethod
    # def get_controller_for_resource(cls, resource):
        # resource = resource.replace('_', '-')
        # res_ctrl_mappings = cls.get_instance().resource_controller_mappings
        # # If no controller is found for resource, try replacing dashes with
        # # underscores
        # return res_ctrl_mappings.get(
            # resource,
            # res_ctrl_mappings.get(resource.replace('-', '_')))

    # TODO(blogan): This isn't used by anything else other than tests and
    # probably should be removed
    # @classmethod
    # def get_service_plugin_by_path_prefix(cls, path_prefix):
        # service_plugins = directory.get_unique_plugins()
        # for service_plugin in service_plugins:
            # plugin_path_prefix = getattr(service_plugin, 'path_prefix', None)
            # if plugin_path_prefix and plugin_path_prefix == path_prefix:
                # return service_plugin

    # @classmethod
    # def add_resource_for_path_prefix(cls, resource, path_prefix):
        # resources = cls.get_instance().path_prefix_resource_mappings[
            # path_prefix].append(resource)
        # return resources

    # @classmethod
    # def get_resources_for_path_prefix(cls, path_prefix):
        # return cls.get_instance().path_prefix_resource_mappings[path_prefix]


def init():
    """Call to load the plugins (core+services) machinery."""
    if not directory.is_loaded():
        manager = NeutronManager.get_instance()
    return manager


if __name__ == "__main__":
    # import pdb; pdb.set_trace()
    load_config()
    mage = init()
    lbaas_plugin = directory.get_plugin("LOADBALANCERV2")
    f5_driver = F5DriverV2(lbaas_plugin, "Project")

    # loadbalancer_id = "99805628-e608-4f3b-9a18-5150a24eb60a"
    context = ncontext.get_admin_context()
    # lb = lbaas_plugin.db.get_loadbalancer(context, id=loadbalancer_id)

    # lb = LoadBalancer(**lb) if type(lb) == dict else lb
    # agent = f5_driver.plugin.db.get_agent_hosting_loadbalancer(
        # context,
        # loadbalancer_id
    # )
    # agent = (agent['agent'] if 'agent' in agent else agent)
    # service = f5_driver.service_builder.build(context, lb, agent)
    # print service

    project_id = "34a1a8395d0f460f9854609505f6e0c6"

    acl_group = {"acl_group": {
            "name": "pzhang",
            "description": "pzhang",
            "project_id": project_id,
            "region": "rz1"
        }
    }
#     acl_group = lbaas_plugin.create_acl_group(context, acl_group)
#     print acl_group

#     acl_group_id = acl_group['id']

    # new_acl_group = {
        # "acl_group": {
            # "project_id": "test" # }
    # }

    # lbaas_plugin.update_acl_group(context, acl_group_id, new_acl_group)

    # import pdb; pdb.set_trace()
    # lbaas_plugin.delete_acl_group(context, acl_group_id)

    # acl_group_id = acl_group['id']

    # new_acl_group = {
        # "acl_group": {
            # "name": "test"
        # }
    # }

    # lbaas_plugin.update_acl_group(context, acl_id, new_acl_group)

    # new_acl_group = {
        # "acl_group": {
            # "project_id": "test"
        # }
    # }

    # lbaas_plugin.update_acl_group(context, acl_id, new_acl_group)

    # acl_group = lbaas_plugin.get_acl_group(context, acl_id)
    # print acl_group

    # acl_groups = lbaas_plugin.get_acl_groups(context)
    # print acl_groups
    # import pdb; pdb.set_trace()

    # acl_rule = {
        # "acl_rule": {
            # "description": "desc_acl_r1",
            # "ip_version": "IPv4",
            # "ip_address": "1.1.1.1",
            # 'project_id': project_id
        # }
    # }

    # lbaas_plugin.create_acl_group_acl_rule(context, acl_group_id, acl_rule)

    # acl_rule = {
        # "acl_rule": {
            # "description": "desc_acl_r1",
            # "ip_version": "IPv4",
            # "ip_address": "1.2.2.2",
            # 'project_id': project_id
        # }
    # }

    # lbaas_plugin.create_acl_group_acl_rule(context, acl_group_id, acl_rule)

    # acl_group_id = "f4cbfa2e-6f71-4f75-ac47-13e679d1542a"
    # acl_rule_id = "d0703271-1bec-459b-a6dd-c535ec853ce4"

    # acl_rule = {
        # "acl_rule": {
            # "description": "desc_acl_r1",
            # "ip_version": "IPv4",
            # "ip_address": "4.4.4.4",
            # 'project_id': "741f6f88b9454609993ef7c9ca38d485"
            # 'project_id': "aaaf6f88b9454609993ef7c9ca38d485"
        # }
    # }

    # lbaas_plugin.update_acl_group_acl_rule(context, acl_rule_id, acl_group_id, acl_rule)

    # acl_rule_id = "c2c27700-47ea-46be-9df5-d806c1ed16f4"
    # acl_group_id = "2aa197d0-3c83-4568-b43e-156f9d3bc4a5"

    # lbaas_plugin.delete_acl_group_acl_rule(context, acl_rule_id, acl_group_id)

    # acl_group_id = "6be5ccf0-e825-411c-823e-be43469a4cfc"

    # listener_id = "92a7d60b-d57d-4f02-952a-31f4331d3120"

    # acl_group_id = "bc270eea-bd21-4289-ad55-46d257e559d4"
    # acl_group_id = "5c0fbc88-919e-432a-beb5-f3ba0dbcbc54"
    # binding_info = {
        # "enabled": True,
        # "listener_id": listener_id,
        # "type": "whitelist"
    # }

    # import pdb; pdb.set_trace()
    # lbaas_plugin.add_listener(context, acl_group_id, binding_info)
    # lbaas_plugin.remove_listener(context, acl_group_id, binding_info)


    # lbaas_plugin.flush_acl_rules(context, acl_group_id)

    # import pdb; pdb.set_trace()

    # acl_bind_list = lbaas_plugin.db.get_acl_listener_binding_by_listener_id(
        # context, listener_id)

    # import pdb; pdb.set_trace()
    # print acl_bind_list

    # lbaas_plugin.delete_listener(context, listener_id)
    # lbaas_plugin.delete_acl_group(context, acl_group_id)

    # acl_group = {
    #     "id": "00000000-e608-4f3b-9a18-5150a24eb60a",
    #     "tanant_id": "346052548d924ee095b3c2a4f05244ac",
    #     "rules":[
    #         "192.168.0.111",
    #         "192.168.0.222",
    #         "192.168.0.123"
    #     ]
    # }

    # old_acl_group = {
    #     "id": "00000000-e608-4f3b-9a18-5150a24eb60a",
    #     "tanant_id": "346052548d924ee095b3c2a4f05244ac",
    #     "rules":[
    #         "192.168.0.222",
    #         "192.168.0.123",
    #         "10.10.0.10"
    #     ]
    # }

    # f5_driver.acl_group.create(context, acl_group)
    # f5_driver.acl_group.update(context, acl_group, old_acl_group)
    # f5_driver.acl_group.delete(context, acl_group)

# ------------------------ recover data --------------------------------------------

    # recover loadbalancer

    # lb_id = "76038dff-4438-4afa-9068-9c5905db8582"
    # loadbalancer_id = "36638069-1c7b-4a33-9fe5-5238f947793d"
    # data = lbaas_plugin.create_loadbalancer(
        # context, loadbalancer_id)

# ----------------------------------------------

    # recover listener

    # if both listener and pool are miss
    # we must recover pool first
    # ls_id = "8477ba31-0c52-477b-aba0-99babdb3f3c1"
    # data = lbaas_plugin.create_listener(
        # context, ls_id)
    # print data

# ----------------------------------------------

    # recover pool under loadbalancer

    # pl_id = "6eca763c-445a-4423-8597-37c51fa803bc"
    # data = lbaas_plugin.create_pool(
        # context, pl_id)
    # print data

# ---------------------------------------------

    # recover pool under listener. listener --> pool

    # test later
    # if the both are disappered, create pool --> listener

    # pl_id = "061408d4-3d57-4317-8b35-8ee2eb3d2f18"
    # data = lbaas_plugin.create_pool(
        # context, pl_id)
    # print data

# ---------------------------------------------

    # recover member

    member_id = "b9cb8864-c954-4665-a606-272af6f08781"
    pl_id = "6eca763c-445a-4423-8597-37c51fa803bc"
    data = lbaas_plugin.create_pool_member(
        context, pl_id, member_id)
