# Copyright (c) 2025-2026 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import argparse
import time

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

parser.add_argument(
    '--operation',
    required=False,
    default='get',
    choices=['get', 'save', 'update', 'delete'],
    help='Watermark operation to perform (default: get)')

args = parser.parse_args()
server = args.server
user = args.user
password = args.password
token = args.token
operation = args.operation

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
print("VCF Operations for Networks - Watermark Operations Examples")
print("=" * 80)

# Example 1: Get current watermark (baseline)
if operation == 'get':
    print("\n[1] Getting current VCF Watermark configuration...")
    try:
        current_watermark = ops_networks_client.Watermark.get_vcf_watermark()
    
        if current_watermark:
            print(f"✓ Current watermark exists:")
            if hasattr(current_watermark, '__dict__'):
                for key, value in current_watermark.__dict__.items():
                    print(f"  - {key}: {value}")
        else:
            print("✓ No current watermark configuration")
        
    except Exception as e:
        print(f"✗ Error getting watermark: {e}")

# Example 2: Save new watermark configuration
if operation == 'save':
    print("\n[2] Saving new VCF Watermark configuration...")
    try:
        from vcf.operations_networks.model_client import VCFWatermarkConfiguration
        
        # Create watermark configuration
        new_watermark_config = VCFWatermarkConfiguration()
        
        # Set watermark properties
        if hasattr(new_watermark_config, 'managedby'):
            new_watermark_config.managedby = "abc.com"
        if hasattr(new_watermark_config, 'version'):
            new_watermark_config.version = "vcf-4.0"
        if hasattr(new_watermark_config, 'logtoken'):
            new_watermark_config.logtoken = "VCF"
        if hasattr(new_watermark_config, 'deployedby'):
            new_watermark_config.deployedby = "VMware Cloud Foundation"
        if hasattr(new_watermark_config, 'instanceid'):
            new_watermark_config.instanceid = "UUID-1234"

        print(f"  Saving watermark with configuration:")
        saved_watermark = ops_networks_client.Watermark.save_vcf_watermark(
            v_cf_watermark_configuration=new_watermark_config)
        
        print(f"✓ Watermark saved successfully:")
        if saved_watermark:
            print("Saved watermark : ", saved_watermark)
                
    except Exception as e:
        print(f"✗ Error saving watermark: {e}")
        import traceback
        traceback.print_exc()

# Example 3: Update existing watermark configuration
if operation == 'update':
    print("\n[3] Updating existing VCF Watermark configuration...")
    try:
        from vcf.operations_networks.model_client import VCFWatermarkConfiguration
        
        # First, get current watermark to update
        try:
            current = ops_networks_client.Watermark.get_vcf_watermark()
        except:
            current = None
        
        if current:
            print(f"✓ Current watermark found, updating...")
            
            # Create updated configuration
            updated_config = VCFWatermarkConfiguration()
            
            # Set watermark properties
            if hasattr(updated_config, 'managedby'):
                updated_config.managedby = "abc.com"
            if hasattr(updated_config, 'version'):
                updated_config.version = "vcf-4.0"
            if hasattr(updated_config, 'logtoken'):
                updated_config.logtoken = "VCF"
            if hasattr(updated_config, 'deployedby'):
                updated_config.deployedby = "VMware Cloud Foundation"
            if hasattr(updated_config, 'instanceid'):
                updated_config.instanceid = "UUID-5678"
            
            print(f"  Updating watermark with new properties...")
            
            updated_watermark = ops_networks_client.Watermark.update_vcf_watermark(
                v_cf_watermark_configuration=updated_config)
            
            print(f"✓ Watermark updated successfully:")
            if updated_watermark:
                print("Updated watermark : ", updated_watermark)
        else:
            print("✗ No existing watermark to update. Create one first with --operation save")
            
    except Exception as e:
        print(f"✗ Error updating watermark: {e}")
        import traceback
        traceback.print_exc()

# Example 4: Delete watermark configuration
if operation == 'delete':
    print("\n[4] Deleting VCF Watermark configuration...")
    try:
        print("⚠️  WARNING: This will delete the watermark configuration!")
        print("    Watermarks are typically managed by VCF deployment tools.")
        print("    Only proceed if you understand the implications.\n")
        
        # Check if watermark exists before deletion
        try:
            existing = ops_networks_client.Watermark.get_vcf_watermark()
            if not existing:
                print("✗ No watermark found to delete")
            else:
                print("✓ Watermark exists, proceeding with deletion...")
                ops_networks_client.Watermark.delete_vcf_watermark()
                print("✓ Watermark deleted successfully")
        except Exception as check_err:
            print(f"✗ Error checking watermark before deletion: {check_err}")
            
    except Exception as e:
        print(f"✗ Error deleting watermark: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print("Watermark Operations Guide")
print("=" * 80)
print("""
Available Operations:
  --operation get      : Retrieve current watermark (default)
  --operation save     : Create new watermark configuration
  --operation update   : Update existing watermark
  --operation delete   : Delete watermark configuration

Examples:
  # Get watermark
  python watermark_operations.py --server <ip> --user <user> --password <pass>

  # Save new watermark
  python watermark_operations.py --server <ip> --user <user> --password <pass> --operation save

  # Update watermark
  python watermark_operations.py --server <ip> --user <user> --password <pass> --operation update

  # Delete watermark
  python watermark_operations.py --server <ip> --user <user> --password <pass> --operation delete

⚠️  IMPORTANT NOTES:
  - Watermarks are typically managed by VCF deployment tools
  - Only modify watermarks if you understand the implications
  - Admin privileges required for all watermark operations
  - Deleting watermarks may affect VCF tracking and deployment records
  - Always backup current configuration before modifying watermarks
""")
print("=" * 80)
