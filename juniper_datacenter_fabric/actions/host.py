import sys
from colorama import Fore, Style
from juniper_datacenter_fabric.exceptions import exceptions
from juniper_datacenter_fabric.utils.unique import add_unique_interface, is_list_unique, host_is_unique_or_error
from juniper_datacenter_fabric.utils.validate import (validate_choice, validate_str, validate_bool, validate_interface,
                                                      validate_int, validate_ip_address, validate_ip_network)


def add_host(args, vc):
  # Initial questions
  vlans = []
  hostname = validate_str(f"{Fore.YELLOW}\nHostname (tag) of end device (this is used to group interfaces)\n"
                          f"If this host has more than one interface group then name it accordingly\n"
                          f"  i.e. hostname-mgmt or hostname-data\n\n{Style.RESET_ALL}"
                          f"Enter hostname/interface group tag: ", cli_input=args.hostname)
  host_is_unique_or_error(vc['host_interfaces'], hostname, vc['fabric_name'])
  trunk = validate_bool("Is this host trunking Vlans? (y or n): ", default=True, cli_input=args.trunk)
  jumbo = validate_bool("Enable Jumbo Frames? (y or n): ", default=True, cli_input=args.jumbo)
  lag = validate_bool("Is this host using multiple interfaces in a lag? (y or n): ",
                      default=True, cli_input=args.lag)
  if lag:
    ae = validate_int("Enter ae id for lag (bond): ", 0, 48, cli_input=args.ae)
    ae_description = validate_str("Enter ae interface description: ", cli_input=args.ae_description)
    lacp = validate_bool("Is ae using lacp?: ", default=True, cli_input=args.lacp)
    if lacp:
      lacp_active = validate_bool("Use lacp active (y for active, n for passive)?: ",
                                  default=True, cli_input=args.lacp_active)

  # Construct VLAN list
  existing_vlans = [v['name'] for v in vc['vlans']]

  def add_vlan_to_list(vlan_name=None):
    new_vlan = validate_str("Enter vlan name for host interface: ", cli_input=vlan_name)
    if new_vlan in existing_vlans:
      vlans.append(new_vlan)
    else:
      raise exceptions.VlanDoesNotExist(f"VLAN named {new_vlan} does not exist. Add the VLAN to the fabric first.")

  if args.vlan_name:
    for vlan_name in args.vlan_name:
      add_vlan_to_list(vlan_name)
  else:
    while True:
      add_vlan_to_list()
      if not trunk or not validate_bool("Do you want to enter another vlan to this trunk? (y or n): ",
                                        default=False):
        break

  # Private Interface Function
  def build_interface(interface_name=None, description=None):
    interface = validate_interface("Enter interface name: ", cli_input=interface_name)
    description = validate_str("Enter interface description: ", cli_input=description)
    speed = validate_choice("Enter physical interface speed: ", cli_input=args.speed,
                      choices=["1g","10g","25g","40g","100g"])
    host_interface_yml = {
      'name': interface,
      'description': description if description.strip() else None,
      'tag': hostname,
      'speed': speed
    }
    if lag:
      host_interface_yml['ae'] = ae
    else:
      host_interface_yml['vlan'] = list(vlans)
      if jumbo:
        host_interface_yml['mtu'] = 9216
      host_interface_yml['trunk'] = trunk

    add_unique_interface(vc['host_interfaces'], host_interface_yml)
  # Build Interface definition(s)
  if args.interface and args.interface_description and len(args.interface) == len(args.interface_description):
    for idx, interface_name in enumerate(args.interface):
      build_interface(interface_name, args.interface_description[idx])
  elif args.interface:
    for interface_name in args.interface:
      build_interface(interface_name)
  else:
    while True:
      build_interface()
      if validate_bool("Does this host have more interfaces that need to be "
                       "configured at the same time? (y or n): ", default=False):
        continue
      break

  # Build AE Interface definition
  if lag:
    ae_interface = {
      'name': "ae" + str(ae),
      'description': ae_description if ae_description.strip() else None,
      'esi': True,
      'vlan': list(vlans),
      'tag': hostname
    }
    if jumbo:
      ae_interface['mtu'] = 9216
    if lacp:
      ae_interface['lacp'] = {}
      ae_interface['lacp']['active'] = lacp_active
    ae_interface['trunk'] = trunk
    add_unique_interface(vc['host_interfaces'], ae_interface)

  vc['host_interfaces'] = sorted(vc['host_interfaces'], key=lambda x: x['name'])


def delete_host(args, vc):
  hostname = validate_str("Enter hostname of end device: ", cli_input=args.hostname)
  hosts = [h['tag'] for h in vc['host_interfaces']]
  if hostname not in hosts:
    raise exceptions.HostDoesNotExist(f"Host {hostname} does not exist in fabric {vc['fabric_name']}")
  vc['host_interfaces'][:] = [x for x in vc['host_interfaces'] if x['tag'] != hostname]
