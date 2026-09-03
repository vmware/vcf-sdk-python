#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '9.0.0'

import logging
import sys

from helpers.common import sample_util
from vcenter.management.lcm.rdu.update_plugin_util.update_vcenter_lifecycle_manager import UpdateLifecyclePlugin
from vcenter.management.lcm.rdu.rdu_runner.rdu_steps import RDU, UpgradeCancellationException, UpgradeFailureException
from vcenter.management.lcm.rdu.rdu_runner.init_spec import InitSpec
from vcenter.management.lcm.rdu.rdu_runner.apply_spec import ApplySpec
from vcenter.management.lcm.rdu.utils import get_rdu_arg_parser


logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

parser = get_rdu_arg_parser()
parser.add_argument('--start-switchover',
                    action='store',
                    help="After how many hours to schedule the downtime of the upgrade.")
parser.add_argument('--uber-vc-hostname',
                    action='store',
                    required=True,
                    help="The hostname of the uber VC.")
parser.add_argument('--uber-vc-username',
                    action='store',
                    required=True,
                    help="The username for the uber VC.")
parser.add_argument('--uber-vc-password',
                    action='store',
                    required=True,
                    help="The password for the uber VC.")
args = sample_util.process_cli_args(parser.parse_args())

NUM_RETRIES = 120
DELAY_SECONDS = 120


def main():
    """
    This scenario demonstrates how to run the full RDU upgrade against an uber-managed vCenter.
    Running the prechecks by themselves is not demonstrated here, however, it can be added. To see how,
    check the full_upgrade.py scenario.

    It includes the following steps:

    1. Update the lifecycle plugin. If the plugin has already been upgraded this script won't fail
    and will continue with the upgrade.
    2. Set the upgrade repository for the target vCenter version
    3. Create the init spec for configuring the RDU upgrade by including the information for the managing vCenter.
    4. Configure the upgrade with the init spec
    5. Create the apply spec for running the upgrade. The apply spec can also be changed during
       the upgrade by calling the apply method with the new spec.
    6. Run the upgrade.
    7. Monitor the upgrade state till it completes.
    :return:
    """
    logger.info("Step 1: Update lifecycle manager plug-in")
    plugin_update = UpdateLifecyclePlugin(args.server, args.username, args.password, args.skipverification, args.target_upgrade_repo)
    plugin_update.run()

    rdu_upgrade = RDU(username=args.username, password=args.password,
                      server=args.server, skipverification=args.skipverification)

    logger.info("Step 2: Set the upgrade repository for the target vCenter version")
    rdu_upgrade.set_repository(args.target_upgrade_repo)

    logger.info("Step 3: Create init spec for the upgrade.")
    init_spec = InitSpec(root_password=args.target_temp_password,
                         target_version=args.target_version,
                         target_ova=args.target_ova,
                         enable_autocancel=args.autocancellation,
                         preserve_original_name=args.preserve_original_name,
                         uber_vc_hostname=args.uber_vc_hostname,
                         uber_vc_user=args.uber_vc_username,
                         uber_vc_password=args.uber_vc_password).get_init_spec()

    logger.info("Step 4: Configure the upgrade")
    rdu_upgrade.configure(init_spec=init_spec)

    logger.info("Step 5: Create apply spec for the upgrade.")
    apply_spec = ApplySpec(schedule_downtime=int(args.start_switchover) if args.start_switchover else None).get_apply_spec()

    logger.info("Step 6: Run the upgrade")
    rdu_upgrade.apply(apply_spec=apply_spec)

    logger.info("Step 7: Monitor the upgrade")
    try:
        rdu_upgrade.monitor_upgrade(num_retries=NUM_RETRIES, delay=DELAY_SECONDS,
                                    autocancellation=args.autocancellation, apply_spec=apply_spec)
    except UpgradeCancellationException:
        logger.error("Autocancellation has failed. Retrying the cancel operation again.")
        rdu_upgrade.cancel()
    except UpgradeFailureException:
        logger.error("Upgrade has failed. Fix the problems and retry.")
        # When the upgrade fails these scripts will log the error and notifications from the status. Based on the issue
        # described there you can add the fix in the place of this comment.
        logger.info("Retrying the upgrade with the same apply spec.")
        rdu_upgrade.apply(apply_spec)


if __name__ == "__main__":
    main()
