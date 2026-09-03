# Copyright (c) 2025-2026 Broadcom Inc. and/or its subsidiaries. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from operations.config.auth.user_config import UserConfig
from operations.config.auth.user_group_config import UserGroupConfig
from operations.config.auth.user_role_config import UserRoleConfig


class UserManagementConfig:
    def __init__(self, userConfig=None, userGroupConfig=None, userRoleConfig=None):
        """
        Configuration for comprehensive user management
        
        :param userConfig: UserConfig object
        :param userGroupConfig: UserGroupConfig object
        :param userRoleConfig: UserRoleConfig object
        """

        missing = []
        if not userConfig:
            missing.append("userConfig")
        if not userGroupConfig:
            missing.append("userGroupConfig")
        if not userRoleConfig:
            missing.append("userRoleConfig")

        if missing:
            raise ValueError(f"Invalid configuration for UserManagementConfig: missing {', '.join(missing)}")

        self.userConfig = UserConfig(**(userConfig or {}))
        self.userGroupConfig = UserGroupConfig(**(userGroupConfig or {}))
        self.userRoleConfig = UserRoleConfig(**(userRoleConfig or {}))
