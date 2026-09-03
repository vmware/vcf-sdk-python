# Copyright (c) 2025-2026 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0
import uuid


class CredentialConfig:
    def __init__(self, name=None, adapterKindKey=None, credentialKindKey=None, fields=None):
        """
        Configuration for credential management examples
        
        :param name: Name of the credential
        :param adapterKindKey: Adapter kind key
        :param credentialKindKey: Credential kind key
        :param fields: Dictionary of credential fields
        """

        missing = []
        if not adapterKindKey:
            missing.append("adapterKindKey")
        if not credentialKindKey:
            missing.append("credentialKindKey")
        if not fields:
            missing.append("fields")

        if missing:
            raise ValueError(f"Invalid configuration for CredentialConfig: missing {', '.join(missing)}")

        if name is None:
            name = f"credential_{uuid.uuid4()}"

        self.name = name
        self.adapterKindKey = adapterKindKey
        self.credentialKindKey = credentialKindKey
        self.fields = fields or {}
