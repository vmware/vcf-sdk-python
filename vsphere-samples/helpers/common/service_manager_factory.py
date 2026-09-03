#!/usr/bin/env python

# Copyright (c) 2013-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0


from helpers.common.service_manager import ServiceManager


class ServiceManagerFactory(object):
    """
    Factory class for getting service manager for a management node.
    """
    service_manager = None

    @classmethod
    def get_service_manager(cls, server, username, password, skip_verification):
        cls.service_manager = ServiceManager(server,
                                             username,
                                             password,
                                             skip_verification)
        cls.service_manager.connect()
        return cls.service_manager

    @classmethod
    def disconnect(cls):
        if cls.service_manager:
            cls.service_manager.disconnect()


import atexit
atexit.register(ServiceManagerFactory.disconnect)
