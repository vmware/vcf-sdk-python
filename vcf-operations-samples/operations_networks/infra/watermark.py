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
    help='Pre-generated authentication token (optional)')

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
    stub_factory_type=StubFactoryType.INFRA)

print("=" * 80)
print("VCF Operations for Networks - Watermark API Examples")
print("=" * 80)

# Example 1: Get VCF Watermark
print("\n[1] Getting VCF Watermark configuration...")
try:
    watermark = ops_networks_client.Watermark.get_vcf_watermark()
    
    if watermark:
        print(f"✓ VCF Watermark retrieved successfully:")
        
        # Display watermark properties
        if hasattr(watermark, '__dict__'):
            for key, value in watermark.__dict__.items():
                print(f"  - {key}: {value}")
        else:
            print(f"  Watermark Details: {watermark}")
    else:
        print("✓ Watermark retrieved (empty/None)")
        
except Exception as e:
    print(f"✗ Error getting watermark: {e}")
    import traceback
    traceback.print_exc()

# Example 2: Display watermark information
print("\n[2] Displaying watermark information...")
try:
    watermark = ops_networks_client.Watermark.get_vcf_watermark()
    
    if watermark:
        print(f"\n✓ VCF Watermark Configuration:")
        print("─" * 60)
        
        # Try to display common watermark properties
        properties = [
            'vcf_id',
            'vcf_version',
            'deployment_id',
            'product_name',
            'deployment_info',
            'creation_timestamp',
            'update_timestamp'
        ]
        
        for prop in properties:
            if hasattr(watermark, prop):
                value = getattr(watermark, prop)
                print(f"  {prop}: {value}")
        
        print("─" * 60)
    else:
        print("  No watermark information available")
        
except Exception as e:
    print(f"✗ Error displaying watermark: {e}")

# Example 3: Check watermark status
print("\n[3] Checking VCF watermark status...")
try:
    watermark = ops_networks_client.Watermark.get_vcf_watermark()
    
    if watermark:
        print(f"✓ Watermark Status:")
        print(f"  - Watermark Exists: Yes")
        
        if hasattr(watermark, 'vcf_id'):
            print(f"  - VCF ID: {watermark.vcf_id}")
        if hasattr(watermark, 'vcf_version'):
            print(f"  - VCF Version: {watermark.vcf_version}")
            
        # Check for specific properties
        has_properties = []
        for attr in dir(watermark):
            if not attr.startswith('_'):
                has_properties.append(attr)
        
        if has_properties:
            print(f"  - Available Properties Count: {len(has_properties)}")
            print(f"  - Available Properties: {has_properties}")
    else:
        print(f"✓ Watermark Status:")
        print(f"  - Watermark Exists: No")
        
except Exception as e:
    print(f"✗ Error checking watermark status: {e}")

print("\n" + "=" * 80)
print("Watermark Examples - NOTES:")
print("=" * 80)
print("""
Note: The Watermark API provides the following operations:
  - get_vcf_watermark()      : Retrieve current watermark configuration
  - save_vcf_watermark(cfg)  : Create/save new watermark (requires configuration)
  - update_vcf_watermark(cfg): Update existing watermark (requires configuration)
  - delete_vcf_watermark()   : Delete watermark configuration

The watermark records VCF deployment information and is typically managed
by VCF deployment tools. Direct modification through this API is typically
not recommended unless specifically needed.
""")
print("=" * 80)
