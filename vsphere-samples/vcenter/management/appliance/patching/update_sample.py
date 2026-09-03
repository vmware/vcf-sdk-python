#!/usr/bin/env python

# Copyright (c) 2022-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '8.0+'

from com.vmware.appliance.update_client import Pending, Staged
from com.vmware.appliance_client import Update

from helpers.common import sample_cli, sample_util
from helpers.common.ssl_helper import get_unverified_session
from vcenter.management.host.hcl.utils import get_configuration
import time


class SampleUpdate(object):
    """
     Sample demonstrating Patching APIs
     Sample Prerequisites:
     vCenter on linux platform
     """

    def __init__(self):
        parser = sample_cli.build_arg_parser()
        parser.add_argument('-com', '--component',
                            action='store',
                            required=False,
                            help='Component to be updated.')

        parser.add_argument('-url', '--url',
                            action='store',
                            required=False,
                            help='Custom target url.')
        args = sample_util.process_cli_args(parser.parse_args())
        # cis session
        session = get_unverified_session() if args.skipverification else None
        stub_config = get_configuration(
                args.server, args.username, args.password,
                session)
        self.url = args.url if args.url else None
        self.component = args.component if args.component else None
        self.pending_client = Pending(stub_config)
        self.staged_client = Staged(stub_config)
        self.appliance_client = Update(stub_config)
        self.password = args.password

    def list_quick_patches(self, version_list):
        """
        Filter and display quick patches from the update list
        """
        quick_patches = []
        for update_summary in version_list:
            try:
                update_info = self.pending_client.get(update_summary.version, self.component)
                if (hasattr(update_info, 'quick_patch') and 
                    update_info.quick_patch is not None and 
                    update_info.quick_patch):
                    quick_patches.append(update_summary)
            except Exception:
                # Skip if unable to get detailed info
                continue
        return quick_patches

    def run(self):
        """
        Access the Pending APIs to list and do a pending update
        """

        version_list = self.pending_client.list("LOCAL_AND_ONLINE", self.url)
        print("\nFull patch update list: \n", version_list)
        
        # Display quick patches if available
        quick_patches = self.list_quick_patches(version_list)
        if quick_patches:
            print("\n=== Quick Patches Available ===")
            for qp in quick_patches:
                print(f"  - {qp.version}: {qp.name}")
            print("================================\n")
        
        version = version_list[0].version

        # Upgradeable Component List
        if self.component:
            component_list = self.pending_client.list_upgradeable_components(version)
            # component = component_list[0]["component"]
            print("\nUpgradeable Component list: \n", component_list)

        # get Update info
        update_info = self.pending_client.get(version, self.component)
        print("\nGet Information of Update: ")
        ServicesToBeStopped = [x.service for x in update_info.services_will_be_stopped]
        print("name: ", update_info.name)
        print("services_will_be_stopped: ", ServicesToBeStopped)
        print("staged: ", update_info.staged)
        print("knowledge_base: ", update_info.knowledge_base)
        print("priority: ", update_info.priority)
        print("severity: ", update_info.severity)
        print("update_type: ", update_info.update_type)
        print("release_date: ", update_info.release_date)
        print("reboot_required: ", update_info.reboot_required)
        print("size: ", update_info.size)
        
        # Quick Patch Information (if available)
        if hasattr(update_info, 'quick_patch') and update_info.quick_patch is not None:
            is_quick_patch = update_info.quick_patch
            print("quick_patch: ", is_quick_patch)
            
            # If it's a quick patch, display workload_management_impact
            if is_quick_patch:
                if hasattr(update_info, 'workload_management_impact') and update_info.workload_management_impact is not None:
                    print("workload_management_impact: ", update_info.workload_management_impact)
                    if not update_info.workload_management_impact:
                        print("*** This is a Quick Patch - No workload management downtime expected ***")
                    else:
                        print("!!! Quick Patch with workload management impact !!!")
            
            # Display estimated time if available
            if hasattr(update_info, 'estimated_time_to_install') and update_info.estimated_time_to_install is not None:
                print("estimated_time_to_install (minutes): ", update_info.estimated_time_to_install)


        user_data = {"vmdir.password": self.password}
        # Precheck Update
        precheck_result = self.pending_client.precheck(version, self.component)
        print("\nPrecheck result : \n", precheck_result)
        for question in precheck_result.questions:
            print("Please provide answer to following question")
            print(question.text.default_message)
            print("Question Description : ", question.description.default_message)
            print("Provide your answer: ")
            ans = str(input())
            user_data[question.data_item] = ans

        # Validate an Update
        validate_result = self.pending_client.validate(version, user_data, self.component)
        print("\nValidate result for update: \n", validate_result)

        # Stage an Update

        self.pending_client.stage(version, self.component)
        print("Staging the update")

        # Monitor Stage
        monitor_stage = self.appliance_client.get()
        while monitor_stage.task.status == "RUNNING":
            time.sleep(50)
            monitor_stage = self.appliance_client.get()

        print("State: ", monitor_stage.state)
        print("Status: ", monitor_stage.task.status)
        if monitor_stage.task.status == "FAILED":
            print("")
            return
        print("\nStage result: \n", monitor_stage)

        staged_result = self.staged_client.get()
        print("\nStaged Update: ", staged_result)

        # Install an update
        self.pending_client.install(version, user_data, self.component)

        # Monitor Install
        print("Installing the update")
        monitor_install = self.appliance_client.get()
        while monitor_install.task.status == "RUNNING":
            monitor_install = self.appliance_client.get()
        print("\nInstall result: \n", monitor_install)


def main():
    """
     Entry point for the sample client
    """
    pending_update = SampleUpdate()
    pending_update.run()


if __name__ == '__main__':
    main()
