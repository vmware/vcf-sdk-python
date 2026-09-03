#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights
# The term "Broadcom" refers to Broadcom
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import argparse

from utils.client import create_policy_client
from vcf.nsx.model_client import IpAddressBlock
from vmware.vapi.bindings.struct import PrettyPrinter

"""
The example shows fetching IP usage of a created IP block
under a default Project, in Vmware NSX.

Sample prerequisites: NSX Manager instance.

APIs used:
- Create IP block: PUT /policy/api/v1/infra/ip-blocks/{ip-block-id}
- Get IP block: GET /policy/api/v1/infra/ip-blocks/{ip-block-id}
- GET IP Usage: GET /infra/ip-blocks/usage
"""

# Default values of optional parameters, in case they are not provided as command line arguments.
EXTERNAL_IP_BLOCK_CIDR = "142.2.3.0/24"
EXTERNAL_IP_ID = "external-ip"

parser = argparse.ArgumentParser()
parser.add_argument("--server", required=True, help="NSX Host Name")
parser.add_argument("--user", required=True, help="NSX username", dest="username")
parser.add_argument("--password", required=True, help="NSX password")
parser.add_argument(
    "--external-ip-block-cidr",
    default=EXTERNAL_IP_BLOCK_CIDR,
    help="IP Block Cidr used to create an IP Block of Type EXTERNAL",
)
parser.add_argument(
    "--external-ip-id", default=EXTERNAL_IP_ID, help="ID of IP Block of Type EXTERNAL"
)

args = parser.parse_args()
server = args.server
username = args.username
password = args.password
external_ip_block_cidr = args.external_ip_block_cidr
external_ip_id = args.external_ip_id
pp = PrettyPrinter()

try:
    policy_client = create_policy_client(server, username, password)
    # Initialize service classes required: IpBlock Service, Usage Service.
    infra_service = policy_client.infra.IpBlocks
    ip_block_service = policy_client.infra.ip_blocks.Usage

    # Create an external IP block
    ip_block = IpAddressBlock(
        cidr=external_ip_block_cidr,
        ip_address_type=IpAddressBlock.IP_ADDRESS_TYPE_IPV4,
        visibility=IpAddressBlock.VISIBILITY_EXTERNAL,
        id=external_ip_id,
    )

    infra_service.policy_lm_create_or_patch_ip_address_block(ip_block.id, ip_block)

    # Get External IP Blocks
    ip_block = infra_service.policy_lm_read_ip_address_block(ip_block.id)
    print("External Ip block: ")
    pp.pprint(ip_block)

    ip_address_usage = ip_block_service.policy_lm_get_ip_address_block_usage(
        ip_block.id
    )
    print("External Ip block usage: ")
    pp.pprint(ip_address_usage)

except Exception as e:
    print(f"Unexpected error: {e}")
