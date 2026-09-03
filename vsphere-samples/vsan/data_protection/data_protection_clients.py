#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '8.0.3+'

from helpers.common.ssl_helper import get_unverified_session
from vsan.data_protection.vsan_snapservice_client import create_snapservice_client
from vsan.data_protection.vsan_snapservice_client import get_saml_token

from vmware.vapi.vsphere.client import create_vsphere_client


class DataProtectionClients(object):
    def __init__(self, args):
        _skipverification = True if args.skipverification else False
        _vc_session = get_unverified_session() if _skipverification else None
        self.vsphere_client = create_vsphere_client(server=args.server,
                                                    username=args.username,
                                                    password=args.password,
                                                    session=_vc_session)

        _ss_session = get_unverified_session() if _skipverification else None
        _saml_token = get_saml_token(vc=args.server, username=args.username, password=args.password,
                                     skip_verification=_skipverification)
        self.snapservice_client = create_snapservice_client(server=args.snapservice,
                                                            session=_ss_session,
                                                            saml_token=_saml_token)
