#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights
# The term "Broadcom" refers to Broadcom
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import argparse

from utils.client import create_policy_client
from vcf.nsx.model_client import (
    Project,
    Vpc,
    VpcDhcpRelayConfig,
    VpcProfileDhcpConfig,
    VpcServiceProfile,
)
from vmware.vapi.bindings.struct import PrettyPrinter

"""
The example shows basic creation operation of a Vpc Service Profile and a VPC
under a default Project, in Vmware NSX.

Sample prerequisites: NSX Manager instance with default org created.

APIs used:
- Create custom project: PUT /policy/api/v1/orgs/{org-id}/projects/{project-id}
- Get custom project: GET /policy/api/v1/orgs/{org-id}/projects/{project-id}
- Create Vpc Service Profile: PUT /policy/api/v1/orgs/{org-id}/projects/{project-id}/vpc-service-profiles/{vpc-service-profile-id}
- Create VPC: PUT /policy/api/v1/orgs/{org-id}/projects/{project-id}/vpcs/{vpc-id}
"""

# Constants to create VPC, with example values, please modify as required.
DHCP_SERVER_ADDRESS = "20.24.2.3"
SERVICE_PROFILE_ID = "VCF-NSX-SDK-vpc-service-profile"
VPC_PRIVATE_IPS = "10.1.1.0/24"
PROJECT_ID = "VCF-NSX-SDK-project1"
VPC_ID = "VCF-NSX-SDK-custom-vpc1"

# Keyword is reserved for Default objects.
DEFAULT = "default"

parser = argparse.ArgumentParser()
parser.add_argument("--server", required=True, help="NSX Host Name")
parser.add_argument("--user", required=True, help="NSX username", dest="username")
parser.add_argument("--password", required=True, help="NSX password")
parser.add_argument(
    "--dhcp-server-address",
    default=DHCP_SERVER_ADDRESS,
    help="DHCP Server address to be set in Vpc Service Config",
)
parser.add_argument(
    "--service-profile-id", default=SERVICE_PROFILE_ID, help="Vpc Service Profile id"
)
parser.add_argument(
    "--vpc-private-ips", default=VPC_PRIVATE_IPS, help="Vpc Private Ip CIDR"
)
parser.add_argument(
    "--project-id", default=PROJECT_ID, help="Project ID for custom project"
)
parser.add_argument("--vpc-id", default=VPC_ID, help="Vpc ID to be created")

args = parser.parse_args()
server = args.server
username = args.username
password = args.password
dhcp_server_address = args.dhcp_server_address
service_profile_id = args.service_profile_id
vpc_private_ips = args.vpc_private_ips
project_id = args.project_id
vpc_id = args.vpc_id
pp = PrettyPrinter()

try:
    policy_client = create_policy_client(server, username, password)
    # Initialize service classes
    org_service = policy_client.Orgs
    project_service = policy_client.orgs.Projects
    vpc_service = policy_client.orgs.projects.Vpcs
    service_profile_service = policy_client.orgs.projects.VpcServiceProfiles

    # Read default org, make sure it exists.
    default_org = org_service.policy_lm_get_org(DEFAULT)

    custom_project = Project(
        id=project_id,
        activate_default_dfw_rules=False,
    )

    project_service.policy_lm_update_project(
        default_org.id, custom_project.id, custom_project
    )
    print("Custom Project Created under default org: ")
    pp.pprint(custom_project.id)
    custom_project = project_service.policy_lm_get_project(
        default_org.id, custom_project.id
    )
    print("Custom Project fetched: ")
    pp.pprint(custom_project)
    server_addresses_list = [dhcp_server_address]
    vpc_dhcp_relay_config = VpcDhcpRelayConfig(server_addresses=server_addresses_list)
    vpc_profile_dhcp_config = VpcProfileDhcpConfig(
        dhcp_relay_config=vpc_dhcp_relay_config,
    )
    vpc_service_profile = VpcServiceProfile(
        id=service_profile_id, dhcp_config=vpc_profile_dhcp_config
    )
    service_profile_service.policy_lm_create_or_replace_vpc_service_profile(
        default_org.id, custom_project.id, service_profile_id, vpc_service_profile
    )

    vpc = Vpc(id=vpc_id, vpc_service_profile=vpc_service_profile.path)
    vpc_service.policy_lm_update_vpc(default_org.id, custom_project.id, vpc_id, vpc)
    vpc = vpc_service.policy_lm_get_vpc(default_org.id, custom_project.id, vpc_id)

    print("Vpc Created: ")
    pp.pprint(vpc)
except Exception as exception:
    print(f"Unexpected error: {exception}")
