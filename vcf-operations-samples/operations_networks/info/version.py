# Copyright (c) 2025-2026 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import argparse

from operations_networks.helpers.client import create_vcf_operations_for_networks_client, get_unverified_session, StubFactoryType

parser = argparse.ArgumentParser()

parser.add_argument(
    '--server',
    required=True,
    help='VCF Operations Networks Instance Host Name')

parser.add_argument(
    '--user',
    required=False,
    help='VCF Operations Networks username (required if --token not provided)')

parser.add_argument(
    '--password',
    required=False,
    help='VCF Operations Networks password (required if --token not provided)')

parser.add_argument(
    '--token',
    required=False,
    help='Pre-generated authentication token (optional, if provided username/password not required)')

args = parser.parse_args()
server = args.server
user = args.user
password = args.password
token = args.token

# Validate that either token or username/password is provided
if not token and (not user or not password):
    parser.error("Either --token or both --user and --password must be provided")

session = get_unverified_session()
ops_networks_client = create_vcf_operations_for_networks_client(
    server=server,
    username=user,
    password=password,
    token=token,
    session=session,
    stub_factory_type=StubFactoryType.INFO)

print("=" * 80)
print("VCF Operations for Networks - Version API Examples")
print("=" * 80)

# Example 1: Get version information
print("\n[1] Getting VCF Operations for Networks version info...")
try:
    version_info = ops_networks_client.Version.get_version()
    print(f"✓ Version information retrieved successfully")
    print("Version Details: ", version_info)
    
    if version_info:
        # Display all available attributes
        print("\nVersion Details:")
        print(f"  - api_version: ", version_info.api_version)
        print(f"  - version_string: ", version_info.version_string)
except Exception as e:
    print(f"✗ Error getting version information: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("Examples completed")
print("=" * 80)
