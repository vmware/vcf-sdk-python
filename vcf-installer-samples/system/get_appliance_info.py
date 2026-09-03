#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import argparse

from utils.client import create_vcf_installer_client
from utils.misc_util import parse_bool_or_str

"""
Demonstrates how to obtain appliance info
"""

parser = argparse.ArgumentParser()

parser.add_argument(
    '--vcf_installer_host_address',
    required=True,
    help='VCF Installer Appliance address')

parser.add_argument(
    '--vcf_installer_admin_password',
    required=True,
    help='VCF Installer Appliance password for admin@local user')

parser.add_argument(
    '--ca_certs',
    default=True,
    type=parse_bool_or_str,
    help="""By default uses built-in CA.
    To pass custom CA provide absolute path to the folder containing CA certs to use for SSL verifications.
    Pass False to disable SSL verifications
    (do not leave it empty on production environments).""")

args = parser.parse_args()
server = args.vcf_installer_host_address
password = args.vcf_installer_admin_password
client = create_vcf_installer_client(server=server,
                                     password=password,
                                     ca_certs=args.ca_certs)

appliance_info = client.v1.system.ApplianceInfo.get_appliance_info()
print("VCF Installer version: {}".format(appliance_info.version))

print("Sample completed successfully")
