#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '9.0+'

import logging
import uuid

from helpers.common import sample_cli
from helpers.common import sample_util
from vmware.vapi.vsphere.client import create_vsphere_client
from com.vmware.vapi.std_client import DynamicID
from com.vmware.vapi.std.errors_client import NotFound
from helpers.common.ssl_helper import get_unverified_session

"""
This example demonstrates how to create, update and delete global and 
inventory permissions from a vCenter using the corresponding vCenter REST APIs.


Sample Prerequisites:
    - vCenter 9.0+
"""

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def get_permission_details(perms, perm_id):
    logger.info("Getting permission details")
    info = perms.get(perm_id)
    logger.info(f"Permission = {info}")


def create_global_permission(perms, username, domain, group):
    logger.info(f"Creating global permission for principal {username}@{domain}")
    spec = perms.CreateSpec()
    globalPerm = DynamicID()
    globalPerm.type = "GlobalAcl"
    globalPerm.id = "GlobalAcl"
    spec.object = globalPerm
    principal = perms.Principal()
    if group:
        principal.type = perms.Principal.Type.GROUP
    else:
        principal.type = perms.Principal.Type.USER
    principal.name = username
    principal.domain = domain
    spec.principal = principal
    spec.role = "-1"
    spec.propagating = True
    new_perm = perms.create(spec)
    logger.info(f"Global permission with ID {new_perm} created")
    return new_perm


def create_inventory_permission(perms, username, domain, group):
    logger.info(f"Creating inventory permission for principal {username}@{domain}")
    spec = perms.CreateSpec()
    invt_perm = DynamicID()
    invt_perm.type = "ManagedEntity"
    invt_perm.id = "group-d1"
    spec.object = invt_perm
    principal = perms.Principal()
    if group:
        principal.type = perms.Principal.Type.GROUP
    else:
        principal.type = perms.Principal.Type.USER
    principal.name = username
    principal.domain = domain
    spec.principal = principal
    spec.role = "-1"
    spec.propagating = True
    new_perm = perms.create(spec)
    logger.info(f"Inventory permission with ID {new_perm} created")
    return new_perm


def update_permission_role(perms, permission_id, role_id):
    logger.info(f"Updating permission with ID {permission_id}")
    spec = perms.UpdateSpec()
    spec.role = role_id
    perms.update(permission_id, spec)


def delete_permission(perms, permission_id):
    logger.info(f"Deleting permission with ID {permission_id}")
    perms.delete(permission_id)


def example_global_permissions(perms):
    # Create a new global permission for a person user
    p_uuid = str(uuid.uuid4())
    username = f"test-user-{p_uuid}"
    domain = f"tes.domain.{p_uuid}"
    new_global_perm = create_global_permission(perms=perms,
                                               username=username,
                                               domain=domain,
                                               group=True)
    # Gets the details of the newly created global permission
    get_permission_details(perms=perms,
                           perm_id=new_global_perm)

    # Updates the roles of the newly created global permission
    update_permission_role(perms=perms,
                           permission_id=new_global_perm,
                           role_id="-2")

    # Gets the details of the newly updated global permission
    get_permission_details(perms=perms,
                           perm_id=new_global_perm)

    # Delete the global permission
    delete_permission(perms=perms,
                      permission_id=new_global_perm)

    try:
        get_permission_details(perms=perms,
                               perm_id=new_global_perm)
    except NotFound:
        logger.info("Global permission deletion confirmed")


def example_inventory_permissions(perms):
    # Create a new inventory permission for a person user
    p_uuid = str(uuid.uuid4())
    username = f"test-user-{p_uuid}"
    domain = f"tes.domain.{p_uuid}"
    new_invt_perm = create_inventory_permission(perms=perms,
                                                username=username,
                                                domain=domain,
                                                group=False)
    # Gets the details of the newly created inventory permission
    get_permission_details(perms=perms,
                           perm_id=new_invt_perm)

    # Updates the roles of the newly created inventory permission
    update_permission_role(perms=perms,
                           permission_id=new_invt_perm,
                           role_id="-2")

    # Gets the details of the newly updated inventory permission
    get_permission_details(perms=perms,
                           perm_id=new_invt_perm)

    # Delete the inventory permission
    delete_permission(perms=perms,
                      permission_id=new_invt_perm)

    try:
        get_permission_details(perms=perms,
                               perm_id=new_invt_perm)
    except NotFound:
        logger.info("Inventory permission deletion confirmed")


if __name__ == '__main__':
    parser = sample_cli.build_arg_parser()
    args = sample_util.process_cli_args(parser.parse_args())

    # Login in vCenter
    session = get_unverified_session() if args.skipverification else None
    client = create_vsphere_client(server=args.server,
                                   username=args.username,
                                   password=args.password,
                                   session=session)
    permissions_svc = client.vcenter.authorization.Permissions
    example_global_permissions(perms=permissions_svc)
    example_inventory_permissions(perms=permissions_svc)
