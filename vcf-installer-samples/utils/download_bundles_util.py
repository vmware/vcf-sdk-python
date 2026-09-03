#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

from utils.misc_util import poll
from vmware.vcf_installer.model_client import DepotAccount, DepotSettings, \
    BundleDownloadSpec, BundleUpdateSpec, ProductReleaseComponent, Error

DEFAULT_DEPOT_SYNC_TIMEOUT_MINS = 5
DEFAULT_WAIT_BETWEEN_POLLS_DEPOT_SYNC_SEC = 5
DEFAULT_POLL_DOWNLOAD_STATUS_TIMEOUT_HOURS = 24
DEFAULT_WAIT_BETWEEN_POLLS_DOWNLOAD_STATUS_SEC = 60

_BUNDLE_IMAGE_TYPE = "INSTALL"

_START_BUNDLE_DOWNLOAD_ERRORS_TO_IGNORE = {
    # happens when download has already been initiated, but download has not started yet
    "BUNDLE_DOWNLOAD_ALREADY_SCHEDULED",
    # happens when bundle has already been downloaded
    "BUNDLE_DOWNLOAD_ALREADY_DOWNLOADED",
    # happens when bundle is being validated
    "BUNDLE_DOWNLOAD_NOT_AVAILABLE"}


def configure_online_depot(client, depot_account_username, depot_account_password):
    depot_account = DepotAccount()
    depot_account.username = depot_account_username
    depot_account.password = depot_account_password

    depot_settings = DepotSettings()
    depot_settings.vmware_account = depot_account
    client.v1.system.settings.Depot.update_depot_settings(depot_settings)


def is_depot_synced(client):
    try:
        sync_info = client.v1.system.settings.depot.DepotSyncInfo.get_depot_sync_info()
    except Exception as e:
        print("Caught exception while trying to retrieve depot sync info.", e)
        return False

    if sync_info.sync_status == "SYNC_FAILED":
        raise AssertionError("Syncing depot failed")

    synced = sync_info.sync_status == "SYNCED"
    if synced:
        print("Syncing depot succeeded")

    return synced


def force_sync_depot(client, timeout_in_mins=DEFAULT_DEPOT_SYNC_TIMEOUT_MINS,
                     poll_interval_in_sec=DEFAULT_WAIT_BETWEEN_POLLS_DEPOT_SYNC_SEC):
    """
    Sync the depot and wait until the operation is complete
    :param timeout_in_mins: Optional - if not provided will default to DEFAULT_DEPOT_SYNC_TIMEOUT_MINS
    :param poll_interval_in_sec: Optional - if not provided will default to DEFAULT_WAIT_BETWEEN_POLLS_DEPOT_SYNC_SEC
    :return:
    """

    client.v1.system.settings.depot.DepotSyncInfo.sync_depot_metadata()

    def poller():
        return is_depot_synced(client)

    print("Polling depot sync")
    return poll(poller, timeout_in_mins, poll_interval_in_sec)


def get_latest_product_release_components(client, sku, release_version,
                                          product_release_components_names_to_include):
    release_components = client.v1.releases.ReleaseComponents.get_release_components_by_sku(
        sku=sku, release_version=release_version, image_type=_BUNDLE_IMAGE_TYPE,
        automated_install=True).elements

    if not release_components:
        raise AssertionError("No release component details were returned.")

    latest_release_component = release_components[0]

    return [comp for comp in latest_release_component.components if
            comp.name in product_release_components_names_to_include]


def start_bundles_download(client, release_components: ProductReleaseComponent):
    bundle_download_spec = BundleDownloadSpec()
    bundle_download_spec.download_now = True
    bundle_update_spec = BundleUpdateSpec()
    bundle_update_spec.bundle_download_spec = bundle_download_spec

    bundle_ids_being_downloaded = []

    for component in release_components:
        latest = component.versions[0]

        ids = [patch_bundle_info.id for patch_bundle_info in latest.artifacts.bundles]

        for id in ids:
            try:
                client.v1.Bundles.start_bundle_download_by_id(id, bundle_update_spec)
                bundle_ids_being_downloaded.append(id)
            except Error as e:
                err_code = e.error_code or (e._extra_fields.get(
                    "errorCode").value if e._extra_fields.get(
                    "errorCode") else None)

                if err_code in _START_BUNDLE_DOWNLOAD_ERRORS_TO_IGNORE:
                    print(
                        "Not downloading bundle with name: '{}' and id: '{}' "
                        "as download has already been initiated previously.".format(
                            component.name, id))

                    bundle_ids_being_downloaded.append(id)
                else:
                    print(
                        "Failed to download bundle with name: '{}' and id: '{}'".format(
                            component.name, id))

                    raise e

    return bundle_ids_being_downloaded


def are_bundles_downloaded(client, bundle_ids_being_downloaded, release_version):
    try:
        bundle_download_status_infos = client.v1.bundles.DownloadStatus.get_bundle_download_status(
            release_version=release_version, image_type=_BUNDLE_IMAGE_TYPE)
    except Exception as e:
        print("Caught exception while retrieving download status", e)
        return False

    all_downloaded = True
    for status_info in bundle_download_status_infos.elements:
        if status_info.bundle_id in bundle_ids_being_downloaded:
            if status_info.download_status == "FAILED":
                raise AssertionError(
                    "Failed to download bundle with id: {}".format(status_info.bundle_id))
            elif status_info.download_status == "CANCELLED":
                raise AssertionError(
                    "Download bundle with id: {} has been cancelled.".format(status_info.bundle_id))
            elif status_info.download_status != "SUCCESS":
                all_downloaded = False
                break

    if all_downloaded:
        print("All bundles have been successfully downloaded.")
        return True
    else:
        return False


def poll_bundles_downloaded(
        client,
        bundle_ids_being_downloaded,
        release_version,
        poll_timeout_in_hours=DEFAULT_POLL_DOWNLOAD_STATUS_TIMEOUT_HOURS,
        poll_interval_in_sec=DEFAULT_WAIT_BETWEEN_POLLS_DOWNLOAD_STATUS_SEC):
    """
    Polls until bundles are downloaded or timeout is reached in which case an exception is thrown.

    :type: client: :class:`utils.client.VcfInstallerClient`
    :param client: VCF Installer Client
    :param bundle_ids_being_downloaded: bundles to check
    :param release_version: release version of the bundles to check
    :param poll_timeout_in_hours: Optional - if not provided will default to
    :param poll_interval_in_sec: Optional - if not provided will default to DEFAULT_WAIT_BETWEEN_POLLS_DOWNLOAD_STATUS_SEC
    :return:
    """

    def poller():
        return are_bundles_downloaded(client, bundle_ids_being_downloaded, release_version)

    print("Polling download status.")
    return poll(poller, poll_timeout_in_hours, poll_interval_in_sec)
