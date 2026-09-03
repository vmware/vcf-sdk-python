#!/usr/bin/env python

# Copyright (c) 2025-2026 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import argparse

from vmware.vcf_installer import model_client

from utils.ssl_helper import get_ssl_cert_thumbprint
from utils.sddc_spec_util import WorkflowType, VERSION, \
    create_vcf_operations_spec, hostname_to_fqdn, \
    AUTO_GENERATED_PASSWORD, create_sddc_vcenter_spec, CLUSTER_NAME, \
    CLUSTER_DATACENTER_NAME, save_sddc_spec_to_file, create_vsp_cluster_spec, create_vsp_ipv4_pool, \
    create_vsp_ipv6_pool, create_license_server_spec
from utils.client import create_vcf_installer_client
from utils.sddc_task_util import poll_sddc_validation_status, \
    poll_sddc_deployment_status
from utils.misc_util import parse_bool_or_str, \
    get_version_without_build_number

"""
Description:
Demonstrates how to deploy new VVF Instance, reusing existing Vcenter.
In addition to that deploy VSP components.
Prerequisites for successful deployment:
    1. Existing components need to be configured and reachable by the VCF Installer appliance
    2. All provided hostnames must be resolvable from the VCF Installer appliance
    3. The addresses of all components must be resolvable from the VCF Installer appliance (NTP, various VCF
       components, etc.)
    4. The Depot configuration must be complete
    5. The respective binary bundles need to be downloaded
Downloading respective bundles can be achieved by running the download_bundles_vvf_instance_existing_vcenter
sample
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
    help='Hostname or FQDN of the VCF Operations that will be deployed. Example: vcfops1')

parser.add_argument(
    '--vcenter_fqdn',
    required=True,
    help='Hostname or FQDN of the existing vCenter deployment. Example: vc1.vcf.local')

parser.add_argument(
    '--vcenter_thumbprint',
    help='SSL Certificate SHA256 Thumbprint of the vCenter deployment.')

parser.add_argument(
    '--vcenter_root_password',
    required=True,
    help='Password for the root user of the existing vCenter deployment.')

parser.add_argument(
    '--vcenter_sso_domain',
    default='vsphere.local',
    help='SSO domain for the vCenter deployment. Defaults to vsphere.local')

parser.add_argument(
    '--vcenter_admin_sso_username',
    required=True,
    help='Admin SSO Username for the existing vCenter deployment. Example: Administrator@VSPHERE.LOCAL')

parser.add_argument(
    '--vcenter_admin_sso_password',
    required=True,
    help='Admin SSO Password for the existing vCenter deployment')

parser.add_argument(
    '--sddc_id',
    required=True,
    help='SDDC ID. Example: sddc-01')

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
    help="VCF Services Platform IPv4 end ip address. All IPv4 fields are optional,"
         "however IPv4Pool is required for the VCF Services Platform cluster spec."
         "Either provide vsp_ipv4_addresses or provide"
         "vsp_ipv4_cidr, or vsp_ipv4_start_ip_address and vsp_ipv4_end_ip_address.")

parser.add_argument(
    "--vsp_ipv4_addresses",
    help="VCF Services Platform IPv4 ip addresses. All IPv4 fields are optional,"
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
    help="VCF Services Platform IPv6 end ip address. All IPv6 fields are optional,"
         "however IPv6Pool is required for the VCF Services Platform cluster spec."
         "Either provide vsp_ipv6_addresses or provide"
         "vsp_ipv6_cidr, or vsp_ipv6_start_ip_address and vsp_ipv6_end_ip_address.")

parser.add_argument(
    "--vsp_ipv6_addresses",
    help="VCF Services Platform IPv6 ip addresses. All IPv6 fields are optional,"
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
    "--license_server_hostname",
    required=True,
    help="License server hostname.")

parser.add_argument(
    "--license_server_use_existing_deployment",
    help="License server use existing deployment.")

args = parser.parse_args()
server = args.vcf_installer_fqdn
password = args.vcf_installer_admin_password
client = create_vcf_installer_client(server=server,
                                     password=password,
                                     ca_certs=args.ca_certs)


def create_sddc_spec_for_new_vvf_instance_with_existing_vc(vcf_client, args):
    spec = model_client.SddcSpec()
    spec.workflow_type = WorkflowType.VVF.name
    spec.ceip_enabled = True
    spec.version = get_version_without_build_number(vcf_client) or VERSION
    spec.ntp_servers = args.ntp_servers.split(',')
    spec.dns_spec = model_client.DnsSpec(subdomain=args.dns_domain,
                                         nameservers=args.dns_nameserver.split(","))

    # Operations stack
    spec.vcf_operations_spec = create_vcf_operations_spec(
        hostname_to_fqdn(args.vcf_ops_fqdn, args.dns_domain),
        AUTO_GENERATED_PASSWORD)  # VCF Ops Admin Password

    # vCenter
    vcenter_fqdn = hostname_to_fqdn(args.vcenter_fqdn, args.dns_domain)
    vcenter_thumbprint = args.vcenter_thumbprint or get_ssl_cert_thumbprint(vcenter_fqdn)
    spec.vcenter_spec = create_sddc_vcenter_spec(
        hostname_to_fqdn(args.vcenter_fqdn, args.dns_domain),
        vcenter_thumbprint,
        args.vcenter_root_password,
        None,
        args.vcenter_admin_sso_username,  # vCenter Admin User SSO Username
        args.vcenter_admin_sso_password,  # vCenter Admin User SSO Password
        True)  # Use Existing vCenter

    spec.cluster_spec = model_client.SddcClusterSpec(CLUSTER_NAME.format(
        args.sddc_id), CLUSTER_DATACENTER_NAME.format(args.sddc_id))
    spec.sddc_id = args.sddc_id

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

    spec.license_server_spec = create_license_server_spec(args.license_server_hostname,
                                                          args.license_server_use_existing_deployment,
                                                          None)

    return spec


sddc_spec = create_sddc_spec_for_new_vvf_instance_with_existing_vc(client, args)
print("Crafted Deployment Spec is: " + sddc_spec.to_json())

validation = client.v1.sddcs.Validations.validate_sddc_spec(sddc_spec)
print("Started VVF Instance Deployment Spec validation task with id: {}".format(validation.id))
# poll the task status
poll_sddc_validation_status(client, validation.id, 3)
print("Finished VVF Instance Deployment Spec validation task with id: {}".format(validation.id))

if not args.validate_only:
    print("Starting VVF Instance deployment")
    sddc_task = client.v1.Sddcs.deploy_sddc(sddc_spec)
    print("Started VVF Instance deployment task with id: {}".format(sddc_task.id))
    # poll the task status
    poll_sddc_deployment_status(client, sddc_task.id, 7)
    print("Finished VVF Instance deployment task with id: {}".format(sddc_task.id))
    save_sddc_spec_to_file(client, sddc_task.id, args.deployment_spec_save_file_path)

print("Sample completed successfully")
