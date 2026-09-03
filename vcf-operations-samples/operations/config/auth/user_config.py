# Copyright (c) 2025-2026 Broadcom Inc. and/or its subsidiaries. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

class UserConfig:
    def __init__(self, firstname=None, lastname=None, username=None, password=None, email="first.last@somedomain.com"):
        """

        :param firstname: Firstname of the user
        :param lastname: Lastname of the user
        :param username: Username of the user
        :param password: Password of the user
        :param email: Email of the user
        """

        missing = []
        if not firstname:
            missing.append("firstname")
        if not lastname:
            missing.append("lastname")
        if not username:
            missing.append("username")
        if not password:
            missing.append("password")

        if missing:
            raise ValueError(f"Invalid configuration for UserConfig: missing {', '.join(missing)}")

        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.password = password
        self.email = email
