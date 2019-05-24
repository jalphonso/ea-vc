import argparse
import ruamel.yaml
import sys
from colorama import Fore, Style
from lib.host_vars.host import Host
from netaddr import IPAddress, IPNetwork
from netaddr.core import AddrFormatError
from ruamel.yaml.scalarstring import DoubleQuotedScalarString as dq
from lib.utils.validate import validate_input
from lib.utils.unique import is_list_unique
from pathlib import Path
from lib.exceptions.exceptions import UnEqualCorrespondingArgs

yaml = ruamel.yaml.YAML()
yaml.indent(sequence=4, offset=2)
yaml.explicit_start = True


def exit(msg):
  print(msg)
  print('Quitting')
  sys.exit(1)


def main():
  parser = argparse.ArgumentParser(description='Initialize yaml files for devices in fabric')
  parser.add_argument('--name', dest='fabric_name', metavar='<fabric name>',
                      help='provide fabric name')
  parser.add_argument('--type', dest='fabric_type', metavar='<fabric type>', choices=['vc', 'ip'],
                      help='provide fabric type (vc or ip)')
  parser.add_argument('--hosts', dest='hosts', metavar='<hosts>', nargs='+',
                      help='provide list of hosts belonging to this fabric')
  parser.add_argument('--serial', dest='serial', metavar='<serial>', nargs='+',
                      help='provide list of serial numbers for fabric devices (must provide one per device)')
  parser.add_argument('--role', dest='role', metavar='<role>', choices=['spine', 'leaf'], nargs='+',
                      help='provide role for host to be added (spine or leaf)')
  parser.add_argument('--mgmt-ip', dest='mgmt_ip', metavar='<mgmt_ip>', nargs='+',
                      help='provide mgmt_ip in CIDR format x.x.x.x/x')
  parser.add_argument('--image', dest='image', metavar='<junos image>', nargs='+',
                      help='provide junos image filename for each device')
  parser.add_argument('--ztp-ip', dest='ztp_server_ip', metavar='<ztp server ip>',
                      help='provide ztp server ip')
  args = parser.parse_args()

  print(f"{Fore.YELLOW}Fabric Initialization Assistant{Style.RESET_ALL}")

  fabric_type = validate_input("Enter fabric type (vc or ip): ", input_type=list,
                               cli_input=args.fabric_type, choices=['vc', 'ip'])
  if fabric_type == 'ip':
    exit('Fabric type IP has not been implemented yet')

  fabric_name = validate_input("Enter fabric name: ", cli_input=args.fabric_name)
  fabric_file = Path("./inventory/dc1/group_vars/" + fabric_name + ".yml")
  ansible_hosts_file = Path("./inventory/dc1/hosts.yml")

  if fabric_file.is_file():
    exit(f"Fabric with name '{fabric_name}' already exists.")

  hosts = validate_input("Enter hostnames of fabric devices: ", cli_input=args.hosts)
  if not args.hosts:
    hosts = hosts.split()
  if not is_list_unique(hosts):
    exit('fabric device names must be unique')

  try:
    if args.hosts:
      if args.serial:
        if len(args.hosts) != len(args.serial):
          raise UnEqualCorrespondingArgs("When providing hosts and serial arguments the number of each must be equal")
      if args.role:
        if len(args.hosts) != len(args.role):
          raise UnEqualCorrespondingArgs("When providing hosts and role arguments the number of each must be equal")
      if args.mgmt_ip:
        if len(args.hosts) != len(args.mgmt_ip):
          raise UnEqualCorrespondingArgs("When providing hosts and mgmt_ip arguments the number of each must be equal")
      if args.image:
        if len(args.hosts) != len(args.image):
          raise UnEqualCorrespondingArgs("When providing hosts and image arguments the number of each must be equal")
    else:
      args.serial = None
      args.role = None
      args.mgmt_ip = None
      args.image = None
  except UnEqualCorrespondingArgs as e:
    exit(e)

  if fabric_type == 'vc' and len(hosts) > 2:
    exit('Fabric type VC only supports 2 members')

  ztp_server_ip = validate_input(f"Enter ZTP Server IP Address x.x.x.x: ", "IPAddress",
                                 cli_input=args.ztp_server_ip)

  try:
    yaml.dump({'ztp_server_ip': str(ztp_server_ip), 'host_interfaces': [], 'vlans': []}, fabric_file)
  except Exception as e:
    print(f"Error creating fabric group_vars file {fabric_file}")
    exit(e)

  try:
    ansible_hosts = yaml.load(ansible_hosts_file)
  except:
    exit("Unable to load ansible hosts file")

  ansible_hosts['all']['children']['all_vcs']['children'][fabric_name] = {'hosts': {}}
  hosts_sub_yml_fabric = ansible_hosts['all']['children']['all_vcs']['children'][fabric_name]['hosts']
  hosts_sub_yml_switches = ansible_hosts['all']['children']['switches']
  for idx, host in enumerate(hosts):
    node_file = Path("./inventory/dc1/host_vars/" + host + ".yml")
    node_id = idx
    neighbor_node_id = 0 if node_id else 1
    vgw_local_index = node_id + 2
    serial = validate_input(f"Enter serial number for host {host}: ",
                            cli_input=args.serial[idx] if args.serial else None)
    role = validate_input(f"Enter role for host {host} (spine or leaf): ", input_type=list, choices=['spine', 'leaf'],
                          cli_input=args.role[idx] if args.role else None)
    mgmt_ip = validate_input(f"Enter management IP for host '{host}' in CIDR format x.x.x.x/x: ", "IPNetwork",
                             cli_input=args.mgmt_ip[idx] if args.mgmt_ip else None)
    image = validate_input(f"Enter image for host {host}: ",
                           cli_input=args.image[idx] if args.image else None)
    mgmt_default_gw = mgmt_ip[1]
    ztp_subnet = 'subnet_' + str(mgmt_ip.ip)[2]
    try:
      ansible_hosts['all']['children'][ztp_subnet]['hosts'].update({host: None})
    except KeyError:
      ansible_hosts['all']['children'][ztp_subnet] = {'hosts': {host: None}}

    try:
      ztp_subnets = ansible_hosts['all']['vars']['ztp_subnets']
      if ztp_subnet not in ztp_subnets:
        ztp_subnets.append(ztp_subnet)
    except Exception as e:
      exit(e)

    try:
      hosts_sub_yml_switches['hosts'].update({host: None})
    except KeyError:
      hosts_sub_yml_switches = {'hosts': {host: None}}

    hosts_sub_yml_fabric.update({host: {'ansible_host': str(mgmt_ip.ip)}})

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

    host = Host(vgw_local_index, mgmt_default_gw, serial, image, role)
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
      yaml.dump(host, node_file)
    except Exception as e:
      print(e)

  try:
    yaml.dump(ansible_hosts, ansible_hosts_file)
  except Exception as e:
    print("Error writing to ansible hosts file")
    exit(e)


if __name__ == '__main__':
  main()
