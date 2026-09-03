#!/usr/bin/env python

# Copyright (c) 2013-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0


from pyVmomi import vim

from helpers.common.sample_base import SampleBase
from helpers.common.vim.helpers.vim_utils import get_obj


class GetClusterByName(SampleBase):
    """
    Retrieves the given cluster MOID from VC using container view
    """

    def __init__(self):
        SampleBase.__init__(self, self.__doc__)
        self.cluster_name = None
        self.mo_id = None
        self.servicemanager = None

    def _options(self):
        self.argparser.add_argument('-clustername', '--clustername',
                                    help='Name of the cluster to be queried')

    def _setup(self):
        if self.cluster_name is None:
            self.cluster_name = self.args.clustername
        assert self.cluster_name is not None
        if self.servicemanager is None:
            self.servicemanager = self.get_service_manager()

    def _execute(self):
        content = self.servicemanager.content
        cluster_obj = get_obj(content, [vim.ClusterComputeResource],
                              self.cluster_name)
        if cluster_obj is not None:
            self.mo_id = cluster_obj._GetMoId()
            print('Cluster MoId: {0}'.format(self.mo_id))
        else:
            print('Cluster: {0} not found'.format(self.cluster_name))

    def _cleanup(self):
        pass


def get_cluster_id(service_manager, cluster_name):
    """
    Returns the cluster's MoId, or None if the cluster doesn't exist
    """
    get_cluster_by_name = GetClusterByName()
    get_cluster_by_name.servicemanager = service_manager
    get_cluster_by_name.cluster_name = cluster_name
    get_cluster_by_name.run()
    return get_cluster_by_name.mo_id


def main():
    get_cluster_by_name = GetClusterByName()
    get_cluster_by_name.main()


# Start program
if __name__ == "__main__":
    main()
