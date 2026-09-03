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
    required=True,
    help='Application name for creation')

parser.add_argument(
    '--tier-name',
    required=True,
    help='Tier name for creation')

args = parser.parse_args()
server = args.server
user = args.user
password = args.password
token = args.token
app_name = args.app_name
tier_name = args.tier_name

# Validate that either token or username/password is provided
if not token and (not user or not password):
    parser.error("Either --token or both --user and --password must be provided")

session = get_unverified_session()

# Create client for Groups API (general groups operations)
ops_networks_client_groups = create_vcf_operations_for_networks_client(
    server=server,
    username=user,
    password=password,
    token=token,
    session=session,
    stub_factory_type=StubFactoryType.GROUPS)

# Create client for Groups Applications API (application-specific operations)
ops_networks_client_groups_applications = create_vcf_operations_for_networks_client(
    server=server,
    username=user,
    password=password,
    token=token,
    session=session,
    stub_factory_type=StubFactoryType.GROUPS_APPLICATIONS)

print("=" * 80)
print("VCF Operations for Networks - Tiers API Complete Workflow")
print("=" * 80)
print(f"Application Name: {app_name}")
print(f"Tier Name: {tier_name}")
print("=" * 80)

from vcf.operations_networks.model_client import (
    ApplicationRequest,
    TierRequest,
    GroupMembershipCriteria,
    SearchMembershipCriteria
)

# Variables to store IDs
created_app_id = None
created_tier_id = None

# Step 1: Create Application
print(f"\n[Step 1] Creating application '{app_name}'...")
try:
    app_request = ApplicationRequest(
        name=app_name,
    )
    
    new_app = ops_networks_client_groups.Applications.add_application(
        application_request=app_request)
    
    created_app_id = new_app.entity_id
    print(f"✓ Application created successfully")
    print(f"  - Application ID: {created_app_id}")
    print(f"  - Application Name: {new_app.name}")
    
except Exception as e:
    print(f"✗ Error creating application: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 2: Add Tier to Application
print(f"\n[Step 2] Adding tier '{tier_name}' to application '{app_name}'...")
try:
    # Create search membership criteria
    # This defines the search criteria for including entities in the tier
    search_criteria = SearchMembershipCriteria(
        entity_type='VirtualMachine',  
        filter="security_groups.entity_id = '18230:82:604573173'"
    )
    
    # Create group membership criteria for the tier
    # This defines how VMs/entities are included in this tier
    membership_criteria = GroupMembershipCriteria(
        membership_type='SearchMembershipCriteria',
        search_membership_criteria=search_criteria,  # Use the search criteria created above
    )
    
    # Create new tier object with all required parameters
    new_tier = TierRequest(
        name=tier_name,
        group_membership_criteria=[membership_criteria],  # Pass as a list
    )
    
    added_tier = ops_networks_client_groups_applications.Tiers.add_tier(
        id=created_app_id,
        tier_request=new_tier)
    
    # Get the tier ID from the added tier
    created_tier_id = added_tier.id if hasattr(added_tier, 'id') else None
                
    print(f"✓ Tier added successfully")
    created_tier_id = added_tier.entity_id
    print(f"  - Tier ID: {created_tier_id}")
    print(f"  - Tier Name: {added_tier.name}")
    print(f"  - Application ID: {added_tier.application.entity_id}")
    print(f"  - Tier: {added_tier}")
    
except Exception as e:
    print(f"✗ Error adding tier: {e}")
    import traceback
    traceback.print_exc()
    # Continue to cleanup even if tier creation fails

# Step 3: List Tiers (by listing application and showing its tiers)
print(f"\n[Step 3] Listing tiers in application '{app_name}'...")
try:
    tiers_response = ops_networks_client_groups_applications.Tiers.list_application_tiers(
        id=created_app_id)
    
    print(f"✓ Tiers retrieved successfully")
    print(f"  - Tiers: {tiers_response}")
    
    # Check if we have results
    if hasattr(tiers_response, 'results') and tiers_response.results:
        print(f"  - Total Tiers: {len(tiers_response.results)}")
        print(f"  - Tiers in application '{app_name}':")
        
        # Iterate through each tier and display details
        for idx, tier in enumerate(tiers_response.results, 1):
            tier_id = tier.entity_id if hasattr(tier, 'entity_id') else 'N/A'
            tier_name_display = tier.name if hasattr(tier, 'name') else 'N/A'
            
            print(f"\n    [{idx}] Tier:")
            print(f"        - Tier ID: {tier_id}")
            print(f"        - Tier Name: {tier_name_display}")
            
            # Display additional tier properties if available
            if hasattr(tier, 'group_membership_criteria'):
                print(f"        - Membership Criteria: {len(tier.group_membership_criteria)} criteria defined")
            
            # Get detailed tier information using Tiers.get_tier
            if tier_id != 'N/A':
                try:
                    tier_detail = ops_networks_client_groups.Tiers.get_tier(tier_id=tier_id)
                    if hasattr(tier_detail, 'member_count'):
                        print(f"        - Member Count: {tier_detail.member_count}")
                except Exception as e:
                    print(f"        - Could not fetch detailed tier info: {e}")
    else:
        print(f"  ⚠ No tiers found in application")
        
except Exception as e:
    print(f"✗ Error listing tiers: {e}")
    import traceback
    traceback.print_exc()

# Step 4: Delete Tier
print(f"\n[Step 4] Deleting tier '{tier_name}' - '{created_tier_id}' from application...")
try:
    if created_tier_id:
        ops_networks_client_groups_applications.Tiers.delete_tier(
            id=created_app_id,
            tier_id=created_tier_id)
        
        print(f"✓ Tier deleted successfully")
        print(f"  - Deleted Tier ID: {created_tier_id}")
    else:
        print(f"⚠ No tier ID available to delete")
        
except Exception as e:
    print(f"✗ Error deleting tier: {e}")
    import traceback
    traceback.print_exc()

# Step 5: Delete Application
print(f"\n[Step 5] Deleting application '{app_name}'...")
try:
    if created_app_id:
        ops_networks_client_groups.Applications.delete_application(id=created_app_id)
        print(f"✓ Application deleted successfully")
        print(f"  - Deleted Application ID: {created_app_id}")
        print(f"  - Deleted Application Name: {app_name}")
    else:
        print(f"⚠ No application ID available to delete")
        
except Exception as e:
    print(f"✗ Error deleting application: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("Workflow completed successfully!")
print("=" * 80)
print("\nSummary:")
print(f"  1. ✓ Created application: {app_name}")
print(f"  2. ✓ Added tier: {tier_name}")
print(f"  3. ✓ Listed tiers in application")
print(f"  4. ✓ Deleted tier: {tier_name}")
print(f"  5. ✓ Deleted application: {app_name}")
print("=" * 80)
