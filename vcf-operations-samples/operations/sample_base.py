# Copyright (c) 2025-2026 Broadcom Inc. and/or its subsidiaries. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json

from operations.helpers.client import create_vcf_operations_client
from operations.config.client_config import ClientConfig


class SampleBase:

    def __init__(self, client_config):
        """
        parse client config file
        :param client_config:
        """

        with open(client_config, "r") as f:
            data = json.load(f)

        self.client_config = ClientConfig(**data)
        self.ops_client = create_vcf_operations_client(server=self.client_config.host,
                                                       username=self.client_config.username,
                                                       password=self.client_config.password)
