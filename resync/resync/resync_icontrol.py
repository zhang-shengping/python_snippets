# -*- coding: utf-8 -*-

from f5_openstack_agent.lbaasv2.drivers.bigip.icontrol_driver \
    import iControlDriver
from f5_openstack_agent.lbaasv2.drivers.bigip.virtual_address import \
    VirtualAddress
import time

def exception_catcher():
    def decorater():
        pass

class ResynciControlDriver(iControlDriver):
    def __init__(self, conf, db_rpcclient):
        super(ResynciControlDriver, self).__init__(conf)
        self.db_rpcclient = db_rpcclient
        self.NONEXIST_PARTITION = {}
        self.NONEXIST_VIP = {}

    def _init_bigips(self):

        for hostname in self.hostnames:
            bigip = self._open_bigip(hostname)
            if bigip.status == "active":
                continue

            if bigip.status == 'connected':
                bigip.status = 'initializing'
                bigip.status_message = 'initializing HA viability'
                device_group_name = None

                if not self.ha_validated:
                    device_group_name = self._validate_ha(bigip)
                    self.ha_validated = True
                if not self.tg_initialized:
                    self._init_traffic_groups(bigip)
                    self.tg_initialized = True

                self._init_bigip(bigip, hostname, device_group_name)
                self._init_agent_config(bigip)
                bigip.status = 'active'

    def skip_nonexist_partition(self, partition, bigip_hostname):
        hostname = self.NONEXIST_PARTITION.get(partition)
        if hostname == bigip_hostname:
            return True

    def skip_nonexist_loadbalancer(self, loadbalancer, bigip_hostname):
        virtual_address = VirtualAddress(self.service_adapter,
                                         loadbalancer)
        hostname = self.NONEXIST_VIP.get(virtual_address.name)
        if hostname == bigip_hostname:
            return True

    def service_exists(self, loadbalancer):

        folder_name = self.service_adapter.get_folder_name(
            loadbalancer['tenant_id']
        )

        self.partition_exists(folder_name)

        # self.assgin_vip_routedomain(loadbalancer)

        self.vip_exists(loadbalancer)

        self.vs_exists(loadbalancer, folder_name)

        self.pool_resources_exists(loadbalancer, folder_name)

        print "------------------------------------------------"

    def assgin_vip_routedomain(self, loadbalancer):

        subnet_id = loadbalancer.get("vip_subnet_id")
        subnet = self.db_rpcclient.get_subnet_by_id(subnet_id)

        network_id = subnet.get("network_id")
        network  = self.db_rpcclient.get_network_by_id(network_id)

        loadbalancer["network_id"] = network.get("id")

        service = {"loadbalancer": loadbalancer,
                   "networks": {network_id: network},
                   "subnets":{subnet_id: subnet}}

        self.network_builder._annotate_service_route_domains(service)

    def assgin_member_routedomain(self, member_obj):

        subnet_id = member_obj.get("subnet_id")
        subnet = self.db_rpcclient.get_subnet_by_id(subnet_id)

        network_id = subnet.get("network_id")
        network  = self.db_rpcclient.get_network_by_id(network_id)

        member_obj["network_id"] = network.get("id")

        service = {"members": [member_obj],
                   "networks": {network_id: network},
                   "subnets":{subnet_id: subnet}}

        self.network_builder._annotate_service_route_domains(service)

    # output bigip
    # output partition name
    # output loadbalancer body
    # then break
    def partition_exists(self, folder_name):
        t1 = time.time()
        for bigip in self.get_config_bigips():
            try:
                self.system_helper.folder_exists(bigip, folder_name)
            except Exception as ec:
                with open("/tmp/missing_partition.txt", 'a') as writer:
                    outstr = "bigip: {}, partition: {}\n".format(
                        bigip.hostname, folder_name)
                    writer.write(outstr)
                self.NONEXIST_PARTITION[folder_name] = bigip.hostname
        t2 = time.time()
        spd = t2 - t1
        print("partiton check finished: %f" % spd)

    # output bigip host
    # output partition, vip name
    # output loadbalancer body
    # then break
    def vip_exists(self, loadbalancer):
        t1 = time.time()
        for bigip in self.get_config_bigips():
            try:
                virtual_address = VirtualAddress(self.service_adapter,
                                                 loadbalancer)

                skip = self.skip_nonexist_partition(virtual_address.partition,
                                        bigip.hostname)
                if skip:
                    continue

                exist = virtual_address.exists(bigip)

                if exist is False:
                    with open("/tmp/missing_vip.txt", 'a') as writer:
                        outstr = "bigip: {}, partition: {}, vip: {}\n".format(
                            bigip.hostname, virtual_address.partition,
                            virtual_address.name)
                        writer.write(outstr)
                    self.NONEXIST_VIP[virtual_address.name] = bigip.hostname

            except Exception as ec:
                raise ec
        t2 = time.time()
        spd = t2 -t1
        print("vip check finished: %f" % spd)

    # output bigip host
    # output partition, vs name
    # output listener body
    def vs_exists(self, loadbalancer, folder_name):
        t1 = time.time()
        for bigip in self.get_config_bigips():
            skip_pt = self.skip_nonexist_partition(folder_name,
                                    bigip.hostname)
            skip_lb = self.skip_nonexist_loadbalancer(loadbalancer,
                                       bigip.hostname)
            if skip_pt or skip_lb:
                continue

            for listener in loadbalancer.get("listeners"):
                try:
                    name_dict = self.service_adapter._init_virtual_name(
                        loadbalancer, listener
                    )
                    exist = self.vs_manager.exists(bigip,
                                           name=name_dict["name"],
                                           partition=folder_name)

                    if exist is False:
                        with open("/tmp/missing_vs.txt", 'a') as writer:
                            outstr = "bigip: {}, partition: {}, vs: {}\n".format(
                                bigip.hostname, folder_name, name_dict["name"])
                            writer.write(outstr)

                except Exception as ec:
                    raise ec
        t2 = time.time()
        spd = t2 -t1
        print("vs check finished: %f" % spd)

    # outuput bigip host
    # outuput partition, pool name/ healthmonitor name/ member name
    # output pool body/ member body/ healthmonitor body
    # pool, monitor, node all exist on bigip independently
    def pool_resources_exists(self, loadbalancer, folder_name):
        t1 = time.time()
        for bigip in self.get_config_bigips():
            skip = self.skip_nonexist_partition(folder_name,
                                           bigip.hostname)
            if skip:
                continue

            pool_ids = loadbalancer.get("pools")
            for pool in pool_ids:
                _bigip_pool = None
                pool_id = pool.get("id")
                # we may put this in service_builder?
                pool_obj = self.db_rpcclient.get_pool_by_id(pool_id)

                name_dict = self.service_adapter.init_pool_name(
                    loadbalancer,
                    pool
                )

                try:
                    _bigip_pool = self.pool_manager.load(
                        bigip,
                        name=name_dict['name'],
                        partition=folder_name
                    )
                except Exception as ec:
                    with open("/tmp/missing_pool.txt", 'a') as writer:
                        outstr = "bigip: {}, partition: {}, pool: {}\n".format(
                            bigip.hostname, folder_name, name_dict["name"])
                        writer.write(outstr)
                    # althogh pool namd member could exist on bigip independently,
                    # we follow the lbaas rule when we check resouces.
                    # but vip, vs, and pool follow lbaas or bigip?
                    # continue

                self.healthmonitor_exists(
                    loadbalancer,
                    pool_obj,
                    _bigip_pool,
                    folder_name,
                    bigip
                )

                self.member_exists(
                    pool_obj,
                    _bigip_pool,
                    folder_name,
                    bigip
                )
        t2 = time.time()
        spd = t2 -t1
        print("pool/healthmonitor/member check finished: %f" % spd)

    def healthmonitor_exists(self, loadbalancer,
                             pool_obj, bigip_pool, folder_name,
                             bigip):
        hmt1 = time.time()
        healthmonitor_id = pool_obj.get("healthmonitor_id")

        if healthmonitor_id:
            # we may put this in service_builder?
            healthmonitor_obj = self.db_rpcclient.get_healthmonitor_by_id(
                healthmonitor_id)
            monitor_dict = self.service_adapter.init_monitor_name(
                loadbalancer, healthmonitor_obj)

            service = {"healthmonitor": healthmonitor_obj}
            monitor_ep = self._get_monitor_endpoint(bigip, service)

            try:
                exist = monitor_ep.exists(name=monitor_dict['name'],
                                  partition=folder_name)
                if exist is False:
                    bigip_pool_name = None if bigip_pool is None else bigip_pool.name

                    with open("/tmp/missing_healthmonitor.txt", 'a') as writer:
                        outstr = "bigip: {}, partition: {}, pool: {}, healthmonitor: {}\n".format(
                            bigip.hostname, folder_name, bigip_pool_name, monitor_dict["name"])
                        writer.write(outstr)

            except Exception as ec:
                raise ec
        hmt2 = time.time()
        spd = hmt2 - hmt1
        output = "on bigip {} pool {} related healthmonitor check finished: {}".format(
            bigip.hostname, pool_obj.get("id"), spd)
        print output

    def member_exists(self, pool_obj,
                      bigip_pool, folder_name, bigip):
        mt1 = time.time()
        if bigip_pool is not {}:
            bigip_members = bigip_pool.members_s.get_collection()
            bigip_member_names = [self.convert_member_name(m.name)
                                  for m in bigip_members]

            member_ids = pool_obj.get("members")
            if member_ids:
                for member_id in member_ids:
                    # assert member has id
                    id = member_id["id"]
                    member_obj = self.db_rpcclient.get_member_by_id(id)
                    address = member_obj["address"]
                    port = member_obj["protocol_port"]
                    name = address + ":" + str(port)

                    if name not in bigip_member_names:
                        bigip_pool_name = None if bigip_pool is None else bigip_pool.name

                        with open("/tmp/missing_member.txt", 'a') as writer:
                            outstr = "bigip: {}, partition: {}, pool: {},  member: {}\n".format(
                                bigip.hostname, folder_name, bigip_pool_name, member_id)
                            writer.write(outstr)
        else:
            pass
        mt2 = time.time()
        spd = mt2 - mt1
        output = "on bigip {} pool {} related member check finished: {}".format(
            bigip.hostname, pool_obj.get("id"), spd)
        print output

    @staticmethod
    def convert_member_name(bigip_member_name):
        # remove the routedomain id
        if "%" in bigip_member_name:
            port = bigip_member_name.split(":")[1]
            address = bigip_member_name.split("%")[0]
            bigip_member_name = address + ":" + port

        return bigip_member_name
