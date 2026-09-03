# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import requests
from vcf.operations_networks.auth_client import Token
from vcf.operations_networks.model_client import UserCredential, Domain
from vmware.vapi.lib.connect import get_requests_connector
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory

class TokenService:
    """
    Class responsible for fetching authentication tokens from VCF Operations for Networks.
    This centralizes token generation logic.
    """
    
    def __init__(self, server, username, password, session=None, domain_type='LOCAL', domain_value='example.com'):
        """
        Initialize TokenService with server credentials.
        
        :type  server: :class:`str`
        :param server: VCF Operations Networks instance hostname or IP
        :type  username: :class:`str`
        :param username: Username for authentication
        :type  password: :class:`str`
        :param password: Password for authentication
        :type  session: :class:`requests.Session` or ``None``
        :param session: Requests HTTP session instance. If not specified, then one
            is automatically created and used
        :type  domain_type: :class:`str`
        :param domain_type: Domain type for authentication (default: 'LOCAL')
        :type  domain_value: :class:`str`
        :param domain_value: Domain value for authentication (default: 'example.com')
        """
        self.server = server
        self.username = username
        self.password = password
        self.session = session if session else self._create_default_session()
        self.domain_type = domain_type
        self.domain_value = domain_value
        self._cached_token = None
    
    def _create_default_session(self):
        """
        Create a default requests session with SSL verification disabled.
        
        :rtype: :class:`requests.Session`
        :return: Configured requests session
        """
        session = requests.Session()
        session.verify = False
        return session
    
    def fetch_token(self):
        """
        Fetch authentication token for VCF Operations for Networks.
        This method can be called once and the token can be reused across multiple API clients.
        
        :rtype: :class:`str`
        :return: Authentication token string
        :raises Exception: If authentication fails or credentials are missing
        """
        if not self.username or not self.password:
            raise Exception("Unable to authenticate. Missing username/password.")
        
        host_url = f"https://{self.server}/api/ni"
        
        try:
            request_connector = get_requests_connector(
                session=self.session, 
                msg_protocol='rest', 
                url=host_url)
            
            token_service = Token(
                StubConfigurationFactory.new_std_configuration(request_connector))
            
            domain = Domain(domain_type=self.domain_type, value=self.domain_value)
            username_credentials_spec = UserCredential(
                domain=domain, 
                username=self.username, 
                password=self.password)
            
            auth_token = token_service.create(user_credential=username_credentials_spec)
            
            # Cache the token for potential reuse
            self._cached_token = auth_token.token
            
            return self._cached_token
            
        except Exception as e:
            raise Exception(f"Failed to generate authentication token: {e}")
    
    def get_cached_token(self):
        """
        Get the cached token if available, otherwise fetch a new one.
        
        :rtype: :class:`str`
        :return: Authentication token string
        """
        if self._cached_token:
            return self._cached_token
        return self.fetch_token()
    
    def clear_cache(self):
        """
        Clear the cached token. Useful when token expires or needs to be refreshed.
        """
        self._cached_token = None
