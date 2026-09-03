#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '9.0.0'

import logging
import sys
import time

from helpers.common import sample_util
from vcenter.management.lcm.rdu.update_plugin_util.update_vcenter_lifecycle_manager import UpdateLifecyclePlugin
from vcenter.management.lcm.rdu.rdu_runner.rdu_steps import RDU, UpgradeCancellationException
from vcenter.management.lcm.rdu.rdu_runner.init_spec import InitSpec
from vcenter.management.lcm.rdu.rdu_runner.apply_spec import ApplySpec
from vcenter.management.lcm.rdu.utils import get_rdu_arg_parser
from vcenter.management.lcm.rdu.rdu_runner.status import notifications_to_str


logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

parser = get_rdu_arg_parser()
parser.add_argument('--start-switchover',
                    action='store',
                    help="After how many hours to schedule the downtime of the upgrade.")
args = sample_util.process_cli_args(parser.parse_args())

NUM_RETRIES = 120
DELAY_SECONDS = 30
CANCEL_AFTER_SECONDS = 120


def main():
    """
    This scenario demonstrates how to cancel a running RDU upgrade.

    It includes the following steps:

    1. Update the lifecycle plugin. If the plugin has already been upgraded this script won't fail
    and will continue with the upgrade.
    2. Set the upgrade repository for the target vCenter version
    3. Create the init spec for configuring the RDU upgrade. You can further customize by hand the init spec if needed.
    4. Configure the upgrade with the init spec
    5. Run prechecks against the configured init spec
    6. Create the apply spec for running the upgrade.
    7. Run the upgrade.
    8. Cancel the upgrade at some point. Here it is cancelled after 2 minutes, but it can be done at any point of the upgrade.
    9. Monitor the upgrade state till it completes.
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
                         preserve_original_name=args.preserve_original_name).get_init_spec()

    logger.info("Step 4: Configure the upgrade")
    rdu_upgrade.configure(init_spec=init_spec)

    logger.info("Step 5: Run prechecks")
    precheck_result = rdu_upgrade.precheck()

    if precheck_result.notifications.errors:
        logger.error("Provided init spec didn't pass the prechecks. "
                     "Check the prechecks result for problems and try again:\n %s",
                     notifications_to_str(precheck_result.notifications))
        return

    logger.info("Step 6: Create apply spec for the upgrade.")
    apply_spec = ApplySpec(schedule_downtime=int(args.start_switchover) if args.start_switchover else None).get_apply_spec()

    logger.info("Step 7: Run the upgrade")
    rdu_upgrade.apply(apply_spec=apply_spec)

    time.sleep(CANCEL_AFTER_SECONDS)

    logger.info("Step 8: Cancel upgrade")
    rdu_upgrade.cancel()

    logger.info("Step 9: Monitor the upgrade cancellation")
    try:
        rdu_upgrade.monitor_upgrade(num_retries=NUM_RETRIES, delay=DELAY_SECONDS,
                                    autocancellation=args.autocancellation, apply_spec=apply_spec)
    except UpgradeCancellationException:
        logger.info("Cancellation has failed. Retrying the cancel operation again.")
        rdu_upgrade.cancel()


if __name__ == "__main__":
    main()
