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
    '--discovery-type',
    required=False,
    default='FLOW_BASED_DISCOVERY',
    help='Discovery type: SERVICE_NOW or FLOW_BASED_DISCOVERY (default: FLOW_BASED_DISCOVERY)')

parser.add_argument(
    '--granularity',
    required=False,
    default='MEDIUM',
    help='Granularity for flow-based discovery: FINE, MEDIUM, or COARSE (default: MEDIUM)')

parser.add_argument(
    '--page-size',
    required=False,
    type=int,
    default=20,
    help='Page size for paginated results (default: 20)')

args = parser.parse_args()
server = args.server
user = args.user
password = args.password
token = args.token
discovery_type = args.discovery_type
granularity = args.granularity
page_size = args.page_size

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
print("VCF Operations for Networks - Discovered Applications API Examples")
print("=" * 80)

# Example 1: Get discovered applications with default parameters
print("\n[1] Getting discovered applications (default parameters)...")
try:
    discovered_apps = ops_networks_client.DiscoveredApplications.get_discovered_applications(
        discovery_type='FLOW_BASED_DISCOVERY',
        granularity=granularity)
    print(f"✓ Retrieved discovered applications")
    if discovered_apps and discovered_apps.results:
        print(f"  Total results: {len(discovered_apps.results)}")
        for app in discovered_apps.results[:5]:  # Show first 5
            print(f"  - Application ID: {app.id}")
        if len(discovered_apps.results) > 5:
            print(f"  ... and {len(discovered_apps.results) - 5} more")
    else:
        print("  No discovered applications found")
except Exception as e:
    print(f"✗ Error getting discovered applications: {e}")

# Example 2: Get discovered applications with FLOW_BASED_DISCOVERY
print(f"\n[2] Getting discovered applications (FLOW_BASED_DISCOVERY, granularity={granularity})...")
try:
    discovered_apps = ops_networks_client.DiscoveredApplications.get_discovered_applications(
        discovery_type='FLOW_BASED_DISCOVERY',
        granularity=granularity)
    print(f"✓ Retrieved discovered applications (flow-based)")
    if discovered_apps and discovered_apps.results:
        print(f"  Total results in this page: {len(discovered_apps.results)}")
        if discovered_apps.cursor:
            print(f"  Cursor for next page: {discovered_apps.cursor}")
        # Display first few results
        for i, app in enumerate(discovered_apps.results[:3], 1):
            print(f"  [{i}] Application ID: {app.id}")
    else:
        print("  No flow-based discovered applications found")
except Exception as e:
    print(f"✗ Error getting flow-based discovered applications: {e}")

# Example 3: Get discovered applications with SERVICE_NOW discovery
print("\n[3] Getting discovered applications (SERVICE_NOW discovery type)...")
try:
    discovered_apps = ops_networks_client.DiscoveredApplications.get_discovered_applications(
        discovery_type='SERVICE_NOW')
    print(f"✓ Retrieved discovered applications (SERVICE_NOW)")
    if discovered_apps and discovered_apps.results:
        print(f"  Total results in this page: {len(discovered_apps.results)}")
        if discovered_apps.cursor:
            print(f"  Cursor for next page: {discovered_apps.cursor}")
        for i, app in enumerate(discovered_apps.results[:3], 1):
            print(f"  [{i}] Application ID: {app.id}")
    else:
        print("  No SERVICE_NOW discovered applications found")
except Exception as e:
    print(f"✗ Error getting SERVICE_NOW discovered applications: {e}")

# Example 4: Get discovered applications with FINE granularity
print("\n[4] Getting discovered applications (FLOW_BASED_DISCOVERY, FINE granularity)...")
try:
    discovered_apps = ops_networks_client.DiscoveredApplications.get_discovered_applications(
        discovery_type='FLOW_BASED_DISCOVERY',
        granularity='FINE')
    print(f"✓ Retrieved discovered applications (fine granularity)")
    if discovered_apps and discovered_apps.results:
        print(f"  Total results in this page: {len(discovered_apps.results)}")
        if discovered_apps.cursor:
            print(f"  Cursor for next page: {discovered_apps.cursor}")
    else:
        print("  No fine-granularity discovered applications found")
except Exception as e:
    print(f"✗ Error getting fine-granularity discovered applications: {e}")

# Example 5: Get discovered applications with COARSE granularity
print("\n[5] Getting discovered applications (FLOW_BASED_DISCOVERY, COARSE granularity)...")
try:
    discovered_apps = ops_networks_client.DiscoveredApplications.get_discovered_applications(
        discovery_type='FLOW_BASED_DISCOVERY',
        granularity='COARSE')
    print(f"✓ Retrieved discovered applications (coarse granularity)")
    if discovered_apps and discovered_apps.results:
        print(f"  Total results in this page: {len(discovered_apps.results)}")
        if discovered_apps.cursor:
            print(f"  Cursor for next page: {discovered_apps.cursor}")
    else:
        print("  No coarse-granularity discovered applications found")
except Exception as e:
    print(f"✗ Error getting coarse-granularity discovered applications: {e}")

# Example 6: Paginate through discovered applications
print("\n[6] Paginating through discovered applications...")
try:
    cursor = None
    page_count = 0
    total_apps = 0
    
    while page_count < 3:  # Limit to 3 pages for demo
        discovered_apps = ops_networks_client.DiscoveredApplications.get_discovered_applications(
            discovery_type='FLOW_BASED_DISCOVERY',
            granularity='MEDIUM',
            cursor=cursor)
        
        if discovered_apps and discovered_apps.results:
            page_count += 1
            total_apps += len(discovered_apps.results)
            print(f"  Page {page_count}: {len(discovered_apps.results)} applications")
            
            if not discovered_apps.cursor:
                print("  No more pages available")
                break
            
            cursor = discovered_apps.cursor
        else:
            print("  No results found")
            break
    
    print(f"✓ Retrieved {total_apps} applications across {page_count} pages")
except Exception as e:
    print(f"✗ Error paginating discovered applications: {e}")

print("\n" + "=" * 80)
print("Examples completed")
print("=" * 80)
