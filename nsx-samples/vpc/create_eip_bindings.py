#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import argparse

from utils.client import create_policy_client
from vcf.nsx.model_client import PortAddressBindingEntry, VpcSubnetPort
from vmware.vapi.bindings.struct import PrettyPrinter

"""
The example shows creation operation of EIP Port Bindings
for a given VPC Subnet.

Sample prerequisites: NSX Manager instance with default org, Project, VPC, VPC Subnet created.

APIs used:
- Create custom project: PUT /policy/api/v1/orgs/{org-id}/projects/{project-id}/vpcs/{vpc-id}/subnets/{subnet-id}/ports/{port-id}
"""

# Keyword is reserved for Default objects, do not modify.
DEFAULT = "default"

# Default values of optional parameters, in case they are not provided as command line arguments.
VCF_NSX_SDK_VPC_SUBNET_ID = "VCF-NSX-SDK-vpcSubnet"
PROJECT_ID = "VCF-NSX-SDK-Project"
VPC_ID = "VCF-NSX-SDK-VPC"
VCF_NSX_SDK_VPC_SUBNET_PORT_ID = "VCF-NSX-SDK-vpcSubnetPort"
EXTERNAL_IP_CIDR = "11.11.40.0/24"
EXTERNAL_MAC_ADDRESS = "aa:bb:cc:dd:ee:f1"

parser = argparse.ArgumentParser()
parser.add_argument("--server", required=True, help="NSX Host Name")
parser.add_argument("--user", required=True, help="NSX username", dest="username")
parser.add_argument("--password", required=True, help="NSX password")
parser.add_argument("--project-id", default=PROJECT_ID, help="Custom project ID")
parser.add_argument("--vpc-id", default=VPC_ID, help="VPC ID")
parser.add_argument("--subnet-id", default=VCF_NSX_SDK_VPC_SUBNET_ID, help="Subnet ID")
parser.add_argument(
    "--subnet-port-id", default=VCF_NSX_SDK_VPC_SUBNET_PORT_ID, help="Subnet Port ID"
)
parser.add_argument(
    "--external-ip-cidr",
    default=EXTERNAL_IP_CIDR,
    help="External IP CIDR used to create Subnet port",
)
parser.add_argument(
    "--external-mac-address",
    default=EXTERNAL_MAC_ADDRESS,
    help="External MAC address used to create Subnet port",
)

args = parser.parse_args()
server = args.server
username = args.username
password = args.password
project_id = args.project_id
vpc_id = args.vpc_id
subnet_id = args.subnet_id
subnet_port_id = args.subnet_port_id
external_ip_cidr = args.external_ip_cidr
external_mac_address = args.external_mac_address
pp = PrettyPrinter()

try:
    policy_client = create_policy_client(server, username, password)
    # Initialize service classes required to create VPC: Subnet Service, Port Service.
    vpc_subnet_service = policy_client.orgs.projects.vpcs.Subnets
    vpc_subnet_port_service = policy_client.orgs.projects.vpcs.subnets.Ports

    # Fetch subnet to create IP bindings
    subnet = vpc_subnet_service.policy_lm_get_vpc_subnet(
        DEFAULT, project_id, vpc_id, subnet_id
    )
    print("Fetched Subnet: ")
    pp.pprint(subnet)
    address_binding = PortAddressBindingEntry(
        ip_address=external_ip_cidr, mac_address=external_mac_address
    )
    subnet_port = VpcSubnetPort(id=subnet_port_id, address_bindings=[address_binding])
    subnet_port = vpc_subnet_port_service.policy_lm_update_vpc_subnet_port(
        DEFAULT, project_id, vpc_id, subnet_id, subnet_port_id, subnet_port
    )

    print("Created Subnet port: ")
    pp.pprint(subnet_port)
except Exception as exception:
    print(f"Unexpected error: {exception}")
