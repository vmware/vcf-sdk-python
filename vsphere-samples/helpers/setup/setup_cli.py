#!/usr/bin/env python

# Copyright (c) 2016-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

"""
This module implements simple helper functions for python samples
"""



import argparse


def build_arg_parser():
    """
    Builds a standard argument parser with arguments for executing sample
    setup script

    -s, --testbed_setup
    -t, --testbed_validate
    -c, --testbed_cleanup
    -o, --iso_cleanup
    -e, --samples_setup
    -r, --samples
    -i, --samples_incremental
    -l, --samples_cleanup
    -v, --skipverification
    -server, --vcenterserver
    -p, --vcenterpassword
    -e1, --esxhost1
    -e2, --esxhost2
    -eu1, --esxuser1
    -eu2, --esxuser2
    -epass1, --esxpassword1
    -epass2, --esxpassword2
    -n,  --nfsserver

    """
    parser = argparse.ArgumentParser(
        description='Arguments for running sample setup script')

    parser.add_argument('-s', '--testbed_setup',
                        action='store_true',
                        help='Build the testbed.  Will run cleanup before '
                             'trying to build in case there is '
                             'an intermediate failure')

    parser.add_argument('-t', '--testbed_validate',
                        action='store_true',
                        help='Validate if the testbed is ready for the samples')

    parser.add_argument('-c', '--testbed_cleanup',
                        action='store_true',
                        help='Tear down the testbed')

    parser.add_argument('-o', '--iso_cleanup',
                        action='store_true',
                        help='Delete iso during cleanup. ')

    parser.add_argument('-e', '--samples_setup',
                        action='store_true',
                        help='Run sample setup. ')

    parser.add_argument('-r', '--samples',
                        action='store_true',
                        help='Run samples. ')

    parser.add_argument('-i', '--samples_incremental',
                        action='store_true',
                        help='Runs samples that incrementally updates the VM '
                             'configuration. ')

    parser.add_argument('-l', '--samples_cleanup',
                        action='store_true',
                        help='Clean up after sample run. ')

    parser.add_argument('-v', '--skipverification',
                        action='store_true',
                        help='Verify server certificate when connecting to '
                             'vcenter. ')

    parser.add_argument('-server', '--vcenterserver',
                        action='store',
                        help='Vcenter server IP to prepare the testbed to run the samples.'
                             'If not passed as argument, update testbed.py file')

    parser.add_argument('-p', '--vcenterpassword',
                        action='store',
                        help='Vcenter server password'
                             'If not passed as argument, update testbed.py file')

    parser.add_argument('-e1', '--esxhost1',
                        action='store',
                        help='IP of ESX 1 to prepare the testbed to run the samples.'
                             'If not passed as argument, update testbed.py file')

    parser.add_argument('-e2', '--esxhost2',
                        action='store',
                        help='IP of ESX 2 to prepare the testbed to run the samples.'
                             'If not passed as argument, update testbed.py file')

    parser.add_argument('-eu1', '--esxuser1',
                        action='store',
                        help='Username of ESX 1 '
                             'If not passed as argument, update testbed.py file')

    parser.add_argument('-eu2', '--esxuser2',
                        action='store',
                        help='Username of ESX 2 '
                             'If not passed as argument, update testbed.py file')
    parser.add_argument('-epass1', '--esxpassword1',
                        action='store',
                        help='Password of ESX 1'
                             'If not passed as argument, update testbed.py file')
    parser.add_argument('-epass2', '--esxpassword2',
                        action='store',
                        help='Password of ESX 2'
                             'If not passed as argument, update testbed.py file')

    parser.add_argument('-n', '--nfsserver',
                        action='store',
                        help='NFS Server IP to setup datastore for samples run.'
                             'If not passed as argument, update testbed.py file')
    return parser
