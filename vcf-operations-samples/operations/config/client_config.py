# Copyright (c) 2025-2026 Broadcom Inc. and/or its subsidiaries. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

class ClientConfig:
    def __init__(self, username, password, host):
        """
        :param username: username
        :param password: password
        :param host: host url
        """
        self.username = username
        self.password = password
        self.host = host

        self.validate()

    def validate(self):
        missing = []
        if not self.username:
            missing.append("username")
        if not self.password:
            missing.append("password")
        if not self.host:
            missing.append("host")
        if missing:
            raise ValueError(f"Invalid configuration for {self.__class__.__name__}: missing {', '.join(missing)}")
