#!/usr/bin/env python

# Copyright (c) 2020-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '7.0+'

from vmware.vapi.vsphere.client import create_vsphere_client
from helpers.common import (sample_cli, sample_util)
from helpers.common.ssl_helper import get_unverified_session

"""
Description: Demonstrates getting the vCenter Server or Platform service
controler node information.

Sample Prerequisites:
- The user invoking the API should have the System.Read privilege.
"""

parser = sample_cli.build_arg_parser()

parser.add_argument('--node',
                    required=True,
                    help='Identifier of the vCenter or Platform Services'
                         ' Controller node. Identifier should be DNS'
                         ' resolvable name of the node')

args = sample_util.process_cli_args(parser.parse_args())

session = get_unverified_session() if args.skipverification else None

# Login to vCenter
vsphere_client = create_vsphere_client(server=args.server,
                                       username=args.username,
                                       password=args.password,
                                       session=session)

print(vsphere_client.vcenter.topology.Nodes.get(args.node))
