#!/usr/bin/env python
import copy
# Copyright (c) 2025-2026 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import os.path
from copy import deepcopy
from enum import Enum
from ipaddress import ip_address

from vmware.vcf_installer import model_client
from vmware.vcf_installer.model_client import IpRange, \
    VcfOperationsDiscoverySpec, VcfAutomationNodeInfo, DvsSpec, VidbSpec, LicenseServerSpec, IPv4Pool, \
    IPv6Pool, IpRangeV6, SddcVspClusterSpec
from utils.ssl_helper import get_ssl_cert_thumbprint

WorkflowType = Enum("WorkflowType", ["VCF", "VVF"])
VERSION = "9.0.0.0"

CLUSTER_NAME = "{}-cl-01"
CLUSTER_DATACENTER_NAME = "{}-cl-vdc-01"

_VSAN_ESA_ENABLED = False
_VSAN_DATASTORE_NAME = "sddc-cl-ds-vsan-01"

SDDC_ID = "sddc-id-01"

_VSAN_STORAGE_TYPE = "VSAN"

_VSAN_NETWORK_TYPE = "VSAN"
_MANAGEMENT_NETWORK_TYPE = "MANAGEMENT"
_VMOTION_NETWORK_TYPE = "VMOTION"
_VM_MANAGEMENT_NETWORK_TYPE = "VM_MANAGEMENT"

_BASE_ESX_FQDN = "esx{}.{}"

_VM_APPLIANCE_SIZE_SMALL = "small"
_NSX_APPLIANCE_SIZE_MEDIUM = "medium"
_VCENTER_STORAGE_LARGE = "lstorage"

_VCFA_INTERNAL_CLUSTER_CIDR = "198.18.0.0/15"


_VCF_OPS_APPLIANCE_SIZE_MEDIUM = "medium"
_VCF_OPS_APPLIANCE_SIZE_LARGE = "large"
_VCF_OPS_APPLIANCE_SIZE_XLARGE = "xlarge"

_VCF_OPS_MASTER_NODE_TYPE = "master"
_VCF_OPS_REPLICA_NODE_TYPE = "replica"
_VCF_OPS_DATA_NODE_TYPE = "data"

_NUMBER_OF_HOSTS = 4

_ROOT_USER = "root"
_VCF_USERNAME = "vcf"
_ADMIN_USER = "admin"

AUTO_GENERATED_PASSWORD = None  # Password is to be auto-generated.

_FQDN_NODE_ADDRESS_TYPE = "Fqdn"

_VCFA_NODE_PREFIX = "vcfa"

def hostname_to_fqdn(hostname, dns_domain):
    if not hostname:
        return None

    if not "." in hostname:
        return hostname.strip() + "." + dns_domain.strip()
    return hostname.strip()


def get_hosts_to_thumbprint(host_fqdn_to_thumbprint, dns_domain, ca_certs):
    host_fqdn_to_thumbprint_dict = {}
    if not host_fqdn_to_thumbprint:
        for i in range(0, _NUMBER_OF_HOSTS):
            host_fqdn = _BASE_ESX_FQDN.format(i + 1, dns_domain)
            host_fqdn_to_thumbprint_dict[host_fqdn] = get_ssl_cert_thumbprint(host_fqdn, ca_certs)
    else:
        host_fqdn_to_thumbprint_pairs = host_fqdn_to_thumbprint.split(",")
        for pair in host_fqdn_to_thumbprint_pairs:
            fqdn_thumbprint_pair = pair.split("=")
            host_fqdn = hostname_to_fqdn(fqdn_thumbprint_pair[0], dns_domain)
            if fqdn_thumbprint_pair and len(fqdn_thumbprint_pair) < 2:
                fqdn_thumbprint_pair.append(
                    get_ssl_cert_thumbprint(host_fqdn, ca_certs))
            host_fqdn_to_thumbprint_dict[host_fqdn] = fqdn_thumbprint_pair[1]
    return host_fqdn_to_thumbprint_dict


def create_sddc_host_specs(host_password, host_fqdn_to_thumbprint):
    host_specs = []
    for (host_fqdn, host_thumbprint) in host_fqdn_to_thumbprint.items():
        host_specs.append(create_sddc_host_spec(host_fqdn, host_password, host_thumbprint))
    return host_specs


def create_sddc_host_spec(hostname, host_password, host_thumbprint):
    sddc_host_spec = model_client.SddcHostSpec()

    sddc_credentials = model_client.SddcCredentials()
    sddc_credentials.username = _ROOT_USER
    sddc_credentials.password = host_password

    sddc_host_spec.credentials = sddc_credentials
    sddc_host_spec.hostname = hostname
    sddc_host_spec.ssl_thumbprint = host_thumbprint
    return sddc_host_spec


def create_vcf_operations_spec(fqdn, vcf_ops_admin_password,
                               thumbprint=None, node_infos=None):
    def node_info_to_node(node_info):
        node = model_client.VcfOperationsNode()
        node.hostname = node_info.address
        node.type = node_info.type
        if node_info.address == fqdn:
            node.ssl_thumbprint = thumbprint
        return node

    operations_nodes = []
    if node_infos:
        # Using existing VCF Operations Fleet Management
        operations_nodes = [node_info_to_node(info) for info in node_infos]
    else:
        vcf_operations_node = model_client.VcfOperationsNode()
        vcf_operations_node.hostname = fqdn
        vcf_operations_node.type = _VCF_OPS_MASTER_NODE_TYPE
        operations_nodes.append(vcf_operations_node)

    vcf_operations_spec = model_client.VcfOperationsSpec()
    vcf_operations_spec.admin_user_password = vcf_ops_admin_password
    vcf_operations_spec.use_existing_deployment = bool(node_infos)
    vcf_operations_spec.appliance_size = _VCF_OPS_APPLIANCE_SIZE_MEDIUM
    vcf_operations_spec.nodes = operations_nodes
    return vcf_operations_spec

def create_vcf_operations_spec_HA(fqdn1, fqdn2, fqdn3, vcf_ops_admin_password,
                               thumbprint=None, node_infos=None):
    def node_info_to_node(node_info):
        node = model_client.VcfOperationsNode()
        node.hostname = node_info.address
        node.type = node_info.type
        if node_info.address == fqdn1:
            node.ssl_thumbprint = thumbprint
        return node

    operations_nodes = []
    if node_infos:
        # Using existing VCF Operations Fleet Management
        operations_nodes = [node_info_to_node(info) for info in node_infos]
    else:
        vcf_operations_node1 = model_client.VcfOperationsNode()
        vcf_operations_node1.hostname = fqdn1
        vcf_operations_node1.type = _VCF_OPS_MASTER_NODE_TYPE
        operations_nodes.append(vcf_operations_node1)

        vcf_operations_node2 = model_client.VcfOperationsNode()
        vcf_operations_node2.hostname = fqdn2
        vcf_operations_node2.type = _VCF_OPS_REPLICA_NODE_TYPE
        operations_nodes.append(vcf_operations_node2)

        vcf_operations_node3 = model_client.VcfOperationsNode()
        vcf_operations_node3.hostname = fqdn3
        vcf_operations_node3.type = _VCF_OPS_DATA_NODE_TYPE
        operations_nodes.append(vcf_operations_node3)

    vcf_operations_spec = model_client.VcfOperationsSpec()
    vcf_operations_spec.admin_user_password = vcf_ops_admin_password
    vcf_operations_spec.use_existing_deployment = bool(node_infos)
    vcf_operations_spec.appliance_size = _VCF_OPS_APPLIANCE_SIZE_MEDIUM
    vcf_operations_spec.nodes = operations_nodes
    return vcf_operations_spec


def create_vcf_automation_spec_on_vsp(
        fqdn,
        ipv4_addresses,
        platform_fqdn,
        use_existing_deployment):
    if not fqdn and not platform_fqdn and not ipv4_addresses:
        print("VCF Automation FQDN not found. Skipping creation of VCF Automation deployment.")
        return None

    if not fqdn or not platform_fqdn or not ipv4_addresses:
        raise Exception("Invalid arguments provided for VCF Automation deployment. "
                        "Either all arguments (FQDN, platform FQDN, and IPv4 addresses) "
                        "need to be provided or all should be null to skip VCF Automation deployment.")

    spec = model_client.VcfAutomationSpec()
    spec.hostname = fqdn
    spec.node_prefix = _VCFA_NODE_PREFIX
    spec.admin_user_password = AUTO_GENERATED_PASSWORD
    spec.internal_cluster_cidr = _VCFA_INTERNAL_CLUSTER_CIDR
    spec.ip_pool = [ip.strip() for ip in ipv4_addresses.split(",")]
    spec.platform_fqdn = platform_fqdn
    spec.use_existing_deployment = use_existing_deployment

    return spec


def create_vcf_automation_spec(
        fqdn,
        vcfa_admin_password,
        thumbprint=None,
        vcf_automation_pool_ip_range_start=None,
        vcf_automation_pool_ip_range_end=None,
        node_infos=None,
        ca_certs=None,
        use_existing_deployment=False):
    vcf_automation_spec = model_client.VcfAutomationSpec()

    if use_existing_deployment and not vcfa_admin_password:
        print("VCF Automation Password not provided. Skipping VCF Automation setup in the SDDC spec.")
        return None

    if use_existing_deployment:
        if not fqdn:
            # get fqdn from vcf-ops discovery if not passed in
            fqdn = [a.value for a in node_infos[0].addresses if a.type == _FQDN_NODE_ADDRESS_TYPE][0]
            thumbprint = node_infos[0].certificate_thumbprints[0]
        else:
            thumbprint = thumbprint or get_ssl_cert_thumbprint(fqdn, ca_certs)
    else:
        vcf_automation_spec.internal_cluster_cidr = _VCFA_INTERNAL_CLUSTER_CIDR
        vcf_automation_spec.ip_pool = [
            vcf_automation_pool_ip_range_start,
            vcf_automation_pool_ip_range_end]

    if not fqdn:
        # VCF Automation FQDN was not provided and was not found during VCF Ops discovery
        print("VCF Automation FQDN not found. Skipping VCF Automation setup in the SDDC spec.")
        return None

    vcf_automation_spec.hostname = fqdn
    vcf_automation_spec.ssl_thumbprint = thumbprint
    vcf_automation_spec.admin_user_password = vcfa_admin_password
    vcf_automation_spec.use_existing_deployment = use_existing_deployment

    return vcf_automation_spec

def create_vcf_automation_spec_HA(
        fqdn,
        vcf_automation_pool_ip_node_1=None,
        vcf_automation_pool_ip_node_2=None,
        vcf_automation_pool_ip_node_3=None,
        vcf_automation_pool_ip_node_4=None,
        platform_fqdn=None):

    if not (fqdn or platform_fqdn or vcf_automation_pool_ip_node_1
            or vcf_automation_pool_ip_node_2 or vcf_automation_pool_ip_node_3
            or vcf_automation_pool_ip_node_4):
        # VCF Automation FQDN was not provided and was not found during VCF Ops discovery
        print("VCF Automation FQDN not found. Skipping VCF Automation setup in the SDDC spec.")
        return None

    if not (fqdn and platform_fqdn and vcf_automation_pool_ip_node_1
            and vcf_automation_pool_ip_node_2 and vcf_automation_pool_ip_node_3
            and vcf_automation_pool_ip_node_4):
        raise Exception("Invalid arguments provided for VCF Automation deployment. "
                        "Either all arguments (fqdn, platform_fqdn, and ip addresses for all 4 nodes) "
                        "need to be provided or all should be null to skip VCF Automation deployment.")

    vcf_automation_spec = model_client.VcfAutomationSpec()

    vcf_automation_spec.internal_cluster_cidr = _VCFA_INTERNAL_CLUSTER_CIDR
    vcf_automation_spec.ip_pool = [
        vcf_automation_pool_ip_node_1,
        vcf_automation_pool_ip_node_2,
        vcf_automation_pool_ip_node_3,
        vcf_automation_pool_ip_node_4]

    vcf_automation_spec.hostname = fqdn
    vcf_automation_spec.platform_fqdn = platform_fqdn
    vcf_automation_spec.admin_user_password = AUTO_GENERATED_PASSWORD

    return vcf_automation_spec


def create_vcf_operations_collector_spec(fqdn, use_existing_deployment):
    vcf_operations_collector_spec = model_client.VcfOperationsCollectorSpec()
    vcf_operations_collector_spec.hostname = fqdn
    vcf_operations_collector_spec.appliance_size = _VM_APPLIANCE_SIZE_SMALL
    vcf_operations_collector_spec.use_existing_deployment = use_existing_deployment
    return vcf_operations_collector_spec


def create_sddc_vcenter_spec(fqdn, ssl_thumbprint, root_vcenter_password,
                             sso_domain, sso_admin_username, sso_admin_password,
                             use_existing_deployment):
    sddc_vcenter_spec = model_client.SddcVcenterSpec()
    sddc_vcenter_spec.vcenter_hostname = fqdn
    sddc_vcenter_spec.root_vcenter_password = root_vcenter_password
    sddc_vcenter_spec.use_existing_deployment = use_existing_deployment

    if use_existing_deployment:
        sddc_vcenter_spec.sso_domain = sso_domain
        sddc_vcenter_spec.admin_user_sso_username = sso_admin_username
        sddc_vcenter_spec.admin_user_sso_password = sso_admin_password
        sddc_vcenter_spec.ssl_thumbprint = ssl_thumbprint
    else:
        sddc_vcenter_spec.storage_size = _VCENTER_STORAGE_LARGE
        sddc_vcenter_spec.vm_size = _VM_APPLIANCE_SIZE_SMALL

    return sddc_vcenter_spec


def create_ip_address_pool_spec(
        ip_address_pool_gateway,
        ip_address_pool_subnet,
        ip_address_pool_range_start,
        ip_address_pool_range_end):

    ip_address_pool_range_spec = model_client.IpAddressPoolRangeSpec()
    ip_address_pool_range_spec.start = ip_address_pool_range_start
    ip_address_pool_range_spec.end = ip_address_pool_range_end

    ip_address_pool_subnet_spec = model_client.IpAddressPoolSubnetSpec()
    ip_address_pool_subnet_spec.cidr = ip_address_pool_subnet
    ip_address_pool_subnet_spec.gateway = ip_address_pool_gateway
    ip_address_pool_subnet_spec.ip_address_pool_ranges = [ip_address_pool_range_spec]

    ip_address_pool_spec = model_client.IpAddressPoolSpec()
    ip_address_pool_spec.description = "ESXi Host Overlay TEP IP Pool"
    ip_address_pool_spec.name = "tep01"
    ip_address_pool_spec.subnets = [ip_address_pool_subnet_spec]

    return ip_address_pool_spec


def create_sddc_nsxt_spec(
        fqdn,
        vip_fqdn,
        nsxt_ssl_thumbprint,
        nsxt_root_password,
        nsxt_admin_password,
        nsxt_audit_password,
        ip_address_pool_spec,
        vlan_id,
        use_existing_deployment):

    sddc_nsxt_spec = model_client.SddcNsxtSpec()

    if not use_existing_deployment:
        sddc_nsxt_spec.ip_address_pool_spec = ip_address_pool_spec

        sddc_nsxt_spec.nsxt_manager_size = _NSX_APPLIANCE_SIZE_MEDIUM
        sddc_nsxt_spec.skip_nsx_overlay_over_management_network = True
        sddc_nsxt_spec.transport_vlan_id = vlan_id

    sddc_nsxt_spec.root_nsxt_manager_password = nsxt_root_password
    sddc_nsxt_spec.nsxt_admin_password = nsxt_admin_password
    sddc_nsxt_spec.nsxt_audit_password = nsxt_audit_password

    nsxt_manager_spec = model_client.NsxtManagerSpec(fqdn)
    sddc_nsxt_spec.nsxt_managers = [nsxt_manager_spec]
    sddc_nsxt_spec.ssl_thumbprint = nsxt_ssl_thumbprint
    sddc_nsxt_spec.use_existing_deployment = use_existing_deployment
    sddc_nsxt_spec.vip_fqdn = vip_fqdn
    sddc_nsxt_spec.enable_edge_cluster_sync = False

    if use_existing_deployment:
        sddc_nsxt_spec.ssl_thumbprint = nsxt_ssl_thumbprint

    return sddc_nsxt_spec

def create_sddc_nsxt_spec_HA(
        fqdn1,
        fqdn2,
        fqdn3,
        vip_fqdn,
        nsxt_root_password,
        nsxt_admin_password,
        nsxt_audit_password,
        ip_address_pool_spec,
        vlan_id,
        use_existing_deployment):

    sddc_nsxt_spec = model_client.SddcNsxtSpec()

    if not use_existing_deployment:
        sddc_nsxt_spec.ip_address_pool_spec = ip_address_pool_spec

        sddc_nsxt_spec.nsxt_manager_size = _NSX_APPLIANCE_SIZE_MEDIUM
        sddc_nsxt_spec.skip_nsx_overlay_over_management_network = True
        sddc_nsxt_spec.transport_vlan_id = vlan_id

    sddc_nsxt_spec.root_nsxt_manager_password = nsxt_root_password
    sddc_nsxt_spec.nsxt_admin_password = nsxt_admin_password
    sddc_nsxt_spec.nsxt_audit_password = nsxt_audit_password

    nsxt_manager_spec1 = model_client.NsxtManagerSpec(fqdn1)
    nsxt_manager_spec2 = model_client.NsxtManagerSpec(fqdn2)
    nsxt_manager_spec3 = model_client.NsxtManagerSpec(fqdn3)

    sddc_nsxt_spec.nsxt_managers = [nsxt_manager_spec1, nsxt_manager_spec2, nsxt_manager_spec3]
    sddc_nsxt_spec.use_existing_deployment = use_existing_deployment
    sddc_nsxt_spec.vip_fqdn = vip_fqdn
    sddc_nsxt_spec.enable_edge_cluster_sync = False

    return sddc_nsxt_spec


def create_vsan_spec():
    vsan_esa_config = model_client.VsanEsaConfig(_VSAN_ESA_ENABLED)

    vsan_spec = model_client.VsanSpec()
    vsan_spec.datastore_name = _VSAN_DATASTORE_NAME
    vsan_spec.vsan_dedup = False
    vsan_spec.failures_to_tolerate = 1
    vsan_spec.esa_config = vsan_esa_config
    return vsan_spec


def get_default_network_profile(vcf_client, dns_domain, host_specs):
    sddc_network_config_profile_spec = model_client.SddcNetworkConfigProfileSpec()
    sddc_network_config_profile_spec.host_specs = host_specs
    sddc_network_config_profile_spec.subdomain = dns_domain
    sddc_network_config_profile_spec.storage_type = _VSAN_STORAGE_TYPE

    try:
        network_config_profile_response = (
            vcf_client.v1.sddcs.NetworkConfigProfiles.get_network_config_profiles(
                sddc_network_config_profile_spec))
        if network_config_profile_response and network_config_profile_response.profiles and not len(
                network_config_profile_response.profiles) == 0:
            return network_config_profile_response.profiles[0]
        else:
            raise Exception("Empty profile response")
    except Exception as e:
        print("Failed to acquire network config profiles from VCF.")
        raise e


def create_sddc_manager_spec(fqdn, root_user_password,
                             local_user_password, vcf_user_password,
                             use_existing_deployment):

    sddc_manager_spec = model_client.SddcManagerSpec()
    sddc_manager_spec.hostname = fqdn
    sddc_manager_spec.root_password = root_user_password
    sddc_manager_spec.ssh_password = vcf_user_password
    sddc_manager_spec.local_user_password = local_user_password
    sddc_manager_spec.use_existing_deployment = use_existing_deployment

    return sddc_manager_spec


def create_sddc_network_specs(default_portgroup_list,
                              management_network_gateway,
                              management_network_subnet,
                              management_network_vlan_id,
                              vsan_network_gateway,
                              vsan_network_subnet,
                              vsan_network_vlan_id,
                              vsan_network_ip_range_start,
                              vsan_network_ip_range_end,
                              vmotion_network_gateway,
                              vmotion_network_subnet,
                              vmotion_network_vlan_id,
                              vmotion_ip_range_start,
                              vmotion_ip_range_end):
    if not default_portgroup_list:
        return []

    network_type_to_portgroup_dict = {pg.network_type: pg for pg in default_portgroup_list}

    sddc_network_specs = []
    # VM_MANAGEMENT Network Spec
    sddc_network_specs.append(create_sddc_network_spec(
        network_type_to_portgroup_dict.get(_VM_MANAGEMENT_NETWORK_TYPE),
        management_network_gateway,
        management_network_subnet,
        management_network_vlan_id,
        None))

    # MANAGEMENT Network Spec
    sddc_network_specs.append(create_sddc_network_spec(
        network_type_to_portgroup_dict.get(_MANAGEMENT_NETWORK_TYPE),
        management_network_gateway,
        management_network_subnet,
        management_network_vlan_id,
        None))

    # VSAN Network Spec
    vsan_ip_range = IpRange()
    vsan_ip_range.start_ip_address = vsan_network_ip_range_start
    vsan_ip_range.end_ip_address = vsan_network_ip_range_end

    sddc_network_specs.append(create_sddc_network_spec(
        network_type_to_portgroup_dict.get(_VSAN_NETWORK_TYPE),
        vsan_network_gateway,
        vsan_network_subnet,
        vsan_network_vlan_id,
        [vsan_ip_range]))

    # VMOTION Network Spec
    vmotion_ip_range = IpRange()
    vmotion_ip_range.start_ip_address = vmotion_ip_range_start
    vmotion_ip_range.end_ip_address = vmotion_ip_range_end

    sddc_network_specs.append(create_sddc_network_spec(
        network_type_to_portgroup_dict.get(_VMOTION_NETWORK_TYPE),
        vmotion_network_gateway,
        vmotion_network_subnet,
        vmotion_network_vlan_id,
        [vmotion_ip_range]))

    return sddc_network_specs


def create_sddc_network_spec(port_group, gateway, subnet, vlan_id, ip_ranges):
    sddc_network_spec = deepcopy(port_group)
    sddc_network_spec.gateway = gateway
    sddc_network_spec.subnet = subnet
    sddc_network_spec.vlan_id = vlan_id
    sddc_network_spec.include_ip_address_ranges = ip_ranges
    return sddc_network_spec


def discover_vcf_ops(vcf_client, vcf_ops_fqdn, vcf_ops_admin_password, vcf_ops_ssl_thumbprint):
    vcf_operations_discovery_spec = VcfOperationsDiscoverySpec()
    vcf_operations_discovery_spec.address = vcf_ops_fqdn
    vcf_operations_discovery_spec.admin_username = 'admin'
    vcf_operations_discovery_spec.admin_password = vcf_ops_admin_password
    vcf_operations_discovery_spec.ssl_thumbprint = vcf_ops_ssl_thumbprint

    vcf_operations_discovery_result = vcf_client.v1.sddcs.VcfopsDiscovery.discover_vcf_ops(
        vcf_operations_discovery_spec)

    return vcf_operations_discovery_result


def save_sddc_spec_to_file(vcf_client, sddc_task_id, deployment_spec_save_file_path):
    if deployment_spec_save_file_path:
        if os.path.isdir(deployment_spec_save_file_path):
            deployment_spec_save_file_path = \
                os.path.join(deployment_spec_save_file_path,
                             "sddc_spec-{}.json".format(sddc_task_id))

        deployment_spec = vcf_client.v1.sddcs.Spec.get_sddc_spec_by_id(sddc_task_id)
        with open(deployment_spec_save_file_path, "w") as file:
            file.write(deployment_spec.to_json())
            print("Sddc Spec, provided by {} Instance deployment task '{}', was successfully saved in '{}'.".format(
                deployment_spec.workflow_type,
                sddc_task_id,
                deployment_spec_save_file_path))


def create_dvs_specs(default_dvs_specs: list[DvsSpec],
                     mtu: int):
    dvs_specs = copy.deepcopy(default_dvs_specs)

    if mtu is None:
        return dvs_specs

    for spec in dvs_specs:
        spec.mtu = mtu

    return dvs_specs


def create_vidb_spec(hostname, size):
    spec = VidbSpec()

    spec.hostname = hostname
    spec.size = size

    return spec


def create_vsp_ipv4_pool(cidr,
                         start_ip_address,
                         end_ip_address,
                         addresses,
                         excluded_addresses):
    if not cidr and (not start_ip_address or not end_ip_address) and not addresses:
        raise Exception("IPv4 pool settings not provided for VSP.")

    pool = IPv4Pool()

    if cidr:
        pool.cidr = cidr

    if start_ip_address and end_ip_address:
        ip_range = IpRange()
        ip_range.start_ip_address = start_ip_address
        ip_range.end_ip_address = end_ip_address
        pool.ip_range = ip_range

    if addresses:
        pool.addresses = [address.strip() for address in addresses.split(",")]

    if excluded_addresses:
        pool.excluded_addresses = [excluded_address.strip() for excluded_address in excluded_addresses.split(",")]

    return pool


def create_vsp_ipv6_pool(cidr,
                         start_ip_address,
                         end_ip_address,
                         addresses,
                         excluded_addresses):
    if not cidr and (not start_ip_address or not end_ip_address) and not addresses:
        return None

    pool = IPv6Pool()

    if cidr:
        pool.cidr = cidr

    if start_ip_address and end_ip_address:
        ip_range = IpRangeV6()
        ip_range.start_ip_address = start_ip_address
        ip_range.end_ip_address = end_ip_address
        pool.ip_range = ip_range

    if addresses:
        pool.addresses = [address.strip() for address in addresses.split(",")]

    if excluded_addresses:
        pool.excluded_addresses = [excluded_address.strip() for excluded_address in excluded_addresses.split(",")]

    return pool


def create_vsp_cluster_spec(platform_fqdn,
                            ipv4_pool,
                            ipv6_pool,
                            size,
                            internal_cluster_cidr_ipv4,
                            internal_cluster_cidr_ipv6,
                            instance_fqdn,
                            fleet_fqdn):
    spec = SddcVspClusterSpec()

    spec.platform_fqdn = platform_fqdn
    spec.ipv4_pool = ipv4_pool
    spec.ipv6_pool = ipv6_pool
    spec.size = size
    spec.internal_cluster_cidr_ipv4 = internal_cluster_cidr_ipv4
    spec.internal_cluster_cidr_ipv6 = internal_cluster_cidr_ipv6
    spec.instance_fqdn = instance_fqdn
    spec.fleet_fqdn = fleet_fqdn

    return spec


def create_license_server_spec(hostname, use_existing_deployment, ssl_thumbprint):
    spec = LicenseServerSpec()

    spec.hostname = hostname
    spec.use_existing_deployment = use_existing_deployment
    spec.ssl_thumbprint = ssl_thumbprint

    return spec