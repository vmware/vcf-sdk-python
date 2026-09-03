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
from vcenter.management.lcm.rdu.rdu_runner.rdu_steps import RDU
from vcenter.management.lcm.rdu.rdu_runner.init_spec import InitSpec
from vcenter.management.lcm.rdu.utils import get_rdu_arg_parser
from vcenter.management.lcm.rdu.rdu_runner.status import notifications_to_str


logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

parser = get_rdu_arg_parser()
args = sample_util.process_cli_args(parser.parse_args())


def main():
    """
    This scenario demonstrates how to check if the environment is ready for upgrade
    without actually triggering the upgrade.

    It includes the following steps:

    1. Update the lifecycle plugin. If the plugin has already been upgraded this script won't fail
    and will continue with the upgrade.
    2. Set the upgrade repository for the target vCenter version
    3. Create an init spec. This example create an init spec with only the mandatory fields.
       All other fields will be autopopulated by the framework.
    4. Run the precheck API with the init spec.
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
                         target_ova=args.target_ova).get_init_spec()
    logger.info("Init spec can be further customized than what is show in this sample. "
                "For details check the API documentation.")

    logger.info("Step 4: Run prechecks against the created init spec")
    precheck_result = rdu_upgrade.precheck(init_spec=init_spec)
    if precheck_result.notifications.errors:
        logger.error("Provided init spec didn't pass the prechecks. "
                     "Check the prechecks result for problems and try again:\n %s",
                     notifications_to_str(precheck_result.notifications))
        return


if __name__ == "__main__":
    main()
