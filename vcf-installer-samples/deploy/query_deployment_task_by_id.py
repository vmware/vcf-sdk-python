#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import argparse
import time

from vmware.vcf_installer import model_client
from utils.client import create_vcf_installer_client
from utils.misc_util import parse_bool_or_str
from utils.sddc_spec_util import save_sddc_spec_to_file
from utils.sddc_task_util import poll_sddc_deployment_status

"""
Description:
Queries an existing VCF deployment by SDDC ID and prints the SDDC spec in JSON format.
"""

parser = argparse.ArgumentParser()

parser.add_argument(
    '--vcf_installer_fqdn',
    required=True,
    help='VCF Installer Appliance hostname or FQDN.')

parser.add_argument(
    '--vcf_installer_admin_password',
    required=True,
    help='VCF Installer Appliance password for admin@local user.')

parser.add_argument(
    '--deployment_task_id',
    required=True,
    help='Deployment task ID to query (e.g., 2a90abde-0c88-4b6e-a184-85b4fa57facc).')

parser.add_argument(
    '--ca_certs',
    default=True,
    type=parse_bool_or_str,
    help="""By default uses built-in CA.
    To pass custom CA provide absolute path to the folder containing CA certs to use for SSL verifications.
    Pass False to disable SSL verifications
    (do not leave it empty on production environments).""")

parser.add_argument(
    '--deployment_spec_save_file_path', required=False,
    help='Optional path to save the final SDDC spec as a JSON file.')

args = parser.parse_args()
server = args.vcf_installer_fqdn
password = args.vcf_installer_admin_password

client = create_vcf_installer_client(
    server=server,
    password=password,
    ca_certs=args.ca_certs
)

sddc_task = poll_sddc_deployment_status(client, args.deployment_task_id, timeout=7)
print("Finished deployment task with id: {}".format(sddc_task.id))
        
save_sddc_spec_to_file(client, sddc_task.id, args.deployment_spec_save_file_path)

print("Sample completed successfully")