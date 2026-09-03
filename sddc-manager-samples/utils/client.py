#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import requests

from vmware.sddc_manager.v1_client import Tokens
from vmware.sddc_manager.model_client import TokenCreationSpec
from vmware.sddc_manager_client import StubFactory

from vmware.vapi.bindings.stub import ApiClient
from vmware.vapi.lib.connect import get_requests_connector
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory
from utils.sddc_manager_filter import SDDCManagerSecurityContextFilter



class SDDCManagerStubFactory(StubFactory):
    def __init__(self, stub_config):
        StubFactory.__init__(self, stub_config)


class SDDCManagerClient(ApiClient):
    """
    SDDC Manager Client class that providess access to stubs for all the services in the
    SDDC Manager API
    """
    def __init__(self, session, server, username, password, refresh_token):
        """
        Initialize SDDCManagerClient by creating a stub factory instance

        :type  session: :class:`requests.Session`
        :param session: Requests HTTP session instance. If not specified,
        then one is automatically created and used
        :type  server: :class:`str`
        :param server: vCenter host name or IP address
        :type  username: :class:`str`
        :param username: Name of the user
        :type  password: :class:`str`
        :param password: Password of the user
        :type  refresh_token: :class:`str`
        :param refresh_token: refresh token obtained from the token service.
        """
        if not session:
            session = requests.Session()
        session.verify = False
        self.session = session

        host_url = "https://" + server
        access_token = None
        if username is not None and password is not None:
            tokens_service = Tokens(
            StubConfigurationFactory.new_std_configuration(
                get_requests_connector(
                    session=session, msg_protocol='rest', url=host_url)))
            create_token_spec = TokenCreationSpec(username=username, password=password)
            token_pair = tokens_service.create_token(token_creation_spec=create_token_spec)
            access_token = token_pair.access_token
            refresh_token = token_pair.refresh_token.id

        stub_factory = SDDCManagerStubFactory(
            StubConfigurationFactory.new_std_configuration(
                get_requests_connector(
                    session=session, msg_protocol='rest', url=host_url,
                    provider_filter_chain=[
                        SDDCManagerSecurityContextFilter(session=session,
                                                         refresh_token=refresh_token,
                                                         host_url=host_url,
                                                         access_token=access_token)])))
        ApiClient.__init__(self, stub_factory)


def create_sddc_manager_client(server=None,
                               username=None,
                               password=None,
                               refresh_token=None,
                               session=None):
    """
    Helper method to create an instance of the SDDCManagerClient.

    :type  server: :class:`str`
    :param server: SDDC Manager host name or IP address
    :type  username: :class:`str`
    :param username: SDDC Manager username
    :type  password: :class:`str`
    :param password: SDDC Manager password
    :type  refresh_token: :class:`str`
    :param refresh_token: Refresh token obtained from TokenService
    :type  session: :class:`requests.Session` or ``None``
    :param session: Requests HTTP session instance. If not specified, then one
        is automatically created and used
    :rtype: :class:`utils.client.SDDCManagerClient`
    :return: SDDCManagerClient instance
    """
    session = session or requests.Session()
    return SDDCManagerClient(session=session,
                             server=server,
                             username=username,
                             password=password,
                             refresh_token=refresh_token)
