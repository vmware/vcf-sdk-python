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
from com.vmware.vapi.std_client import DynamicID
from helpers.common.ssl_helper import get_unverified_session

"""
This example demonstrates how to query global and inventory 
permissions from a vCenter using the corresponding vCenter REST APIs.

Sample Prerequisites:
    - vCenter 9.0+
"""

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def parse_list_result(permissions_list):
    for perm in permissions_list.items:
        if perm.info.object.type == 'GlobalAcl':
            logger.info('============ Global Permission ============')
        else:
            logger.info('============ Inventory Permission ============')
        logger.info(f"ID = {perm.permission}")
        logger.info(f"Principal = {perm.info.principal}")
        logger.info(f"Role ID = {perm.info.role}")
        logger.info(f"isPropagating = {perm.info.propagating}\n")

def get_all_permissions(perms):
    logger.info('Getting all permissions in the vCenter')
    perms = perms.list()
    parse_list_result(permissions_list=perms)
    return perms

def get_global_permissions_only(perms):
    logger.info("Getting only global permissions from vCenter")
    fs = perms.FilterSpec()
    global_perm = DynamicID()
    global_perm.type = "GlobalAcl"
    global_perm.id = "GlobalAcl"
    fs.objects = [global_perm]
    parse_list_result(perms.list(fs))

def get_root_folder_permissions_only(perms):
    logger.info("Getting inventory permissions on vCenter's root folder only")
    fs = perms.FilterSpec()
    root_folder_perm = DynamicID()
    root_folder_perm.type = "ManagedEntity"
    root_folder_perm.id = "group-d1"
    fs.objects = [root_folder_perm]
    parse_list_result(perms.list(fs))

def get_permission_details(perms, perm_id):
    logger.info("Getting permission details")
    info = perms.get(perm_id)
    logger.info(f"Permission = {info}")


if __name__ == '__main__':
    parser = sample_cli.build_arg_parser()
    args = sample_util.process_cli_args(parser.parse_args())

    # Login in vCenter
    session = get_unverified_session() if args.skipverification else None
    client = create_vsphere_client(server=args.server,
                                   username=args.username,
                                   password=args.password,
                                   session=session)

    # Create permission stub
    permissions_svc = client.vcenter.authorization.Permissions

    # List all permissions in the vCenter
    all_permissions = get_all_permissions(perms=permissions_svc)

    # List only inventory permissions
    get_root_folder_permissions_only(perms=permissions_svc)

    # List only global permissions
    get_global_permissions_only(perms=permissions_svc)

    # Getting details for each permission
    for perm in all_permissions.items:
        get_permission_details(perms=permissions_svc,
                               perm_id=perm.permission)
