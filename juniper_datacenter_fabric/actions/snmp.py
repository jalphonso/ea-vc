import os
import ruamel.yaml
import subprocess
from colorama import Fore, Style
from jnpr.junos import Device
from jnpr.junos.exception import ConnectError, ProbeError, ConnectAuthError
from lxml import etree
from juniper_datacenter_fabric.utils.exit import exit
from juniper_datacenter_fabric.utils.unique import add_unique_snmp_user
from juniper_datacenter_fabric.utils.validate import validate_str, validate_password
from pathlib import Path

def snmp_init(args, vc):
    # Initial questions
    user = validate_str("Enter network device username: ", cli_input=args.user)
    passwd = validate_password("Enter network device password: ", cli_input=args.passwd)

    # push initial snmp configuration
    fabric = vc['fabric_name']
    env = os.environ.copy()
    env['ANSIBLE_NET_USERNAME'] = user
    env['ANSIBLE_NET_PASSWORD'] = passwd
    remote_python_interpreter = subprocess.run(['which', 'python3'], stdout=subprocess.PIPE).stdout.decode('utf-8')

    subprocess.call(['ansible-playbook', '-i', 'inventory/dc1/hosts.yml', 
                '-e', f"fabric={fabric}",
                '-e snmp_template=snmp_init',
                '-e', f"ansible_python_interpreter={remote_python_interpreter}",
                "--ask-vault-pass",
                os.path.dirname(os.path.abspath(__file__)) + '/../playbooks/snmp.yml'],
                env=env)

    retrieve_snmp_hash(vc, user, passwd)

def get_snmp_hash(args, vc):
    # Initial questions
    user = validate_str("Enter network device username: ", cli_input=args.user)
    passwd = validate_password("Enter network device password: ", cli_input=args.passwd)
    retrieve_snmp_hash(vc, user, passwd)
    
def push_snmp_hash(args,vc):
    # Initial questions
    user = validate_str("Enter network device username: ", cli_input=args.user)
    passwd = validate_password("Enter network device password: ", cli_input=args.passwd)

    # push snmp with hashes
    fabric = vc['fabric_name']
    env = os.environ.copy()
    env['ANSIBLE_NET_USERNAME'] = user
    env['ANSIBLE_NET_PASSWORD'] = passwd
    remote_python_interpreter = subprocess.run(['which', 'python3'], stdout=subprocess.PIPE).stdout.decode('utf-8')

    subprocess.call(['ansible-playbook', '-i', 'inventory/dc1/hosts.yml', 
                '-e', f"fabric={fabric}", 
                '-e snmp_template=snmp_hash',
                '-e', f"ansible_python_interpreter={remote_python_interpreter}",
                os.path.dirname(os.path.abspath(__file__)) + '/../playbooks/snmp.yml'],
                env=env)

def retrieve_snmp_hash(vc, username, passwd):
    yaml = ruamel.yaml.YAML()
    yaml.indent(sequence=4, offset=2)
    yaml.explicit_start = True

    # discover hosts in fabric
    host_file = Path("./inventory/dc1/hosts.yml")
    hosts = yaml.load(host_file)
    if 'lg' in vc['fabric_name']:
        vc_hosts = hosts['all']['children']['leaf']['children'][vc['fabric_name']]['hosts']
    else:
        vc_hosts = hosts['all']['children'][vc['fabric_name']]['hosts']

    for host in vc_hosts:
        print(f"{Fore.YELLOW}Getting snmp hashes from {host}{Style.RESET_ALL}")
        host_vars_file = Path("./inventory/dc1/host_vars/" + host + ".yml")
        host_vars = yaml.load(host_vars_file)

        # log in to device
        try:
            with Device(host=host, user=username, password=passwd) as dev:
                config = dev.rpc.get_config(options={'format':'text'})
        except ConnectAuthError as err:
            exit(f"Unable to login. Check username/password: {err}")
        except (ProbeError, ConnectError) as err:
            exit(f"Cannot connect to device: {err}\nMake sure device is reachable and "
              f"'set system services netconf ssh' is set")
        except Exception as err:
            exit(f"Abnormal termination: {err.__class__.__name__, err}")

        # Get SNMP user information and write to host_vars
        lines = etree.tostring(config, encoding='unicode')
        try:
            snmp_users = lines.split('snmp {')[1].split('local-engine')[1].split('vacm')[0]
            for idx in range(0,snmp_users.count('user')):
                user = snmp_users.split('user ')[idx+1].split(' ')[0]
                auth_key = snmp_users.split('authentication-key ')[idx+1].split(';')[0]
                priv_key = snmp_users.split('privacy-key ')[idx+1].split(';')[0]
                snmp_user_yml = {
                    'user': user,
                    'auth_key': auth_key,
                    'priv_key': priv_key
                }
                if 'snmp_encrypted' in host_vars:
                    add_unique_snmp_user(host_vars['snmp_encrypted'], snmp_user_yml)
                else:
                    host_vars['snmp_encrypted'] = [snmp_user_yml]
                    yaml.dump(host_vars, host_vars_file)
        except:
            print(f"No snmp users found on {host}")
        yaml.dump(host_vars, host_vars_file)

