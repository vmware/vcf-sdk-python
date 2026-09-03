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
    '--node-id',
    required=False,
    help='Node ID to retrieve or delete')

args = parser.parse_args()
server = args.server
user = args.user
password = args.password
token = args.token
node_id = args.node_id

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
print("VCF Operations for Networks - Nodes API Examples")
print("=" * 80)

# Example 1: List all nodes
print("\n[1] Listing all infrastructure nodes...")
try:
    node_list = ops_networks_client.Nodes.list_nodes()
    
    if node_list and hasattr(node_list, 'results'):
        print(f"✓ Found {len(node_list.results)} infrastructure nodes")
        for i, node in enumerate(node_list.results, 1):
            print(f"\n  Node {i}:", node)
            if not node_id:
                node_id = node.id
    else:
        print(f"✓ Node list retrieved")
        print(f"  Result: {node_list}")
        
except Exception as e:
    print(f"✗ Error listing nodes: {e}")
    import traceback
    traceback.print_exc()

# Example 2: Get node by ID
if node_id:
    print(f"\n[2] Getting node details for ID: {node_id}...")
    try:
        node_detail = ops_networks_client.Nodes.get_node(id=node_id)
        print(f"✓ Node details retrieved:")
        
        if node_detail:
            if hasattr(node_detail, 'id'):
                print(f"  - ID: {node_detail.id}")
            if hasattr(node_detail, 'name'):
                print(f"  - Name: {node_detail.name}")
            if hasattr(node_detail, 'ip_address'):
                print(f"  - IP Address: {node_detail.ip_address}")
            if hasattr(node_detail, 'node_type'):
                print(f"  - Node Type: {node_detail.node_type}")
            if hasattr(node_detail, 'proxy_id'):
                print(f"  - Proxy ID: {node_detail.proxy_id}")
            if hasattr(node_detail, 'model_key'):
                print(f"  - Model Key: {node_detail.model_key}")
                
    except Exception as e:
        print(f"✗ Error getting node: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\n[2] Skipping get node by ID (use --node-id to test)")

# Example 3: Display all nodes with details
print("\n[3] Displaying all nodes with detailed information...")
try:
    node_list = ops_networks_client.Nodes.list_nodes()
    
    if node_list and hasattr(node_list, 'results') and node_list.results:
        print(f"\n✓ Infrastructure Nodes Summary:")
        print("─" * 80)
        print(f"{'Index':<6} {'ID':<20} {'Name':<20} {'IP Address':<20}")
        print("─" * 80)
        
        for i, node in enumerate(node_list.results, 1):
            node_id_display = str(node.id)[:19] if hasattr(node, 'id') else "N/A"
            node_name = str(node.name)[:19] if hasattr(node, 'name') else "N/A"
            ip_addr = str(node.ip_address)[:19] if hasattr(node, 'ip_address') else "N/A"
            
            print(f"{i:<6} {node_id_display:<20} {node_name:<20} {ip_addr:<20}")
        
        print("─" * 80)
        print(f"Total Nodes: {len(node_list.results)}")
    else:
        print("  No nodes found or unable to retrieve node list")
        
except Exception as e:
    print(f"✗ Error displaying nodes: {e}")

print("\n" + "=" * 80)
print("Examples completed")
print("=" * 80)
