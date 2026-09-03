#!/usr/bin/env python

# Copyright (c) 2023-2026 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

"""
This module provides utility methods for working with API clients.
It includes methods for creating API client instances and other common API client tasks.
"""

import logging
import os
import urllib3
import requests
from pathlib import Path

from vmware.vapi.bindings.stub import StubConfiguration
from vmware.vapi.lib.connect import get_requests_connector


__author__ = 'Broadcom, Inc.'
__docformat__ = 'restructuredtext en'

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class ApiClientUtil:
    """
    This class provides utility methods for working with API clients.
    
    It includes methods for creating API client instances and other common API client tasks.
    """
    
    RESPONSE_TIMEOUT = 180  # seconds
    CONNECT_TIMEOUT = 180  # seconds
    
    def __init__(self):
        """Initialize the API client utility."""
        self.LOGS_HOST = None
        self.LOGS_PORT = None
        self.OPS_HOST = None
        self.username = None
        self.password = None
        self.OPS_AUTH_URL = "/api/auth/token/acquire"
        self.TOKEN_EXCHANGE_URL = "/api/auth/token/exchange"
        self.TOKEN_EXCHANGE_BODY = {
            "serviceKeys": ["ops-li"]
        }
        
        # Client components
        self.stub_config = None
        self.connector = None
        self.session = None

    def get_ops_token(self):
        """
        Get OPS authentication token.
        
        :return: OPS token string
        :raises: RuntimeError if token acquisition fails
        """
        try:
            # Create session with SSL verification disabled
            session = requests.Session()
            session.verify = False
            
            # Prepare request body
            json_body = {
                "username": self.username,
                "password": self.password
            }
            
            # Make request
            url = f"{self.OPS_HOST}{self.OPS_AUTH_URL}"
            response = session.post(
                url,
                json=json_body,
                headers={"Content-Type": "application/json"},
                timeout=self.CONNECT_TIMEOUT
            )
            
            response.raise_for_status()
            
            # Parse response
            json_response = response.json()
            token = json_response.get("token")
            
            if not token:
                raise RuntimeError("No token in response")
            
            logger.info("Successfully acquired OPS token")
            return token
            
        except Exception as e:
            logger.error(f"ERROR in API Client getOpsToken: {e}")
            raise RuntimeError(f"Failed to get OPS token: {e}")
    
    def get_logs_token(self, ops_token):
        """
        Exchange OPS token for Logs service token.
        
        :param ops_token: The OPS authentication token
        :return: Logs JWT token string
        :raises: RuntimeError if token exchange fails
        """
        try:
            # Create session with SSL verification disabled
            session = requests.Session()
            session.verify = False
            
            # Make request
            url = f"{self.OPS_HOST}{self.TOKEN_EXCHANGE_URL}"
            response = session.post(
                url,
                json=self.TOKEN_EXCHANGE_BODY,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"OpsToken {ops_token}"
                },
                timeout=self.CONNECT_TIMEOUT
            )
            
            response.raise_for_status()
            
            # Parse response
            json_response = response.json()
            jwt_token = json_response.get("jwtToken")
            
            if not jwt_token:
                raise RuntimeError("No jwtToken in response")
            
            logger.info("Successfully acquired Logs token")
            return jwt_token
            
        except Exception as e:
            logger.error(f"ERROR in API Client getLogsToken: {e}")
            raise RuntimeError(f"Failed to get Logs token: {e}")
    
    def read_client_properties(self):
        """
        Read client configuration properties from file.
        
        :return: Dictionary of configuration properties
        :raises: RuntimeError if properties file cannot be read
        """
        props = {}
        
        try:
            # Try multiple locations for the properties file
            possible_paths = [
                # Relative to current working directory
                "src/main/resources/client-config.properties",
                # Relative to this file's location
                Path(__file__).parent.parent / "resources" / "client-config.properties"
            ]
            
            config_file = None
            for path in possible_paths:
                if isinstance(path, Path):
                    path = str(path)
                if os.path.exists(path):
                    config_file = path
                    break
            
            if not config_file:
                raise FileNotFoundError(f"Could not find client-config.properties in any of: {possible_paths}")
            
            # Read properties file
            with open(config_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        props[key.strip()] = value.strip()
            
            logger.info(f"Successfully read client properties from {config_file}")
            return props
            
        except Exception as e:
            logger.error(f"Unable to read client config properties: {e}")
            raise RuntimeError(f"Failed to read properties: {e}")
    
    def create_url(self, host_address, port):
        """
        Create URL for the API endpoint.
        
        :param host_address: Host address
        :param port: Port number
        :return: Complete URL string
        """
        return f"https://{host_address}:{port}"
    
    def initialize_client(self, OPS, uname, pword, LI_HOST, PORT):
        """
        Initialize the vRLI client with proper authentication and configuration.
        
        :raises RuntimeError: If client initialization fails
        """
        logger.info("Initializing vRLI client...")
        
        try:

            self.OPS_HOST = "https://" + OPS + "/suite-api"
            self.username = uname
            self.password = pword
            self.LOGS_HOST = LI_HOST
            self.LOGS_PORT = int(PORT)
            
            # Validate required properties
            if not all([self.OPS_HOST, self.username, self.password, self.LOGS_HOST, self.LOGS_PORT]):
                raise ValueError("Missing required configuration properties")
            
            # Get authentication tokens
            ops_token = self.get_ops_token()
            logs_token = self.get_logs_token(ops_token)
            
            # Build the base URL
            base_url = self.create_url(self.LOGS_HOST, self.LOGS_PORT)
            
            # Create HTTP connector with SSL configuration
            session = requests.Session()
            session.verify = False  # Disable SSL verification
            
            # Add the JWT token as a custom header (X-JWT-Token)
            # This is required for Logs API authentication
            session.headers.update({
                'X-JWT-Token': logs_token
            })
            
            self.connector = get_requests_connector(
                session=session,
                msg_protocol='rest',
                url=base_url
            )
            
            # Create stub configuration without security context
            # The X-JWT-Token header is already set in the session
            self.stub_config = StubConfiguration(self.connector)

            logger.info("vRLI client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize vRLI client: {e}")
            raise RuntimeError(f"Client initialization failed: {e}")

    def get_stub_config(self):
        return self.stub_config


    def cleanup(self):
        """Clean up resources and close connections."""
        logger.info("Cleaning up resources...")
        try:
            if self.connector:
                # Close the connector
                self.connector.disconnect()
                logger.info("API client closed successfully")
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")
