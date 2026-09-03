# Copyright (c) 2025-2026 Broadcom Inc. and/or its subsidiaries. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from operations.config.credentials.credential_config import CredentialConfig


class VcenterIntegrationConfig:
    def __init__(self, name="Adapter-Instance", description="Adapter instance for illustrative purposes",
                 collectorId="1", credentialConfig=None, identifiers=None, enableVSAN=True, smartDataCollection=True,
                 enableSDMP=True, enableAutoDiscovery=True, force=False, forceManagementOwnership=False):
        """
        Configuration for vCenter integration examples
        
        :param name: Integration name
        :param description: Integration description
        :param collectorId: Collector ID
        :param credentialConfig: CredentialConfig object
        :param identifiers: Dictionary of identifiers
        :param enableVSAN: Enable vSAN
        :param smartDataCollection: Enable smart data collection
        :param enableSDMP: Enable SDMP
        :param enableAutoDiscovery: Enable auto discovery
        :param force: Force creation
        :param forceManagementOwnership: Force management ownership
        """

        missing = []
        if not credentialConfig:
            missing.append("credentialConfig")
        if not identifiers:
            missing.append("identifiers")

        if missing:
            raise ValueError(f"Invalid configuration for VcenterIntegrationConfig: missing {', '.join(missing)}")

        self.name = name
        self.description = description
        self.collectorId = collectorId
        self.credentialConfig = CredentialConfig(**(credentialConfig or {}))
        self.identifiers = identifiers or {}
        self.enableVSAN = enableVSAN or False
        self.smartDataCollection = smartDataCollection or False
        self.enableSDMP = enableSDMP or False
        self.enableAutoDiscovery = enableAutoDiscovery or False
        self.force = force or False
        self.forceManagementOwnership = forceManagementOwnership or False
