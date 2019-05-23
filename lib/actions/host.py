from lib.exceptions import exceptions
from lib.utils.unique import add_unique_interface
from lib.utils.validate import validate_input

import sys


def add_host(args, vc):
  # Initial questions
  vlans = []
  hostname = validate_input("Enter hostname of end device: ", cli_input=args.hostname)
  trunk = validate_input("Is this host trunking Vlans? (y or n): ", bool, default=True, cli_input=args.trunk)
  jumbo = validate_input("Enable Jumbo Frames? (y or n): ", bool, default=True, cli_input=args.jumbo)
  lag = validate_input("Is this host using multiple interfaces in a lag? (y or n): ",
                       bool, default=True, cli_input=args.lag)
  if lag:
    ae = validate_input("Enter ae id for lag (bond): ", int, 0, 48, cli_input=args.ae)
    ae_description = validate_input("Enter ae interface description: ", cli_input=args.ae_description)
    lacp = validate_input("Is ae using lacp?: ", bool, default=True, cli_input=args.lacp)
    if lacp:
      lacp_active = validate_input("Use lacp active (y for active, n for passive)?: ",
                                   bool, default=True, cli_input=args.lacp_active)

  # Construct VLAN list
  if args.vlan_id:
    for vlan_id in args.vlan_id:
      vlans.append(validate_input("Enter vlan id for host interface: ", int, 1, 4094, cli_input=vlan_id))
  else:
    while True:
      vlans.append(validate_input("Enter vlan id for host interface: ", int, 1, 4094))
      if not trunk or not validate_input("Do you want to enter another vlan to this trunk? (y or n): ",
                                         bool, default=False):
        break

  # Private Interface Function
  def build_interface(interface_name=None, description=None):
    interface = validate_input("Enter interface name: ", cli_input=interface_name)
    description = validate_input("Enter interface description: ", cli_input=description)
    host_interface_yml = {
      'name': interface,
      'description': description,
      'tag': hostname
    }
    if lag:
      host_interface_yml['ae'] = ae
    else:
      host_interface_yml['vlan'] = list(vlans)
      if jumbo:
        host_interface_yml['mtu'] = 9216
    add_unique_interface(vc['host_interfaces'], host_interface_yml)

  # Build Interface definition(s)
  if args.interface and args.interface_description:
    if len(args.interface) == len(args.interface_description):
      for idx, interface_name in enumerate(args.interface):
        build_interface(interface_name, args.interface_description[idx])
  elif args.interface:
    for interface_name in args.interface:
      build_interface(interface_name)
  else:
    while True:
      build_interface()
      if validate_input("Does this host have more interfaces that need to be "
                        "configured at the same time? (y or n): ", bool, default=False):
        continue
      break

  # Build AE Interface definition
  if lag:
    ae_interface = {
      'name': "ae" + str(ae),
      'description': ae_description,
      'esi': True,
      'vlan': list(vlans),
      'tag': hostname
    }
    if jumbo:
      ae_interface['mtu'] = 9216
    if lacp:
      ae_interface['lacp'] = {}
      ae_interface['lacp']['active'] = lacp_active
    if trunk:
      ae_interface['trunk'] = True
    add_unique_interface(vc['host_interfaces'], ae_interface)

  vc['host_interfaces'] = sorted(vc['host_interfaces'], key=lambda x: x['name'])


def delete_host(args, vc):
  hostname = validate_input("Enter hostname of end device: ", cli_input=args.hostname)
  vc['host_interfaces'][:] = [x for x in vc['host_interfaces'] if x['tag'] != hostname]
