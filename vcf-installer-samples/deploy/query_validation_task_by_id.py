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
from utils.sddc_task_util import poll_sddc_validation_status, log_validation_result

"""
Description:
Queries an existing VCF validation by SDDC ID.
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
    '--validation_task_id',
    required=True,
    help='Validation task ID to query (e.g., 2a90abde-0c88-4b6e-a184-85b4fa57facc).')

parser.add_argument(
    '--wait_for_task_completion',
    default=True,
    help='Boolean flag if waitng for task completion is needed.'
)

parser.add_argument(
    '--ca_certs',
    default=True,
    type=parse_bool_or_str,
    help="""By default uses built-in CA.
    To pass custom CA provide absolute path to the folder containing CA certs to use for SSL verifications.
    Pass False to disable SSL verifications
    (do not leave it empty on production environments).""")

args = parser.parse_args()
server = args.vcf_installer_fqdn
password = args.vcf_installer_admin_password

client = create_vcf_installer_client(
    server=server,
    password=password,
    ca_certs=args.ca_certs
)

if args.wait_for_task_completion == True:
    sddc_task = poll_sddc_validation_status(client, args.validation_task_id, timeout=3)
    print("Finished validation task with id: {}".format(sddc_task.id))
else:
    validation = client.v1.sddcs.Validations.get_sddc_spec_validation(args.validation_task_id)
    log_validation_result(validation)

print("Sample completed successfully")