#!/usr/bin/env python

# Copyright (c) 2017-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '6.0+'

import requests

from vmware.vapi.vsphere.client import create_vsphere_client

from com.vmware.cis.tagging_client import CategoryModel

from helpers.common.sample_util import process_cli_args
from helpers.common import sample_cli


class CertConnect(object):
    """
    Demonstrates how to Connect to vCenter vAPI service with
    with Valid Cert
    """

    def __init__(self):
        parser = sample_cli.build_arg_parser()
        parser.add_argument('-cpath', '--cert_path',
                            action='store',
                            help='path to a CA_BUNDLE file or directory with certificates of trusted CAs')
        args = parser.parse_args()
        self.args = process_cli_args(args)

    def run(self):
        print('\n\n#### Example: Login to vCenter server with '
              'Valid Cert Verification')

        # Create a requests session and load the CA cert
        session = requests.session()
        session.verify = self.args.cert_path

        # Connect to VAPI
        client = create_vsphere_client(server=self.args.server,
                                       username=self.args.username,
                                       password=self.args.password,
                                       session=session)

        # List Tag Categories to verify the connection is successful
        print('\nStep 3: Listing the Tag Categories...\n')
        create_spec = client.tagging.Category.CreateSpec()
        create_spec.name = 'TestTag_connect_with_cert'
        create_spec.description = 'TestTagDesc'
        create_spec.cardinality = CategoryModel.Cardinality.MULTIPLE
        create_spec.associable_types = set()
        category_id = client.tagging.Category.create(create_spec)
        assert category_id is not None
        print('Tag category created; Id: {0}\n'.format(category_id))

        # Delete TagCategory
        client.tagging.Category.delete(category_id)


def main():
    connect_with_cert = CertConnect()
    connect_with_cert.run()


# Start program
if __name__ == '__main__':
    main()
