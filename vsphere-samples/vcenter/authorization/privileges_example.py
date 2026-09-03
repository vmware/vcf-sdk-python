#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '9.0+'

import logging

from helpers.common import sample_cli
from helpers.common import sample_util
from vmware.vapi.vsphere.client import create_vsphere_client
from helpers.common.ssl_helper import get_unverified_session

"""
This example demonstrates how to list and get privileges from 
a vCenter using the corresponding vCenter REST APIs.

Sample Prerequisites:
    - vCenter 9.0+
"""

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def parse_list_result(privileges_list):
    for priv in privileges_list.items:
        logger.info(f"ID = {priv.privilege}")
        logger.info(f"Name = {priv.info.name}")
        logger.info(f"Description = {priv.info.description}")
        logger.info(f"IsOnParent = {priv.info.on_parent}\n")


def get_all_privileges(privs_stub):
    logger.info('Getting all privileges in the vCenter')
    privs = privs_stub.list()
    parse_list_result(privileges_list=privs)
    return privs

def get_privilege_details(privs_stub, priv_id):
    logger.info("Getting privilege details")
    info = privs_stub.get(priv_id)
    logger.info(f"Privilege = {info}")


if __name__ == '__main__':
    parser = sample_cli.build_arg_parser()
    args = sample_util.process_cli_args(parser.parse_args())

    # Login in vCenter
    session = get_unverified_session() if args.skipverification else None
    client = create_vsphere_client(server=args.server,
                                   username=args.username,
                                   password=args.password,
                                   session=session)

    # Create privilege stub
    privileges_svc = client.vcenter.authorization.Privileges

    # List all privileges in the vCenter
    all_privileges = get_all_privileges(privs_stub=privileges_svc)

    # Get the details for each privilege
    for priv in all_privileges.items:
        get_privilege_details(privs_stub=privileges_svc,
                              priv_id=priv.privilege)
