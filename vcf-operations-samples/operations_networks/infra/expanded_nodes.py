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
print("VCF Operations for Networks - Expanded Nodes API Examples")
print("=" * 80)

# Example 1: List all expanded nodes
print("\n[1] Listing all infrastructure nodes with full details...")
try:
    expanded_node_list = ops_networks_client.ExpandedNodes.list_expanded_nodes()
    
    if expanded_node_list and hasattr(expanded_node_list, 'results'):
        print(f"✓ Found {len(expanded_node_list.results)} infrastructure nodes")
        
        for i, node in enumerate(expanded_node_list.results, 1):
            print(f"\n  Node {i}:")
            if hasattr(node, 'id'):
                print(f"    - ID: {node.id}")
            if hasattr(node, 'name'):
                print(f"    - Name: {node.name}")
            if hasattr(node, 'ip_address'):
                print(f"    - IP Address: {node.ip_address}")
            if hasattr(node, 'node_type'):
                print(f"    - Type: {node.node_type}")
            if hasattr(node, 'version'):
                print(f"    - Version: {node.version}")
            if hasattr(node, 'status'):
                print(f"    - Status: {node.status}")
    else:
        print(f"✓ Expanded node list retrieved")
        print(f"  Result: {expanded_node_list}")
        
except Exception as e:
    print(f"✗ Error listing expanded nodes: {e}")
    import traceback
    traceback.print_exc()

# Example 2: Detailed node information display
print("\n[2] Displaying detailed expanded node information...")
try:
    expanded_node_list = ops_networks_client.ExpandedNodes.list_expanded_nodes()
    
    if expanded_node_list and hasattr(expanded_node_list, 'results') and expanded_node_list.results:
        print(f"\n✓ Expanded Infrastructure Nodes Details:")
        print("─" * 120)
        print(f"{'Index':<6} {'ID':<25} {'Name':<20} {'IP Address':<20} {'Type':<15}")
        print("─" * 120)
        
        for i, node in enumerate(expanded_node_list.results, 1):
            node_id_display = str(node.id)[:24] if hasattr(node, 'id') else "N/A"
            node_name = str(node.name)[:19] if hasattr(node, 'name') else "N/A"
            ip_addr = str(node.ip_address)[:19] if hasattr(node, 'ip_address') else "N/A"
            node_type = str(node.node_type)[:14] if hasattr(node, 'node_type') else "N/A"
            
            print(f"{i:<6} {node_id_display:<25} {node_name:<20} {ip_addr:<20} {node_type:<15}")
        
        print("─" * 120)
        print(f"Total Expanded Nodes: {len(expanded_node_list.results)}")
    else:
        print("  No expanded nodes found or unable to retrieve list")
        
except Exception as e:
    print(f"✗ Error displaying expanded nodes: {e}")

# Example 3: Compare with regular nodes
print("\n[3] Comparing Nodes vs Expanded Nodes...")
try:
    regular_nodes = ops_networks_client.Nodes.list_nodes()
    expanded_nodes = ops_networks_client.ExpandedNodes.list_expanded_nodes()
    
    regular_count = len(regular_nodes.results) if (regular_nodes and hasattr(regular_nodes, 'results')) else 0
    expanded_count = len(expanded_nodes.results) if (expanded_nodes and hasattr(expanded_nodes, 'results')) else 0
    
    print(f"✓ Comparison Results:")
    print(f"  - Regular Nodes Count: {regular_count}")
    print(f"  - Expanded Nodes Count: {expanded_count}")
    print(f"  - Same Count: {'✓ Yes' if regular_count == expanded_count else '✗ No'}")
    
    # Show which properties are available in expanded nodes
    if expanded_nodes and hasattr(expanded_nodes, 'results') and expanded_nodes.results:
        sample_node = expanded_nodes.results[0]
        print(f"\n  Sample Expanded Node Properties:")
        if hasattr(sample_node, '__dict__'):
            for key, value in sample_node.__dict__.items():
                print(f"    - {key}: {type(value).__name__}")
                
except Exception as e:
    print(f"✗ Error in comparison: {e}")

print("\n" + "=" * 80)
print("Examples completed")
print("=" * 80)
