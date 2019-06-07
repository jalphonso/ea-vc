import argparse
import ruamel.yaml
from colorama import Fore, Style
from lib.host_vars.host import Host
from netaddr import IPAddress, IPNetwork
from netaddr.core import AddrFormatError
from pyfiglet import Figlet
from ruamel.yaml.scalarstring import DoubleQuotedScalarString as dq
from lib.utils.validate import validate_input
from lib.utils.update import update
from lib.utils.exit import exit
from lib.utils.unique import is_list_unique
from pathlib import Path
from lib.exceptions.exceptions import UnEqualCorrespondingArgs

yaml = ruamel.yaml.YAML()
yaml.indent(sequence=4, offset=2)
yaml.explicit_start = True

fig = Figlet(width=120)


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

  print(f"{Fore.GREEN}" + fig.renderText("FABRIC ASSISTANT") + f"{Style.RESET_ALL}")

  fabric_type = validate_input("Enter fabric type (vc or ip): ", input_type=list,
                               cli_input=args.fabric_type, choices=['vc', 'ip'])
  if fabric_type == 'ip':
    exit('Fabric type IP has not been implemented yet')

  fabric_name = validate_input("Enter fabric name: ", cli_input=args.fabric_name)
  fabric_file = Path("./inventory/dc1/group_vars/" + fabric_name + ".yml")
  ansible_hosts_file = Path("./inventory/dc1/hosts.yml")

  if fabric_file.is_file():
    exit(f"Fabric with name '{fabric_name}' already exists.")

  try:
    ansible_hosts = yaml.load(ansible_hosts_file)
  except FileNotFoundError:
    ansible_hosts = None

  # create list of all hosts, mgmt_ips, and sns for later use
  all_hosts = []
  all_mgmt_ips = []
  all_sns = []
  if ansible_hosts:
    if 'all' in ansible_hosts:
      ansible_all = ansible_hosts['all']
      if 'children' in ansible_all:
        children = ansible_all['children']
        if 'all_vcs' in children:
          all_vcs = children['all_vcs']
          if 'children' in all_vcs:
            all_vcs_children = all_vcs['children']
            for vc, vc_val in all_vcs_children.items():
              if 'hosts' in vc_val:
                vc_hosts = vc_val['hosts']
                for host, host_val in vc_hosts.items():
                  all_hosts.append(host)
                  if 'ansible_host' in host_val:
                    all_mgmt_ips.append(IPAddress(host_val['ansible_host']))
                  if 'serial_number' in host_val:
                    all_sns.append(str(host_val['serial_number']))

  hosts = validate_input("Enter hostnames of fabric devices: ", cli_input=args.hosts)
  if not args.hosts:
    hosts = hosts.split()
  if not is_list_unique(hosts):
    exit('fabric device names must be unique')
  host_set_diff = set(hosts) - set(all_hosts)
  overlapping_hosts = set(hosts) - host_set_diff
  if overlapping_hosts:
    exit(f"The following device(s) are in use on another fabric: {sorted(list(overlapping_hosts))}\n"
         f"Make sure device hostnames are unique and try again")

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

  ztp_server_ip = str(validate_input(f"Enter ZTP Server IP Address x.x.x.x: ", "IPAddress",
                                     cli_input=args.ztp_server_ip))
  ztp_group = "ztp_group_" + ztp_server_ip.replace(".", "_")

  fabric_data = {'fabric_name': fabric_name, 'ztp_server_ip': ztp_server_ip, 'ztp_group': ztp_group,
                 'subnets': [], 'host_interfaces': [], 'vlans': []}

  for idx, host in enumerate(hosts):
    node_file = Path("./inventory/dc1/host_vars/" + host + ".yml")
    node_id = idx
    neighbor_node_id = 0 if node_id else 1
    vgw_local_index = node_id + 2

    while True:
      serial = validate_input(f"Enter serial number for host {host}: ",
                              cli_input=args.serial[idx] if args.serial else None)
      if serial not in all_sns:
        all_sns.append(serial)
        break
      print(f"{Fore.YELLOW}Serial number is already in use, please check and "
            f"enter the correct unique serial{Style.RESET_ALL}")

    role = validate_input(f"Enter role for host {host} (spine or leaf): ", input_type=list, choices=['spine', 'leaf'],
                          cli_input=args.role[idx] if args.role else None)

    while True:
      mgmt_ip = validate_input(f"Enter management IP for host '{host}' in CIDR format x.x.x.x/x: ", "IPNetwork",
                               cli_input=args.mgmt_ip[idx] if args.mgmt_ip else None)
      if mgmt_ip.ip not in all_mgmt_ips:
        all_mgmt_ips.append(mgmt_ip.ip)
        break
      print(f"{Fore.YELLOW}Mgmt IP is already in use, please check and enter the correct unique IP{Style.RESET_ALL}")

    image = validate_input(f"Enter image for host {host}: ",
                           cli_input=args.image[idx] if args.image else None)
    mgmt_default_gw = mgmt_ip[1]

    ztp_subnet = 'subnet_' + str(mgmt_ip.ip).split('.')[2]
    if ztp_subnet not in fabric_data['subnets']:
      fabric_data['subnets'].append(ztp_subnet)

    new_host = {
      'all':
      {
        'children':
        {
          'all_vcs':
          {
            'children':
            {
              fabric_name:
              {
                'hosts':
                {
                  host:
                  {
                    'ansible_host': str(mgmt_ip.ip),
                    'serial_number': serial
                  }
                }
              }
            }
          },
          ztp_group:
          {
            'children':
            {
              ztp_subnet:
              {
                'hosts':
                {
                  host: None
                }
              }
            }
          }
        }
      }
    }
    if ansible_hosts:
      update(ansible_hosts, new_host)
    else:
      ansible_hosts = new_host

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
    print(f"{Fore.RED}Error writing to ansible hosts file{Style.RESET_ALL}")
    exit(e)

  try:
    yaml.dump(fabric_data, fabric_file)
  except Exception as e:
    print(f"{Fore.RED}Error creating fabric group_vars file {fabric_file}{Style.RESET_ALL}")
    exit(e)

  print(f"{Fore.YELLOW}Fabric {fabric_name} Initialization Complete!{Style.RESET_ALL}")


if __name__ == '__main__':
  main()
