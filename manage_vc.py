import argparse
import ruamel.yaml
import sys
from colorama import Fore, Style
from lib.actions import ansible as ansible_actions
from lib.actions import fabric as fabric_actions
from lib.actions import host as host_actions
from lib.actions import switch as switch_actions
from lib.actions import vlan as vlan_actions
from lib.exceptions import exceptions
from lib.utils.validate import validate_input
from pathlib import Path

yaml = ruamel.yaml.YAML()
yaml.indent(sequence=4, offset=2)
yaml.explicit_start = True


def exit(msg):
  print(msg)
  print('Quitting')
  sys.exit(1)

def main():
  oper_choices = ["add_host", "delete_host", "add_vlan", "delete_vlan", "build_configs", "provision_ztp",
                  "push_change"]

  # Top level parser
  parser = argparse.ArgumentParser(description='Execute operation(s)')

  # Top level subparser
  subparsers = parser.add_subparsers(help='choose one of the positional arguments',
                                     dest='{vlan,host,fabric,switch,ansible}')

  # 2nd level parsers
  parser_vlan = subparsers.add_parser('vlan')
  parser_host = subparsers.add_parser('host')
  parser_fabric = subparsers.add_parser('fabric')
  parser_switch = subparsers.add_parser('switch')
  parser_ansible = subparsers.add_parser('ansible')

  # 2nd level subparsers
  subparsers_vlan = parser_vlan.add_subparsers(help='choose one of the positional arguments', dest='{add,del}')
  subparsers_host = parser_host.add_subparsers(help='choose one of the positional arguments', dest='{add,del}')
  subparsers_fabric = parser_fabric.add_subparsers(help='choose one of the positional arguments', dest='{add,del}')

  # required must be set to True and each subparser must have a dest to make sub commands mandatory
  subparsers.required = True
  subparsers_vlan.required = True
  subparsers_host.required = True
  subparsers_fabric.required = True

  # 3rd level parsers
  parser_vlan_add = subparsers_vlan.add_parser('add')
  parser_vlan_delete = subparsers_vlan.add_parser('del')
  parser_host_add = subparsers_host.add_parser('add')
  parser_host_delete = subparsers_host.add_parser('del')
  parser_fabric_add = subparsers_fabric.add_parser('add')
  parser_fabric_delete = subparsers_fabric.add_parser('del')

  # Parser function associations (Sets function to be called per parser)
  parser_vlan_add.set_defaults(func=vlan_actions.add_vlan)
  parser_vlan_delete.set_defaults(func=vlan_actions.delete_vlan)
  parser_host_add.set_defaults(func=host_actions.add_host)
  parser_host_delete.set_defaults(func=host_actions.delete_host)
  parser_fabric_add.set_defaults(func=fabric_actions.add_fabric)
  parser_fabric_delete.set_defaults(func=fabric_actions.delete_fabric)

  # 3rd level vlan parser arguments
  parser_vlan_add.add_argument('--vlan_id', dest='vlan_id', metavar='<vlan_id(s)>', nargs='+',
                               help='provide one or more vlan_id(s)')
  parser_vlan_add.add_argument('--vlan_name', dest='vlan_name', metavar='<vlan_name(s)>', nargs='+',
                               help='provide one or more vlan_name(s) (must have one for each vlan_id)')

  parser_vlan_delete.add_argument('--vlan_id', dest='vlan_id', metavar='<vlan_id>', nargs='+',
                                  help='provide one or more vlan_id(s)')

  # Setup mutually exclusive argument groups for host parser
  group_trunk = parser_host_add.add_mutually_exclusive_group()
  group_jumbo = parser_host_add.add_mutually_exclusive_group()
  group_lag = parser_host_add.add_mutually_exclusive_group()
  group_lacp = parser_host_add.add_mutually_exclusive_group()
  group_lacp_mode = parser_host_add.add_mutually_exclusive_group()
  group_ae_desc = parser_host_add.add_mutually_exclusive_group()
  group_int_desc = parser_host_add.add_mutually_exclusive_group()

  # 3rd level host parser arguments
  parser_host_add.add_argument('--vlan-id', dest='vlan_id', metavar='<vlan_id>', nargs='+',
                               help='provide one or more vlan_id(s)')
  parser_host_add.add_argument('--int', dest='interface', metavar='<interface>', nargs='+',
                               help='provide one or more interface name(s)')
  group_int_desc.add_argument('--int-desc', dest='interface_description', metavar='<interface_description>',
                              help='provide interface description')
  group_int_desc.add_argument('--no-int-desc', dest='interface_description', metavar='<interface_description>',
                              help='provide interface description')
  parser_host_add.add_argument('--ae', dest='ae', metavar='<ae>',
                               help='provide ae id for host lag')
  group_ae_desc.add_argument('--ae-desc', dest='ae_description', metavar='<ae_description>',
                             help='provide ae description for host lag')
  group_ae_desc.add_argument('--no-ae-desc', dest='ae_description', action='store_const',
                             const=" ", metavar='<ae_description>',
                             help='provide ae description for host lag')
  parser_host_add.add_argument('--hostname', dest='hostname', metavar='<hostname>',
                               help='provide hostname of end device')
  parser_host_delete.add_argument('--hostname', dest='hostname', metavar='<hostname>',
                                  help='provide hostname of end device')
  group_trunk.add_argument('--trunk', dest='trunk', action='store_true', default=None,
                           help='enable vlan trunk mode for host')
  group_trunk.add_argument('--access', dest='trunk', action='store_false', default=None,
                           help='enable vlan access mode for host')
  group_jumbo.add_argument('--jumbo', dest='jumbo', action='store_true', default=None,
                           help='enable jumbo frames for host')
  group_jumbo.add_argument('--no-jumbo', dest='jumbo', action='store_false', default=None,
                           help='do not use jumbo frames for host')
  group_lag.add_argument('--lag', dest='lag', action='store_true', default=None,
                         help='enable lag for host')
  group_lag.add_argument('--no-lag', dest='lag', action='store_false', default=None,
                         help='enable lag for host')
  group_lacp.add_argument('--lacp', dest='lacp', action='store_true', default=None,
                          help='enable lacp for host (only applies to lag)')
  group_lacp.add_argument('--no-lacp', dest='lacp', action='store_false', default=None,
                          help='enable lacp for host (only applies to lag)')
  group_lacp_mode.add_argument('--lacp-active', dest='lacp_active', action='store_true', default=None,
                               help='set lacp to active if lacp is enabled for host')
  group_lacp_mode.add_argument('--lacp-passive', dest='lacp_active', action='store_false', default=None,
                               help='set lacp to active if lacp is enabled for host')
  parser_fabric_add.add_argument('--name', dest='fabric', metavar='<fabric name>',
                                 help='set lacp to active if lacp is enabled for host')
  parser_vlan_add.add_argument('--fabric', dest='fabric', metavar='<fabric name>',
                               help='set lacp to active if lacp is enabled for host')
  parser_vlan_delete.add_argument('--fabric', dest='fabric', metavar='<fabric name>',
                               help='set lacp to active if lacp is enabled for host')
  parser_host_add.add_argument('--fabric', dest='fabric', metavar='<fabric name>',
                               help='set lacp to active if lacp is enabled for host')
  parser_host_delete.add_argument('--fabric', dest='fabric', metavar='<fabric name>',
                               help='set lacp to active if lacp is enabled for host')
  args = parser.parse_args()
  print(f"{Fore.YELLOW}Fabric Management Assistant{Style.RESET_ALL}")

  fabric_name = validate_input("Enter fabric name: ", cli_input=args.fabric_name)
  fabric_file = Path("./inventory/dc1/group_vars/" + fabric_name + ".yml")

  try:
    with open(fabric_file) as f:
      vc = yaml.load(f)
      args.func(args, vc)
    with open(fabric_file, 'w') as f:
      yaml.dump(vc, f)
  except FileNotFoundError as e:
    exit(e)
  except exceptions.UnEqualCorrespondingArgs as e:
    exit(e)
  except exceptions.InterfaceAlreadyExists as e:
    exit(e)
  except exceptions.VlanAlreadyExists as e:
    exit(e)
  except AttributeError:
    exit("Feature has probably not been implemented yet")

if __name__ == '__main__':
  main()
