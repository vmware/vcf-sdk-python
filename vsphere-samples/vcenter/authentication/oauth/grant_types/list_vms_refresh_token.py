#!/usr/bin/env python

# Copyright (c) 2020-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

from vmware.vapi.vsphere.client import create_vsphere_client

from helpers.common import sample_cli
from helpers.common import sample_util
from helpers.common.ssl_helper import get_unverified_session
from vcenter.authentication.oauth.grant_types.oauth_utility \
    import login_using_refresh_token
import argparse

__vcenter_version__ = '7.0+'

"""
To run this sample,
$ python list_vms_refresh_token.py \
    --server <VC_IP> --client_id <client_id> --client_secret <client_secret>\
    --refresh_token <refresh_token> --skipverification
"""

parser = argparse.ArgumentParser()
parser.add_argument("--server",
                    help="VC IP or hostname")
parser.add_argument("--client_id",
                    help="Client/Application ID of the server to server app")
parser.add_argument("--client_secret",
                    help="Client/Application secret \
                        of the server to server app")
parser.add_argument("--refresh_token",
                    help="Refresh token used to refresh the access token")
parser.add_argument('--skipverification',
                    action='store_true',
                    help='Verify server certificate when connecting to vc.')

args = parser.parse_args()

session = get_unverified_session() if args.skipverification else None
saml_assertion = login_using_refresh_token(
                    args.server,
                    session,
                    args.client_id,
                    args.client_secret,
                    args.refresh_token)

client = create_vsphere_client(
            server=args.server,
            bearer_token=saml_assertion,
            session=session)
vms = client.vcenter.VM.list()
print(vms)
