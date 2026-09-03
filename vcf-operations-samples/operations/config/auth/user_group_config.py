# Copyright (c) 2025-2026 Broadcom Inc. and/or its subsidiaries. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

class UserGroupConfig:
    def __init__(self, name=None, description=None):
        """
        Configuration for user group management
        
        :param name: Group name
        :param description: Group description
        """

        missing = []
        if not name:
            missing.append("name")
        if not description:
            missing.append("description")

        if missing:
            raise ValueError(f"Invalid configuration for UserGroupConfig: missing {', '.join(missing)}")

        self.name = name
        self.description = description
