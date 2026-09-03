This directory contains bundle management samples for VCF Installer:

Running sample to configure online depot and download bundles necessary for deploying
a new VCF Fleet with its first VCF Instance

    $ python download_bundles_vcf_fleet_first_vcf_instance.py \
      --vcf_installer_host_address <VCF_INSTALLER_HOST_ADDRESS> \
      --vcf_installer_admin_password <VCF_INSTALLER_ADMIN_PASSWORD> \
      --depot_account_username <DEPOT_ACCOUNT_USERNAME> \
      --depot_account_password <DEPOT_ACCOUNT_PASSWORD> \
      [--ca_certs <CA_CERTS>] \
      [--time_to_wait_for_depot_sync_in_minutes <TIME_TO_WAIT_FOR_DEPOT_SYNC_IN_MINUTES>] \
      [--time_to_wait_in_between_polls_for_depot_sync_in_seconds <TIME_TO_WAIT_IN_BETWEEN_POLLS_FOR_DEPOT_SYNC_IN_SECONDS>] \
      [--max_time_to_poll_download_status_in_hours <MAX_TIME_TO_POLL_DOWNLOAD_STATUS_IN_HOURS>] \
      [--time_to_sleep_in_between_polls_for_download_status_in_seconds <TIME_TO_SLEEP_IN_BETWEEN_POLLS_FOR_DOWNLOAD_STATUS_IN_SECONDS>]


Running sample to configure online depot and download bundles necessary for deploying a new VCF Fleet with its 
first VCF Instance, assuming that you already have vCenter and NSX deployed

      $ python download_bundles_vcf_fleet_first_vcf_instance_from_existing_components.py \
        --vcf_installer_host_address <VCF_INSTALLER_HOST_ADDRESS> \
        --vcf_installer_admin_password <VCF_INSTALLER_ADMIN_PASSWORD> \
        --depot_account_username <DEPOT_ACCOUNT_USERNAME> \
        --depot_account_password <DEPOT_ACCOUNT_PASSWORD> \
        [--ca_certs <CA_CERTS>] \
        [--time_to_wait_for_depot_sync_in_minutes <TIME_TO_WAIT_FOR_DEPOT_SYNC_IN_MINUTES>] \
        [--time_to_wait_in_between_polls_for_depot_sync_in_seconds <TIME_TO_WAIT_IN_BETWEEN_POLLS_FOR_DEPOT_SYNC_IN_SECONDS>] \
        [--max_time_to_poll_download_status_in_hours <MAX_TIME_TO_POLL_DOWNLOAD_STATUS_IN_HOURS>] \
        [--time_to_sleep_in_between_polls_for_download_status_in_seconds <TIME_TO_SLEEP_IN_BETWEEN_POLLS_FOR_DOWNLOAD_STATUS_IN_SECONDS>]


Running sample to configure online depot and download bundles necessary for deploying VVF

      $ python download_bundles_vvf_instance.py \
        --vcf_installer_host_address <VCF_INSTALLER_HOST_ADDRESS> \
        --vcf_installer_admin_password <VCF_INSTALLER_ADMIN_PASSWORD> \
        --depot_account_username <DEPOT_ACCOUNT_USERNAME> \
        --depot_account_password <DEPOT_ACCOUNT_PASSWORD> \
        [--ca_certs <CA_CERTS>] \
        [--time_to_wait_for_depot_sync_in_minutes <TIME_TO_WAIT_FOR_DEPOT_SYNC_IN_MINUTES>] \
        [--time_to_wait_in_between_polls_for_depot_sync_in_seconds <TIME_TO_WAIT_IN_BETWEEN_POLLS_FOR_DEPOT_SYNC_IN_SECONDS>] \
        [--max_time_to_poll_download_status_in_hours <MAX_TIME_TO_POLL_DOWNLOAD_STATUS_IN_HOURS>] \
        [--time_to_sleep_in_between_polls_for_download_status_in_seconds <TIME_TO_SLEEP_IN_BETWEEN_POLLS_FOR_DOWNLOAD_STATUS_IN_SECONDS>]


Running sample to configure online depot and download bundles necessary for deploying VVF assuming you have an
existing vCenter

      $ python download_bundles_vvf_instance_existing_vcenter.py \
        --vcf_installer_host_address <VCF_INSTALLER_HOST_ADDRESS> \
        --vcf_installer_admin_password <VCF_INSTALLER_ADMIN_PASSWORD> \
        --depot_account_username <DEPOT_ACCOUNT_USERNAME> \
        --depot_account_password <DEPOT_ACCOUNT_PASSWORD> \
        [--ca_certs <CA_CERTS>] \
        [--time_to_wait_for_depot_sync_in_minutes <TIME_TO_WAIT_FOR_DEPOT_SYNC_IN_MINUTES>] \
        [--time_to_wait_in_between_polls_for_depot_sync_in_seconds <TIME_TO_WAIT_IN_BETWEEN_POLLS_FOR_DEPOT_SYNC_IN_SECONDS>] \
        [--max_time_to_poll_download_status_in_hours <MAX_TIME_TO_POLL_DOWNLOAD_STATUS_IN_HOURS>] \
        [--time_to_sleep_in_between_polls_for_download_status_in_seconds <TIME_TO_SLEEP_IN_BETWEEN_POLLS_FOR_DOWNLOAD_STATUS_IN_SECONDS>]


Running sample to configure online depot and download bundles necessary for deploying VVF assuming you have
existing VCF Operations

      $ python download_bundles_vvf_instance_existing_vcf_ops.py \
        --vcf_installer_host_address <VCF_INSTALLER_HOST_ADDRESS> \
        --vcf_installer_admin_password <VCF_INSTALLER_ADMIN_PASSWORD> \
        --depot_account_username <DEPOT_ACCOUNT_USERNAME> \
        --depot_account_password <DEPOT_ACCOUNT_PASSWORD> \
        [--ca_certs <CA_CERTS>] \
        [--time_to_wait_for_depot_sync_in_minutes <TIME_TO_WAIT_FOR_DEPOT_SYNC_IN_MINUTES>] \
        [--time_to_wait_in_between_polls_for_depot_sync_in_seconds <TIME_TO_WAIT_IN_BETWEEN_POLLS_FOR_DEPOT_SYNC_IN_SECONDS>] \
        [--max_time_to_poll_download_status_in_hours <MAX_TIME_TO_POLL_DOWNLOAD_STATUS_IN_HOURS>] \
        [--time_to_sleep_in_between_polls_for_download_status_in_seconds <TIME_TO_SLEEP_IN_BETWEEN_POLLS_FOR_DOWNLOAD_STATUS_IN_SECONDS>]


Running sample to configure online depot and download bundles necessary for extending
a VCF Fleet with a VCF Instance

      $ python download_bundles_extend_vcf_fleet_with_vcf_instance.py \
        --vcf_installer_host_address <VCF_INSTALLER_HOST_ADDRESS> \
        --vcf_installer_admin_password <VCF_INSTALLER_ADMIN_PASSWORD> \
        --depot_account_username <DEPOT_ACCOUNT_USERNAME> \
        --depot_account_password <DEPOT_ACCOUNT_PASSWORD> \
        [--ca_certs <CA_CERTS>] \
        [--time_to_wait_for_depot_sync_in_minutes <TIME_TO_WAIT_FOR_DEPOT_SYNC_IN_MINUTES>] \
        [--time_to_wait_in_between_polls_for_depot_sync_in_seconds <TIME_TO_WAIT_IN_BETWEEN_POLLS_FOR_DEPOT_SYNC_IN_SECONDS>] \
        [--max_time_to_poll_download_status_in_hours <MAX_TIME_TO_POLL_DOWNLOAD_STATUS_IN_HOURS>] \
        [--time_to_sleep_in_between_polls_for_download_status_in_seconds <TIME_TO_SLEEP_IN_BETWEEN_POLLS_FOR_DOWNLOAD_STATUS_IN_SECONDS>]
