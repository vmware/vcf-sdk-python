#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import requests
from vcf.nsx.api.v1_client import StubFactory
from vmware.vapi.bindings.stub import ApiClient
from vmware.vapi.lib.connect import get_requests_connector
from vmware.vapi.security.user_password import \
    create_user_password_security_context
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory
from vcf.nsx.policy.api.v1_client import StubFactory as PolicyV1StubFactory


def create_nsx_stub_config(server, username, password):
    host_url = "https://" + server
    session = requests.Session()
    session.verify = False

    security_context = create_user_password_security_context(
        username, password
    )
    connector = get_requests_connector(
        session=session, msg_protocol="rest", url=host_url
    )
    connector.set_security_context(security_context)
    config = StubConfigurationFactory.new_std_configuration(connector)
    return config


def create_policy_client(server, username, password):
    """
    Helper method to create an ApiClient for an NSX server's policy APIs.

    :type  server: :class:`str`
    :param server: vCenter host name or IP address
    :type  username: :class:`str`
    :param username: Name of the user
    :type  password: :class:`str`
    :param password: Password of the user
    :rtype: :class:`vmware.vapi.bindings.stub.ApiClient`
    :return: ApiClient instance
    """
    nsx_client_config = create_nsx_stub_config(server, username, password)
    policy_stub_factory =  PolicyV1StubFactory(nsx_client_config)
    return ApiClient(policy_stub_factory)


def create_nsx_client(server, username, password):
    """
    Helper method to create an ApiClient for an NSX server.

    :type  server: :class:`str`
    :param server: vCenter host name or IP address
    :type  username: :class:`str`
    :param username: Name of the user
    :type  password: :class:`str`
    :param password: Password of the user
    :rtype: :class:`vmware.vapi.bindings.stub.ApiClient`
    :return: ApiClient instance
    """
    nsx_client_config = create_nsx_stub_config(server, username, password)
    stub_factory = StubFactory(nsx_client_config)
    return ApiClient(stub_factory)
