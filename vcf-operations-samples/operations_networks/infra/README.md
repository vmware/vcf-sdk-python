# VCF Operations for Networks - Infrastructure API Examples

This folder contains examples demonstrating how to use the **Infrastructure APIs** in VCF Operations for Networks. 
These APIs provide management of infrastructure components like nodes and watermarks.

## Authentication

All samples support two authentication methods:

1. **Username/Password Authentication** (default):
   ```bash
   python -m infra.<sample> --server <server-ip> --user <username> --password <password>
   ```

2. **Token Authentication** (recommended for test frameworks):
   ```bash
   # First, generate a token using the auth_token module
   python -m auth_token.token_example --server <server-ip> --user <username> --password <password>
   
   # Then use the token with any sample
   python -m infra.<sample> --server <server-ip> --token <your-auth-token>
   ```

Token authentication is more efficient when running multiple samples as it avoids repeated authentication calls to the server.

## Overview

The Infrastructure API provides three main service groups:

1. **Nodes** - Manage infrastructure nodes
2. **ExpandedNodes** - Get detailed infrastructure node information
3. **Watermark** - Manage VCF watermark configuration

## API Services

### 1. Nodes Service

The Nodes service allows you to manage infrastructure nodes.

**Key Methods:**

- `list_nodes()` - Get list of all infrastructure nodes
- `get_node(id)` - Get details of a specific node
- `delete_node(id)` - Delete a proxy node

**Example File:** `nodes.py`

**Permissions:** Only admin users can retrieve node information

**Usage:**

```bash
# List all nodes (run from operations_networks root folder)
python -m infra.nodes --server <server-ip> --user <username> --password <password>

# Get specific node details
python -m infra.nodes --server <server-ip> --user <username> --password <password> --node-id <node-id>
```

**Concepts:**

- **Node ID**: Unique identifier for infrastructure node
- **Node Type**: Type of node (proxy, appliance, etc.)
- **Proxy ID**: Required for adding data sources
- **Model Key**: Alternative identifier for nodes

---

### 2. ExpandedNodes Service

The ExpandedNodes service provides detailed information about infrastructure nodes with all available properties.

**Key Methods:**

- `list_expanded_nodes()` - Get list of nodes with complete details

**Example File:** `expanded_nodes.py`

**Permissions:** Only admin users can retrieve this information

**Usage:**

```bash
# List expanded nodes with full details (run from operations_networks root folder)
python -m infra.expanded_nodes --server <server-ip> --user <username> --password <password>
```

**Concepts:**

- **Expanded Nodes**: Nodes list with additional properties (version, status, etc.)
- **Detailed Information**: Additional metadata not available in regular nodes API
- **Comparison**: Shows difference between regular and expanded node data

---

### 3. Watermark Service

The Watermark service manages VCF deployment watermark information.

**Key Methods:**

- `get_vcf_watermark()` - Retrieve VCF watermark configuration
- `save_vcf_watermark(config)` - Create/save watermark configuration
- `update_vcf_watermark(config)` - Update existing watermark
- `delete_vcf_watermark()` - Delete watermark configuration

**Example File:** `watermark.py`

**Permissions:** Only admin/auditor users can access watermark information

**Usage:**

```bash
# Get watermark information (run from operations_networks root folder)
python -m infra.watermark --server <server-ip> --user <username> --password <password>
```

---

### 4. Watermark Operations (Advanced)

The Watermark Operations examples provide detailed guidance on modifying watermark configurations.

**Key Methods:**

- `save_vcf_watermark(config)` - Create/save new watermark configuration
- `update_vcf_watermark(config)` - Update existing watermark configuration
- `delete_vcf_watermark()` - Delete watermark configuration

**Example File:** `watermark_operations.py`

**Permissions:** Only admin users can modify watermarks

**Usage:**

```bash
# Get watermark (default) - run from operations_networks root folder
python -m infra.watermark_operations --server <server-ip> --user <username> --password <password>

# Save new watermark
python -m infra.watermark_operations --server <server-ip> --user <username> --password <password> --operation save

# Update watermark
python -m infra.watermark_operations --server <server-ip> --user <username> --password <password> --operation update

# Delete watermark
python -m infra.watermark_operations --server <server-ip> --user <username> --password <password> --operation delete

# Execute complete workflow
python -m infra.watermark_operations --server <server-ip> --user <username> --password <password> --operation workflow
```

**Concepts:**

- **Save Watermark**: Create new deployment tracking information
- **Update Watermark**: Modify existing watermark configuration
- **Delete Watermark**: Remove watermark (use with caution)
- **Workflow**: Complete get -> update -> verify cycle

---

## Common Usage Patterns

### Pattern 1: List All Nodes

```python
from operations_networks.helpers.client import create_vcf_operations_for_networks_client, StubFactoryType

client = create_vcf_operations_for_networks_client(
    server='<server-ip>',
    username='<username>',
    password='<password>',
    stub_factory_type=StubFactoryType.INFRA)

# List nodes
node_list = client.Nodes.list_nodes()
for node in node_list.results:
    print(f"Node: {node.name} ({node.id})")
```

### Pattern 2: Get Node Details

```python
# Get specific node
node = client.Nodes.get_node(id="node-123")
print(f"Name: {node.name}")
print(f"IP: {node.ip_address}")
print(f"Type: {node.node_type}")
```

### Pattern 3: List Expanded Nodes

```python
# Get expanded node information
expanded_nodes = client.ExpandedNodes.list_expanded_nodes()
for node in expanded_nodes.results:
    print(f"Node: {node.name}")
    print(f"  Version: {node.version}")
    print(f"  Status: {node.status}")
```

### Pattern 4: Get Watermark Information

```python
# Get watermark
watermark = client.Watermark.get_vcf_watermark()
print(f"VCF ID: {watermark.vcf_id}")
print(f"VCF Version: {watermark.vcf_version}")
```

---

## Error Handling

The Infrastructure APIs may raise exceptions in these cases:

- **401 Unauthorized** - Authentication failed
- **403 Forbidden** - User lacks required permissions (non-admin)
- **404 Not Found** - Node or resource not found
- **500 Internal Error** - Server error

**Example Error Handling:**

```python
from vcf.operations_networks.model_client import ApiError

try:
    nodes = client.Nodes.list_nodes()
except ApiError as e:
    print(f"API Error: {e.message}")
    if e.error_code == 403:
        print("Admin privileges required")
except Exception as e:
    print(f"Error: {e}")
```

---

## Parameter Reference

### Nodes Methods

| Method | Parameters | Returns | Required |
|--------|-----------|---------|----------|
| list_nodes | None | NodeListResult | - |
| get_node | id (string) | Node | Yes |
| delete_node | id (string) | Node | Yes |

### ExpandedNodes Methods

| Method | Parameters | Returns |
|--------|-----------|---------|
| list_expanded_nodes | None | ExpandedNodeListResult |

### Watermark Methods

| Method | Parameters | Returns |
|--------|-----------|---------|
| get_vcf_watermark | None | VCFWatermarkConfiguration |
| save_vcf_watermark | config (VCFWatermarkConfiguration) | VCFWatermarkConfiguration |
| update_vcf_watermark | config (VCFWatermarkConfiguration) | VCFWatermarkConfiguration |
| delete_vcf_watermark | None | None |

---

## Running the Examples

### Prerequisites

1. VCF Operations for Networks instance running
2. Admin user credentials (required for infrastructure APIs)
3. Python 3.10+ with VCF SDK installed

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

# Nodes API
python -m infra.nodes \
  --server <VCF_OPS_NETWORKS_IP> \
  --user <ADMIN_USERNAME> \
  --password <PASSWORD>

# Expanded Nodes API
python -m infra.expanded_nodes \
  --server <VCF_OPS_NETWORKS_IP> \
  --user <ADMIN_USERNAME> \
  --password <PASSWORD>

# Watermark API
python -m infra.watermark \
  --server <VCF_OPS_NETWORKS_IP> \
  --user <ADMIN_USERNAME> \
  --password <PASSWORD>
```

---

## API Response Structures

### Node Object

```python
{
    "id": "10000:901:649591578347200326",
    "name": "node-1",
    "ip_address": "<server_ip>",
    "node_type": "PROXY",
    "proxy_id": "proxy-123",
    "model_key": "IAPG7M8JS18458ROSJQRGQ0LLV",
    "version": "9.1.0",
    "status": "ACTIVE"
}
```

### ExpandedNode Object

```python
{
    "id": "10000:901:649591578347200326",
    "name": "node-1",
    "ip_address": "<server_ip>",
    "node_type": "PROXY",
    "version": "9.1.0",
    "status": "ACTIVE",
    "cpu_count": 8,
    "memory_gb": 16,
    "uptime": 3600000
}
```

### Watermark Object

```python
{
    "vcf_id": "vcf-12345",
    "vcf_version": "9.1.0",
    "deployment_id": "deploy-67890",
    "creation_timestamp": 1634567890000,
    "update_timestamp": 1634567890000
}
```

---

## Best Practices

1. **Admin Only**: Use admin credentials for infrastructure APIs
2. **Error Handling**: Always wrap API calls in try-except blocks
3. **Admin Verification**: Check user role before using these APIs
4. **Node Management**: Be careful when deleting nodes (proxy nodes only)
5. **Watermark**: Typically managed by deployment tools, avoid manual changes
6. **Logging**: Add logging for infrastructure operations
7. **Permissions**: Ensure users have required admin privileges

---

## Troubleshooting

### Issue: 401 Unauthorized
**Solution**: Check credentials and ensure they are valid

### Issue: 403 Forbidden
**Solution**: User must have admin privileges for infrastructure APIs

### Issue: 404 Not Found
**Solution**: Verify node ID exists

### Issue: Connection Timeout
**Solution**: Check network connectivity to VCF Operations for Networks

### Issue: SSL Certificate Error
**Solution**: Use `get_unverified_session()` for testing (not for production)

---

## Support

For issues or questions:
- Check the example files for usage patterns
- Refer to the VCF API documentation
- Review error messages and HTTP status codes
- Check network connectivity and credentials
- Verify admin user privileges

---

**Last Updated**: 2025
**VCF SDK Version**: 9.1+
**Python Version**: 3.10+
