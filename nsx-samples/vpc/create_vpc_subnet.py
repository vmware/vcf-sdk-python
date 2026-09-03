#!/usr/bin/env python

# Copyright (c) 2025-2026 Broadcom. All Rights
# The term "Broadcom" refers to Broadcom
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import argparse

from utils.client import create_policy_client
from vcf.nsx.model_client import (
    IpAddressBlock,
    Project,
    SubnetDhcpConfig,
    TransitGatewayListResult,
    Vpc,
    VpcAttachment,
    VpcConnectivityProfile,
    VpcDhcpAdvancedConfig,
    VpcDhcpServerConfig,
    VpcProfileDhcpConfig,
    VpcServiceProfile,
    VpcSubnet,
)
from vmware.vapi.bindings.struct import PrettyPrinter

"""
Example to create VPC Subnet and associated objects as, Project, VPC, IPBlocks,
VpcServiceProfile, VPCAttachment.

The Subnet created is a Public Subnet with DHCP mode as DHCP_SERVER under VPC.

The subnet traffic is routed out of VPC via Transit Gateway.

The Transit Gateway is attached to VPC using VPCConnectivityProfile.

The DHCP Server configurations are provided in VPCServiceProfile.

Sample prerequisites: NSX Manager instance with default org created.

APIs used:
- Create IP block: PUT /policy/api/v1/infra/ip-blocks/{ip-block-id}
- GET custom project: GET /policy/api/v1/orgs/{org-id}/projects/{project-id}
- Create Vpc Service Profile: PUT /policy/api/v1/orgs/{org-id}/projects/{project-id}/vpc-service-profiles/{vpc-service-profile-id}
- Create VPC: PUT policy/api/v1/orgs/{org-id}/projects/{project-id}/vpcs/{vpc-id}
- Create VPC Connectivity Profile: PUT /policy/api/v1/orgs/{org-id}/projects/{project-id}/vpc-connectivity-profiles/{vpc-connectivity-profile-id}
- Create VPC Attachment: PUT /policy/api/v1/orgs/{org-id}/projects/{project-id}/vpcs/{vpc-id}/attachments/{vpc-attachment-id}
- Create VPC Subnet: PUT /policy/api/v1/orgs/{org-id}/projects/{project-id}/vpcs/{vpc-id}/subnets/{subnet-id}
"""

# Default values of optional parameters, in case they are not provided as command line arguments.
EXTERNAL_IP_CIDR = "142.2.0.0/24"
VCF_NSX_SDK_EXTERNAL_IP_ID = "VCF-NSX-SDK-external-ip"
VCF_NSX_SDK_SERVICE_PROFILE_ID = "VCF-NSX-SDK-serviceProfile"
VCF_NSX_SDK_CONNECTIVITY_PROFILE_ID = "VCF-NSX-SDK-connectivity-profile"
VCF_NSX_SDK_VPC_ATTACHMENT_ID = "VCF-NSX-SDK-vpcAttachment"
VCF_NSX_SDK_VPC_SUBNET_ID = "VCF-NSX-SDK-vpcSubnet"
PROJECT_ID = "VCF-NSX-SDK-Project"
VPC_ID = "VCF-NSX-SDK-VPC"

# Keyword reserved for Pre defined values.
DEFAULT_NAME = "default"

parser = argparse.ArgumentParser()
parser.add_argument("--server", required=True, help="NSX Host Name")
parser.add_argument("--user", required=True, help="NSX username", dest="username")
parser.add_argument("--password", required=True, help="NSX password")
parser.add_argument(
    "--external-ip-cidr",
    default=EXTERNAL_IP_CIDR,
    help="CIDR of External IP block be used by VpcSubnet that is to be created",
)
parser.add_argument(
    "--external-ip-id",
    default=VCF_NSX_SDK_EXTERNAL_IP_ID,
    help="Name of External IP block be used by VpcSubnet that is to be created",
)
parser.add_argument(
    "--vpc-service-profile-id",
    default=VCF_NSX_SDK_SERVICE_PROFILE_ID,
    help="Vpc Service profile ID",
)
parser.add_argument(
    "--vpc-connectivity-profile-id",
    default=VCF_NSX_SDK_CONNECTIVITY_PROFILE_ID,
    help="Vpc Connectivity profile ID",
)
parser.add_argument(
    "--vpc-attachment-id",
    default=VCF_NSX_SDK_VPC_ATTACHMENT_ID,
    help="Vpc Attachment ID",
)
parser.add_argument(
    "--vpc-subnet-id",
    default=VCF_NSX_SDK_VPC_SUBNET_ID,
    help="Subnet ID for subnet to be created under Vpc",
)
parser.add_argument("--project-id", default=PROJECT_ID, help="Custom Project ID")
parser.add_argument("--vpc-id", default=VPC_ID, help="Vpc ID")

args = parser.parse_args()
server = args.server
username = args.username
password = args.password
external_ip_cidr = args.external_ip_cidr
external_ip_id = args.external_ip_id
vpc_service_profile_id = args.vpc_service_profile_id
vpc_connectivity_profile_id = args.vpc_connectivity_profile_id
vpc_attachment_id = args.vpc_attachment_id
vpc_subnet_id = args.vpc_subnet_id
project_id = args.project_id
vpc_id = args.vpc_id
pp = PrettyPrinter()

try:
    policy_client = create_policy_client(server, username, password)
    transit_gateways = TransitGatewayListResult
    # Initialize service classes
    org_service = policy_client.Orgs
    ip_block_service = policy_client.infra.IpBlocks
    project_service = policy_client.orgs.Projects
    vpc_service = policy_client.orgs.projects.Vpcs
    transit_gateway_service = policy_client.orgs.projects.TransitGateways
    service_profile_service = policy_client.orgs.projects.VpcServiceProfiles
    vpc_connectivity_profile_service = (
        policy_client.orgs.projects.VpcConnectivityProfiles
    )
    subnet_service = policy_client.orgs.projects.vpcs.Subnets
    vpc_attachment_service = policy_client.orgs.projects.vpcs.Attachments

    # Read default org, make sure it exists.
    default_org = org_service.policy_lm_get_org(DEFAULT_NAME)

    external_ip_block = IpAddressBlock(
        cidr=external_ip_cidr,
        ip_address_type=IpAddressBlock.IP_ADDRESS_TYPE_IPV4,
        visibility=IpAddressBlock.VISIBILITY_EXTERNAL,
        id=external_ip_id,
    )
    # Please use ip_blocks.policy_lm_create_or_replace_ip_address_block() to catch exceptions while creating IP Blocks
    ip_block_service.policy_lm_create_or_patch_ip_address_block(
        external_ip_block.id, external_ip_block
    )
    external_ip_block = ip_block_service.policy_lm_read_ip_address_block(
        external_ip_block.id
    )
    print("External IP block path: ")
    pp.pprint(external_ip_block.path)

    custom_project = Project(
        id=project_id, external_ipv4_blocks=[external_ip_block.path]
    )
    project_service.policy_lm_update_project(
        default_org.id, custom_project.id, custom_project
    )
    custom_project = project_service.policy_lm_get_project(
        default_org.id, custom_project.id
    )
    custom_project.external_ipv4_blocks = [external_ip_block.path]
    project_service.policy_lm_update_project(
        default_org.id, custom_project.id, custom_project
    )
    transit_gateways = transit_gateway_service.policy_lm_list_transit_gateway(default_org.id, custom_project.id)
    default_transit_gateway_path = transit_gateways.results[0].path
    vpc_dhcp_advanced_config = VpcDhcpAdvancedConfig(is_distributed_dhcp=False)
    vpc_dhcp_server_config = VpcDhcpServerConfig(
        lease_time=86400, advanced_config=vpc_dhcp_advanced_config
    )
    vpc_profile_dhcp_config = VpcProfileDhcpConfig(
        dhcp_server_config=vpc_dhcp_server_config
    )

    vpc_service_profile = VpcServiceProfile(
        id=vpc_service_profile_id, dhcp_config=vpc_profile_dhcp_config
    )
    service_profile_service.policy_lm_patch_vpc_service_profile(
        default_org.id, custom_project.id, vpc_service_profile_id, vpc_service_profile
    )

    vpc = Vpc(id=vpc_id, vpc_service_profile=vpc_service_profile.path)
    vpc_service.policy_lm_update_vpc(default_org.id, custom_project.id, vpc_id, vpc)

    connectivity_profile = VpcConnectivityProfile(
        id=vpc_connectivity_profile_id,
        transit_gateway_path=default_transit_gateway_path,
        external_ip_blocks=[external_ip_block.path],
    )
    connectivity_profile = vpc_connectivity_profile_service.policy_lm_create_or_replace_vpc_connectivity_profile(
        default_org.id, custom_project.id, connectivity_profile.id, connectivity_profile
    )

    vpc_attachment = VpcAttachment(
        id=vpc_attachment_id, vpc_connectivity_profile=connectivity_profile.path
    )
    vpc_attachment_service.policy_lm_update_vpc_attachment(
        default_org.id, custom_project.id, vpc.id, vpc_attachment.id, vpc_attachment
    )

    subnet_dhcp_config = SubnetDhcpConfig(mode=SubnetDhcpConfig.MODE_DHCP_SERVER)
    vpc_subnet = VpcSubnet(
        id=vpc_subnet_id,
        access_mode=VpcSubnet.ACCESS_MODE_PUBLIC,
        ip_blocks=[external_ip_block.path],
        ipv4_subnet_size=16,
        subnet_dhcp_config=subnet_dhcp_config,
    )
    vpc_subnet = subnet_service.policy_lm_update_vpc_subnet(
        default_org.id, custom_project.id, vpc.id, vpc_subnet.id, vpc_subnet
    )
    print("Subnet Created: ")
    pp.pprint(vpc_subnet)

except Exception as e:
    print(f"Unexpected error: {e}")
