#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '8.0.3+'

from helpers.common import sample_cli
from helpers.common import sample_util
from vsan.data_protection.data_protection_clients import DataProtectionClients
from vsan.data_protection.tasks.task_utils import wait_for_snapservice_task

from com.vmware.vcenter_client import VM
from com.vmware.snapservice_client import *


class CreateProtectionGroup(object):
    """
    Description: Demonstrates creating a protection group.
    """

    def __init__(self, vsphere_client, snapservice_client, args):
        self._vsphere_client = vsphere_client
        self._snapservice_client = snapservice_client
        self._args = args

    def create_task(self):
        vm_names = set(self._args.vm_names.split(","))
        vm_list = self._vsphere_client.vcenter.VM.list(VM.FilterSpec(names=vm_names))

        vm_ids = set()
        for vm_info in vm_list:
            print("vm_info:", vm_info)
            vm_ids.add(vm_info.vm)

        # Build protection group Spec
        target_entities = TargetEntities(vms=vm_ids)
        snapshot_policies = [SnapshotPolicy(name='test_snapshot_policy_02',
                                            schedule=SnapshotSchedule(TimeUnit("MINUTE"), 30),
                                            retention=RetentionPeriod(TimeUnit("HOUR"), 6))]
        replication_policies = [ReplicationPolicy(cluster_pair=self._args.cluster_pair_id,
                                                  recovery_point_objective=TimePeriod(TimeUnit("MINUTE"), 5),
                                                  snapshot_retention=RetentionPolicy(
                                                      short_term=ShortTermRetention(keep_last=5),
                                                      long_term=LongTermRetention(
                                                          hourly=HourlyRetention(
                                                              retention=TimePeriod(TimeUnit("HOUR"), 2)),
                                                          daily=DailyRetention(
                                                              hour=12,
                                                              retention=TimePeriod(TimeUnit("DAY"), 1)))))]
        spec = ProtectionGroupSpec(name='test_protection_group_02',
                                   target_entities=target_entities,
                                   snapshot_policies=snapshot_policies,
                                   replication_policies=replication_policies)
        print("----------------------------------------")
        print("Creating protection group with spec:")
        print("----------------------------------------")
        print(spec)
        return self._snapservice_client.clusters.ProtectionGroups.create_task(self._args.cluster_mo_id, spec=spec)


def get_args():
    parser = sample_cli.build_arg_parser()
    required_args = parser.add_argument_group('snapservice required arguments')
    required_args.add_argument('--snapservice',
                               action='store',
                               required=True,
                               help='Snapservice IP/hostname to connect to')
    required_args.add_argument('--cluster_mo_id',
                               action='store',
                               required=True,
                               help='Cluster MoRef ID where the protection group locates')
    required_args.add_argument('--cluster_pair_id',
                               action='store',
                               required=True,
                               help='Cluster pair ID where the protection group locates')
    required_args.add_argument('--vm_names',
                               action='store',
                               required=True,
                               help='Comma separated list of VM names')
    return sample_util.process_cli_args(parser.parse_args())


def main():
    args = get_args()
    clients = DataProtectionClients(args)

    create_pg = CreateProtectionGroup(clients.vsphere_client, clients.snapservice_client, args)
    create_task = create_pg.create_task()
    print('Create protection group task:', create_task.task_id)

    wait_for_snapservice_task(clients.snapservice_client, create_task.task_id)


if __name__ == '__main__':
    main()
