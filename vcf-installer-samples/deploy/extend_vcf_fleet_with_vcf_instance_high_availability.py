#!/usr/bin/env python

# Copyright (c) 2025-2026 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import argparse

from vmware.vcf_installer import model_client
from vmware.vcf_installer.model_client import SddcDatastoreSpec

from utils.ssl_helper import get_ssl_cert_thumbprint
from utils.sddc_spec_util import WorkflowType, VERSION, \
    hostname_to_fqdn, discover_vcf_ops, \
    create_vcf_operations_spec, create_vcf_operations_collector_spec, \
    create_vcf_automation_spec, create_sddc_vcenter_spec, \
    AUTO_GENERATED_PASSWORD, SDDC_ID, CLUSTER_NAME, CLUSTER_DATACENTER_NAME, \
    create_sddc_nsxt_spec_HA, create_vsan_spec, get_hosts_to_thumbprint, \
    create_sddc_host_specs, get_default_network_profile, \
    create_sddc_network_specs, create_sddc_manager_spec, save_sddc_spec_to_file, \
    create_ip_address_pool_spec, create_vidb_spec, create_vsp_cluster_spec, create_vsp_ipv4_pool, \
    create_vsp_ipv6_pool
from utils.client import create_vcf_installer_client
from utils.misc_util import parse_bool_or_str, \
    get_version_without_build_number
from utils.sddc_task_util import poll_sddc_validation_status, \
    poll_sddc_deployment_status

"""
Description:
Demonstrates how to deploy new VCF Instance within an existing VCF Fleet, reusing existing VCF Operations, VCF
Operations Fleet Management, VCF Automation, VSP and VIDB.
Prerequisites for successful deployment:
    1. At least 4 prepared ESXi hosts
    2. An existing VCF Fleet, which is to be extended with a new VCF Instance
    3. All provided hostnames must be resolvable from the VCF Installer appliance
    4. The addresses of all components must be resolvable from the VCF Installer appliance (NTP, various VCF
       components, etc.)
    5. The Depot configuration must be complete
    6. The respective binary bundles need to be downloaded.

Downloading respective bundles can be achieved by running the download_bundles_extend_vcf_fleet_with_vcf_instance
sample.
Deploying a new VCF Fleet with a VCF Instance can by achieved by running either
deploy_vcf_fleet_first_vcf_instance or deploy_vcf_fleet_first_vcf_instance_from_existing_components sample.
"""

parser = argparse.ArgumentParser()

parser.add_argument(
    '--vcf_installer_fqdn',
    required=True,
    help='VCF Installer Appliance hostname or FQDN.')

parser.add_argument(
    '--vcf_installer_admin_password',
    required=True,
    help='VCF Installer Appliance password for admin@local user.')

parser.add_argument(
    '--dns_domain',
    required=True,
    help='Domain of existing and to-be-deployed appliances. Example: vcf.local')

parser.add_argument(
    '--dns_nameserver',
    required=True,
    help='Nameserver containing the domain\'s DNS records. Example: 192.168.0.1')

parser.add_argument(
    '--ntp_servers',
    required=True,
    help='Comma separated list of NTP servers used when deploying SDDC Manager appliance.')

parser.add_argument(
    '--vcf_ops_fqdn',
    required=True,
    help=' Hostname or FQDN of the existing VCF Operations. Example: vcfops1')

parser.add_argument(
    '--vcf_ops_admin_password',
    required=True,
    help='Admin user password of existing the VCF Operations.')

parser.add_argument(
    '--vcf_ops_thumbprint',
    help='SSL Certificate SHA256 Thumbprint of the existing VCF Operations.')

parser.add_argument(
    '--vcf_automation_fqdn',
    help='Hostname or FQDN of the existing VCF Automation. If passed discovery will be skipped for VCF Automation.')

parser.add_argument(
    '--vcf_automation_thumbprint',
    help='SSL Certificate SHA256 Thumbprint of the existing the VCF Automation deployment.')

parser.add_argument(
    '--vcf_automation_admin_password',
    help='Admin user password of existing the VCF Automation.')

parser.add_argument(
    '--vcf_ops_collector_fqdn',
    required=True,
    help='Hostname or FQDN of the existing VCF Operations Collector. Example: vcfopscp')

parser.add_argument(
    '--vcenter_fqdn',
    required=True,
    help='Hostname or FQDN of the vCenter that will be deployed. Example: vc1.vcf.local')

parser.add_argument(
    '--vcenter_sso_domain',
    default='vsphere.local',
    help='SSO domain for the vCenter deployment. Defaults to vsphere.local')

parser.add_argument(
    '--nsx_fqdn1',
    required=True,
    help='First hostname or FQDN of the NSX-T that will be deployed. Example: nsx1.vcf.local')

parser.add_argument(
    '--nsx_fqdn2',
    required=True,
    help='Second hostname or FQDN of the NSX-T that will be deployed. Example: nsx2.vcf.local')

parser.add_argument(
    '--nsx_fqdn3',
    required=True,
    help='Third hostname or FQDN of the NSX-T that will be deployed. Example: nsx3.vcf.local')

parser.add_argument(
    '--nsx_vip_fqdn',
    required=True,
    help='Hostname or FQDN of the cluster for the NSX-T deployment. Example: nsx.vcf.local')

parser.add_argument(
    '--nsx_gateway',
    required=True,
    help='Gateway for the NSX-T deployment. Example: 192.168.11.1')

parser.add_argument(
    '--nsx_subnet',
    required=True,
    help='Subnet of the NSX-T deployment. Example: 192.168.11.0/24')

parser.add_argument(
    '--nsx_vlan_id',
    required=True,
    help='Transport VLAN ID of the NSX-T deployment. Example: 4',
    type=int)

parser.add_argument(
    '--nsx_ip_range_start',
    required=True,
    help='Start of the IP Pool Range of the NSX-T deployment. Example: 192.168.11.2')

parser.add_argument(
    '--nsx_ip_range_end',
    required=True,
    help='End of the IP Pool Range of the NSX-T deployment. Example: 192.168.11.2')

parser.add_argument(
    '--esxi_host_root_password',
    required=True,
    help='Password for the hosts used.')

parser.add_argument(
    '--esx_hosts',
    required=True,
    help=""""String of a list of comma separated ESXi fqdns and (optional) SSL Certificate SHA256 thumbprints.
Example:
esx1.vcf.local,
esx2,
esx3=51:8D:84:62:AB:06:9E:BC:1D:2C:F5:72:FB:D2:C4:CA:D3:7D:BF:E1:19:98:D7:6D:A9:F4:9A:A4:03:E3:0B:38,
esx4.vcf.local=3F:AD:17:6C:80:29:10:B2:C6:BB:B9:41:18:CD:1C:3D:04:FF:F8:22:4E:58:F0:FD:D4:44:D2:B1:0A:9B:94:20""")

parser.add_argument(
    '--management_network_gateway',
    required=True,
    help='Gateway of the Management network. Example: 192.168.1.1')

parser.add_argument(
    '--management_network_subnet',
    required=True,
    help='Subnet of the Management network. Example: 192.168.1.0/24')

parser.add_argument(
    '--management_network_vlan_id',
    required=True,
    help='VLAN ID Of the management network. Example: 1',
    type=int)

parser.add_argument(
    '--vsan_network_gateway',
    required=True,
    help='Gateway of the vSAN network. Example: 192.168.2.1')

parser.add_argument(
    '--vsan_network_subnet',
    required=True,
    help='Subnet of the vSAN network. Example: 192.168.2.0/24')

parser.add_argument(
    '--vsan_network_vlan_id',
    required=True,
    help='VLAN ID Of the vSAN network. Example: 2',
    type=int)

parser.add_argument(
    '--vsan_network_ip_range_start',
    required=True,
    help='Start of the IP pool range of the vSAN network. Example: 192.168.2.2')

parser.add_argument(
    '--vsan_network_ip_range_end',
    required=True,
    help='End of the IP pool range of the vSAN network. Example: 192.168.2.200')

parser.add_argument(
    '--vmotion_network_gateway',
    required=True,
    help='Gateway of the vMotion network. Example: 192.168.3.1')

parser.add_argument(
    '--vmotion_network_subnet',
    required=True,
    help='Subnet of the vMotion network. Example: 192.168.3.0/24')

parser.add_argument(
    '--vmotion_network_vlan_id',
    required=True,
    help='VLAN ID Of the vMotion network. Example: 3',
    type=int)

parser.add_argument(
    '--vmotion_network_ip_range_start',
    required=True,
    help='Start of the IP pool range of the vMotion network. Example: 192.168.3.2')

parser.add_argument(
    '--vmotion_network_ip_range_end',
    required=True,
    help='End of the IP pool range of the vMotion network. Example: 192.168.3.200')

parser.add_argument(
    '--sddc_id',
    required=True,
    help='SDDC ID. Example: sddc-01')

parser.add_argument(
    '--sddc_manager_fqdn',
    required=True,
    help='Hostname or FQDN of the SDDC Manager that will be deployed. Example: sm.vcf.local')

parser.add_argument(
    "--vidb_hostname",
    required=True,
    help="VCF Identity Broker hostname.")

parser.add_argument(
    "--vidb_size",
    help="VCF Identity Broker size.")

parser.add_argument(
    "--vsp_platform_fqdn",
    required=True,
    help="VCF Services Platform FQDN.")

parser.add_argument(
    "--vsp_ipv4_cidr",
    help="VCF Services Platform IPv4 CIDR. All IPv4 fields are optional, "
         "however IPv4Pool is required for the VCF Services Platform cluster spec. "
         "Either provide vsp_ipv4_addresses or provide "
         "vsp_ipv4_cidr, or vsp_ipv4_start_ip_address and vsp_ipv4_end_ip_address.")

parser.add_argument(
    "--vsp_ipv4_start_ip_address",
    help="VCF Services Platform IPv4 start ip address. All IPv4 fields are optional,"
         "however IPv4Pool is required for the VCF Services Platform cluster spec."
         "Either provide vsp_ipv4_addresses or provide"
         "vsp_ipv4_cidr, or vsp_ipv4_start_ip_address and vsp_ipv4_end_ip_address.")

parser.add_argument(
    "--vsp_ipv4_end_ip_address",
    help="VCF Services Platform IPv4 start ip address. All IPv4 fields are optional,"
         "however IPv4Pool is required for the VCF Services Platform cluster spec."
         "Either provide vsp_ipv4_addresses or provide"
         "vsp_ipv4_cidr, or vsp_ipv4_start_ip_address and vsp_ipv4_end_ip_address.")

parser.add_argument(
    "--vsp_ipv4_addresses",
    help="VCF Services Platform IPv4 start ip address. All IPv4 fields are optional,"
         "however IPv4Pool is required for the VCF Services Platform cluster spec."
         "Either provide vsp_ipv4_addresses or provide"
         "vsp_ipv4_cidr, or vsp_ipv4_start_ip_address and vsp_ipv4_end_ip_address.")

parser.add_argument(
    "--vsp_ipv4_excluded_addresses",
    help="VCF Services Platform IPv4 excluded addresses.")

parser.add_argument(
    "--vsp_ipv6_cidr",
    help="VCF Services Platform IPv6 CIDR. All IPv6 fields are optional, "
         "however IPv6Pool is required for the VCF Services Platform cluster spec. "
         "Either provide vsp_ipv6_addresses or provide "
         "vsp_ipv6_cidr, or vsp_ipv6_start_ip_address and vsp_ipv6_end_ip_address.")

parser.add_argument(
    "--vsp_ipv6_start_ip_address",
    help="VCF Services Platform IPv6 start ip address. All IPv6 fields are optional,"
         "however IPv6Pool is required for the VCF Services Platform cluster spec."
         "Either provide vsp_ipv6_addresses or provide"
         "vsp_ipv6_cidr, or vsp_ipv6_start_ip_address and vsp_ipv6_end_ip_address.")

parser.add_argument(
    "--vsp_ipv6_end_ip_address",
    help="VCF Services Platform IPv6 start ip address. All IPv6 fields are optional,"
         "however IPv6Pool is required for the VCF Services Platform cluster spec."
         "Either provide vsp_ipv6_addresses or provide"
         "vsp_ipv6_cidr, or vsp_ipv6_start_ip_address and vsp_ipv6_end_ip_address.")

parser.add_argument(
    "--vsp_ipv6_addresses",
    help="VCF Services Platform IPv6 start ip address. All IPv6 fields are optional,"
         "however IPv6Pool is required for the VCF Services Platform cluster spec."
         "Either provide vsp_ipv6_addresses or provide"
         "vsp_ipv6_cidr, or vsp_ipv6_start_ip_address and vsp_ipv6_end_ip_address.")

parser.add_argument(
    "--vsp_ipv6_excluded_addresses",
    help="VCF Services Platform IPv6 excluded addresses.")

parser.add_argument(
    "--vsp_size",
    help="VCF Services Platform size.")

parser.add_argument(
    "--vsp_internal_cluster_cidr_ipv4",
    help="VCF Services Platform internal cluster CIDR IPv4.")

parser.add_argument(
    "--vsp_internal_cluster_cidr_ipv6",
    help="VCF Services Platform internal cluster CIDR IPv6.")

parser.add_argument(
    "--vsp_instance_fqdn",
    required=True,
    help="VCF Services Platform instance FQDN.")

parser.add_argument(
    "--vsp_fleet_fqdn",
    help="VCF Services Platform cluster fleet FQDN."
         "This should be provided in VVF and primary VCF instance."
         "If building a secondary VCF instance, do not provide this field.")

parser.add_argument(
    "--validate_only",
    default=False,
    action=argparse.BooleanOptionalAction,
    help="Whether to only run the validations and skip deployment. Default: False")

parser.add_argument(
    '--ca_certs',
    default=True,
    type=parse_bool_or_str,
    help="""By default uses built-in CA.
    To pass custom CA provide absolute path to the folder containing CA certs to use for SSL verifications.
    Pass False to disable SSL verifications
    (do not leave it empty on production environments).""")

parser.add_argument(
    '--deployment_spec_save_file_path',
    help="""
    Path to file or directory where to save the actual deployment specification in JSON format used by the
    VCF Installer during deployment.
    """)


def create_sddc_spec_for_extension_of_existing_vcf_fleet(vcf_client, args):
    spec = model_client.SddcSpec()
    spec.workflow_type = WorkflowType.VCF.name
    spec.ceip_enabled = True
    spec.version = get_version_without_build_number(vcf_client) or VERSION
    spec.ntp_servers = args.ntp_servers.split(',')
    spec.dns_spec = model_client.DnsSpec(subdomain=args.dns_domain,
                                         nameservers=args.dns_nameserver.split(","))

    vcf_ops_fqdn = hostname_to_fqdn(args.vcf_ops_fqdn, args.dns_domain)
    vcf_ops_thumbprint = args.vcf_ops_thumbprint or get_ssl_cert_thumbprint(
        vcf_ops_fqdn, args.ca_certs)
    vcf_ops_discovery_result = discover_vcf_ops(vcf_client, vcf_ops_fqdn,
                                                args.vcf_ops_admin_password,
                                                vcf_ops_thumbprint)

    # Operations stack
    # Use Existing VCF Operations
    spec.vcf_operations_spec = create_vcf_operations_spec(
        hostname_to_fqdn(args.vcf_ops_fqdn, args.dns_domain),
        args.vcf_ops_admin_password,
        args.vcf_ops_thumbprint,
        vcf_ops_discovery_result.vcf_operations_nodes)

    spec.vcf_operations_collector_spec = create_vcf_operations_collector_spec(
        hostname_to_fqdn(args.vcf_ops_collector_fqdn, args.dns_domain), False)

    if vcf_ops_discovery_result.vcf_automation_nodes:
        # Use Existing VCF Automation
        spec.vcf_automation_spec = create_vcf_automation_spec(
            hostname_to_fqdn(args.vcf_automation_fqdn, args.dns_domain),
            args.vcf_automation_admin_password,
            args.vcf_automation_thumbprint,
            None,
            None,
            vcf_ops_discovery_result.vcf_automation_nodes,
            args.ca_certs,
            True)
    else:
        print("VCF Automation FQDN not found. Skipping VCF Automation setup in the SDDC spec.")

    # vCenter
    spec.vcenter_spec = create_sddc_vcenter_spec(
        hostname_to_fqdn(args.vcenter_fqdn, args.dns_domain),
        None,  # vCenter SSL Thumbprint is required only for existing vCenter deployments
        AUTO_GENERATED_PASSWORD,  # vCenter Root Password
        args.vcenter_sso_domain,
        None,  # vCenter Admin User SSO Username
        AUTO_GENERATED_PASSWORD,  # vCenter Admin User SSO Password
        False)  # Use Existing vCenter

    sddc_id = args.sddc_id or SDDC_ID
    spec.cluster_spec = model_client.SddcClusterSpec(
        CLUSTER_NAME.format(sddc_id),
        CLUSTER_DATACENTER_NAME.format(sddc_id))

    # NSX-T
    ip_pool_spec = create_ip_address_pool_spec(
        args.nsx_gateway,
        args.nsx_subnet,
        args.nsx_ip_range_start,
        args.nsx_ip_range_end)

    spec.nsxt_spec = create_sddc_nsxt_spec_HA(
        hostname_to_fqdn(args.nsx_fqdn1, args.dns_domain),
        hostname_to_fqdn(args.nsx_fqdn2, args.dns_domain),
        hostname_to_fqdn(args.nsx_fqdn3, args.dns_domain),
        hostname_to_fqdn(args.nsx_vip_fqdn, args.dns_domain),
        AUTO_GENERATED_PASSWORD,  # NSX-T Root Password
        AUTO_GENERATED_PASSWORD,  # NSX-T Admin Password
        AUTO_GENERATED_PASSWORD,  # NSX-T Audit Password
        ip_pool_spec,
        args.nsx_vlan_id,
        False)  # Use Existing NSX-T

    # Host Storage
    datastore_spec = SddcDatastoreSpec()
    datastore_spec.vsan_spec = create_vsan_spec()
    spec.datastore_spec = datastore_spec

    # Hosts
    hosts_dict = get_hosts_to_thumbprint(
        args.esx_hosts, args.dns_domain, args.ca_certs)
    host_specs = create_sddc_host_specs(args.esxi_host_root_password, hosts_dict)
    spec.host_specs = host_specs  # Host specs are required for greenfield deployments.

    # Networking
    default_network_profile = get_default_network_profile(vcf_client, args.dns_domain, host_specs)
    default_dvs_specs = default_network_profile.dvs_specs
    dvs_portgroups = default_network_profile.dvs_name_to_portgroup_specs[
        default_dvs_specs[0].dvs_name]
    spec.dvs_specs = default_dvs_specs
    spec.network_specs = create_sddc_network_specs(
        dvs_portgroups,
        args.management_network_gateway,
        args.management_network_subnet,
        args.management_network_vlan_id,
        args.vsan_network_gateway,
        args.vsan_network_subnet,
        args.vsan_network_vlan_id,
        args.vsan_network_ip_range_start,
        args.vsan_network_ip_range_end,
        args.vmotion_network_gateway,
        args.vmotion_network_subnet,
        args.vmotion_network_vlan_id,
        args.vmotion_network_ip_range_start,
        args.vmotion_network_ip_range_end)

    spec.vidb_spec = create_vidb_spec(args.vidb_hostname, args.vidb_size)

    vsp_cluster_ipv4_pool = create_vsp_ipv4_pool(args.vsp_ipv4_cidr,
                                                 args.vsp_ipv4_start_ip_address,
                                                 args.vsp_ipv4_end_ip_address,
                                                 args.vsp_ipv4_addresses,
                                                 args.vsp_ipv4_excluded_addresses)

    vsp_cluster_ipv6_pool = create_vsp_ipv6_pool(args.vsp_ipv6_cidr,
                                                 args.vsp_ipv6_start_ip_address,
                                                 args.vsp_ipv6_end_ip_address,
                                                 args.vsp_ipv6_addresses,
                                                 args.vsp_ipv6_excluded_addresses)

    spec.vsp_cluster_spec = create_vsp_cluster_spec(args.vsp_platform_fqdn,
                                                    vsp_cluster_ipv4_pool,
                                                    vsp_cluster_ipv6_pool,
                                                    args.vsp_size,
                                                    args.vsp_internal_cluster_cidr_ipv4,
                                                    args.vsp_internal_cluster_cidr_ipv6,
                                                    args.vsp_instance_fqdn,
                                                    args.vsp_fleet_fqdn)

    # SDDC Manager
    spec.sddc_id = sddc_id
    spec.sddc_manager_spec = create_sddc_manager_spec(
        hostname_to_fqdn(args.sddc_manager_fqdn, args.dns_domain),
        AUTO_GENERATED_PASSWORD,  # SDDC Manager Root Password
        AUTO_GENERATED_PASSWORD,  # SDDC Manager Local User Password
        AUTO_GENERATED_PASSWORD,  # SDDC Manager VCF User Password
        False)  # Use Existing SDDC Manager

    return spec


args = parser.parse_args()
server = args.vcf_installer_fqdn
password = args.vcf_installer_admin_password
client = create_vcf_installer_client(server=server,
                                     password=password,
                                     ca_certs=args.ca_certs)

sddc_spec = create_sddc_spec_for_extension_of_existing_vcf_fleet(client, args)
print("Crafted Deployment Spec is: " + sddc_spec.to_json())

validation = client.v1.sddcs.Validations.validate_sddc_spec(sddc_spec)
print("Started Sddc Spec validation task with id: {}".format(validation.id))
# poll the task status
poll_sddc_validation_status(client, validation.id, 3)
print("Finished Sddc Spec validation task with id: {}".format(validation.id))

if not args.validate_only:
    print("Starting VCF Instance deployment into existing VCF Fleet")
    sddc_task = client.v1.Sddcs.deploy_sddc(sddc_spec)
    print("Started VCF Instance deployment task with id: {}".format(sddc_task.id))
    # poll the task status
    poll_sddc_deployment_status(client, sddc_task.id, 7)
    print("Finished VCF Instance deployment task with id: {}".format(sddc_task.id))
    save_sddc_spec_to_file(client, sddc_task.id, args.deployment_spec_save_file_path)

print("Sample completed successfully")