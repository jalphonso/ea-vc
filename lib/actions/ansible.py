import subprocess


def build_configs(args, vc):
  subprocess.call(['ansible-playbook', '-i', 'inventory/dc1', 'render_config.yml'])


def push_change(args, vc):
  subprocess.call(['ansible-playbook', '-i', 'inventory/dc1', 'push_change.yml'])


def provision_ztp(args, vc):
  subprocess.call(['ansible-playbook', '-i', 'inventory/dc1', 'ztp.yml'])
