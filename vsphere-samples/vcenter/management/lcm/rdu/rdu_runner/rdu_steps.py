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

from com.vmware.cis_client import Tasks
from com.vmware.vcenter.lcm.deployment_client import MigrationUpgrade, Repository
from com.vmware.vcenter.lcm.deployment.migration_upgrade_client import Status as UpgradeStatus
from com.vmware.vcenter.lcm.deployment.migration_upgrade_client import PlannedDowntime
from com.vmware.vapi.std.errors_client import NotFound
from com.vmware.vcenter.lcm.deployment.common_client import Status

from helpers.common import sample_util
from vcenter.management.lcm.rdu.utils import get_vcenter_client, get_rdu_arg_parser
from vcenter.management.lcm.rdu.rdu_runner.init_spec import InitSpec
from vcenter.management.lcm.rdu.rdu_runner.apply_spec import ApplySpec
from vcenter.management.lcm.rdu.rdu_runner.prechecks import Prechecks
from vcenter.management.lcm.rdu.rdu_runner.status import status_to_str, messages_to_str, notifications_to_str


logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

NUM_RETRIES = 120
DELAY_SECONDS = 120

NUM_RETRIES_SWITCHOVER = 20
DELAY_SWITCHOVER_SECONDS = 20


class UpgradeCancellationException(Exception):
    """
    Exception type for cancellation failure
    """
    pass


class UpgradeFailureException(Exception):
    """
    Exception type for upgrade failure
    """
    pass


class RDU:
    def __init__(self, server: str, username: str, password: str, skipverification: bool):
        """
        Class provides methods to run each of the RDU (reduced downtime upgrade)
        steps against a vCenter. The steps that can be run are described in the

        Sample Prerequisites:
        - vCenter (self-managed or uber-managed)
        - Server hosting the upgrade repository.
        - Updated lifecycle plug-in to the wanted target version

        :param server: The IP or FQDN of the source vCenter
        :param username: Username to authenticate with the given vCenter (root or a sso user part of the administrator group)
        :param password: Password for the given user
        :param skipverification: Whether to skip ssl verification
        """
        stub_config, _ = get_vcenter_client(server, username, password, skipverification, "lcm/api")

        self.migration_client = MigrationUpgrade(stub_config)
        self.repository_client = Repository(stub_config)
        self.task_client = Tasks(stub_config)
        self.status_client = UpgradeStatus(stub_config)
        self.planned_maintenance_client = PlannedDowntime(stub_config)

    def monitor_upgrade(self, num_retries: int, delay: int, autocancellation: bool, apply_spec: MigrationUpgrade.ApplySpec):
        """
        Monitor the status of the RDU upgrade. Method will complete when the upgrade
        completes successfully, it fails, it is cancelled or has reached the pause point before switchover.
        If the method times-out, it doesn't necessary mean that the upgrade has failed it could
        be taking more time than expected. In this situation you can rerun the monitor.
        :param num_retries: Number or times the status of the update is fetched
        :param delay: Delay between the retries in seconds
        :param autocancellation: Whether the upgrade has autocancellation configured
        :param apply_spec: The apply spec used to run the upgrade.
        :return:
        """
        if apply_spec.start_switchover:
            import datetime

            switchover_start_time = apply_spec.start_switchover
            timeout = num_retries * delay
            current_time = datetime.datetime.utcnow()

            if switchover_start_time >= current_time + datetime.timedelta(seconds=timeout):
                # Extending the timeout if switchover is scheduled after the expected timeout
                time_till_switchover = switchover_start_time - current_time
                num_retries += int(time_till_switchover.total_seconds() / delay)

        for _ in range(0, num_retries):
            upgrade_status = None
            for connection_attempt in range(0, NUM_RETRIES_SWITCHOVER):
                try:
                    upgrade_status = self.status_client.get()
                except requests.exceptions.ConnectionError:
                    logger.info("A connection error has occurred while fetching the RDU status. "
                                "This could be due to the network switchover. "
                                "Waiting %d seconds to see if it is resolved.", DELAY_SWITCHOVER_SECONDS)
                    time.sleep(DELAY_SWITCHOVER_SECONDS)

            if not upgrade_status:
                raise Exception("Connectivity issue while fetching RDU status.")

            if upgrade_status.current_state == UpgradeStatus.State.UPGRADED:
                logger.info("Upgrade has completed successfully.")
                return

            if upgrade_status.current_state == UpgradeStatus.State.CANCELED:
                logger.info("Upgrade has been successfully cancelled. You can check the error field from the status "
                            "to see what failed during the upgrade.")
                logger.error("Upgrade error that caused cancellation: %s", messages_to_str(upgrade_status.error.messages))
                logger.info("More information could be found in the notifications \n%s",
                            notifications_to_str(upgrade_status.notifications))
                return

            if (upgrade_status.upgrade_info.pause == MigrationUpgrade.PausePolicy.BEFORE_SWITCHOVER and
                    upgrade_status.current_state == UpgradeStatus.State.PREPARED):
                logger.info("Upgrade is prepared and paused before the switchover.")
                return

            if upgrade_status.status == Status.FAILED:
                if upgrade_status.desired_state == UpgradeStatus.State.CANCELED:
                    logger.error("Cancellation has failed due to error: %s", messages_to_str(upgrade_status.error.messages))
                    raise UpgradeCancellationException

                if autocancellation:
                    logger.error("Upgrade has failed and autocancellation is being triggered.")
                    time.sleep(delay)
                    continue

                logger.error("Upgrade has failed due to error %s", messages_to_str(upgrade_status.error.messages))
                logger.info("More information could be found in the notifications \n%s",
                            notifications_to_str(upgrade_status.notifications))
                raise UpgradeFailureException

            logger.info("Current upgrade state is %s", upgrade_status.current_state)
            time.sleep(delay)

        logger.error("Upgrade has timed-out after %d seconds", num_retries * delay)
        raise Exception("Upgrade timed-out.")

    def is_upgrade_initialized(self):
        try:
            self.migration_client.get()
            logger.info("There is an initialized upgrade on the vCenter.")
            return True
        except NotFound:
            logger.info("An upgrade is not initialized on the vCenter.")
            return False

    def check_planned_maintenance(self, minutes: int):
        response = self.planned_maintenance_client.get(minutes)
        logger.info("Planned Downtime in the next %d minutes: %s", minutes, response.expected)
        return response.expected

    def precheck(self, init_spec: InitSpec = None):
        logger.info("Running pre-checks for RDU")
        prechecks_runner = Prechecks(migration_client=self.migration_client,
                                     task_client=self.task_client)
        return prechecks_runner.run_prechecks(init_spec)

    def set_repository(self, repository: str):
        logger.info("Set the repository for the target version to %s", repository)
        self.repository_client.set(spec=Repository.Spec(address=repository))

    def configure(self, init_spec: MigrationUpgrade.InitSpec):
        logger.info("Configure upgrade with the init spec")
        self.migration_client.set(spec=init_spec)

    def apply(self, apply_spec: MigrationUpgrade.ApplySpec):
        logger.info("Start the upgrade process")
        self.migration_client.apply(spec=apply_spec)

    def cancel(self):
        logger.info("Cancelling upgrade")
        self.migration_client.cancel()

    def status(self):
        logger.info("Getting upgrade status")
        status = self.status_client.get()
        logger.info(status_to_str(status))


def main():
    parser = get_rdu_arg_parser()
    parser.add_help = True

    parser.add_argument('action',
                        action='store',
                        choices=['set-repository', 'configure', 'precheck', 'apply', 'cancel', 'planned-maintenance', 'status', 'monitor-upgrade'],
                        help="Possible actions: "
                             "set-repository - sets the repository from where to get the target vCenter version"
                             "configure - configure what init spec to be used by the upgrade, "
                             "apply - start the upgrade process, "
                             "precheck - run the upgrade sanity tests, "
                             "cancel - cancel an already running upgrade, "
                             "planned-maintenance - check if maintenance is planned,"
                             "status - check the status of the upgrade, "
                             "monitor-upgrade - monitor the upgrade process till it finishes successfully,"
                             "fails or it is cancelled.")
    parser.add_argument('--start-switchover',
                        action='store',
                        help="After how many hours to schedule the downtime of the upgrade.")
    parser.add_argument('--pause-before-switchover',
                        action='store_true',
                        help="Pause the upgrade before it enters the switchover phase.")
    parser.add_argument('--uber-vc-hostname',
                        action='store',
                        help="The hostname of the uber VC.")
    parser.add_argument('--uber-vc-username',
                        action='store',
                        help="The username for the uber VC.")
    parser.add_argument('--uber-vc-password',
                        action='store',
                        help="The password for the uber VC.")
    parser.add_argument('--planned-maintenance-minutes',
                        action='store',
                        help="Check if VC maintenance is planned to start in the next X minutes.")
    args = sample_util.process_cli_args(parser.parse_args())

    init_spec = InitSpec(root_password=args.target_temp_password,
                         target_version=args.target_version,
                         target_ova=args.target_ova,
                         enable_autocancel=args.autocancellation,
                         preserve_original_name=args.preserve_original_name,
                         uber_vc_user=args.uber_vc_username,
                         uber_vc_password=args.uber_vc_password,
                         uber_vc_hostname=args.uber_vc_hostname).get_init_spec()

    apply_spec = ApplySpec(schedule_downtime=int(args.start_switchover) if args.start_switchover else None,
                           pause_before_switchover=args.pause_before_switchover).get_apply_spec()

    logger.info("For this upgrade using:\n Init spec: %s\n Apply spec: %s", init_spec, apply_spec)

    rdu_runner = RDU(username=args.username, password=args.password,
                     server=args.server, skipverification=args.skipverification)

    if args.action == 'set-repository':
        rdu_runner.set_repository(args.target_upgrade_repo)
    elif args.action == 'configure':
        rdu_runner.configure(init_spec)
    elif args.action == 'precheck':
        if rdu_runner.is_upgrade_initialized():
            init_spec = None
        precheck_result = rdu_runner.precheck(init_spec)
        logger.info("Upgrade prechecks result:\n %s", notifications_to_str(precheck_result.notifications))
    elif args.action == 'apply':
        rdu_runner.apply(apply_spec)
    elif args.action == 'cancel':
        rdu_runner.cancel()
    elif args.action == 'planned-maintenance':
        minutes = int(args.planned_maintenance_minutes)
        rdu_runner.check_planned_maintenance(minutes)
    elif args.action == 'status':
        rdu_runner.status()
    elif args.action == 'monitor-upgrade':
        rdu_runner.monitor_upgrade(num_retries=NUM_RETRIES, delay=DELAY_SECONDS,
                                   autocancellation=args.autocancellation, apply_spec=apply_spec)


if __name__ == '__main__':
    main()
