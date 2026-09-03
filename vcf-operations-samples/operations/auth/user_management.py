# Copyright (c) 2025-2026 Broadcom Inc. and/or its subsidiaries. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import logging

from vcf.operations.model_client import User, UserGroup, UserRole, UsernamePassword

from operations.sample_base import SampleBase
from vcf.operations.api import auth_client
from vcf.operations.api.auth import token_client

from operations.config.auth.user_management_config import UserManagementConfig
from operations.helpers.arg_parser import get_args
from vmware.vapi.bindings.error import VapiError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class UserManagement(SampleBase):
    """
    Example that illustrates the use of API client bindings to perform
    user management CRUD operations
    """

    def __init__(self, client_config, sample_config):
        super().__init__(client_config)

        with open(sample_config, "r") as f:
            data = json.load(f)

        user_management_config = UserManagementConfig(**data)
        self.user_config = user_management_config.userConfig
        self.user_group_config = user_management_config.userGroupConfig
        self.user_role_config = user_management_config.userRoleConfig

        self.token_client = token_client.Acquire(self.ops_client.stub_config)
        self.user_client = auth_client.Users(self.ops_client.stub_config)
        self.roles_client = auth_client.Roles(self.ops_client.stub_config)
        self.user_groups_client = auth_client.Usergroups(self.ops_client.stub_config)

    def run(self):
        try:
            # INFO: No need to call it manually, it's called automatically from RestClientProxy.
            self.acquire_token()

            # CRUD for users
            user = self.create_user()
            self.get_user(user.id)
            self.get_users()

            user.first_name = "New-First"
            user.last_name = "New-Last"
            user.email_address = "last.first@somedomain.com"
            user.password = "newPassword@123"

            modified_user = self.modify_user(user)
            self.delete_user(modified_user.id)
            user_list = self.get_users()

            # CRUD for user groups
            group = self.create_user_group(user_list.users if user_list.users else [])
            self.get_user_group(group.id)
            self.get_user_groups()

            group.name = "New-Group-Name"
            group.description = "New-Group-Description"

            group = self.modify_user_group(group)
            self.delete_user_group(group.id)
            self.get_user_groups()

            # CRUD for user roles
            user_role = self.create_user_role()
            self.get_user_role(user_role.name)
            self.get_user_roles()

            user_role.description = "New-Role-Description"

            user_role = self.update_user_role(user_role)
            self.delete_user_role(user_role.name)
            self.get_user_roles()
        except VapiError as vapi_error:
            raise vapi_error
        except Exception as ex:
            logger.error("User management sample failed", ex)
            raise ex

    def acquire_token(self):
        logger.info("Acquiring token...")
        username_password = UsernamePassword()
        username_password.username = self.client_config.username
        username_password.password = self.client_config.password
        try:
            token = self.token_client.acquire_token(username_password)
            logger.info(f"Acquired token: {token.token}")
            return token
        except VapiError as vapi_error:
            logger.error(f"Failed to acquire token: {vapi_error.get_error_value()}")
            raise vapi_error

    def create_user(self):
        logger.info("Creating a local vCenter Operations Manager user account...")
        user = User()
        user.first_name = self.user_config.firstname
        user.last_name = self.user_config.lastname
        user.email_address = self.user_config.email
        user.username = self.user_config.username
        user.password = self.user_config.password
        try:
            user = self.user_client.create_user(user)
            logger.info(f"User ID of the user account created: {user.id}")
            return user
        except VapiError as vapi_error:
            logger.error(f"Failed to create a user: {vapi_error.get_error_value()}")
            raise vapi_error

    def get_user(self, user_id):
        try:
            logger.info(f"Getting user: {user_id}")
            user = self.user_client.get_user(user_id)
            logger.info(f"first name: {user.first_name}, last name: {user.last_name}")
            return user
        except VapiError as vapi_error:
            logger.error(f"Failed to get a user: {vapi_error.get_error_value()}")
            raise vapi_error

    def get_users(self):
        logger.info("List all the local vCenter Operations Manager users in the system...")
        try:
            users = self.user_client.get_users(None, None, None)
            logger.info(f"Number of local vCenter Operations Manager users in the system: {len(users.users) if users.users else 0}")
            return users
        except VapiError as vapi_error:
            logger.error(f"Failed to get users: {vapi_error.get_error_value()}")
            raise vapi_error

    def modify_user(self, user):
        logger.info("Modify the local vCenter Operations Manager user account created...")
        try:
            user = self.user_client.modify_user(user)
            logger.info(f"User Account Details after update: first name: {user.first_name}, last name: {user.last_name}")
            return user
        except VapiError as vapi_error:
            logger.error(f"Failed to modify a user: {vapi_error.get_error_value()}")
            raise vapi_error

    def delete_user(self, user_id):
        logger.info(f"Deleting user: {user_id}")
        try:
            self.user_client.delete_user(user_id)
            logger.info("User account is deleted successfully")
        except VapiError as vapi_error:
            logger.error(f"Failed to delete a user: {vapi_error.get_error_value()}")
            raise vapi_error

    def create_user_group(self, users):
        logger.info("Creating a local vCenter Operations Manager group account...")
        group = UserGroup()
        group.name = self.user_group_config.name
        group.description = self.user_group_config.description
        group.user_ids = [user.id for user in users]
        try:
            group = self.user_groups_client.create_user_group(group)
            logger.info(f"Group ID of the user group created: {group.id}")
            return group
        except VapiError as vapi_error:
            logger.error(f"Failed to create a user group: {vapi_error.get_error_value()}")
            raise vapi_error

    def get_user_group(self, group_id):
        logger.info(f"Getting user group: {group_id}")
        try:
            group = self.user_groups_client.get_user_group(group_id)
            logger.info(f"name: {group.name}, description: {group.description}")
            return group
        except VapiError as vapi_error:
            logger.error(f"Failed to get a user group: {vapi_error.get_error_value()}")
            raise vapi_error

    def get_user_groups(self):
        logger.info("List all the local vCenter Operations Manager user groups in the system...")
        try:
            groups = self.user_groups_client.get_user_groups()
            logger.info(f"Number of local vCenter Operations Manager user groups in the system: {len(groups.user_groups) if groups.user_groups else 0}")
            return groups
        except VapiError as vapi_error:
            logger.error(f"Failed to get user groups: {vapi_error.get_error_value()}")
            raise vapi_error

    def modify_user_group(self, group):
        logger.info("Modify the local vCenter Operations Manager group account created...")
        try:
            self.user_groups_client.modify_user_group(group)
            logger.info(f"Group Account Details after update: name: {group.name}, description: {group.description}")
            return group
        except VapiError as vapi_error:
            logger.error(f"Failed to modfy a user group: {vapi_error.get_error_value()}")
            raise vapi_error

    def delete_user_group(self, group_id):
        logger.info(f"Deleting group: {group_id}")
        try:
            self.user_groups_client.delete_user_group(group_id)
            logger.info("User group is deleted successfully")
        except VapiError as vapi_error:
            logger.error(f"Failed to delete a user group: {vapi_error.get_error_value()}")
            raise vapi_error

    def create_user_role(self):
        logger.info("Creating a local vCenter Operations Manager userRole account...")
        user_role = UserRole()
        user_role.name = self.user_role_config.name
        user_role.description = self.user_role_config.description
        user_role.privilege_keys = self.user_role_config.privilegeKeys
        try:
            user_role = self.roles_client.create_user_role(user_role)
            logger.info(f"Name of the user role created: {user_role.name}")
            return user_role
        except VapiError as vapi_error:
            logger.error(f"Failed to create a user role: {vapi_error.get_error_value()}")
            raise vapi_error

    def get_user_role(self, role_name):
        logger.info(f"Getting userRole: {role_name}")
        try:
            user_role = self.roles_client.get_role_by_name(role_name)
            logger.info(f"name: {user_role.name}, description: {user_role.description}")
            return user_role
        except VapiError as vapi_error:
            logger.error(f"Failed to get a user role: {vapi_error.get_error_value()}")
            raise vapi_error

    def get_user_roles(self):
        logger.info("List all the local vCenter Operations Manager userRoles in the system...")
        try:
            user_roles = self.roles_client.get_roles(None)
            logger.info(f"Number of local vCenter Operations Manager user roles in the system: {len(user_roles.user_roles) if user_roles.user_roles else 0}")
            return user_roles
        except VapiError as vapi_error:
            logger.error(f"Failed to get user roles: {vapi_error.get_error_value()}")
            raise vapi_error

    def update_user_role(self, user_role):
        logger.info("Modify the local vCenter Operations Manager userRole account created...")
        try:
            modified_user_role = self.roles_client.update_user_role(user_role)
            logger.info(f"UserRole Account Details after update: name: {modified_user_role.name}, description: {modified_user_role.description}")
            return user_role
        except VapiError as vapi_error:
            logger.error(f"Failed to update a user role: {vapi_error.get_error_value()}")
            raise vapi_error

    def delete_user_role(self, role_name):
        logger.info(f"Deleting userRole: {role_name}")
        try:
            self.roles_client.delete_user_role(role_name)
            logger.info("User role is deleted successfully")
        except VapiError as vapi_error:
            logger.error(f"Failed to delete a user role: {vapi_error.get_error_value()}")
            raise vapi_error


if __name__ == "__main__":
    args = get_args()

    user_management = UserManagement(args.client_config, args.sample_config)
    user_management.run()
