# Authentication Token Management

This folder contains utilities for managing authentication tokens for VCF Operations for Networks API.

## Overview

The `TokenService` class provides a centralized way to generate and manage authentication tokens, with built-in caching to reduce server load.

## Files

- **`token_service.py`** - Core TokenService class for authentication token management
- **`token_example.py`** - Example demonstrating token usage
- **`__init__.py`** - Package initialization

## Quick Start

### Using the TokenService Class

```python
from auth_token.token_service import TokenService
import requests

# Create session
session = requests.Session()
session.verify = False

# Create TokenService instance with default domain settings
token_service = TokenService(
    server='<server_ip>',
    username='<user_name>',
    password='<password>',
    session=session)

# Or with custom domain settings
token_service = TokenService(
    server='<server_ip>',
    username='<user_name>',
    password='<password>',
    session=session,
    domain_type='LDAP',
    domain_value='mydomain.com')

# Fetch token
token = token_service.fetch_token()
print(f"Token: {token}")

# Get cached token (no server call)
cached_token = token_service.get_cached_token()

# Clear cache when needed
token_service.clear_cache()
```

## Running the Example

The `token_example.py` file demonstrates token usage with configurable domain settings:

### Basic Usage (with default domain)

```bash
cd /path/to/vcf-operations-samples/operations_networks/auth_token

python token_example.py \
  --server <server_ip> \
  --user <user_name> \
  --password <password>
```

### With Custom Domain Settings

```bash
python token_example.py \
  --server <server_ip> \
  --user <user_name> \
  --password <password> \
  --domain-type LDAP \
  --domain-value mydomain.com
```

### Command Line Arguments

- `--server` (required) - VCF Operations Networks hostname or IP
- `--user` (required) - Username for authentication
- `--password` (required) - Password for authentication
- `--domain-type` (optional) - Domain type for authentication (default: LOCAL)
- `--domain-value` (optional) - Domain value for authentication (default: example.com)

## Example Demonstrates

- Creating TokenService instance with default domain settings
- Creating TokenService instance with custom domain settings
- Fetching authentication token from server
- Displaying token information
- Error handling during token generation

## TokenService Class API

### Constructor

```python
TokenService(server, username, password, session=None, domain_type='LOCAL', domain_value='example.com')
```

**Parameters:**
- `server` (str) - VCF Operations Networks hostname or IP
- `username` (str) - Username for authentication
- `password` (str) - Password for authentication
- `session` (requests.Session, optional) - HTTP session (created if not provided)
- `domain_type` (str, optional) - Domain type for authentication (default: 'LOCAL')
- `domain_value` (str, optional) - Domain value for authentication (default: 'example.com')

### Methods

#### `fetch_token()`
Fetches authentication token from the server and caches it.

**Returns:** `str` - Authentication token

**Raises:** `Exception` - If authentication fails

#### `get_cached_token()`
Returns cached token if available, otherwise fetches new token.

**Returns:** `str` - Authentication token

#### `clear_cache()`
Clears the cached token.

## Best Practices

1. **Use TokenService Class for API Clients**
   - Create instance once during initialization
   - Reuse token across API clients
   - Use `get_cached_token()` to avoid server calls

2. **Token Reuse**
   - Generate token once
   - Reuse across multiple API clients
   - Reduces server load significantly

3. **Domain Configuration**
   - Use default 'LOCAL' domain for local authentication
   - Specify 'LDAP' or other domain types as needed
   - Provide correct domain value for your environment

4. **Error Handling**
   - Always wrap token generation in try-except
   - Handle authentication failures gracefully
   - Check for valid credentials before calling

5. **Cache Management**
   - Use `get_cached_token()` for subsequent calls
   - Call `clear_cache()` when token expires
   - Re-fetch token after clearing cache

## Integration with API Clients

The TokenService class can be used with the main client utilities:

```python
from auth_token.token_service import TokenService
from operations_networks.helpers.client import create_vcf_operations_for_networks_client
from operations_networks.helpers.client import StubFactoryType

# Generate token once with custom domain settings
token_service = TokenService(
    server=server,
    username=username,
    password=password,
    domain_type='LOCAL',
    domain_value='example.com')
token = token_service.fetch_token()

# Use token with multiple clients
info_client = create_vcf_operations_for_networks_client(
    server=server,
    token=token,
    stub_factory_type=StubFactoryType.INFO)

groups_client = create_vcf_operations_for_networks_client(
    server=server,
    token=token,
    stub_factory_type=StubFactoryType.GROUPS)
```

## Troubleshooting

### Issue: Authentication Failed
**Solution:** Verify credentials are correct and user has appropriate permissions

### Issue: Token Expired
**Solution:** Call `clear_cache()` and fetch new token

### Issue: Connection Timeout
**Solution:** Check network connectivity to VCF Operations Networks instance

### Issue: SSL Certificate Error
**Solution:** Use session with `verify=False` for testing (not recommended for production)

## Support

For issues or questions:
- Check the example files for usage patterns
- Refer to the VCF API documentation
- Review error messages for specific issues

---
