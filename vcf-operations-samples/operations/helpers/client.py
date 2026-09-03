# Copyright (c) 2025-2026 Broadcom Inc. and/or its subsidiaries. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import requests
from vcf.operations.api.auth.token_client import Acquire

from vcf.operations.model_client import UsernamePassword

from vmware.vapi.lib.connect import get_requests_connector
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory
from vmware.vapi.security.http_authorization import (
    create_http_authorization_security_context,
)
from vmware.vapi.security.client.security_context_filter import (
    LegacySecurityContextFilter,
)


OPS_AUTHZ_SCHEME = "OpsToken"
API_ENDPOINT = "suite-api"


class VcfOperationsClient:
    """
    VCF Operations Client class that providess access to stubs for all the services in the
    VCF Operations API
    """

    def __init__(self, session, server, username, password):
        """
        Initialize VcfOperationsClient by creating a stub factory instance
        :type  session: :class:`requests.Session`
        :param session: Requests HTTP session instance. If not specified,
        then one is automatically created and used
        :type  server: :class:`str`
        :param server: vCenter host name or IP address
        :type  username: :class:`str`
        :param username: Name of the user
        :type  password: :class:`str`
        :param password: Password of the user
        """
        if not session:
            session = requests.Session()
        self.session = session

        host_url = f"https://{server}/{API_ENDPOINT}"
        if username is not None and password is not None:
            aquire_tokens_service = Acquire(
                StubConfigurationFactory.new_std_configuration(
                    get_requests_connector(
                        session=session, msg_protocol="rest", url=host_url
                    )
                )
            )
            username_password_spec = UsernamePassword(
                auth_source=None, username=username, password=password
            )
            auth_token = aquire_tokens_service.acquire_token(
                username_password=username_password_spec
            )
            ops_token = auth_token.token
            sec_ctx = create_http_authorization_security_context(
                authz_credentials=ops_token, authn_scheme=OPS_AUTHZ_SCHEME
            )
            self.stub_config = StubConfigurationFactory.new_std_configuration(
                get_requests_connector(
                    session=session,
                    url=host_url,
                    msg_protocol="rest",
                    provider_filter_chain=[
                        LegacySecurityContextFilter(security_context=sec_ctx)
                    ],
                )
            )
        else:
            raise Exception("Unable to authenticate. Missing username/password.")


def create_vcf_operations_client(server=None, username=None, password=None, session=None):
    """
    Helper method to create an instance of the VCF Operations API client using public
    Token REST API calls".
    :type  session: :class:`requests.Session` or ``None``
    :param session: Requests HTTP session instance. If not specified, then one
        is automatically created and used
    :rtype: :class:`utils..client.VcfOperationsClient`
    :return: VCF Operations Client instance
    """
    session = session or requests.Session()
    session.verify = False
    requests.packages.urllib3.disable_warnings()
    return VcfOperationsClient(
        session=session, server=server, username=username, password=password
    )
