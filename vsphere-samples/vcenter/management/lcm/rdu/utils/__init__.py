#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '9.0.0'

import requests
import logging
import argparse

from com.vmware.cis_client import Session
from vmware.vapi.security.session import create_session_security_context
from vmware.vapi.lib.connect import get_requests_connector
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory
from vmware.vapi.security.client.security_context_filter import \
    LegacySecurityContextFilter
from vmware.vapi.security.user_password import \
    create_user_password_security_context

from helpers.common import sample_cli
from helpers.common.ssl_helper import get_unverified_session

logger = logging.getLogger(__name__)


def get_plugin_update_arg_parser(parser: argparse.ArgumentParser = None):
    if not parser:
        parser = sample_cli.build_arg_parser()

    parser.add_help = True
    parser.add_argument('--plugin-repo',
                        action='store',
                        required=True,
                        help="URL to the lifecycle plugin repository.")
    return parser


def get_rdu_arg_parser(parser: argparse.ArgumentParser = None):
    if not parser:
        parser = sample_cli.build_arg_parser()

    parser.add_help = True
    parser.add_argument('--target-temp-password',
                        action='store',
                        required=True,
                        help="A temporary password for the deployed target machine")
    parser.add_argument('--target-version',
                        action='store',
                        required=True,
                        help="The target version in format A.B.C.D")
    parser.add_argument('--target-upgrade-repo',
                        action='store',
                        required=True,
                        help="URL to the target upgrade repository.")
    parser.add_argument('--target-ova',
                        action='store',
                        required=True,
                        help="URL to the target machine's OVA")
    parser.add_argument('--autocancellation',
                        action='store_true',
                        help="Auto cancel if the upgrade fails")
    parser.add_argument('--preserve-original-name',
                        action='store_true',
                        help="Preserve the original name of the source vCenter VM.")

    return parser


def get_vcenter_client(server: str, username: str, password: str, skip_verification: bool,
                       endpoint: str = "lcm/api", auth_with_session: bool = False):
    """
    Create the session and the connection to the desired vCenter
    :param server: vCenter hostname
    :param username: vCenter username for authentication
    :param password: vCenter password for authentication
    :param skip_verification: Whether to disable the certificate verification when creating a session.
    :param endpoint: Endpoint in which to call the vCenter api's. For RDU the default is lcm/api.
    :param auth_with_session: If set to true, the authentication with the vCenter will happen with a session,
    created by the service answering on the passed endpoint.
                              If set to false, it will use username and password authentication.
    :return: Configuration for the vapi stub and session id if authentication with session is enabled.
    """
    session = get_unverified_session() if skip_verification else None
    if not session:
        session = requests.Session()

    host_url = "https://{}/{}".format(server, endpoint)
    logger.info("Connecting on endpoint: %s", host_url)

    sec_ctx = create_user_password_security_context(username,
                                                    password)
    session_id = ""

    if auth_with_session:
        session_svc = Session(
            StubConfigurationFactory.new_std_configuration(
                get_requests_connector(
                    session=session, url=host_url,
                    provider_filter_chain=[
                        LegacySecurityContextFilter(
                            security_context=sec_ctx)])))

        session_id = session_svc.create()
        logger.info("Authenticating with session ID: %s", session_id)

        sec_ctx = create_session_security_context(session_id)
    else:
        logger.info("Authenticating with username and password")

    stub_config = StubConfigurationFactory.new_std_configuration(
        get_requests_connector(
            session=session, url=host_url,
            provider_filter_chain=[
                LegacySecurityContextFilter(
                    security_context=sec_ctx)]))

    return stub_config, session_id
