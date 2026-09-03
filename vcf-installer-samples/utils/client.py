#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import requests
from vmware.vcf_installer.v1.tokens.access_token_client import Refresh
from vmware.vapi.security.client.security_context_filter import SecurityContextFilter
from vmware.vapi.security.oauth import create_oauth_security_context

from vmware.vcf_installer.v1_client import Tokens
from vmware.vcf_installer.model_client import TokenCreationSpec
from vmware.vcf_installer_client import StubFactory

from vmware.vapi.bindings.stub import ApiClient
from vmware.vapi.lib.connect import get_requests_connector
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory


class VcfInstallerStubFactory(StubFactory):
    def __init__(self, stub_config):
        StubFactory.__init__(self, stub_config)


class _VcfInstallerSecurityContextFilter(SecurityContextFilter):
    """
    VCF Installer Security Context filter in API Provider chain adds the security
    context based on a refresh token to the execution context passed in.
    """

    def __init__(self, session=None, access_token=None, refresh_token=None, host_url=None):
        """
        Initialize SecurityContextFilter

        :type  session: :class:`requests.Session`
        :param session: Requests Session object to use for making HTTP calls
        :type  refresh_token: :class:`str`
        :param refresh_token: Refresh token to use for obtaining an access token
        :type  refresh_url: :class:`str`
        :param refresh_url: URL that allows exchanging a refresh token for an
            access token
        """
        SecurityContextFilter.__init__(self, None)
        self._session = session
        self._refresh_token = refresh_token
        self._host_url = host_url
        self._access_token = access_token

    def get_max_retries(self):
        """
        Get the max number of retries

        :rtype: :class:`int`
        :return: Number of retries
        """
        return 1

    def get_security_context(self, on_error):
        """
        Retrieve security context. If this method is called after an error
        occured, then a new access token is obtained using the refresh token and
        a new security context is created.

        :type  on_error: :class:`bool`
        :param on_error: Whether this method is called after getting an error
        :rtype: :class:`vmware.vapi.core.SecurityContext`
        :return: Security context
        """
        if on_error or not self._access_token:
            refresh_token_service = Refresh(
                StubConfigurationFactory.new_std_configuration(
                    get_requests_connector(
                        session=self._session, msg_protocol='rest', url=self._host_url)))
            self._access_token = refresh_token_service.refresh_access_token(self._refresh_token)
        return create_oauth_security_context(self._access_token)

    def should_retry(self, error_value):
        """
        Returns whether the request should be retried or not based on the error
        specified.

        :type  error_value: :class:`vmware.vapi.data.value.ErrorValue`
        :param error_value: Method error
        :rtype: :class:`bool`
        :return: Returns True if request should be retried in case the error is
            either Unauthenticated or Unauthorized else False
        """
        if error_value and error_value.has_field('errorCode'):
            error_code = error_value.get_field('errorCode').value
            if error_code in ['Unauthorized', 'Unauthenticated']:
                return True
        return False


class VcfInstallerClient(ApiClient):
    """
    VCF Installer Client class that providess access to stubs for all the services in the
    VCF Installer API
    """

    def __init__(self, session, server, username, password, ca_certs):
        """
        Initialize VcfInstallerClient by creating a stub factory instance

        :type  session: :class:`requests.Session`
        :param session: Requests HTTP session instance. If not specified,
        then one is automatically created and used
        :type  server: :class:`str`
        :param server: VCF Installer host name or IP address
        :type  username: :class:`str`
        :param username: Name of the user
        :type  password: :class:`str`
        :param password: Password of the user
        :type  ca_certs: :class:`str`|`bool`
        :param ca_certs: Certificate validation.
            True: validate with built-in root CA;
            False: do not validate;
            "/path/to/certificate": absolute path to local CA certs to use for validation of server cert.
            For more info see: https://requests.readthedocs.io/en/latest/user/advanced/#SSL%20Cert%20Verification
        :rtype: :class:`VcfInstallerClient`
        :return: VCF Installer Client instance
        """
        if not session:
            session = requests.Session()
        session.verify = ca_certs
        self.session = session

        host_url = "https://" + server
        if username is not None and password is not None:
            tokens_service = Tokens(
                StubConfigurationFactory.new_std_configuration(
                    get_requests_connector(
                        session=session, msg_protocol='rest', url=host_url)))
            create_token_spec = TokenCreationSpec(username=username, password=password)
            token_pair = tokens_service.create_token(token_creation_spec=create_token_spec)
            access_token = token_pair.access_token
            refresh_token = token_pair.refresh_token.id
        else:
            raise Exception("Unable to authenticate. Missing username/password.")

        stub_factory = VcfInstallerStubFactory(
            StubConfigurationFactory.new_std_configuration(
                get_requests_connector(
                    session=session, msg_protocol='rest', url=host_url,
                    provider_filter_chain=[
                        _VcfInstallerSecurityContextFilter(session=session,
                                                           access_token=access_token,
                                                           refresh_token=refresh_token,
                                                           host_url=host_url)])))
        ApiClient.__init__(self, stub_factory)


def create_vcf_installer_client(server=None,
                                username='admin@local',
                                password=None,
                                session=None,
                                ca_certs=True):
    """
    Helper method to create an instance of the VCF Installer client using the
    VCF Installer URL.

    :type  session: :class:`requests.Session`
    :param session: Requests HTTP session instance. If not specified,
    then one is automatically created and used
    :type  server: :class:`str`
    :param server: VCF Installer host name or IP address
    :type  username: :class:`str`
    :param username: Name of the user
    :type  password: :class:`str`
    :param password: Password of the user
    :type  ca_certs: :class:`str`|`bool`
    :param ca_certs: Certificate validation.
        True: validate with built-in root CA;
        False: do not validate;
        "/path/to/certificate": absolute path to local CA certs to use for validation of server cert.
        For more info see: https://requests.readthedocs.io/en/latest/user/advanced/#SSL%20Cert%20Verification
    :rtype: :class:`VcfInstallerClient`
    :return: VCF Installer Client instance
    """
    session = session or requests.Session()
    return VcfInstallerClient(session=session,
                              server=server,
                              username=username,
                              password=password,
                              ca_certs=ca_certs)
