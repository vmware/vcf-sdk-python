# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import requests
from enum import Enum

# Import all available StubFactory types
from vcf.operations_networks.info_client import StubFactory as InfoStubFactory
from vcf.operations_networks.infra_client import StubFactory as InfraStubFactory
from vcf.operations_networks.groups_client import StubFactory as GroupsStubFactory
from vcf.operations_networks.groups.applications_client import StubFactory as GroupsApplicationsStubFactory
from vcf.operations_networks.groups.tiers_client import StubFactory as GroupsTiersStubFactory
from vcf.operations_networks.groups.discovered_applications_client import StubFactory as GroupsDiscoveredApplicationsStubFactory
from vcf.operations_networks.entities_client import StubFactory as EntitiesStubFactory
from vcf.operations_networks.entities.problems_client import StubFactory as EntitiesProblemsStubFactory

from vmware.vapi.bindings.stub import ApiClient
from vmware.vapi.lib.connect import get_requests_connector
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory
from vmware.vapi.security.http_authorization import \
    create_http_authorization_security_context
from vmware.vapi.security.client.security_context_filter import \
    LegacySecurityContextFilter

# Import token service
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from auth_token.token_service import TokenService

OPS_NETWORK_AUTHZ_SCHEME = 'NetworkInsight'

class StubFactoryType(Enum):
    """Enumeration of available StubFactory types"""
    INFO = "info"
    INFRA = "infra"
    GROUPS = "groups"
    GROUPS_APPLICATIONS = "groups_applications"
    GROUPS_TIERS = "groups_tiers"
    GROUPS_DISCOVERED_APPLICATIONS = "groups_discovered_applications"
    ENTITIES = "entities"
    ENTITIES_PROBLEMS = "entities_problems"

    @classmethod
    def get_stub_factory_class(cls, factory_type):
        """
        Get the StubFactory class based on the factory type
        
        :type  factory_type: :class:`StubFactoryType` or :class:`str`
        :param factory_type: The type of stub factory to retrieve
        :rtype: class
        :return: The StubFactory class
        :raises ValueError: If factory type is not supported
        """
        # Support both enum and string inputs
        if isinstance(factory_type, str):
            factory_type = cls[factory_type.upper()]
        
        factory_map = {
            cls.INFO: InfoStubFactory,
            cls.INFRA: InfraStubFactory,
            cls.GROUPS: GroupsStubFactory,
            cls.GROUPS_APPLICATIONS: GroupsApplicationsStubFactory,
            cls.GROUPS_TIERS: GroupsTiersStubFactory,
            cls.GROUPS_DISCOVERED_APPLICATIONS: GroupsDiscoveredApplicationsStubFactory,
            cls.ENTITIES: EntitiesStubFactory,
            cls.ENTITIES_PROBLEMS: EntitiesProblemsStubFactory
        }
        
        if factory_type not in factory_map:
            raise ValueError(f"Unsupported factory type: {factory_type}. Supported types: {list(factory_map.keys())}")
        
        return factory_map[factory_type]

class VcfOperationsForNetworksClient(ApiClient):
    """
    VCF Operations for Networks Client class that provides access to stubs for all the services in the
    VCF Operations API
    """
    def __init__(self, session, server, username=None, password=None, token=None, stub_factory_type=StubFactoryType.INFRA):
        """
        Initialize VcfOperationsNetworkClient by creating a stub factory instance

        :type  session: :class:`requests.Session`
        :param session: Requests HTTP session instance. If not specified,
        then one is automatically created and used
        :type  server: :class:`str`
        :param server: vCenter host name or IP address
        :type  username: :class:`str` or ``None``
        :param username: Name of the user (required if token is not provided)
        :type  password: :class:`str` or ``None``
        :param password: Password of the user (required if token is not provided)
        :type  token: :class:`str` or ``None``
        :param token: Pre-generated authentication token (optional). If provided, username/password are not required
        :type  stub_factory_type: :class:`StubFactoryType` or :class:`str`
        :param stub_factory_type: Type of stub factory to use (default: INFRA)
        """

        if not session:
            session = requests.Session()
        session.verify = False
        self.session = session

        host_url = f"https://{server}/api/ni"
        print("host_url: ", host_url)
        
        # Get or generate authentication token
        if token:
            # Use provided token
            ops_nw_token = token
            print("Using provided authentication token")
        elif username is not None and password is not None:
            # Generate new token using TokenService
            print("Generating new authentication token")
            token_service = TokenService(server, username, password, session)
            ops_nw_token = token_service.fetch_token()
        else:
            raise Exception("Unable to authenticate. Either provide a token or username/password.")

        # Create security context with the token
        sec_ctx = create_http_authorization_security_context(authz_credentials=ops_nw_token, authn_scheme=OPS_NETWORK_AUTHZ_SCHEME)
        stub_config = StubConfigurationFactory.new_std_configuration(
                        get_requests_connector(
                            session=session, url=host_url, msg_protocol='rest',
                            provider_filter_chain=[
                                LegacySecurityContextFilter(
                                security_context=sec_ctx)]))

        # Get the appropriate StubFactory class based on the parameter
        stub_factory_class = StubFactoryType.get_stub_factory_class(stub_factory_type)
        stub_factory = stub_factory_class(stub_config)
        ApiClient.__init__(self, stub_factory)

def create_vcf_operations_for_networks_client(server=None,
                                              username=None,
                                              password=None,
                                              token=None,
                                              session=None,
                                              stub_factory_type=StubFactoryType.INFRA):
    """
    Helper method to create an instance of the VCF Operations for Networks API client.
    
    You can either provide username/password for automatic token generation, or provide
    a pre-generated token. Using a pre-generated token is recommended for test frameworks
    to avoid generating a new token for each API client instance.

    :type  server: :class:`str`
    :param server: VCF Operations Networks instance hostname or IP
    :type  username: :class:`str` or ``None``
    :param username: Username for authentication (required if token is not provided)
    :type  password: :class:`str` or ``None``
    :param password: Password for authentication (required if token is not provided)
    :type  token: :class:`str` or ``None``
    :param token: Pre-generated authentication token (optional). If provided, username/password are not required.
        Use TokenService to create a token that can be reused across multiple clients.
    :type  session: :class:`requests.Session` or ``None``
    :param session: Requests HTTP session instance. If not specified, then one
        is automatically created and used
    :type  stub_factory_type: :class:`StubFactoryType` or :class:`str`
    :param stub_factory_type: Type of stub factory to use (default: INFRA).
        Can be StubFactoryType.INFO, StubFactoryType.INFRA, StubFactoryType.GROUPS, 
        StubFactoryType.ENTITIES, or string values "info", "infra", "groups", "entities"
    :rtype: :class:`VcfOperationsForNetworksClient`
    :return: VCF Operations Client instance
    
    Example usage with token reuse:
        # Generate token once using TokenService
        from auth_token.token_service import TokenService
        
        token_service = TokenService(server='10.0.0.1', username='admin', password='pass')
        token = token_service.fetch_token()
        
        # Reuse token for multiple clients
        info_client = create_vcf_operations_for_networks_client(
            server='10.0.0.1', token=token, stub_factory_type=StubFactoryType.INFO)
        
        groups_client = create_vcf_operations_for_networks_client(
            server='10.0.0.1', token=token, stub_factory_type=StubFactoryType.GROUPS)
    """
    session = session or requests.Session()
    return VcfOperationsForNetworksClient(session=session,
                               server=server,
                               username=username,
                               password=password,
                               token=token,
                               stub_factory_type=stub_factory_type)

def get_unverified_session():
    """
    Get a requests session with cert verification disabled.
    Also disable the insecure warnings message.
    Note this is not recommended in production code.
    @return: a requests session with verification disabled.
    """
    session = requests.session()
    session.verify = False
    requests.packages.urllib3.disable_warnings()
    return session
