#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '9.1.0'

import logging
import sys
import time

from helpers.common import sample_util
from helpers.common import sample_cli
from vcenter.management.lcm.rdu.rdu_runner.rdu_steps import RDU

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

parser = sample_cli.build_arg_parser()
parser.add_argument('--minutes',
                    action='store',
                    help="How many minutes ahead of now to ask for planned maintenance.")
parser.add_help = True

args = sample_util.process_cli_args(parser.parse_args())

# How many times do we run the loop?
NUM_RETRIES = 100
# Check the Maintenance API after DELAY_MINUTES minutes.
# Since the parameter to the maintenance API is number of minutes (not seconds),
# it makes sense to ask at most every minute, not sooner.
# Of course, it could be a much bigger number,
# but anything beyond a few hours would be prone to the risk
# the VC admin could schedule an upgrade in the meantime,
# and thus invalidate the current response.
DELAY_MINUTES = 1


def main():
    """
    This scenario demonstrates how to check for VC Planned Downtime / Maintenance.

    Assuming the client knows that a given workload operation
    takes 5 minutes (e.g., create a VM), they can verify that
    there is no Planned Downtime (e.g., for VC upgrade) for this amount of time,
    and only then start the operation.
    Otherwise, this operation might be interrupted by a scheduled
    or otherwise imminent migration upgrade downtime of the VC.

    This sample can be started together with some upgrade
    scenario (e.g., full_upgrade.py or upgrade_with_cancellation.py)
    in parallel - this way you would observe how at some point the Maintenance API
    will start returning "expected": "YES", when Switchover time approaches.

    It includes the following steps:

    1. Check the Planned Downtime API for X minutes
        - If the answer is "NO",
        proceed to perform the desired operation (create VM/Folder, etc.);
        - If the answer is "YES",
        wait and check again once every minute - until the answer is "NO"; We have a scheduled
        or upgrade by this time; or an unscheduled upgrade,
        where the stage of the upgrade is close enough to switchover.
        - If the answer is "UNKNOWN" - the upgrade is not scheduled,
        but likely happening very soon (within very few minutes),
        so important operations should rather wait;
    2. Repeat in loop
    :return:
    """

    rdu = RDU(args.server, args.username, args.password, args.skipverification)

    i = 0

    while i < NUM_RETRIES:
        logger.info("Check for VC Planned Downtime, attempt %d", i)
        expected = rdu.check_planned_maintenance(int(args.minutes))
        if expected == "YES":
            logger.info(
                "VC is expected to enter downtime within %d minutes, not starting workload operations",
                args.minutes)
        elif expected == "NO":
            logger.info(
                "VC is available for workload operations in the next %d minutes, starting a workload operation",
                args.minutes)
            perform_workload_operation()
        elif expected == "UNKNOWN":
            logger.info(
                "VC may enter downtime within %d minutes, it is safer to not start workload operation",
                args.minutes)

        time.sleep(DELAY_MINUTES * 60)
        i = i + 1

def perform_workload_operation():
    """
    perform VM provisioning, or any other
    time-consuming operation on the VC (not subject to this example)
    """
    logger.info("Performing workload operation")

if __name__ == "__main__":
    main()
