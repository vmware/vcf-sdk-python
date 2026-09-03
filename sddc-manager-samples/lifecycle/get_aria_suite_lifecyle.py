#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import argparse

from common.ssl_helper import get_unverified_session
from utils.client import create_sddc_manager_client


parser = argparse.ArgumentParser()

parser.add_argument(
    '--server',
    required=True,
    help='SDDC Manager Instance Host Name')

parser.add_argument(
    '--user',
    required=True,
    help='SDDC Manager username')

parser.add_argument(
    '--password',
    required=True,
    help='SDDC Manager password')

args = parser.parse_args()
server = args.server
user = args.user
password = args.password
# hack to skip server verification
session = get_unverified_session()
sddc_client = create_sddc_manager_client(server=server,
                                         username=user, password=password)

pageOfVrslcm = sddc_client.v1.Vrslcms.get_vrslcms()
print("VMware Aria Suite Lifecycle Info:")
print(pageOfVrslcm)
