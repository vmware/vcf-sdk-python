# VCF Operations for Networks - Groups API Examples

This folder contains examples demonstrating how to use the **Groups APIs** in VMware Cloud Foundation (VCF) Operations for Networks. The Groups API allows you to manage applications, tiers, and discover applications within your VCF infrastructure.

## Authentication

All samples support two authentication methods:

1. **Username/Password Authentication** (default):
   ```bash
   python -m groups.<sample> --server <server-ip> --user <username> --password <password>
   ```

2. **Token Authentication** (recommended for test frameworks):
   ```bash
   # First, generate a token using the auth_token module
   python -m auth_token.token_example --server <server-ip> --user <username> --password <password>
   
   # Then use the token with any sample
   python -m groups.<sample> --server <server-ip> --token <your-auth-token>
   ```

Token authentication is more efficient when running multiple samples as it avoids repeated authentication calls to the server.

## Overview

The Groups API provides three main service groups:

1. **Applications** - Manage custom applications (create, list, retrieve, delete)
2. **Tiers** - Manage application tiers (retrieve tier details)
3. **DiscoveredApplications** - Work with automatically discovered applications

## API Services

### 1. Applications Service

The Applications service allows you to create, list, retrieve, and delete applications in VCF Operations for Networks.

**Key Methods:**

- `list_applications()` - List all applications with optional pagination
- `add_application(application_request)` - Create a new application
- `get_application_by_id(id, fetch_member_counts=None, fetch_update_status=None)` - Get application details
- `delete_application(id)` - Delete an application

**Example File:** `applications.py`

**Usage:**

```bash
# List all applications (run from operations_networks root folder)
python -m groups.applications --server <server_ip> --user <user_name> --password <password>

# Or using a pre-generated token
python -m groups.applications --server <server_ip> --token <your-auth-token>

# Create a new application
python -m groups.applications \
  --server <server_ip> \
  --user <user_name> \
  --password <password> \
  --app-name "MyApp"

# Get a specific application
python -m groups.applications \
  --server <server_ip> \
  --user <user_name> \
  --password <password> \
  --app-id "app-123456"
```

**Concepts:**

- **Applications**: Groupings of tiers that represent business applications
- **Tiers**: Sub-groups within an application (e.g., web tier, app tier, database tier)
- **Members**: Virtual machines or IP addresses within a tier
- **Member Counts**: Number of VMs/IPs in each tier
- **Update Status**: Status of application synchronization with discovered data

---

### 2. Tiers Service

The Tiers service allows you to create, list, retrieve, and delete application tiers.

**Key Methods:**

- `add_tier(id, tier_request)` - Add a tier to an application
- `list_application_tiers(id)` - List all tiers in an application
- `get_tier(tier_id)` - Get tier details for a specific tier ID
- `delete_tier(id, tier_id)` - Delete a tier from an application

**Example File:** `tiers.py`

**Usage:**

```bash
# Complete workflow: Create application, add tier, list tiers, delete tier, delete application
python -m groups.tiers \
  --server <server_ip> \
  --user <user_name> \
  --password <password> \
  --app-name "My Application" \
  --tier-name "Web Tier"

# Or using a pre-generated token
python -m groups.tiers \
  --server <server_ip> \
  --token <your-auth-token> \
  --app-name "Production App" \
  --tier-name "Database Tier"
```

**Workflow Steps:**

The `tiers.py` sample demonstrates a complete tier management workflow:

1. **Create Application** - Creates a new application
2. **Add Tier** - Adds a tier with search membership criteria to the application
3. **List Tiers** - Lists all tiers in the application with details
4. **Delete Tier** - Removes the tier from the application
5. **Delete Application** - Cleans up by deleting the application

**Concepts:**

- **Tier ID**: Unique identifier for a tier within an application
- **Tier Membership**: Criteria for including VMs/IPs in a tier using `SearchMembershipCriteria`
- **Group Membership Criteria**: Defines how entities are grouped into tiers
- **Entity Type**: Type of entities to include (e.g., VirtualMachine, Host)
- **Filter**: Search filter for matching entities (e.g., by security group, tag, name)
- **Member Count**: Number of members in the tier
- **Tier Relations**: Tiers belong to applications

---

### 3. DiscoveredApplications Service

The DiscoveredApplications service allows you to retrieve applications that have been automatically discovered in your infrastructure.

**Key Methods:**

- `get_discovered_applications(size=None, cursor=None, discovery_type=None, granularity=None)` - Get discovered applications

**Example File:** `discovered_applications.py`

**Usage:**

```bash
# Get discovered applications with default settings (run from operations_networks root folder)
python -m groups.discovered_applications --server <server_ip> --user <user_name> --password <password>

# Get flow-based discovered applications with FINE granularity
python -m groups.discovered_applications \
  --server <server_ip> \
  --user <user_name> \
  --password <password> \
  --discovery-type FLOW_BASED_DISCOVERY \
  --granularity FINE \
  --page-size 50

# Get SERVICE_NOW discovered applications
python -m groups.discovered_applications \
  --server <server_ip> \
  --user <user_name> \
  --password <password> \
  --discovery-type SERVICE_NOW
```

**Concepts:**

- **Discovery Types**:
  - `FLOW_BASED_DISCOVERY` - Applications discovered through network flow analysis
  - `SERVICE_NOW` - Applications synced from ServiceNow CMDB
  
- **Granularity** (for flow-based discovery):
  - `FINE` - Detailed application discovery with many small groups
  - `MEDIUM` - Balanced approach (default)
  - `COARSE` - Broader groupings with fewer applications
  
- **Pagination**: Results are paginated with cursor-based navigation
- **Page Size**: Number of results per page (adjustable)

---

## Common Usage Patterns

### Pattern 1: List All Applications

```python
from operations_networks.helpers.client import create_vcf_operations_for_networks_client, StubFactoryType

client = create_vcf_operations_for_networks_client(
    server='<server_ip>',
    username='<user_name>',
    password='<password>',
    stub_factory_type=StubFactoryType.INFRA)

# List applications
app_list = client.Applications.list_applications()
for app in app_list.results:
    print(f"App: {app.name} (ID: {app.id})")
```

### Pattern 2: Create an Application

```python
from vcf.operations_networks.model_client import ApplicationRequest

# Create request
app_request = ApplicationRequest(
    name="MyApplication",
    description="Test application"
)

# Add application
new_app = client.Applications.add_application(application_request=app_request)
print(f"Created: {new_app.name} (ID: {new_app.id})")
```

### Pattern 3: Get Application Details

```python
# Get with member counts and update status
app = client.Applications.get_application_by_id(
    id="app-123",
    fetch_member_counts=True,
    fetch_update_status=True)

print(f"Name: {app.name}")
print(f"Members: {app.member_count}")
```

### Pattern 4: Paginate Through Results

```python
cursor = None
while True:
    results = client.DiscoveredApplications.get_discovered_applications(
        discovery_type='FLOW_BASED_DISCOVERY',
        granularity='MEDIUM',
        size=20,
        cursor=cursor)
    
    # Process results
    for app in results.results:
        print(app.id)
    
    # Check for next page
    if not results.cursor:
        break
    
    cursor = results.cursor
```

### Pattern 5: Create and Manage Tiers

```python
from vcf.operations_networks.model_client import (
    TierRequest,
    GroupMembershipCriteria,
    SearchMembershipCriteria
)

# Create search membership criteria
search_criteria = SearchMembershipCriteria(
    entity_type='VirtualMachine',
    filter="security_groups.entity_id = 'sg-123'"
)

# Create group membership criteria
membership_criteria = GroupMembershipCriteria(
    membership_type='SearchMembershipCriteria',
    search_membership_criteria=search_criteria,
)

# Create tier request
new_tier = TierRequest(
    name="Web Tier",
    group_membership_criteria=[membership_criteria],
)

# Add tier to application
added_tier = client.Tiers.add_tier(
    id="app-123",
    tier_request=new_tier)

print(f"Tier created: {added_tier.name} (ID: {added_tier.entity_id})")
```

### Pattern 6: List Tiers in Application

```python
# List all tiers in an application
tiers_response = client.Tiers.list_application_tiers(id="app-123")

for tier in tiers_response.results:
    print(f"Tier: {tier.name} (ID: {tier.entity_id})")
```

### Pattern 7: Delete a Tier

```python
# Delete tier from application
client.Tiers.delete_tier(
    id="app-123",
    tier_id="tier-456")
print("Tier deleted")
```

### Pattern 8: Delete an Application

```python
# Delete application by ID
client.Applications.delete_application(id="app-123")
print("Application deleted")
```

---

## Error Handling

All API methods may raise exceptions. Common error codes:

- **400 Bad Request** - Invalid parameters
- **401 Unauthorized** - Authentication failed
- **404 Not Found** - Resource not found
- **500 Internal Error** - Server-side error

**Example Error Handling:**

```python
from vcf.operations_networks.model_client import ApiError

try:
    app = client.Applications.get_application_by_id(id="invalid-id")
except ApiError as e:
    print(f"API Error: {e.message}")
    if e.error_code == 404:
        print("Application not found")
except Exception as e:
    print(f"Error: {e}")
```

---

## Parameter Reference

### Applications Parameters

| Method | Parameter | Type | Optional | Description |
|--------|-----------|------|----------|-------------|
| list_applications | size | float | Yes | Page size (default: varies) |
| list_applications | cursor | string | Yes | Cursor from previous response |
| list_applications | modified_after | float | Yes | Timestamp (milliseconds) for filtering |
| add_application | application_request | ApplicationRequest | No | Application details |
| get_application_by_id | id | string | No | Application ID |
| get_application_by_id | fetch_member_counts | bool | Yes | Include member counts |
| get_application_by_id | fetch_update_status | bool | Yes | Include update status |
| delete_application | id | string | No | Application ID |

### Tiers Parameters

| Method | Parameter | Type | Optional | Description |
|--------|-----------|------|----------|-------------|
| add_tier | id | string | No | Application ID |
| add_tier | tier_request | TierRequest | No | Tier details with membership criteria |
| list_application_tiers | id | string | No | Application ID |
| get_tier | tier_id | string | No | Tier ID |
| delete_tier | id | string | No | Application ID |
| delete_tier | tier_id | string | No | Tier ID to delete |

### TierRequest Fields

| Field | Type | Optional | Description |
|-------|------|----------|-------------|
| name | string | No | Tier name |
| group_membership_criteria | list[GroupMembershipCriteria] | No | List of membership criteria |
| description | string | Yes | Tier description |

### GroupMembershipCriteria Fields

| Field | Type | Optional | Description |
|-------|------|----------|-------------|
| membership_type | string | No | Type of membership (e.g., 'SearchMembershipCriteria') |
| search_membership_criteria | SearchMembershipCriteria | No | Search criteria for entity matching |

### SearchMembershipCriteria Fields

| Field | Type | Optional | Description |
|-------|------|----------|-------------|
| entity_type | string | No | Type of entities (e.g., 'VirtualMachine', 'Host') |
| filter | string | Yes | Filter query for matching entities |

### DiscoveredApplications Parameters

| Method | Parameter | Type | Optional | Description |
|--------|-----------|------|----------|-------------|
| get_discovered_applications | size | float | Yes | Page size |
| get_discovered_applications | cursor | string | Yes | Cursor from previous response |
| get_discovered_applications | discovery_type | string | Yes | SERVICE_NOW or FLOW_BASED_DISCOVERY |
| get_discovered_applications | granularity | string | Yes | FINE, MEDIUM, or COARSE |

---

## Running the Examples

### Prerequisites

1. VCF Operations for Networks instance running
2. Valid credentials (username/password)
3. Python 3.10+ with VCF SDK installed

### Basic Setup

```bash
# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install VCF SDK
pip install vcf-sdk
```

### Run Examples

```bash
# Navigate to the operations_networks root folder
cd /path/to/vcf-operations-samples/operations_networks

# Example 1: List applications
python -m groups.applications \
  --server <VCF_OPS_NETWORKS_IP> \
  --user <USERNAME> \
  --password <PASSWORD>

# Example 2: Discover applications
python -m groups.discovered_applications \
  --server <VCF_OPS_NETWORKS_IP> \
  --user <USERNAME> \
  --password <PASSWORD> \
  --discovery-type FLOW_BASED_DISCOVERY \
  --granularity FINE

# Example 3: Complete tier workflow (create app, add tier, list, delete)
python -m groups.tiers \
  --server <VCF_OPS_NETWORKS_IP> \
  --user <USERNAME> \
  --password <PASSWORD> \
  --app-name "Test Application" \
  --tier-name "Web Tier"
```

---

## API Response Structures

### Application Object

```python
{
    "id": "app-123456",
    "name": "WebApplication",
    "description": "Production web application",
    "tiers": [
        {
            "id": "tier-001",
            "name": "Web Tier"
        },
        {
            "id": "tier-002",
            "name": "App Tier"
        }
    ],
    "member_count": 45,
    "update_status": "SYNCED"
}
```

### Tier Object

```python
{
    "id": "tier-123456",
    "name": "Database Tier",
    "description": "Database servers",
    "application_id": "app-123",
    "member_count": 5,
    "members": ["vm-1", "vm-2", "vm-3", "vm-4", "vm-5"]
}
```

### DiscoveredApplication Object

```python
{
    "id": "disco-app-001",
    "name": "DiscoveredApp",
    "discovery_type": "FLOW_BASED_DISCOVERY",
    "granularity": "MEDIUM"
}
```

---

## Best Practices

1. **Pagination**: Always handle pagination for large result sets
2. **Error Handling**: Wrap API calls in try-except blocks
3. **Performance**: Use pagination with appropriate page sizes
4. **Authentication**: Store credentials securely, use environment variables
5. **Resource Cleanup**: Delete applications when no longer needed
6. **Logging**: Add logging for debugging and monitoring
7. **Testing**: Test with both SERVICE_NOW and FLOW_BASED_DISCOVERY discovery types

---

## Troubleshooting

### Issue: 401 Unauthorized
**Solution**: Check credentials and ensure user has permissions in VCF Operations for Networks

### Issue: 404 Not Found
**Solution**: Verify the resource ID exists and use correct discovery type/granularity

### Issue: Connection Timeout
**Solution**: Check network connectivity to VCF Operations for Networks instance

### Issue: SSL Certificate Error
**Solution**: Use the `get_unverified_session()` for testing (not recommended for production)

---

## Related Documentation

- [VCF Operations for Networks API Reference](https://developer.broadcom.com/xapis/vcf-operations-for-networks-api/latest)
- [VCF Python SDK Documentation](https://developer.broadcom.com/vcf-python-sdk)
- [VCF Operations for Networks User Guide](https://techdocs.broadcom.com/us/en/vmware-aria/vmware-aria-operations-for-networks)

---

## Support

For issues or questions:
- Check the example files for usage patterns
- Refer to the VCF API documentation
- Review error messages and HTTP status codes
- Check network connectivity and credentials

---

**Last Updated**: 2025
**VCF SDK Version**: 9.0+
**Python Version**: 3.10+
