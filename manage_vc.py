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
  ## Initial questions
  vlans = []
  trunk = validate_input("Is this host trunking Vlans? (y or n): ", bool, default=True)
  jumbo = validate_input("Enable Jumbo Frames? (y or n): ", bool, default=True)
  lag = validate_input("Is this host using multiple intefaces in a lag? (y or n): ", bool, default=True)
  if lag:
    ae = validate_input("Enter ae id for lag (bond): ", int, 0, 48)
    ae_description = validate_input("Enter ae interface description: ")
    lacp = validate_input("Is ae using lacp?: ", bool, default=True)
    if lacp:
      lacp_active = validate_input("Use lacp active (y for active, n for passive)?: ", bool, default=True)

  ## Construct VLAN list
  while True:
    vlans.append(validate_input("Enter vlan id for host interface: ", int, 1, 4094))
    if not trunk or not validate_input("Do you want to enter another vlan to this trunk? (y or n): ", bool, default=False):
      break

  ## Build Interface definition(s)
  while True:
    interface = validate_input("Enter interface name: ")
    description = validate_input("Enter interface description: ")
    host_interface_yml = {
      'name': interface,
      'description': description,
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

  ## Build AE Interface definition
  if lag:
    ae_interface = {
      'name': "ae" + str(ae),
      'description': ae_description,
      'esi': True,
      'vlan': vlans
    }
    if jumbo:
      ae_interface['mtu'] = 9216
    if lacp:
      ae_interface['lacp'] = {}
      ae_interface['lacp']['active'] = lacp_active
    if trunk:
      ae_interface['trunk'] = True
    vc['host_interfaces'].append(ae_interface)
  vc['host_interfaces'] = sorted(vc['host_interfaces'], key= lambda x: x['name'])


def delete_host(args, vc):
  while True:
    interface_name = validate_input("Enter interface name: ")
    for interface in vc['host_interfaces']:
      if interface['name'] == interface_name:
        vc['host_interfaces'].remove(interface)
    if not validate_input("Delete more interfaces? (y or n): ", bool, default=False):
      break


def add_vlan(args, vc):
  while True:
    vlan = validate_input("Enter vlan id: ", int, 1, 4094)
    vlan_yml = {
      'name': "vlan." + str(vlan),
      'id': vlan
    }
    if vlan_yml not in vc['vlans']:
      vc['vlans'].append(vlan_yml)
      vc['vlans'] = sorted(vc['vlans'], key = lambda x: x['id'])
    if not validate_input("Do you want to add another one? (y or n): ", bool, default=False):
      break


def delete_vlan(args, vc):
  while True:
    vlan = validate_input("Enter vlan id: ", int, 1, 4094)
    vlan_yml = {
      'name': "vlan." + str(vlan),
      'id': vlan
    }
    if vlan_yml in vc['vlans']:
      vc['vlans'].remove(vlan_yml)
    if not validate_input("Do you want to delete another one? (y or n): ", bool, default=False):
      break


def push_changes(args, vc):
  pass


def main():
  oper_choices = ["add_host", "delete_host", "add_vlan", "delete_vlan", "push_changes"]
  parser = argparse.ArgumentParser(description='Execute operation(s)')
  parser.add_argument('-o', '--oper', dest='operations', metavar='<oper>',
                      choices=oper_choices, nargs='+',
                      help='select operation(s) to run from list')
  parser.add_argument('--vlan_id', dest='vlan_id', metavar='<vlan_id>',
                      help='provide vlan_id')
  parser.add_argument('--interface', dest='interface', metavar='<interface>',
                      help='provide interface name')
  args = parser.parse_args()

  print(f"{Fore.YELLOW}Ansible operation assistant{Style.RESET_ALL}")

  vc_file = "./inventory/dc1/group_vars/vc.yml"
  try:
    with open(vc_file) as f:
      oper = validate_input(f"select operation(s) to run from list\n{oper_choices}\n"
                            "Type operation you want to run: ", list, choices=oper_choices)
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
