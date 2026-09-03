#!/usr/bin/env python

# Copyright (c) 2016-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0



from helpers.common.vim.file import (detect_file, delete_file,
                                             parse_datastore_path)
from helpers.common.vim.inventory import get_datastore_mo

from helpers.common.vim import datastore_file


def setup_floppy_image(context):
    """Copy floppy image used to run vcenter samples"""
    floppy_src_url = context.testbed.config['FLOPPY_SRC_URL']
    datacenter_name = context.testbed.config['FLOPPY_DATACENTER_NAME']
    datastore_path = context.testbed.config['FLOPPY_DATASTORE_PATH']
    (datastore_name, path) = parse_datastore_path(datastore_path)

    datastore_mo = get_datastore_mo(context.client,
                                    context.service_instance._stub,
                                    datacenter_name,
                                    datastore_name)
    if not datastore_mo:
        raise Exception("Could not find datastore '{}'".format(datastore_name))

    # See if the Floppy image exists. Copy it into the system if it does not
    # exist
    dsfile = datastore_file.File(datastore_mo)
    if not dsfile.exists(datastore_path):
        print("Putting Floppy file from '{}' at '{}'".
              format(floppy_src_url, datastore_path))
        dsfile.put(path=path, src_url=floppy_src_url)


def cleanup_floppy_image(context):
    """Delete floppy image after running samples"""
    datacenter_name = context.testbed.config['FLOPPY_DATACENTER_NAME']
    datastore_path = context.testbed.config['FLOPPY_DATASTORE_PATH']
    delete_file(context.client,
                context.service_instance,
                'Floppy Image',
                datacenter_name,
                datastore_path)


def detect_floppy_image(context):
    """Find the floppy image used to run vcenter samples"""
    datacenter_name = context.testbed.config['FLOPPY_DATACENTER_NAME']
    datastore_path = context.testbed.config['FLOPPY_DATASTORE_PATH']
    return detect_file(context, 'Floppy Image', datacenter_name, datastore_path)


def setup(context):
    setup_floppy_image(context)


def cleanup(context):
    cleanup_floppy_image(context)


def validate(context):
    return detect_floppy_image(context)
