# Copyright (c) 2025-2026 Broadcom Inc. and/or its subsidiaries. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

class UserRoleConfig:
    def __init__(self, name="Role-Name", description="Role-Description", privilegeKeys=None):
        """
        Configuration for user role management
        
        :param name: Role name
        :param description: Role description
        :param privilegeKeys: List of privilege keys
        """

        missing = []
        if not privilegeKeys:
            missing.append("privilegeKeys")

        if missing:
            raise ValueError(f"Invalid configuration for UserRoleConfig: missing {', '.join(missing)}")

        self.name = name
        self.description = description
        self.privilegeKeys = privilegeKeys or []
