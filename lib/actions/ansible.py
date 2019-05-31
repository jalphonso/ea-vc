import subprocess


def build_configs(args, vc):
  subprocess.call(['ansible-playbook', '-i', 'inventory/dc1', 'render_config.yml'])


def push_change(args, vc):
  subprocess.call(['ansible-playbook', '-i', 'inventory/dc1', 'push_change.yml'])


def provision_ztp(args, vc):
  ztp_server = vc['ztp_server_ip']
  ztp_subnets = vc['subnets']
  ztp_group = vc['ztp_group']
  subprocess.call(['ansible-playbook', '-i', 'inventory/dc1', '-i', f"{ztp_server},",
                   '-e', f"ztp_server={ztp_server}", '-e', f"ztp_group={ztp_group}",
                   '-e', "{ztp_subnets: %s}" % format(ztp_subnets),'ztp.yml'])
