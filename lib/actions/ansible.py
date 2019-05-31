from lib.utils.validate import validate_input
import subprocess
import os


def build_configs(args, vc):
  fabric = vc['fabric_name']
  subprocess.call(['ansible-playbook', '-i', 'inventory/dc1', '-e', f"fabric={fabric}", 'render_config.yml'])


def push_change(args, vc):
  fabric = vc['fabric_name']
  user = validate_input("Enter network device username: ", cli_input=args.user)
  passwd = validate_input("Enter network device password: ", input_type="password", cli_input=args.passwd)

  env = os.environ.copy()
  env['ANSIBLE_NET_USERNAME'] = user
  env['ANSIBLE_NET_PASSWORD'] = passwd

  remote_python_interpreter = subprocess.run(['which', 'python'], stdout=subprocess.PIPE).stdout.decode('utf-8')

  subprocess.call(['ansible-playbook', '-i', 'inventory/dc1', '-e',
                   f"fabric={fabric}", '-e', f"ansible_python_interpreter={remote_python_interpreter}",
                   'push_change.yml'], env=env)


def provision_ztp(args, vc):
  ztp_server = vc['ztp_server_ip']
  ztp_subnets = vc['subnets']
  ztp_group = vc['ztp_group']
  subprocess.call(['ansible-playbook', '-i', 'inventory/dc1', '-i', f"{ztp_server},",
                   '-e', f"ztp_server={ztp_server}", '-e', f"ztp_group={ztp_group}",
                   '-e', "{ztp_subnets: %s}" % format(ztp_subnets), 'ztp.yml'])
