#!/usr/bin/env python

# Copyright (c) 2013-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0


from pyVmomi import vim

from helpers.common.sample_base import SampleBase
from helpers.common.vim.helpers.vim_utils import get_obj


class GetDatastoreByName(SampleBase):
    """
    Retrieves the given datastore MOID from VC using container view
    """

    def __init__(self):
        SampleBase.__init__(self, self.__doc__)
        self.datastore_name = None
        self.mo_id = None
        self.servicemanager = None

    def _options(self):
        self.argparser.add_argument('-datastorename', '--datastorename',
                                    help='Name of the datastore to be queried')

    def _setup(self):
        if self.datastore_name is None:
            self.datastore_name = self.args.datastorename
        assert self.datastore_name is not None
        if self.servicemanager is None:
            self.servicemanager = self.get_service_manager()

    def _execute(self):
        content = self.servicemanager.content
        datastore_obj = get_obj(content, [vim.Datastore], self.datastore_name)
        if datastore_obj is not None:
            self.mo_id = datastore_obj._GetMoId()
            print('Datastore MoId: {0}'.format(self.mo_id))
        else:
            print('Datastore: {0} not found'.format(self.datastore_name))

    def _cleanup(self):
        pass


def get_datastore_id(service_manager, datastore_name):
    """
    returns the datastore's MoId, or None if the datastore doesn't exist
    """
    get_datastore_by_name = GetDatastoreByName()
    get_datastore_by_name.servicemanager = service_manager
    get_datastore_by_name.datastore_name = datastore_name
    get_datastore_by_name.run()
    return get_datastore_by_name.mo_id


def main():
    get_datastore_by_name = GetDatastoreByName()
    get_datastore_by_name.main()


# Start program
if __name__ == "__main__":
    main()
