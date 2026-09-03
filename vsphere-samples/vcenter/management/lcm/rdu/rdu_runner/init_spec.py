#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '9.0.0'

import logging
from com.vmware.vcenter.lcm.deployment_client import MigrationUpgrade, Repository
from com.vmware.vcenter.lcm.deployment.common_client import (ApplianceDeploymentConfig, ApplianceDeployment, OvaInfo,
                                                             Connection, Location, VCenter)

logger = logging.getLogger(__name__)


class InitSpec:
    def __init__(self, root_password: str, target_version: str, target_ova: str,
                 enable_autocancel: bool = False, preserve_original_name: bool = False,
                 uber_vc_hostname: str = None, uber_vc_user: str = None, uber_vc_password: str = None):
        """
        Helper class to populate the init spec used to configure the upgrade.

        :param root_password: A temporary root password which is going to be used for the deployed target machine
        :param target_version: The target's vCSA version
        :param target_ova: URL to the target's version ova file
        :param enable_autocancel: Parameter to enable autocancellation
        :param preserve_original_name: Parameter to preserve the original source VC name. It will be used in the
        post-upgrade configuration.
        :param uber_vc_hostname: The hostname of the uber VC. Can be skipped if the source VC is self-managed.
        :param uber_vc_user: The username for the uber VC. Can be skipped if the source VC is self-managed.
        :param uber_vc_password: The password for the uber VC. Can be skipped if the source VC is self-managed.
        """

        self.root_password = root_password
        self.target_version = target_version
        self.target_ova = target_ova

        self.autocancellation = enable_autocancel
        self.preserve_original_name = preserve_original_name

        self.location = None
        self.source_connection = None

        if uber_vc_hostname and uber_vc_user and uber_vc_password:
            # This example doesn't support setups where the source and targets are not in the same vcenter.
            # To accommodate such setup you, the location in hte init spec can be set manually.
            uber_vc_connection = Connection(hostname=uber_vc_hostname,
                                            username=uber_vc_user,
                                            password=uber_vc_password)
            self.location = Location(vcenter=VCenter(connection=uber_vc_connection))
            self.source_connection = uber_vc_connection
        else:
            logger.info("Missing the full information for the uber vCenter. "
                        "Assuming the source vCenter is self-managed.")

    def _get_cancellation_policy(self):
        """
        Method returns an object which when added to the init spec enables
        the upgrade to cancel automatically on error.
        :return:
        """
        return MigrationUpgrade.CancellationPolicy(automatic=self.autocancellation)

    def _get_post_upgrade_config(self):
        """
        Method returns an object which when added to the init spec enables
        the upgrade to rename the target VC to the source's name after the upgrade process has completed.
        :return:
        """
        return MigrationUpgrade.PostUpgradeConfigurationPolicy(
            rename_vm_policy=MigrationUpgrade.RenameVmPolicy(preserve_original_vm_name=self.preserve_original_name))

    def get_init_spec(self):
        """
        get_init_spec builds the MigrationUpgrade.InitSpec object from the provided parameters.
        :return:
        """
        logger.info("Creating init spec for RDU")
        init_spec = MigrationUpgrade.InitSpec(version=self.target_version)

        logger.info("Populating the target appliance's information.")
        # Providing all necessary fields for the target machine's deployment.
        # The RDU will populate all unset fields based on the source vCenter.
        init_spec.deployment = ApplianceDeploymentConfig(appliance=ApplianceDeployment(root_password=self.root_password,
                                                                                       ova_info=OvaInfo(location=self.target_ova, ssl_verify=False)))

        logger.info("Populating the location of the target appliance. "
                    "Mandatory for uber VC setup, will be left empty for self-managed VC.")
        init_spec.deployment.location = self.location

        logger.info("Populating where the source VC is deployed. "
                    "Mandatory for uber VC setup, will be left empty for self-managed VC.")
        init_spec.deployment.source_container = self.source_connection

        logger.info("Populating the cancellation policy")
        if self.autocancellation:
            init_spec.cancellation_policy = self._get_cancellation_policy()

        logger.info("Populating the post upgrade configuration")
        if self.preserve_original_name:
            init_spec.post_upgrade_configuration = self._get_post_upgrade_config()

        return init_spec
