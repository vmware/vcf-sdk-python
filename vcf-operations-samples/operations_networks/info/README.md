# VCF Operations for Networks - Info API Examples

This folder contains examples demonstrating how to use the **Info API** in  VCF Operations for Networks. The Info API provides system information about your VCF Operations for Networks instance.

## Authentication

All samples support two authentication methods:

1. **Username/Password Authentication** (default):
   ```bash
   python -m info.<sample> --server <server-ip> --user <username> --password <password>
   ```

2. **Token Authentication** (recommended for test frameworks):
   ```bash
   # First, generate a token using the auth_token module
   python -m auth_token.token_example --server <server-ip> --user <username> --password <password>
   
   # Then use the token with any sample
   python -m info.<sample> --server <server-ip> --token <your-auth-token>
   ```

Token authentication is more efficient when running multiple samples as it avoids repeated authentication calls to the server.

## Overview

The Info API provides information about your VCF Operations for Networks deployment:

1. **Version** - Get version and build information

## API Services

### Version Service

The Version service allows you to retrieve version and build information about VCF Operations for Networks.

**Key Methods:**

- `get_version()` - Get version information about VCF Operations for Networks

**Example File:** `version.py`

**Usage:**

```bash
# Get version information (run from operations_networks root folder)
python -m info.version --server <server-ip/fqdn> --user <api-user> --password <password>

# Or using a pre-generated token
python -m info.version --server <server-ip/fqdn> --token <your-auth-token>
```

**Concepts:**

- **Version**: The software version (e.g., "9.0.0")
- **Build Number**: Internal build identifier

---

## Common Usage Patterns

### Pattern 1: Get Version Information

```python
from operations_networks.helpers.client import create_vcf_operations_for_networks_client, StubFactoryType

client = create_vcf_operations_for_networks_client(
    server='<VCF_OPS_NETWORKS_IP>',
    username='<USERNAME>',
    password='<PASSWORD>',
    stub_factory_type=StubFactoryType.INFO)

# Get version
version = client.Version.get_version()
print(f"Version: {version.version}")
print(f"Build: {version.build_number}")
```

### Pattern 2: Check Version Compatibility

```python
version = client.Version.get_version()

if hasattr(version, 'version'):
    version_str = str(version.version)
    major_version = int(version_str.split('.')[0])
    
    if major_version >= 9:
        print("✓ Compatible with VCF 9.0+")
    else:
        print("⚠ Version may not support all features")
```

### Pattern 3: Display Full Version Information

```python
version = client.Version.get_version()

print("Version Details:")
for key, value in version.__dict__.items():
    print(f"  {key}: {value}")
```

---

## Error Handling

The Version API may raise exceptions in these cases:

- **401 Unauthorized** - Authentication failed

**Example Error Handling:**

```python
from vcf.operations_networks.model_client import ApiError

try:
    version = client.Version.get_version()
except ApiError as e:
    print(f"API Error: {e.message}")
    if e.error_code == 401:
        print("Authentication failed")
except Exception as e:
    print(f"Error: {e}")
```

---

## Parameter Reference

### Version Methods

| Method | Parameters | Returns |
|--------|-----------|---------|
| get_version | None | VersionResponse |

### VersionResponse Fields

| Field | Type | Description |
|-------|------|-------------|
| api_version | string | Software version |
| version_string | string | Build identifier |

---

## Running the Examples

### Prerequisites

1. VCF Operations for Networks instance running

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

# Get version information
python -m info.version \
  --server <VCF_OPS_NETWORKS_IP> \
  --user <USERNAME> \
  --password <PASSWORD>
```

---

## API Response Structure

### VersionResponse Object

```python
{
    "api_version": "9.1.0.0",
    "version_string": "9.1.0.0.1760593102",
}
```

---

## Best Practices

1. **Use INFO Factory**: Always use `StubFactoryType.INFO` for Version API
2. **Error Handling**: Wrap API calls in try-except blocks
3. **Version Checking**: Parse version strings carefully for comparisons
4. **Security**: Store credentials securely, use environment variables
5. **Logging**: Add logging for version checks in production

---

## Troubleshooting

### Issue: 401 Unauthorized
**Solution**: Check credentials and ensure user has permissions

### Issue: Connection Timeout
**Solution**: Check network connectivity to VCF Operations for Networks instance

### Issue: SSL Certificate Error
**Solution**: Use the `get_unverified_session()` for testing (not recommended for production)

## Support

For issues or questions:
- Check the example files for usage patterns
- Refer to the VCF API documentation
- Review error messages and HTTP status codes
- Check network connectivity and credentials

---
