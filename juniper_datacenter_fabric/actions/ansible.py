from juniper_datacenter_fabric.utils.validate import validate_input
import subprocess
import os


def build_configs(args, vc):
  fabric = vc['fabric_name']
  subprocess.call(['ansible-playbook', '-i', 'inventory/dc1/hosts.yml', '-e',
                   f"fabric={fabric}", os.path.dirname(os.path.abspath(__file__)) + '/../playbooks/render_config.yml'])


def push_change(args, vc):
  fabric = vc['fabric_name']
  user = validate_input("Enter network device username: ", cli_input=args.user)
  passwd = validate_input("Enter network device password: ", input_type="password", cli_input=args.passwd)

  env = os.environ.copy()
  env['ANSIBLE_NET_USERNAME'] = user
  env['ANSIBLE_NET_PASSWORD'] = passwd

  remote_python_interpreter = subprocess.run(['which', 'python3'], stdout=subprocess.PIPE).stdout.decode('utf-8')

  subprocess.call(['ansible-playbook', '-i', 'inventory/dc1/hosts.yml', '-e',
                   f"fabric={fabric}", '-e', f"ansible_python_interpreter={remote_python_interpreter}",
                   os.path.dirname(os.path.abspath(__file__)) + '/../playbooks/push_change.yml'], env=env)


def provision_ztp(args, vc):
  #Manually retrieving cwd to set as the inventory dir since the built in var results in a None value
  #for this scenario. Probably due to the ad hoc inventory param
  cwd = os.getcwd()
  ztp_server = vc['ztp_server_ip']
  ztp_subnets = vc['subnets']
  ztp_group = vc['ztp_group']
  subprocess.call(['ansible-playbook', '-i', 'inventory/dc1/hosts.yml', '-i', f"{ztp_server},",
                   '-e', f"ztp_server={ztp_server}", '-e', f"ztp_group={ztp_group}",
                   '-e', "{ztp_subnets: %s}" % format(ztp_subnets),
                   '-e', f"inventory_dir={cwd}/inventory/dc1",
                   os.path.dirname(os.path.abspath(__file__)) + '/../playbooks/ztp.yml'])
