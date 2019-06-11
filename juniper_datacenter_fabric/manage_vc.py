# PYTHON_ARGCOMPLETE_OK
import argcomplete
import argparse
import ruamel.yaml

from colorama import Fore, Style
from juniper_datacenter_fabric.actions import ansible as ansible_actions
from juniper_datacenter_fabric.actions import host as host_actions
from juniper_datacenter_fabric.actions import vlan as vlan_actions
from juniper_datacenter_fabric.exceptions import exceptions
from juniper_datacenter_fabric.utils.exit import exit
from juniper_datacenter_fabric.utils.validate import validate_input
from pathlib import Path
from pyfiglet import Figlet

yaml = ruamel.yaml.YAML()
yaml.indent(sequence=4, offset=2)
yaml.explicit_start = True

fig = Figlet(width=120)

# Top level parser
parser = argparse.ArgumentParser(description='Execute operation(s)')

# Top level subparser
subparsers = parser.add_subparsers(help='choose one of the positional arguments',
                                   dest='{vlan,host,ansible}')

# 2nd level parsers
parser_vlan = subparsers.add_parser('vlan')
parser_host = subparsers.add_parser('host')
parser_ansible = subparsers.add_parser('ansible')

# 2nd level subparsers
subparsers_vlan = parser_vlan.add_subparsers(help='choose one of the positional arguments', dest='{add,del}')
subparsers_host = parser_host.add_subparsers(help='choose one of the positional arguments', dest='{add,del}')
subparsers_ansible = parser_ansible.add_subparsers(
    help='choose one of the positional arguments', dest='{build,push,ztp}')

# required must be set to True and each subparser must have a dest to make sub commands mandatory
subparsers.required = True
subparsers_vlan.required = True
subparsers_host.required = True
subparsers_ansible.required = True

# 3rd level parsers
parser_vlan_add = subparsers_vlan.add_parser('add')
parser_vlan_delete = subparsers_vlan.add_parser('del')
parser_host_add = subparsers_host.add_parser('add')
parser_host_delete = subparsers_host.add_parser('del')
parser_ansible_build = subparsers_ansible.add_parser('build')
parser_ansible_push = subparsers_ansible.add_parser('push')
parser_ansible_ztp = subparsers_ansible.add_parser('ztp')

# Parser function associations (Sets function to be called per parser)
parser_vlan_add.set_defaults(func=vlan_actions.add_vlan)
parser_vlan_delete.set_defaults(func=vlan_actions.delete_vlan)
parser_host_add.set_defaults(func=host_actions.add_host)
parser_host_delete.set_defaults(func=host_actions.delete_host)
parser_ansible_build.set_defaults(func=ansible_actions.build_configs)
parser_ansible_push.set_defaults(func=ansible_actions.push_change)
parser_ansible_ztp.set_defaults(func=ansible_actions.provision_ztp)

# 3rd level vlan parser arguments
parser_vlan_add.add_argument('--vlan-id', dest='vlan_id', metavar='<vlan_id(s)>', nargs='+',
                             help='provide one or more vlan_id(s)')
parser_vlan_add.add_argument('--vlan-name', dest='vlan_name', metavar='<vlan_name(s)>', nargs='+',
                             help='provide one or more vlan_name(s) (must have one for each vlan_id)')

parser_vlan_delete.add_argument('--vlan-name', dest='vlan_name', metavar='<vlan_name>', nargs='+',
                                help='provide one or more vlan_name(s)')

# Setup mutually exclusive argument groups for host parser
group_trunk = parser_host_add.add_mutually_exclusive_group()
group_jumbo = parser_host_add.add_mutually_exclusive_group()
group_lag = parser_host_add.add_mutually_exclusive_group()
group_lacp = parser_host_add.add_mutually_exclusive_group()
group_lacp_mode = parser_host_add.add_mutually_exclusive_group()
group_ae_desc = parser_host_add.add_mutually_exclusive_group()
group_int_desc = parser_host_add.add_mutually_exclusive_group()

# 3rd level host parser arguments
parser_host_add.add_argument('--vlan-name', dest='vlan_name', metavar='<vlan_name>', nargs='+',
                             help='provide one or more vlan_name(s)')
parser_host_add.add_argument('--int', dest='interface', metavar='<interface>', nargs='+',
                             help='provide one or more interface name(s)')
group_int_desc.add_argument('--int-desc', dest='interface_description', metavar='<interface_description>',
                            nargs='+', help='provide interface description')
group_int_desc.add_argument('--no-int-desc', dest='interface_description', action='store_const',
                            const=" ", metavar='<disable interface description>',
                            help='disable interface description')
parser_host_add.add_argument('--ae', dest='ae', metavar='<ae>',
                             help='provide ae id for host lag')
group_ae_desc.add_argument('--ae-desc', dest='ae_description', metavar='<ae_description>',
                           help='provide ae description for host lag')
group_ae_desc.add_argument('--no-ae-desc', dest='ae_description', action='store_const',
                           const=" ", metavar='<disable ae interface description>',
                           help='disable ae interface description')
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
                       help='disable lag for host')
group_lacp.add_argument('--lacp', dest='lacp', action='store_true', default=None,
                        help='enable lacp for host (only applies to lag)')
group_lacp.add_argument('--no-lacp', dest='lacp', action='store_false', default=None,
                        help='disable lacp for host (only applies to lag)')
group_lacp_mode.add_argument('--lacp-active', dest='lacp_active', action='store_true', default=None,
                             help='set lacp to active if lacp is enabled for host')
group_lacp_mode.add_argument('--lacp-passive', dest='lacp_active', action='store_false', default=None,
                             help='set lacp to passive if lacp is enabled for host')
parser_vlan_add.add_argument('--fabric', dest='fabric', metavar='<fabric name>',
                             help='specify fabric  name')
parser_vlan_delete.add_argument('--fabric', dest='fabric', metavar='<fabric name>',
                                help='specify fabric  name')
parser_host_add.add_argument('--fabric', dest='fabric', metavar='<fabric name>',
                             help='specify fabric  name')
parser_host_delete.add_argument('--fabric', dest='fabric', metavar='<fabric name>',
                                help='specify fabric  name')
parser_ansible_build.add_argument('--fabric', dest='fabric', metavar='<fabric name>',
                                  help='specify fabric  name')
parser_ansible_push.add_argument('--fabric', dest='fabric', metavar='<fabric name>',
                                 help='specify fabric  name')
parser_ansible_push.add_argument('--user', dest='user', metavar='<username>',
                                 help='specify network device username')
parser_ansible_push.add_argument('--pass', dest='passwd', metavar='<password>',
                                 help='specify network device password')
parser_ansible_ztp.add_argument('--fabric', dest='fabric', metavar='<fabric name>',
                                help='specify fabric  name')
argcomplete.autocomplete(parser)
args = parser.parse_args()


def main():
  print(f"{Fore.GREEN}" + fig.renderText("FABRIC MANAGER") + f"{Style.RESET_ALL}")

  fabric_name = validate_input("Enter fabric name: ", cli_input=args.fabric)
  fabric_file = Path("./inventory/dc1/group_vars/" + fabric_name + ".yml")

  try:
    vc = yaml.load(fabric_file)
    args.func(args, vc)
    yaml.dump(vc, fabric_file)
    print(f"{Fore.YELLOW}Operation {args.func.__name__} Complete!{Style.RESET_ALL}")
  except FileNotFoundError as e:
    exit(e)
  except exceptions.FabricError as e:
    exit(e)
  except AttributeError:
    exit("Feature has probably not been implemented yet")


if __name__ == '__main__':
  main()
