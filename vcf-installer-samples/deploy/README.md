This directory contains deployment samples for VCF Installer:


Running sample to deploy new VCF Fleet with first VCF Instance

    $ python deploy_vcf_fleet_first_vcf_instance.py \
      --vcf_installer_server_address <VCF_INSTALLER_SERVER_ADDRESS> \
      --vcf_installer_admin_password <VCF_INSTALLER_ADMIN_PASSWORD> \
      --esxi_host_root_password <ESXI_HOST_ROOT_PASSWORD> \
      --host_fqdn_to_thumbprint <HOST_FQDN_TO_THUMBPRINT> \
      --dns_domain <DNS_DOMAIN> \
      --dns_nameserver <DNS_NAMESERVER> \
      --ntp_servers <NTP_SERVERS> \
      --sddc_manager_hostname <SDDC_MANAGER_HOSTNAME> \
      --vcenter_fqdn <VCENTER_FQDN> \
      [--vcenter_sso_domain <VCENTER_SSO_DOMAIN>] \
      --nsx_fqdn <NSX_FQDN> \
      --nsx_vip_fqdn <NSX_VIP_FQDN> \
      --management_network_gateway <MANAGEMENT_NETWORK_GATEWAY> \
      --management_network_subnet <MANAGEMENT_NETWORK_SUBNET> \
      --management_network_vlan_id <MANAGEMENT_NETWORK_VLAN_ID> \
      --vsan_network_gateway <VSAN_NETWORK_GATEWAY> \
      --vsan_network_subnet <VSAN_NETWORK_SUBNET> \
      --vsan_network_vlan_id <VSAN_NETWORK_VLAN_ID> \
      --vsan_network_ip_range_start <VSAN_NETWORK_IP_RANGE_START> \
      --vsan_network_ip_range_end <VSAN_NETWORK_IP_RANGE_END> \
      --vmotion_network_gateway <VMOTION_NETWORK_GATEWAY> \
      --vmotion_network_subnet <VMOTION_NETWORK_SUBNET> \
      --vmotion_network_vlan_id <VMOTION_NETWORK_VLAN_ID> \
      --vmotion_ip_range_start <VMOTION_IP_RANGE_START> \
      --vmotion_ip_range_end <VMOTION_IP_RANGE_END> \
      --vcf_ops_fqdn <VCF_OPS_FQDN> \
      [--vcf_automation_fqdn <VCF_AUTOMATION_FQDN>] \
      [--vcf_automation_pool_ip_range_start <VCF_AUTOMATION_POOL_IP_RANGE_START>] \
      [--vcf_automation_pool_ip_range_end <VCF_AUTOMATION_POOL_IP_RANGE_END>] \
      --vcf_ops_collector_fqdn <VCF_OPS_COLLECTOR_FQDN> \
      [--ca_certs CA_CERTS] \
      [--validate_only]

* Testbed Requirement:
    - At least 4 prepared ESXi hosts
    - All provided hostnames must be resolvable from the VCF Installer appliance
    - The addresses of all components must be resolvable from the VCF Installer appliance (NTP, various VCF
       components, etc.)
    - The Depot configuration must be complete
    - The respective binary bundles need to be downloaded


Running sample to deploy new VCF Fleet with first VCF Instance with existing Vcenter and NSX-T

    $ python deploy_vcf_fleet_first_vcf_instance_from_existing_components.py \
      --vcf_installer_admin_password <VCF_INSTALLER_ADMIN_PASSWORD> \
      --vcf_installer_server_address <VCF_INSTALLER_SERVER_ADDRESS> \
      --dns_domain <DNS_DOMAIN> \
      --dns_nameserver <DNS_NAMESERVER> \
      --ntp_servers <NTP_SERVERS> \
      --vcf_ops_fqdn <VCF_OPS_FQDN> \
      [--vcf_automation_fqdn <VCF_AUTOMATION_FQDN>] \
      [--vcf_automation_pool_ip_range_start <VCF_AUTOMATION_POOL_IP_RANGE_START>] \
      [--vcf_automation_pool_ip_range_end <VCF_AUTOMATION_POOL_IP_RANGE_END>] \
      --vcf_ops_collector_fqdn <VCF_OPS_COLLECTOR_FQDN> \
      --vcenter_fqdn <VCENTER_FQDN> \
      [--vcenter_thumbprint <VCENTER_THUMBPRINT>] \
      --vcenter_root_password <VCENTER_ROOT_PASSWORD> \
      --vcenter_admin_sso_username <VCENTER_ADMIN_SSO_USERNAME> \
      --vcenter_admin_sso_password <VCENTER_ADMIN_SSO_PASSWORD> \
      --nsx_fqdn <NSX_FQDN> \
      --nsx_vip_fqdn <NSX_VIP_FQDN> \
      [--nsx_thumbprint <NSX_THUMBPRINT>] \
      --nsx_root_password <NSX_ROOT_PASSWORD> \
      --nsx_admin_password <NSX_ADMIN_PASSWORD> \
      --nsx_audit_password <NSX_AUDIT_PASSWORD> \
      --sddc_id <SDDC_ID> \
      --sddc_manager_fqdn <SDDC_MANAGER_FQDN> \
      [--ca_certs CA_CERTS] \
      [--validate_only]

* Testbed Requirement:
    - Existing components need to be configured and reachable by the VCF Installer appliance
    - All provided hostnames must be resolvable from the VCF Installer appliance
    - The addresses of all components must be resolvable from the VCF Installer appliance (NTP, various VCF
        components, etc.)
    - The Depot configuration must be complete
    - The respective binary bundles need to be downloaded


Running sample to deploy new VVF instance with existing Vcenter

    $ python deploy_vvf_instance_from_existing_components.py \
      --vcf_installer_admin_password <VCF_INSTALLER_ADMIN_PASSWORD> \
      --vcf_installer_server_address <VCF_INSTALLER_SERVER_ADDRESS> \
      --dns_domain <DNS_DOMAIN> \
      --vcf_ops_fqdn <VCF_OPS_FQDN> \
      --vcenter_fqdn <VCENTER_FQDN> \
      [--vcenter_thumbprint <VCENTER_THUMBPRINT>] \
      --vcenter_root_password <VCENTER_ROOT_PASSWORD> \
      [--vcenter_sso_domain <VCENTER_SSO_DOMAIN>] \
      --vcenter_admin_sso_username <VCENTER_ADMIN_SSO_USERNAME> \
      --vcenter_admin_sso_password <VCENTER_ADMIN_SSO_PASSWORD> \
      --sddc_id <SDDC_ID> \
      [--ca_certs <CA_CERTS>] \
      [--validate_only]

* Testbed Requirement:
    - Existing components need to be configured and reachable by the VCF Installer appliance
    - All provided hostnames must be resolvable from the VCF Installer appliance
    - The addresses of all components must be resolvable from the VCF Installer appliance (NTP, various VCF
       components, etc.)
    - The Depot configuration must be complete
    - The respective binary bundles need to be downloaded


Running sample to extend existing VCF fleet with new VCF Instance

    $ python extend_vcf_fleet_with_vcf_instance.py \
      --vcf_installer_admin_password <VCF_INSTALLER_ADMIN_PASSWORD> \
      --vcf_installer_server_address <VCF_INSTALLER_SERVER_ADDRESS> \
      --dns_domain <DNS_DOMAIN> \
      --dns_nameserver <DNS_NAMESERVER> \
      --ntp_servers <NTP_SERVERS> \
      --vcf_ops_fqdn <VCF_OPS_FQDN> \
      --vcf_ops_admin_password <VCF_OPS_ADMIN_PASSWORD> \
      [--vcf_ops_thumbprint <VCF_OPS_THUMBPRINT>] \
      [--vcf_automation_fqdn <VCF_AUTOMATION_FQDN>] \
      [--vcf_automation_thumbprint <VCF_AUTOMATION_THUMBPRINT>] \
      --vcf_automation_admin_password <VCF_AUTOMATION_ADMIN_PASSWORD> \
      --vcf_ops_collector_fqdn <VCF_OPS_COLLECTOR_FQDN> \
      --vcenter_fqdn <VCENTER_FQDN> \
      [--vcenter_sso_domain <VCENTER_SSO_DOMAIN>] \
      --nsx_fqdn <NSX_FQDN> \
      --nsx_vip_fqdn <NSX_VIP_FQDN> \
      --nsx_gateway <NSX_GATEWAY> \
      --nsx_subnet <NSX_SUBNET> \
      --nsx_vlan_id <NSX_VLAN_ID> \
      --nsx_ip_range_start <NSX_IP_RANGE_START> \
      --nsx_ip_range_end <NSX_IP_RANGE_END> \
      --esxi_host_root_password <ESXI_HOST_ROOT_PASSWORD> \
      --host_fqdn_to_thumbprint <HOST_FQDN_TO_THUMBPRINT> \
      --management_network_gateway <MANAGEMENT_NETWORK_GATEWAY> \
      --management_network_subnet <MANAGEMENT_NETWORK_SUBNET> \
      --management_network_vlan_id <MANAGEMENT_NETWORK_VLAN_ID> \
      --vsan_network_gateway <VSAN_NETWORK_GATEWAY> \
      --vsan_network_subnet <VSAN_NETWORK_SUBNET> \
      --vsan_network_vlan_id <VSAN_NETWORK_VLAN_ID> \
      --vsan_network_ip_range_start <VSAN_NETWORK_IP_RANGE_START> \
      --vsan_network_ip_range_end <VSAN_NETWORK_IP_RANGE_END> \
      --vmotion_network_gateway <VMOTION_NETWORK_GATEWAY> \
      --vmotion_network_subnet <VMOTION_NETWORK_SUBNET> \
      --vmotion_network_vlan_id <VMOTION_NETWORK_VLAN_ID> \
      --vmotion_ip_range_start <VMOTION_IP_RANGE_START> \
      --vmotion_ip_range_end <VMOTION_IP_RANGE_END> \
      --sddc_id <SDDC_ID> \
      --sddc_manager_fqdn <SDDC_MANAGER_FQDN> \
      [--ca_certs <CA_CERTS>] \
      [--validate_only]

* Testbed Requirement:
    - At least 4 prepared ESXi hosts
    - An existing VCF Fleet, which is to be extended with a new VCF Instance
    - All provided hostnames must be resolvable from the VCF Installer appliance
    - The addresses of all components must be resolvable from the VCF Installer appliance (NTP, various VCF
       components, etc.)
    - The Depot configuration must be complete
    - The respective binary bundles need to be downloaded.


Running sample to extend existing VCF fleet with new VCF Instance, reusing existing Vcenter, NSX-T,
VCF Operations, VCF Operations Fleet Management and VCF Automation

    $ python extend_vcf_fleet_with_vcf_instance_with_existing_components.py \
      --vcf_installer_admin_password <VCF_INSTALLER_ADMIN_PASSWORD> \
      --vcf_installer_server_address <VCF_INSTALLER_SERVER_ADDRESS> \
      --dns_domain <DNS_DOMAIN> \
      --dns_nameserver <DNS_NAMESERVER> \
      --ntp_servers <NTP_SERVERS> \
      --vcf_ops_fqdn <VCF_OPS_FQDN> \
      --vcf_ops_admin_password <VCF_OPS_ADMIN_PASSWORD> \
      [--vcf_ops_thumbprint <VCF_OPS_THUMBPRINT>] \
      [--vcf_automation_fqdn <VCF_AUTOMATION_FQDN>] \
      [--vcf_automation_thumbprint <VCF_AUTOMATION_THUMBPRINT>] \
      --vcf_automation_admin_password <VCF_AUTOMATION_ADMIN_PASSWORD> \
      --vcf_ops_collector_fqdn <VCF_OPS_COLLECTOR_FQDN> \
      --vcenter_fqdn <VCENTER_FQDN> \
      [--vcenter_thumbprint <VCENTER_THUMBPRINT>] \
      --vcenter_root_password <VCENTER_ROOT_PASSWORD> \
      --vcenter_admin_sso_username <VCENTER_ADMIN_SSO_USERNAME> \
      --vcenter_admin_sso_password <VCENTER_ADMIN_SSO_PASSWORD> \
      --nsx_fqdn <NSX_FQDN> \
      --nsx_vip_fqdn <NSX_VIP_FQDN> \
      [--nsx_thumbprint <NSX_THUMBPRINT>] \
      --nsx_root_password <NSX_ROOT_PASSWORD> \
      --nsx_admin_password <NSX_ADMIN_PASSWORD> \
      --nsx_audit_password <NSX_AUDIT_PASSWORD> \
      --sddc_id <SDDC_ID> \
      --sddc_manager_fqdn <SDDC_MANAGER_FQDN> \
      [--ca_certs <CA_CERTS>] \
      [--validate_only]

* Testbed Requirement:
    - An existing VCF Fleet, which is to be extended with a new VCF Instance
    - Existing components need to be configured and reachable by the VCF Installer appliance
    - All provided hostnames must be resolvable from the VCF Installer appliance
    - The addresses of all components must be resolvable the VCF Installer appliance (NTP, various VCF components,
       etc.)
    - The Depot configuration must be complete
    - The respective binary bundles need to be downloaded
