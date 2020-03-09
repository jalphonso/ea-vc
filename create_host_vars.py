# PYTHON_ARGCOMPLETE_OK
import argcomplete
import argparse
import juniper_datacenter_fabric.about as about
import sys
import ruamel.yaml

from colorama import Fore, Style
from netaddr import IPAddress, IPNetwork
from netaddr.core import AddrFormatError
from pyfiglet import Figlet
from ruamel.yaml.scalarstring import DoubleQuotedScalarString as dq
from juniper_datacenter_fabric.host_vars.host import Host
from juniper_datacenter_fabric.utils.validate import validate_choice, validate_str, validate_ip_address, validate_ip_network
from juniper_datacenter_fabric.utils.update import update
from juniper_datacenter_fabric.utils.exit import exit
from juniper_datacenter_fabric.utils.unique import is_list_unique
from pathlib import Path
from juniper_datacenter_fabric.exceptions.exceptions import UnEqualCorrespondingArgs, FabricError

yaml = ruamel.yaml.YAML()
yaml.indent(sequence=4, offset=2)
yaml.explicit_start = True

fig = Figlet(width=120)

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
parser.add_argument('--version', dest='version', action='store_true', default=False,
                    help='print version and exit')
parser.add_argument('--ztp-ip', dest='ztp_server_ip', metavar='<ztp server ip>',
                    help='provide ztp server ip')
argcomplete.autocomplete(parser)
args = parser.parse_args()


str(validate_ip_address(f"Enter ZTP Server IP Address x.x.x.x: "))
