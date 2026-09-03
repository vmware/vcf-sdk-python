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
    '--entity-id',
    required=False,
    help='Entity ID for get operations')

parser.add_argument(
    '--page-size',
    required=False,
    type=int,
    default=10,
    help='Page size for paginated results (default: 10)')

args = parser.parse_args()
server = args.server
user = args.user
password = args.password
token = args.token
entity_id = args.entity_id
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
    stub_factory_type=StubFactoryType.ENTITIES)

print("=" * 80)
print("VCF Operations for Networks - Entities API Examples")
print("=" * 80)

# Example 1: List VMs
print("\n[1] Listing Virtual Machines...")
try:
    vms_list = ops_networks_client.Vms.list_vms()
    print(f"✓ Found {len(vms_list.results) if vms_list and vms_list.results else 0} VMs")
    if vms_list and vms_list.results:
        for i, vm in enumerate(vms_list.results[:3], 1):
            print(f"  [{i}] VM ID: {vm.entity_id if hasattr(vm, 'entity_id') else 'N/A'}")
            print(f"      Name: {vm.name if hasattr(vm, 'name') else 'N/A'}")
        if len(vms_list.results) > 3:
            print(f"  ... and {len(vms_list.results) - 3} more")
        if vms_list.cursor:
            print(f"  Cursor for next page: {vms_list.cursor}")
except Exception as e:
    print(f"✗ Error listing VMs: {e}")
    import traceback
    traceback.print_exc()

# Example 2: Get specific VM details
if entity_id:
    print(f"\n[2] Getting VM details for ID: {entity_id}...")
    try:
        vm_detail = ops_networks_client.Vms.get_vm(id=entity_id)
        print(f"✓ VM details retrieved:")
        print(f"  - ID: {vm_detail.entity_id if hasattr(vm_detail, 'entity_id') else 'N/A'}")
        print(f"  - Name: {vm_detail.name if hasattr(vm_detail, 'name') else 'N/A'}")
        print(f"  - Details: {vm_detail}")
    except Exception as e:
        print(f"✗ Error getting VM: {e}")
else:
    print("\n[2] Skipping get VM by ID (use --entity-id to test)")

# Example 3: List Hosts
print("\n[3] Listing Hosts...")
try:
    hosts_list = ops_networks_client.Hosts.list_hosts()
    print(f"✓ Found {len(hosts_list.results) if hosts_list and hosts_list.results else 0} hosts")
    if hosts_list and hosts_list.results:
        for i, host in enumerate(hosts_list.results[:3], 1):
            print(f"  [{i}] Host ID: {host.entity_id if hasattr(host, 'entity_id') else 'N/A'}")
            print(f"      Name: {host.name if hasattr(host, 'name') else 'N/A'}")
        if len(hosts_list.results) > 3:
            print(f"  ... and {len(hosts_list.results) - 3} more")
except Exception as e:
    print(f"✗ Error listing hosts: {e}")
    import traceback
    traceback.print_exc()

# Example 4: List Clusters
print("\n[4] Listing Clusters...")
try:
    clusters_list = ops_networks_client.Clusters.list_clusters()
    print(f"✓ Found {len(clusters_list.results) if clusters_list and clusters_list.results else 0} clusters")
    if clusters_list and clusters_list.results:
        for i, cluster in enumerate(clusters_list.results[:3], 1):
            print(f"  [{i}] Cluster ID: {cluster.entity_id if hasattr(cluster, 'entity_id') else 'N/A'}")
            print(f"      Name: {cluster.name if hasattr(cluster, 'name') else 'N/A'}")
        if len(clusters_list.results) > 3:
            print(f"  ... and {len(clusters_list.results) - 3} more")
except Exception as e:
    print(f"✗ Error listing clusters: {e}")
    import traceback
    traceback.print_exc()

# Example 5: List vCenter Datacenters
print("\n[5] Listing vCenter Datacenters...")
try:
    datacenters_list = ops_networks_client.VcDatacenters.list_datacenters()
    print(f"✓ Found {len(datacenters_list.results) if datacenters_list and datacenters_list.results else 0} datacenters")
    if datacenters_list and datacenters_list.results:
        for i, dc in enumerate(datacenters_list.results[:3], 1):
            print(f"  [{i}] Datacenter ID: {dc.entity_id if hasattr(dc, 'entity_id') else 'N/A'}")
            print(f"      Name: {dc.name if hasattr(dc, 'name') else 'N/A'}")
        if len(datacenters_list.results) > 3:
            print(f"  ... and {len(datacenters_list.results) - 3} more")
except Exception as e:
    print(f"✗ Error listing datacenters: {e}")
    import traceback
    traceback.print_exc()

# Example 6: List Datastores
print("\n[6] Listing Datastores...")
try:
    datastores_list = ops_networks_client.Datastores.list_datastores()
    print(f"✓ Found {len(datastores_list.results) if datastores_list and datastores_list.results else 0} datastores")
    if datastores_list and datastores_list.results:
        for i, ds in enumerate(datastores_list.results[:3], 1):
            print(f"  [{i}] Datastore ID: {ds.entity_id if hasattr(ds, 'entity_id') else 'N/A'}")
            print(f"      Name: {ds.name if hasattr(ds, 'name') else 'N/A'}")
        if len(datastores_list.results) > 3:
            print(f"  ... and {len(datastores_list.results) - 3} more")
except Exception as e:
    print(f"✗ Error listing datastores: {e}")
    import traceback
    traceback.print_exc()

# Example 7: List vNICs
print("\n[7] Listing vNICs (Virtual Network Interfaces)...")
try:
    vnics_list = ops_networks_client.Vnics.list_vnics()
    print(f"✓ Found {len(vnics_list.results) if vnics_list and vnics_list.results else 0} vNICs")
    if vnics_list and vnics_list.results:
        for i, vnic in enumerate(vnics_list.results[:3], 1):
            print(f"  [{i}] vNIC ID: {vnic.entity_id if hasattr(vnic, 'entity_id') else 'N/A'}")
        if len(vnics_list.results) > 3:
            print(f"  ... and {len(vnics_list.results) - 3} more")
except Exception as e:
    print(f"✗ Error listing vNICs: {e}")
    import traceback
    traceback.print_exc()

# Example 8: List Security Groups
print("\n[8] Listing Security Groups...")
try:
    security_groups_list = ops_networks_client.SecurityGroups.list_security_groups()
    print(f"✓ Found {len(security_groups_list.results) if security_groups_list and security_groups_list.results else 0} security groups")
    if security_groups_list and security_groups_list.results:
        for i, sg in enumerate(security_groups_list.results[:3], 1):
            print(f"  [{i}] Security Group ID: {sg.entity_id if hasattr(sg, 'entity_id') else 'N/A'}")
            print(f"      Name: {sg.name if hasattr(sg, 'name') else 'N/A'}")
        if len(security_groups_list.results) > 3:
            print(f"  ... and {len(security_groups_list.results) - 3} more")
except Exception as e:
    print(f"✗ Error listing security groups: {e}")
    import traceback
    traceback.print_exc()

# Example 9: List Firewall Rules
print("\n[9] Listing Firewall Rules...")
try:
    firewall_rules_list = ops_networks_client.FirewallRules.list_firewall_rules()
    print(f"✓ Found {len(firewall_rules_list.results) if firewall_rules_list and firewall_rules_list.results else 0} firewall rules")
    if firewall_rules_list and firewall_rules_list.results:
        for i, rule in enumerate(firewall_rules_list.results[:3], 1):
            print(f"  [{i}] Firewall Rule ID: {rule.entity_id if hasattr(rule, 'entity_id') else 'N/A'}")
            print(f"      Name: {rule.name if hasattr(rule, 'name') else 'N/A'}")
        if len(firewall_rules_list.results) > 3:
            print(f"  ... and {len(firewall_rules_list.results) - 3} more")
except Exception as e:
    print(f"✗ Error listing firewall rules: {e}")
    import traceback
    traceback.print_exc()

# Example 10: List vCenter Managers
print("\n[10] Listing vCenter Managers...")
try:
    vcenter_managers_list = ops_networks_client.VcenterManagers.list_vcenter_managers()
    print(f"✓ Found {len(vcenter_managers_list.results) if vcenter_managers_list and vcenter_managers_list.results else 0} vCenter managers")
    if vcenter_managers_list and vcenter_managers_list.results:
        for i, vc in enumerate(vcenter_managers_list.results[:3], 1):
            print(f"  [{i}] vCenter Manager ID: {vc.entity_id if hasattr(vc, 'entity_id') else 'N/A'}")
            print(f"      Name: {vc.name if hasattr(vc, 'name') else 'N/A'}")
        if len(vcenter_managers_list.results) > 3:
            print(f"  ... and {len(vcenter_managers_list.results) - 3} more")
except Exception as e:
    print(f"✗ Error listing vCenter managers: {e}")
    import traceback
    traceback.print_exc()

# Example 11: List Distributed Virtual Switches
print("\n[11] Listing Distributed Virtual Switches...")
try:
    dvs_list = ops_networks_client.DistributedVirtualSwitches.list_distributed_virtual_switches()
    print(f"✓ Found {len(dvs_list.results) if dvs_list and dvs_list.results else 0} distributed virtual switches")
    if dvs_list and dvs_list.results:
        for i, dvs in enumerate(dvs_list.results[:3], 1):
            print(f"  [{i}] DVS ID: {dvs.entity_id if hasattr(dvs, 'entity_id') else 'N/A'}")
            print(f"      Name: {dvs.name if hasattr(dvs, 'name') else 'N/A'}")
        if len(dvs_list.results) > 3:
            print(f"  ... and {len(dvs_list.results) - 3} more")
except Exception as e:
    print(f"✗ Error listing distributed virtual switches: {e}")
    import traceback
    traceback.print_exc()

# Example 12: List Problem Events
print("\n[12] Listing Problem Events...")
try:
    # Get current time and time 7 days ago
    end_time = time.time()
    start_time = end_time - (7 * 24 * 60 * 60)  # 7 days ago
    
    problems_list = ops_networks_client.Problems.list_problem_events(
        event_status='all')
    print(f"✓ Found {len(problems_list.results) if problems_list and problems_list.results else 0} problem events")
    if problems_list and problems_list.results:
        for i, problem in enumerate(problems_list.results[:3], 1):
            print(f"  [{i}] Problem ID: {problem.entity_id if hasattr(problem, 'entity_id') else 'N/A'}")
            print(f"      Type: {problem.event_type if hasattr(problem, 'event_type') else 'N/A'}")
        if len(problems_list.results) > 3:
            print(f"  ... and {len(problems_list.results) - 3} more")
except Exception as e:
    print(f"✗ Error listing problem events: {e}")
    import traceback
    traceback.print_exc()

# Example 13: Bulk Fetch Entities
print("\n[13] Bulk Fetch Entities Example...")
try:
    from vcf.operations_networks.model_client import FetchRequest
    
    # Collect some entity IDs from previous queries
    entity_ids = []
    if vms_list and vms_list.results:
        entity_ids.extend([vm.entity_id for vm in vms_list.results[:2] if hasattr(vm, 'entity_id')])
    
    if entity_ids:
        fetch_request = FetchRequest(entity_ids=entity_ids)
        bulk_response = ops_networks_client.Fetch.post(fetch_request=fetch_request)
        print(f"✓ Bulk fetch completed")
        if bulk_response and hasattr(bulk_response, 'results'):
            print(f"  Retrieved {len(bulk_response.results)} entities")
    else:
        print("  No entity IDs available for bulk fetch")
except Exception as e:
    print(f"✗ Error in bulk fetch: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("Examples completed")
print("=" * 80)
