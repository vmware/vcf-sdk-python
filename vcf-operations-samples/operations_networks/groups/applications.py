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

parser.add_argument(
    '--app-name',
    required=False,
    help='Application name for create/delete operations')

parser.add_argument(
    '--app-id',
    required=False,
    help='Application ID for get/delete operations')

args = parser.parse_args()
server = args.server
user = args.user
password = args.password
token = args.token
app_name = args.app_name
app_id = args.app_id

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
    stub_factory_type=StubFactoryType.GROUPS)

print("=" * 80)
print("VCF Operations for Networks - Applications API Examples")
print("=" * 80)

# Example 1: List all applications
print("\n[1] Listing all applications...")
try:
    app_list = ops_networks_client.Applications.list_applications()
    print(f"✓ Found {len(app_list.results) if app_list and app_list.results else 0} applications")
    if app_list and app_list.results:
        for app in app_list.results:
            print(f"Application: ", app)
#             app_id = app.entity_id
except Exception as e:
    print(f"✗ Error listing applications: {e}")

# Example 2: List applications with pagination
print("\n[2] Listing applications with pagination (size=10)...")
try:
    app_list = ops_networks_client.Applications.list_applications()
    print(f"✓ Retrieved page of applications")
    if app_list and app_list.results:
        print(f"  Total results in this page: {len(app_list.results)}")
        if app_list.cursor:
            print(f"  Cursor for next page: {app_list.cursor}")
except Exception as e:
    print(f"✗ Error listing applications with pagination: {e}")
    traceback.print_exc()

# Example 3: Get application by ID
if app_id:
    print(f"\n[3] Getting application details for ID: {app_id}...")
    try:
        app_detail = ops_networks_client.Applications.get_application_by_id(
            id=app_id,
            fetch_member_counts=True,
            fetch_update_status=True)
        print(f"✓ Application details retrieved:")
        print(f"  - ID: {app_detail.entity_id}")
        print(f"  - Name: {app_detail.name}")
        print(f"  - Details: {app_detail}")

    except Exception as e:
        print(f"✗ Error getting application: {e}")
else:
    print("\n[3] Skipping get application by ID (use --app-id to test)")

# Example 4: Create a new application
if app_name:
    print(f"\n[4] Creating new application: {app_name}...")
    try:
        from vcf.operations_networks.model_client import ApplicationRequest
        
        app_request = ApplicationRequest(
            name=app_name,
        )
        
        new_app = ops_networks_client.Applications.add_application(
            application_request=app_request)
        
        print(f"✓ Application created successfully:")
        print(f"  - ID: {new_app.entity_id}")
        print(f"  - Name: {new_app.name}")
        print("New App - :", new_app)
        
        # Store the new app ID for deletion example
        created_app_id = new_app.entity_id
        
        # List applications after creation to verify
        print(f"\n[4.1] Listing all applications after creation...")
        try:
            app_list_after = ops_networks_client.Applications.list_applications()
            print(f"✓ Found {len(app_list_after.results) if app_list_after and app_list_after.results else 0} applications")
            if app_list_after and app_list_after.results:
                for app in app_list_after.results:
                    print(f"  Application: {app} ")
        except Exception as e:
            print(f"✗ Error listing applications after creation: {e}")
        
        # Example 5: Delete the application
        print(f"\n[5] Deleting application: {created_app_id}...")
        try:
            ops_networks_client.Applications.delete_application(id=created_app_id)
            print(f"✓ Application deleted successfully")
        except Exception as e:
            print(f"✗ Error deleting application: {e}")
            
    except Exception as e:
        print(f"✗ Error creating application: {e}")
else:
    print("\n[4] Skipping create application (use --app-name to test)")
    print("\n[5] Skipping delete application")

print("\n" + "=" * 80)
print("Examples completed")
print("=" * 80)
