import argparse
import ruamel.yaml
import sys
from colorama import Fore, Style
from host import Host
from netaddr import IPAddress, IPNetwork
from netaddr.core import AddrFormatError
from ruamel.yaml.scalarstring import DoubleQuotedScalarString as dq
from lib.utils.validate import validate_input

yaml = ruamel.yaml.YAML()
yaml.indent(sequence=4, offset=2)
yaml.explicit_start = True


def main():
  parser = argparse.ArgumentParser(description='Initialize yaml files for devices in fabric')
  parser.add_argument('--name', dest='fabric_name', metavar='<fabric name>',
                      help='provide fabric name')
  parser.add_argument('--hosts', dest='hosts', metavar='<hosts>', nargs='+',
                      help='provide list of hosts belonging to this fabric')
  parser.add_argument('--role', dest='role', metavar='<role>',
                      help='provide role for host to be added (spine or leaf)')
  parser.add_argument('--mgmt_ip', dest='mgmt_ip', metavar='<mgmt_ip>',
                      help='provide mgmt_ip in CIDR format x.x.x.x/x')
  args = parser.parse_args()


  import sys
  sys.exit()


  fabric_name = validate_input("Enter fabric name: ", cli_input=args.name)
  hosts = validate_input("Enter hostname for device: ", cli_input=args.hosts)
  fabric_file = "./inventory/dc1/group_vars/" + fabric_name + ".yml"
  hosts_file = "./inventory/dc1/hosts.yml"

  for host in hosts:
    node_file = "./inventory/dc1/host_vars/" + host + ".yml"

  try:
    with open(hosts_file) as f:
      host = yaml.load(f)
  except FileNotFoundError:
    print(f"{Fore.YELLOW}Ansible yaml file creator assistant{Style.RESET_ALL}")
    node_id = validate_input("Enter node id (must be unique per VC) 0 or 1: ",
                             int, 0, 1, cli_input=args.node_id)
    neighbor_node_id = 0 if node_id else 1
    vgw_local_index = node_id + 2
    mgmt_ip = validate_input("Enter management IP in CIDR format x.x.x.x/x: ", "IPNetwork",
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
      with open(hosts_file, 'w') as f:
        yaml.dump(host, f)
    except Exception as e:
      print(e)


if __name__ == '__main__':
  main()