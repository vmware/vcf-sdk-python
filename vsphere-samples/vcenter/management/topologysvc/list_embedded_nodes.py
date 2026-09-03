#!/usr/bin/env python

# Copyright (c) 2020-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '7.0+'


from vmware.vapi.vsphere.client import create_vsphere_client
from com.vmware.vcenter.topology_client import Nodes
from helpers.common import (sample_cli, sample_util)
from helpers.common.ssl_helper import get_unverified_session

"""
Description: Demonstrates listing of Embedded vCenter Server node's information
in an SSO Domain.

Sample Prerequisites:
- The user invoking the API should have the System.Read privilege.
"""

parser = sample_cli.build_arg_parser()

args = sample_util.process_cli_args(parser.parse_args())

session = get_unverified_session() if args.skipverification else None

# Login to vCenter
vsphere_client = create_vsphere_client(server=args.server,
                                       username=args.username,
                                       password=args.password,
                                       session=session)

filter_spec = Nodes.FilterSpec({Nodes.ApplianceType.VCSA_EMBEDDED})

print(vsphere_client.vcenter.topology.Nodes.list(filter_spec))
