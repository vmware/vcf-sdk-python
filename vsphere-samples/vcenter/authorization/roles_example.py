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
from com.vmware.vapi.std.errors_client import NotFound
from helpers.common.ssl_helper import get_unverified_session

"""
This example demonstrates how to create, update, delete and get authorization 
roles from a vCenter using the corresponding vCenter REST APIs.


Sample Prerequisites:
    - vCenter 9.0+
"""

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def get_role_details(roles_stub, role_id):
    logger.info("Getting role details")
    info = roles_stub.get(role_id)
    logger.info(f"Details = {info}")

def parse_list_result(roles_list):
    for role in roles_list.items:
        logger.info(f"ID = {role.role}")
        logger.info(f"Name = {role.info.name}")
        logger.info(f"Description = {role.info.description}")
        logger.info(f"IsSystem = {role.info.system}")
        logger.info(f"Privileges = {role.info.privileges}\n")

def create_role(roles_stub, name, description, privileges):
    logger.info(f"Creating new role with name {name}")
    spec = roles_stub.CreateSpec()
    spec.name = name
    spec.description = description
    spec.privileges = privileges
    role_id = roles_stub.create(spec)
    logger.info(f"Created new role with ID {role_id}")
    return role_id

def get_all_roles(roles_stub):
    logger.info('Getting all roles in the vCenter')
    roles = roles_stub.list()
    parse_list_result(roles_list=roles)
    return roles

def update_role(roles_stub, id, privileges):
    logger.info(f"Updating role with ID {id}")
    spec = roles_stub.UpdateSpec()
    spec.privileges = privileges
    roles_stub.update(id, spec)

def delete_role(roles_stub, id):
    logger.info(f"Deleting role with ID {id}")
    roles_stub.delete(id)


if __name__ == '__main__':
    parser = sample_cli.build_arg_parser()
    args = sample_util.process_cli_args(parser.parse_args())

    # Login in vCenter
    session = get_unverified_session() if args.skipverification else None
    client = create_vsphere_client(server=args.server,
                                   username=args.username,
                                   password=args.password,
                                   session=session)

    # Create role stub
    roles_svc = client.vcenter.authorization.Roles

    # List all roles in the vCenter
    all_roles = get_all_roles(roles_stub=roles_svc)

    # Get the details for each role
    for role in all_roles.items:
        get_role_details(roles_stub=roles_svc,
                         role_id=role.role)

    # Create a new role
    new_role_name = f"test-role-{str(uuid.uuid4())}"
    privs = {"System.View", "Global.LogEvent"}
    new_role_id = create_role(roles_stub=roles_svc,
                              name=new_role_name,
                              description="test",
                              privileges=privs)

    # Getting the details of the newly created role
    get_role_details(roles_stub=roles_svc,
                     role_id=new_role_id)

    # Updating the role, adding a new privilege
    privs.add("Global.Settings")
    update_role(roles_stub=roles_svc,
                id=new_role_id,
                privileges=privs)

    # Getting the details of the newly updated role
    get_role_details(roles_stub=roles_svc,
                     role_id=new_role_id)

    # Delete the role
    delete_role(roles_stub=roles_svc,
                id=new_role_id)

    # Try to get the deleted role to make sure it no longer exists
    try:
        get_role_details(roles_stub=roles_svc,
                         role_id=new_role_id)
    except NotFound:
        logger.info("Role deletion confirmed")
