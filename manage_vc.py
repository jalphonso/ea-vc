import argparse
import ruamel.yaml
import sys
from colorama import Fore, Style
from host import Host
from netaddr import IPAddress, IPNetwork
from netaddr.core import AddrFormatError
from ruamel.yaml.scalarstring import DoubleQuotedScalarString as dq
from utils import validate_input

yaml = ruamel.yaml.YAML()
yaml.indent(sequence=4, offset=2)
yaml.explicit_start = True


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
  while True:
    vlans.append(validate_input("Enter vlan id for host interface: ", int, 1, 4094, cli_input=args.vlan_id))
    if not trunk or not validate_input("Do you want to enter another vlan to this trunk? (y or n): ",
                                       bool, default=False):
      break

  # Build Interface definition(s)
  while True:
    interface = validate_input("Enter interface name: ", cli_input=args.interface)
    description = validate_input("Enter interface description: ", cli_input=args.interface_description)
    host_interface_yml = {
      'name': interface,
      'description': description,
      'tag': hostname
    }
    if lag:
      host_interface_yml['ae'] = ae
    else:
      host_interface_yml['vlan'] = vlans
      if jumbo:
        host_interface_yml['mtu'] = 9216
    vc['host_interfaces'].append(host_interface_yml)
    if lag and validate_input("Does this host have more interfaces that need to be "
                              "configured in the same lag? (y or n): ", bool, default=False):
      continue
    break

  # Build AE Interface definition
  if lag:
    ae_interface = {
      'name': "ae" + str(ae),
      'description': ae_description,
      'esi': True,
      'vlan': vlans,
      'tag': hostname
    }
    if jumbo:
      ae_interface['mtu'] = 9216
    if lacp:
      ae_interface['lacp'] = {}
      ae_interface['lacp']['active'] = lacp_active
    if trunk:
      ae_interface['trunk'] = True
    vc['host_interfaces'].append(ae_interface)
  vc['host_interfaces'] = sorted(vc['host_interfaces'], key=lambda x: x['name'])


def delete_host(args, vc):
  hostname = validate_input("Enter hostname of end device: ", cli_input=args.hostname)
  vc['host_interfaces'][:] = [x for x in vc['host_interfaces'] if x['tag'] != hostname]


def add_vlan(args, vc):
  vlan = validate_input("Enter vlan id: ", int, 1, 4094, cli_input=args.vlan_id)
  vlan_yml = {
    'name': "vlan." + str(vlan),
    'id': vlan
  }
  if vlan_yml not in vc['vlans']:
    vc['vlans'].append(vlan_yml)
    vc['vlans'] = sorted(vc['vlans'], key=lambda x: x['id'])


def delete_vlan(args, vc):
  vlan = validate_input("Enter vlan id: ", int, 1, 4094, cli_input=args.vlan_id)
  vc['vlans'][:] = [x for x in vc['vlans'] if x['id'] != vlan]


def push_changes(args, vc):
  pass


def main():
  oper_choices = ["add_host", "delete_host", "add_vlan", "delete_vlan", "push_changes"]
  parser = argparse.ArgumentParser(description='Execute operation(s)')
  parser.add_argument('-o', '--oper', dest='oper', metavar='<oper>',
                      choices=oper_choices,
                      help='select operation(s) to run from list')
  parser.add_argument('--vlan_id', dest='vlan_id', metavar='<vlan_id>',
                      help='provide vlan_id')
  parser.add_argument('--interface', dest='interface', metavar='<interface>',
                      help='provide interface name')
  parser.add_argument('--interface_description', dest='interface_description', metavar='<interface_description>',
                      help='provide interface description')
  parser.add_argument('--hostname', dest='hostname', metavar='<hostname>',
                      help='provide hostname of end device')
  parser.add_argument('--trunk', dest='trunk', action='store_true',
                      help='enable vlan trunk for host')
  parser.add_argument('--jumbo', dest='jumbo', action='store_true',
                      help='enable jumbo frames for host')
  parser.add_argument('--lacp', dest='lacp', action='store_true',
                      help='enable lacp for host (only applies to lag)')
  parser.add_argument('--lacp_active', dest='lacp_active', action='store_true',
                      help='set lacp to active if lacp is enabled for host')
  parser.add_argument('--lag', dest='lag', action='store_true',
                      help='enable lag for host')
  parser.add_argument('--ae', dest='ae', metavar='<ae>',
                      help='provide ae id for host lag')
  parser.add_argument('--ae_description', dest='ae_description', metavar='<ae_description>',
                      help='provide ae description for host lag')
  args = parser.parse_args()

  print(f"{Fore.YELLOW}Ansible operation assistant{Style.RESET_ALL}")

  vc_file = "./inventory/dc1/group_vars/vc.yml"
  try:
    with open(vc_file) as f:
      oper = validate_input(f"select operation(s) to run from list\n{oper_choices}\n"
                            "Type operation you want to run: ", list, choices=oper_choices, cli_input=args.oper)
      vc = yaml.load(f)
      if callable(globals()[oper]):
        globals()[oper](args, vc)
      else:
        print(f"{Fore.RED}Invalid operation: '{oper}'\nProblem with code. {Style.RESET_ALL}")
        sys.exit(2)
    with open(vc_file, 'w') as f:
      yaml.dump(vc, f)
  except FileNotFoundError:
    print("Initializing VC file, please run again")
    with open(vc_file, 'w') as f:
      yaml.dump({'host_interfaces': [], 'vlans': []}, f)


if __name__ == '__main__':
  main()
