import wmi

def ChangeIP(isDHCPEnabled, static_options):
    if isDHCPEnabled:
        return DhcpIpChanger()
    else:
        return StaticIpChanger(static_options)

def DhcpIpChanger():
    print('DhcpIpChanger EnableDHCP')
    selected_adapter.EnableDHCP()
    return True


def StaticIpChanger(static_options):
    ip, subnetmask, gateway, dns = static_options
    dns1, dns2 = dns.split('-')
    dns1 = dns1.split()[0]
    dns2 = dns2.split()[0]
    print('StaticIpChanger: ',ip, subnetmask, gateway, dns1, dns2)

    global selected_adapter
    if selected_adapter is None:
        print('Error: No adapter selected!')
        return False

    a = selected_adapter.EnableStatic(IPAddress=[ip], SubnetMask=[subnetmask])
    b = selected_adapter.SetGateways(DefaultIPGateway=[gateway])
    c = selected_adapter.SetDNSServerSearchOrder([dns1, dns2])
    d = selected_adapter.SetDynamicDNSRegistration(FullDNSRegistrationEnabled=1)

    print(a)
    print(b)
    print(c)
    print(d)
    if [a[0], b[0], c[0], d[0]] == [0, 0, 0, 0]:
        return True
    else:
        return False

def get_adapter(adapted_text):
    nic_configs = wmi_inst.Win32_NetworkAdapterConfiguration(IPEnabled=True)
    for adapter in nic_configs:
        if adapter.Caption == adapted_text:
            print(adapter.DHCPEnabled)
            return adapter
    return None


selected_adapter = None

def set_selected_adapter(adapter):
    global selected_adapter
    print('set_selected_adapter: ', adapter)
    selected_adapter = adapter

adapter_options = []
adapters = []
wmi_inst = wmi.WMI()

def get_adapters():
    adapters.clear()
    for nic in wmi_inst.Win32_NetworkAdapterConfiguration(IPEnabled=True):
        adapters.append(nic)
        print(nic.Caption)

def get_adapters_name():
    return [i.Caption for i in adapters]