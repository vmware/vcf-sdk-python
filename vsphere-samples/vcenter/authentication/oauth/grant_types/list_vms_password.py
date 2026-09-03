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
    import login_using_password
import argparse

__vcenter_version__ = '7.0+'

"""
To run this sample,
$ python list_vms_password --server <VC_IP> \
    --username <username> --password <password> --skipverification
"""

parser = argparse.ArgumentParser()
parser.add_argument("--server",
                    help="VC IP or hostname")
parser.add_argument("--username",
                    help="username to login \
                        to vCenter")
parser.add_argument("--password",
                    help="password to login \
                        to vCenter")
parser.add_argument('--skipverification',
                    action='store_true',
                    help='Verify server certificate when connecting to vc.')

args = parser.parse_args()

session = get_unverified_session() if args.skipverification else None
saml_assertion = login_using_password(
                    args.server,
                    session,
                    args.username,
                    args.password)

client = create_vsphere_client(
            server=args.server,
            bearer_token=saml_assertion,
            session=session)
vms = client.vcenter.VM.list()
print(vms)
