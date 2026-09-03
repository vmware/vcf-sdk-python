# VCF Operations for Networks - Entities API Examples

This folder contains examples demonstrating how to use the **Entities APIs** in VCF Operations for Networks. The Entities API provides access to infrastructure entities like VMs, hosts, clusters, networks, security groups, and more.

## Authentication

All samples support two authentication methods:

1. **Username/Password Authentication** (default):
   ```bash
   python -m entities.<sample> --server <server-ip> --user <username> --password <password>
   ```

2. **Token Authentication** (recommended for test frameworks):
   ```bash
   # First, generate a token using the auth_token module
   python -m auth_token.token_example --server <server-ip> --user <username> --password <password>
   
   # Then use the token with any sample
   python -m entities.<sample> --server <server-ip> --token <your-auth-token>
   ```

Token authentication is more efficient when running multiple samples as it avoids repeated authentication calls to the server.

## Overview

The Entities API provides comprehensive access to infrastructure entities across your VCF environment:

1. **Compute Entities** - VMs, Hosts, Clusters, vCenter Datacenters
2. **Network Entities** - vNICs, Distributed Virtual Switches, Port Groups
3. **Storage Entities** - Datastores, Virtual Disks
4. **Security Entities** - Security Groups, Security Tags, Firewall Rules, Firewalls
5. **Management Entities** - vCenter Managers, NSX Managers, Firewall Managers
6. **Problem Events** - System problems and events
7. **Bulk Operations** - Fetch multiple entities at once

## API Services

### 1. Virtual Machines (Vms)

Manage and query virtual machines in your infrastructure.

**Key Methods:**
- `list_vms(size=None, cursor=None, start_time=None, end_time=None)` - List all VMs
- `get_vm(id, time=None)` - Get details of a specific VM

**Example File:** `entities_sample.py`

**Usage:**

```bash
# List VMs and other entities (run from operations_networks root folder)
python -m entities.entities_sample --server <server-ip> --user <username> --password <password>

# Or using a pre-generated token
python -m entities.entities_sample --server <server-ip> --token <your-auth-token>

# Get specific entity details
python -m entities.entities_sample --server <server-ip> --user <username> --password <password> --entity-id <entity-id>
```

---

### 2. Hosts

Query ESXi hosts in your infrastructure.

**Key Methods:**
- `list_hosts(size=None, cursor=None, start_time=None, end_time=None)` - List all hosts
- `get_host(id, time=None)` - Get details of a specific host

---

### 3. Clusters

Query vSphere clusters.

**Key Methods:**
- `list_clusters(size=None, cursor=None, start_time=None, end_time=None)` - List all clusters
- `get_cluster(id, time=None)` - Get details of a specific cluster

---

### 4. vCenter Datacenters (VcDatacenters)

Query vCenter datacenters.

**Key Methods:**
- `list_datacenters(size=None, cursor=None, start_time=None, end_time=None)` - List all datacenters
- `get_datacenter(id, time=None)` - Get details of a specific datacenter

---

### 5. Datastores

Query datastores in your infrastructure.

**Key Methods:**
- `list_datastores(size=None, cursor=None, start_time=None, end_time=None)` - List all datastores
- `get_datastore(id, time=None)` - Get details of a specific datastore

---

### 6. Virtual Network Interfaces (Vnics)

Query virtual network interfaces attached to VMs.

**Key Methods:**
- `list_vnics(size=None, cursor=None, start_time=None, end_time=None)` - List all vNICs
- `get_vnic(id, time=None)` - Get details of a specific vNIC

---

### 7. Security Groups

Query security groups in your NSX environment.

**Key Methods:**
- `list_security_groups(size=None, cursor=None, start_time=None, end_time=None)` - List all security groups
- `get_security_group(id, time=None)` - Get details of a specific security group

---

### 8. Security Tags

Query security tags applied to entities.

**Key Methods:**
- `list_security_tags(size=None, cursor=None, start_time=None, end_time=None)` - List all security tags
- `get_security_tag(id, time=None)` - Get details of a specific security tag

---

### 9. Firewall Rules

Query firewall rules in your NSX environment.

**Key Methods:**
- `list_firewall_rules(size=None, cursor=None, start_time=None, end_time=None)` - List all firewall rules
- `get_firewall_rule(id, time=None)` - Get details of a specific firewall rule

---

### 10. Firewalls

Query firewall entities.

**Key Methods:**
- `list_firewalls(size=None, cursor=None, start_time=None, end_time=None)` - List all firewalls
- `get_firewall(id, time=None)` - Get details of a specific firewall

---

### 11. vCenter Managers

Query vCenter Server instances.

**Key Methods:**
- `list_vcenter_managers(size=None, cursor=None, start_time=None, end_time=None)` - List all vCenter managers
- `get_vcenter_manager(id, time=None)` - Get details of a specific vCenter manager

---

### 12. NSX Managers

Query NSX Manager instances.

**Key Methods:**
- `list_nsx_managers(size=None, cursor=None, start_time=None, end_time=None)` - List all NSX managers
- `get_nsx_manager(id, time=None)` - Get details of a specific NSX manager

---

### 13. Distributed Virtual Switches

Query VMware Distributed Virtual Switches.

**Key Methods:**
- `list_distributed_virtual_switches(size=None, cursor=None, start_time=None, end_time=None)` - List all DVS
- `get_distributed_virtual_switch(id, time=None)` - Get details of a specific DVS

---

### 14. Distributed Virtual Port Groups

Query distributed virtual port groups.

**Key Methods:**
- `list_distributed_virtual_portgroups(size=None, cursor=None, start_time=None, end_time=None)` - List all port groups
- `get_distributed_virtual_portgroup(id, time=None)` - Get details of a specific port group

---

### 15. Problem Events

Query problem events and alerts in your infrastructure.

**Key Methods:**
- `list_problem_events(size, cursor, start_time, end_time, event_type, event_tags, event_status, update_time_from, update_time_to, event_severity, managers)` - List problem events
- `get_problem_event(id, time=None)` - Get details of a specific problem event

**Event Status Values:**
- `open` - Open events
- `closed` - Closed events
- `all` - All events

**Event Severity Values:**
- `Critical` - Critical severity
- `Warning` - Warning severity
- `Moderate` - Moderate severity
- `Info` - Informational

---

### 16. Bulk Fetch (Fetch)

Fetch multiple entities at once using their IDs.

**Key Methods:**
- `post(fetch_request)` - Bulk fetch entity details (max 1000 entities)

**Usage:**
```python
from vcf.operations_networks.model_client import FetchRequest

fetch_request = FetchRequest(entity_ids=['entity-id-1', 'entity-id-2', 'entity-id-3'])
response = client.Fetch.post(fetch_request=fetch_request)
```

---

### 17. Additional Entity Types

The Entities API also supports many other entity types:

- **Folders** - vCenter folders
- **Vmknics** - VMkernel network interfaces
- **Layer2Networks** - Layer 2 networks
- **IpSets** - IP sets
- **Flows** - Network flows
- **Services** - Network services
- **ServiceGroups** - Service groups
- **LogicalRouters** - NSX logical routers
- **Routerinterfaces** - Router interfaces
- **Switchports** - Physical switch ports
- **VirtualDisk** - Virtual disks
- **KubernetesClusters** - Kubernetes clusters
- **KubernetesNamespaces** - Kubernetes namespaces
- **KubernetesNodes** - Kubernetes nodes
- **KubernetesPods** - Kubernetes pods
- **KubernetesServices** - Kubernetes services
- **HcxManagers** - HCX managers
- **HcxSites** - HCX sites
- **HcxAppliances** - HCX appliances
- **HcxTunnels** - HCX tunnels
- **HcxL2extensions** - HCX L2 extensions
- **HcxServiceMeshes** - HCX service meshes
- **HcxServices** - HCX services
- **HcxNetworkProfiles** - HCX network profiles
- **HcxComputeProfiles** - HCX compute profiles

---

## Common Usage Patterns

### Pattern 1: List Entities with Pagination

```python
from operations_networks.helpers.client import create_vcf_operations_for_networks_client, StubFactoryType

client = create_vcf_operations_for_networks_client(
    server='<VCF_OPS_NETWORKS_IP>',
    username='<USERNAME>',
    password='<PASSWORD>',
    stub_factory_type=StubFactoryType.ENTITIES)

# List VMs with pagination
vms = client.Vms.list_vms(size=50.0)
print(f"Found {len(vms.results)} VMs")

# Get next page if cursor exists
if vms.cursor:
    next_page = client.Vms.list_vms(size=50.0, cursor=vms.cursor)
```

### Pattern 2: Get Entity Details

```python
# Get specific VM details
vm_id = "vm-12345"
vm_detail = client.Vms.get_vm(id=vm_id)
print(f"VM Name: {vm_detail.name}")
print(f"VM ID: {vm_detail.entity_id}")
```

### Pattern 3: Filter by Time Range

```python
import time

# Get entities from last 24 hours
end_time = time.time()
start_time = end_time - (24 * 60 * 60)

vms = client.Vms.list_vms(
    start_time=start_time,
    end_time=end_time,
    size=100.0)
```

### Pattern 4: Query Problem Events

```python
# Get critical problem events from last 7 days
end_time = time.time()
start_time = end_time - (7 * 24 * 60 * 60)

problems = client.Problems.list_problem_events(
    start_time=start_time,
    end_time=end_time,
    event_status='open',
    event_severity=['Critical', 'Warning'],
    size=50.0)

for problem in problems.results:
    print(f"Problem: {problem.event_type}")
    print(f"Severity: {problem.severity}")
```

### Pattern 5: Bulk Fetch Multiple Entities

```python
from vcf.operations_networks.model_client import FetchRequest

# Collect entity IDs
entity_ids = ['vm-1', 'vm-2', 'host-1', 'cluster-1']

# Bulk fetch
fetch_request = FetchRequest(entity_ids=entity_ids)
response = client.Fetch.post(fetch_request=fetch_request)

for entity in response.results:
    print(f"Entity: {entity.name} (ID: {entity.entity_id})")
```

---

## Error Handling

The Entities API may raise exceptions in these cases:

- **400 Bad Request** - Invalid parameters
- **401 Unauthorized** - Authentication failed
- **404 Not Found** - Entity not found
- **500 Internal Error** - Server error

**Example Error Handling:**

```python
from vcf.operations_networks.model_client import ApiError

try:
    vm = client.Vms.get_vm(id='invalid-id')
except ApiError as e:
    print(f"API Error: {e.message}")
    if e.error_code == 404:
        print("VM not found")
except Exception as e:
    print(f"Error: {e}")
```

---

## Running the Examples

### Prerequisites

1. VCF Operations for Networks instance running
2. Valid credentials with appropriate permissions

### Basic Setup

```bash
# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install VCF SDK
pip install vcf-operations-networks==9.1.0.0
```

### Run Examples

```bash
# Navigate to the operations_networks root folder
cd /path/to/vcf-operations-samples/operations_networks

# List all entities
python -m entities.entities_sample \
  --server <VCF_OPS_NETWORKS_IP> \
  --user <USERNAME> \
  --password <PASSWORD>

# Get specific entity details
python -m entities.entities_sample \
  --server <VCF_OPS_NETWORKS_IP> \
  --user <USERNAME> \
  --password <PASSWORD> \
  --entity-id <ENTITY_ID>

# Customize page size
python -m entities.entities_sample \
  --server <VCF_OPS_NETWORKS_IP> \
  --user <USERNAME> \
  --password <PASSWORD> \
  --page-size 20
```

---

## Best Practices

1. **Use ENTITIES Factory**: Always use `StubFactoryType.ENTITIES` for Entities API
2. **Pagination**: Use pagination for large result sets to avoid timeouts
3. **Time Filters**: Use time filters to limit query scope and improve performance
4. **Bulk Operations**: Use bulk fetch for retrieving multiple entities efficiently
5. **Error Handling**: Wrap API calls in try-except blocks
6. **Entity IDs**: Store entity IDs for subsequent operations
7. **Caching**: Consider caching entity data to reduce API calls

---

## Troubleshooting

### Issue: 401 Unauthorized
**Solution**: Check credentials and ensure user has permissions to view entities

### Issue: 404 Not Found
**Solution**: Verify entity ID is correct and entity exists

### Issue: Timeout on Large Queries
**Solution**: Use smaller page sizes and pagination

### Issue: Empty Results
**Solution**: Check time filters and ensure entities exist in the specified time range

---

## Support

For issues or questions:
- Check the example files for usage patterns
- Refer to the VCF API documentation
- Review error messages and HTTP status codes
- Check network connectivity and credentials

---
