#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '9.0.0'

import time
import logging
import sys
import requests

from com.vmware.appliance.update_client import Policy
from com.vmware.appliance_client import Update
from com.vmware.vapi.std.errors_client import NotFound
from com.vmware.appliance.update_client import Pending

from helpers.common import sample_util, sample_cli
from vcenter.management.lcm.rdu.utils import get_vcenter_client


VLCM_SERVICE = "vlcm"
NUM_RETRIES = 20
DELAY_SECONDS = 30

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RestUpdateClient:
    def __init__(self, server: str, skipverification: bool, session_id: str):
        """
        Helper class to use rest for fetching the update status.
        Using a rest request since this api endpoint is not meant to be called
        through the bindings.
        :param server: The IP or FQDN of the source vCenter
        :param skipverification: Whether to skip ssl verification
        :param session_id: A session id to authenticate with the given vCenter
        """
        self.server = server
        self.skip_verification = skipverification
        self.session_id = session_id

    def get_update_status(self):
        """
        Method makes a request to get the update status and returns the deserialized response.
        :return:
        """
        url = f"https://{self.server}/rest/appliance/update"
        headers = {
            'vmware-api-session-id': self.session_id
        }

        response = requests.request("GET", url, headers=headers, verify=(not self.skip_verification))
        if 200 <= response.status_code < 400:
            import json
            response_text = json.loads(response.text)
            return response_text

        raise Exception("Failed when fetching update status")


class UpdateLifecyclePlugin:
    def __init__(self, server: str, username: str, password: str, skipverification: bool, plugin_repo: str):
        """
        Sample for updating the vCenter lifecycle manager plug-in - a required step
        before executing RDU upgrade.

        Sample Prerequisites:
            - vCenter
            - Server hosting the lifecycle plug-in upgrade repository.

        :param server: The IP or FQDN of the source vCenter
        :param username: Username to authenticate with the given vCenter (root or a sso user part of th administrator group)
        :param password: Password for the given user
        :param skipverification: Whether to skip ssl verification
        :param plugin_repo: URL to the upgrade repository. For information on how to set it up, check the prerequisites
        """
        stub_config, session_id = get_vcenter_client(server + ":5480", username, password, skipverification,
                                                     "api", auth_with_session=True)

        self.plugin_repo = plugin_repo
        self.policy_client = Policy(stub_config)
        self.pending_client = Pending(stub_config)
        self.update_client = RestUpdateClient(server + ":5480", skipverification, session_id)

    def monitor_update(self, num_retries: int, delay: int):
        """
        Monitor the status of the lifecycle plug-in update
        :param num_retries: Number of times the status of the update is fetched
        :param delay: Delay between the retries in seconds
        :return:
        """
        for _ in range(0, NUM_RETRIES):
            status = self.update_client.get_update_status()

            if status["state"] == Update.State.UP_TO_DATE:
                logger.info("Update has completed successfully")
                return

            if status["state"] == Update.State.INSTALL_IN_PROGRESS or status["state"] == Update.State.STAGE_IN_PROGRESS:
                logger.info("Update is in progress")

            if status["state"] == Update.State.INSTALL_FAILED:
                logger.error("Update has failed")
                return

            time.sleep(DELAY_SECONDS)

        logger.error("Update has timed-out after %d seconds", num_retries * delay)
        raise Exception("Update of lifecycle plug-in timed-out")

    def run(self):
        """
        The method demonstrates the workflow for doing the vCenter lifecycle manager plug-in update.
        The component that is being updated is called "vlcm" in the context of this API endpoint,
        however, it does not have anything in common with the esxi vlcm service.
        """

        logger.info("Update plug-in step 1: Setting the repository needed for the update")
        policy_config = Policy.Config(custom_url=self.plugin_repo,
                                      auto_stage=False,
                                      certificate_check=True,
                                      check_schedule=[])
        self.policy_client.set(policy_config)

        logger.info("Update plug-in step 2: Check if there are any available updates.")
        try:
            available_updates = self.pending_client.list(source_type=Pending.SourceType.LOCAL_AND_ONLINE,
                                                         enable_list_major_upgrade_versions=True)
        except NotFound:
            logger.warning("There are no available updates in the passed repository %s", self.plugin_repo)
            return

        logger.info("Available updates: %s", available_updates)
        target_version = available_updates[0].version

        upgradable_components = self.pending_client.list_upgradeable_components(target_version)
        logger.info("Listing the upgradable components for "
                    "update version %s: %s", target_version, upgradable_components)
        if not list(filter(lambda x: x.component == VLCM_SERVICE, upgradable_components)):
            logger.info("vlcm service is not listed as an upgradable component.")
            return

        logger.info("Update plug-in step 3: Starting the update of the service.")
        self.pending_client.stage_and_install(version=target_version,
                                              user_data={},
                                              component=VLCM_SERVICE)

        logger.info("Update plug-in step 4: Checking the status of the update")
        self.monitor_update(NUM_RETRIES, DELAY_SECONDS)


def main():
    """
     Entry point for the lifecycle plug-in update
    """
    parser = sample_cli.build_arg_parser()
    parser.add_argument('--plugin-repo',
                        action='store',
                        required=True,
                        help="URL to the lifecycle plugin repository.")
    args = sample_util.process_cli_args(parser.parse_args())

    update = UpdateLifecyclePlugin(args.server, args.username, args.password,
                                   args.skipverification, args.plugin_repo)
    update.run()


if __name__ == '__main__':
    main()
