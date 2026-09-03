#!/usr/bin/env python

# Copyright (c) 2023-2026 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

class ClientConfig:
    def __init__(self, vcf_operations_address, vcf_operations_username, vcf_operations_password,
                 log_management_address, log_management_port):
        """
        :param vcf_operations_address: ops host url
        :param vcf_operations_username: username
        :param vcf_operations_password: password
        :param log_management_address: logs host url
        :param log_management_port: logs port
        """
        self.opsHost = vcf_operations_address
        self.username = vcf_operations_username
        self.password = vcf_operations_password
        self.logsHost = log_management_address
        self.logsPort = log_management_port

        self.validate()

    def validate(self):
        missing = []
        if not self.opsHost:
            missing.append("opsHost")
        if not self.username:
            missing.append("username")
        if not self.password:
            missing.append("password")
        if not self.logsHost:
            missing.append("logsHost")
        if not self.logsPort:
            missing.append("logsPort")
        if missing:
            raise ValueError(f"Invalid configuration for {self.__class__.__name__}: missing {', '.join(missing)}")
