#!/usr/bin/env python

# Copyright (c) 2016-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0


import argparse


def build_arg_parser():
    """
    Builds a standard argument parser with arguments for talking to vCenter

    -s server
    -u username
    -p password
    -c cleanup
    -v skipverification

    """
    parser = argparse.ArgumentParser(
        description='Standard Arguments for talking to vCenter')

    required_args = parser.add_argument_group(
            'required arguments')
    required_args.add_argument('-s', '--server',
                        action='store',
                        required=True,
                        help='vSphere service IP to connect to')

    required_args.add_argument('-u', '--username',
                        action='store',
                        required=True,
                        help='Username to use when connecting to vc')

    required_args.add_argument('-p', '--password',
                        action='store',
                        required=True,
                        help='Password to use when connecting to vc')

    parser.add_argument('-c', '--cleardata',
                        action='store_true',
                        help='Clean up after sample run. ')

    parser.add_argument('-v', '--skipverification',
                        action='store_true',
                        help='Verify server certificate when connecting to vc.')

    return parser
