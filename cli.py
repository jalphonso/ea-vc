import argparse
import ruamel.yaml
import sys
from colorama import Fore, Style
from host import Host
from netaddr import IPAddress, IPNetwork
from netaddr.core import AddrFormatError
from ruamel.yaml.scalarstring import DoubleQuotedScalarString as dq

yaml = ruamel.yaml.YAML()
yaml.indent(sequence=4, offset=2)
yaml.explicit_start = True


def _validate_input(prompt, input_type=str, input_min=None, input_max=None, cli_input = None, default = None, choices = None):
    max_tries = 5
    tries = 0
    if default is not None:
      if default is False:
        print_default = 'n'
      elif default is True:
        print_default = 'y'
      else:
        print_default = default
      prompt = prompt + "[" + str(print_default) + "]: "
    while True and tries < max_tries:
        if not cli_input:
          user_input = input(prompt).strip()
        else:
          user_input = cli_input
          cli_input = None
        if not user_input:
            if default is None:
              print("Input cannot be blank, please try again")
            else:
              user_input = default
              break
        elif input_type == int:
            try:
                user_input = int(user_input)
            except ValueError:
                print("Input needs to be an integer, please try again")
                tries +=1
                continue
            if input_min and input_max and input_min < input_max:
                if user_input < input_min or user_input > input_max:
                    print(f"Input needs to between {input_min} and {input_max}, please try again")
                else:
                    break
            elif input_min and user_input < input_min :
                print(f"Input needs to be greater than or equal to {input_min}, please try again")
            elif input_max and user_input > input_max :
                print(f"Input needs to be less than or equal to {input_max}, please try again")
            else:
                break
        elif input_type == bool:
            bool_char = user_input.lower()
            if bool_char == 'y' or bool_char == 'yes':
                user_input = True
                break
            elif bool_char == 'n' or bool_char == 'no':
                user_input = False
                break
            else:
                print(f"Input needs to be yes/no or y/n, please try again")
        elif input_type == list:
          if user_input in choices:
            break
          else:
            print(f"Selection must be one of the following {choices}")
        elif input_type == 'IPAddress':
          try:
            if len(user_input.split('.')) != 4:
              raise ValueError("Not a properly formatted IP Address x.x.x.x")
            user_input = IPAddress(user_input)
            break
          except (ValueError, AddrFormatError) as e:
            print(e)
        elif input_type == 'IPNetwork':
          try:
            if len(user_input.split('.')) != 4 or '/' not in user_input:
              raise ValueError("Not a properly formatted IP/CIDR x.x.x.x/x")
            user_input = IPNetwork(user_input)
            break
          except (ValueError, AddrFormatError) as e:
            print(e)
        else:
            break
        tries +=1
    if tries == max_tries:
        print("Reached maximum attempts to validate input, quitting...")
        sys.exit(1)
    return user_input


def add_host(args, vc):
  vlans = []
  trunk = _validate_input("Is this host trunking Vlans? (y or n): ", bool, default=True)
  jumbo = _validate_input("Enable Jumbo Frames? (y or n): ", bool, default=True)
  lag = _validate_input("Is this host using multiple intefaces in a lag? (y or n): ", bool, default=True)
  if lag:
    ae = _validate_input("Enter ae id for lag (bond): ", int, 0, 48)
  while True:
    vlans.append(_validate_input("Enter vlan id for host interface: ", int, 1, 4094))
    if not trunk or not _validate_input("Do you want to enter another vlan to this trunk? (y or n): ", bool, default=False):
      break
  while True:
    interface = _validate_input("Enter interface name: ")
    description = _validate_input("Enter interface description: ")
    host_interface_yml = {
      'name': interface,
      'description': description,
    }
    if lag:
      host_interface_yml['ae'] = ae
    else:
      host_interface_yml['vlan'] = vlans
    vc['host_interfaces'].append(host_interface_yml)
    vc['host_interfaces'] = sorted(vc['host_interfaces'], key= lambda x: x['name'])
    if lag and _validate_input("Does this host have more interfaces that need to be "
                           "configured in the same lag? (y or n): ", bool, default=False):
      continue
    break


def delete_host(args, vc):
  while True:
    interface_name = _validate_input("Enter interface name: ")
    for interface in vc['host_interfaces']:
      if interface['name'] == interface_name:
        vc['host_interfaces'].remove(interface)
    if not _validate_input("Delete more interfaces? (y or n): ", bool, default=False):
      break


def add_vlan(args, vc):
  while True:
    vlan = _validate_input("Enter vlan id: ", int, 1, 4094)
    vlan_yml = {
      'name': "vlan." + str(vlan),
      'id': vlan
    }
    if vlan_yml not in vc['vlans']:
      vc['vlans'].append(vlan_yml)
      vc['vlans'] = sorted(vc['vlans'], key = lambda x: x['id'])
    if not _validate_input("Do you want to add another one? (y or n): ", bool, default=False):
      break


def delete_vlan(args, vc):
  while True:
    vlan = _validate_input("Enter vlan id: ", int, 1, 4094)
    vlan_yml = {
      'name': "vlan." + str(vlan),
      'id': vlan
    }
    if vlan_yml in vc['vlans']:
      vc['vlans'].remove(vlan_yml)
    if not _validate_input("Do you want to delete another one? (y or n): ", bool, default=False):
      break


def push_changes(args, vc):
  pass


def ui():
  oper_choices = ["add_host", "delete_host", "add_vlan", "delete_vlan", "push_changes"]
  parser = argparse.ArgumentParser(description='Execute operation(s)')
  parser.add_argument('--hostname', dest='hostname', metavar='<hostname>',
                      help='provide hostname of device')
  parser.add_argument('-o', '--oper', dest='operations', metavar='<oper>',
                      choices=oper_choices, nargs='+',
                      help='select operation(s) to run from list')
  parser.add_argument('--vlan_id', dest='vlan_id', metavar='<vlan_id>',
                      help='provide vlan_id')
  parser.add_argument('--interface', dest='interface', metavar='<interface>',
                      help='provide interface name')
  args = parser.parse_args()

  print(f"{Fore.YELLOW}Ansible operation assistant{Style.RESET_ALL}")
  oper = _validate_input(f"select operation(s) to run from list\n{oper_choices}\n"
                         "Type operation you want to run: ", list, choices=oper_choices)

  vc_file = "./inventory/dc1/group_vars/vc.yml"
  try:
    with open(vc_file) as f:
      vc = yaml.load(f)
      if callable(globals()[oper]):
        globals()[oper](args, vc)
      else:
        print(f"{Fore.RED}Invalid operation: '{oper}'\nProblem with code. {Style.RESET_ALL}")
        sys.exit(2)
    with open(vc_file, 'w') as f:
      yaml.dump(vc, f)
  except FileNotFoundError:
    pass


def main():
  parser = argparse.ArgumentParser(description='Initialize yaml file for device')
  parser.add_argument('--hostname', dest='hostname', metavar='<hostname>',
                      help='provide hostname of device')
  parser.add_argument('--node_id', dest='node_id', metavar='<node_id>',
                      help='provide node id (must be unique per VC) 0 or 1')
  parser.add_argument('--mgmt_ip', dest='mgmt_ip', metavar='<mgmt_ip>',
                      help='provide mgmt_ip in CIDR format x.x.x.x/x')
  args = parser.parse_args()

  hostname = _validate_input("Enter hostname for device: ", cli_input=args.hostname)
  host_file = "./inventory/dc1/host_vars/" + hostname + ".yml"
  try:
    with open(host_file) as f:
      host = yaml.load(f)
  except FileNotFoundError:
    print(f"{Fore.YELLOW}Ansible yaml file creator assistant{Style.RESET_ALL}")
    node_id = _validate_input("Enter node id (must be unique per VC) 0 or 1: ",
                                      int, 0, 1, cli_input=args.node_id)
    neighbor_node_id = 0 if node_id else 1
    vgw_local_index = node_id + 2
    mgmt_ip = _validate_input("Enter management IP in CIDR format x.x.x.x/x: ", "IPNetwork",
                                      cli_input=args.mgmt_ip)
    mgmt_default_gw = mgmt_ip[1]
    underlay_asn = "65535.6550" + str(node_id)
    neighbor_underlay_asn = "65535.6550" + str(neighbor_node_id)
    overlay_local_ip = "10.255.255." + str(node_id)
    overlay_asn = "65535.64999"

    mgmt_interface = {
      'name': "em0",
      'ip_cidr': str(mgmt_ip)
    }
    underlay_neighbor = {
      'ip': "10.255.254." + str(neighbor_node_id),
      'asn': dq(neighbor_underlay_asn)
    }
    overlay_neighbor = {
      'ip': "10.255.255." + str(neighbor_node_id)
    }
    system_lo0 = {
      'name': "lo0",
      'ip_cidr': f"10.255.255.{node_id}/32"
    }

    host = Host(vgw_local_index, mgmt_default_gw)
    host.add_mgmt_interface(**mgmt_interface)

    system_interfaces = ["et-0/0/52", "et-0/0/53", "et-0/0/54", "et-0/0/55"]
    for interface in system_interfaces:
      system_interface = {
        'name': f"{interface}",
        'description': "Used for inter-chassis LAG",
        'ae': 49
      }
      host.add_system_interface(**system_interface)

    system_ae = {
      'name': "ae49",
      'description': "Inter-chassis LAG for VC pair",
      'mtu': 9216,
      'lacp': {
        'active': True
      },
      'ip_cidr': f"10.255.254.{node_id}/31",
      'is_icl': True
    }
    host.add_system_interface(**system_ae)
    host.add_system_interface(**system_lo0)
    host.initialize_underlay(underlay_asn)
    host.initialize_overlay(overlay_asn, overlay_local_ip)
    host.add_underlay_neighbor(**underlay_neighbor)
    host.add_overlay_neighbor(**overlay_neighbor)

    host = host.host

    try:
      with open(host_file, 'w') as f:
        yaml.dump(host, f)
    except Exception as e:
      print(e)
  ui()


if __name__ == '__main__':
  main()
