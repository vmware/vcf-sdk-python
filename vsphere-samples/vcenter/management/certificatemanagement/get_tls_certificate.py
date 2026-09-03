#!/usr/bin/env python

# Copyright (c) 2020-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '7.0+'

import argparse
from helpers.common import (sample_cli, sample_util)
from vmware.vapi.vsphere.client import create_vsphere_client
import requests

"""
Description: Demonstrates retrieval of the MACHINE SSL certificate from the vCenter
along with the decoded X.509 certificate fields

Sample Prerequisites:
- The user invoking the API should have the System.Read privilege.
"""

parser = sample_cli.build_arg_parser()

args = sample_util.process_cli_args(parser.parse_args())

session = requests.session()
session.verify = False if args.skipverification else True

# Login to vCenter
vsphere_client = create_vsphere_client(server=args.server,
                                       username=args.username,
                                       password=args.password,
                                       session=session)

print('Listing the MACHINE SSL certificate along with the decoded X.509 fields ')
print(vsphere_client.vcenter.certificate_management.vcenter.Tls.get())
