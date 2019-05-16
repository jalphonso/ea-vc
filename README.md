# Render Jinja2 Template and push to device via Ansible

Builds EVPN configs and pushes to devices

`ansible-playbook -i inventory/MD build_and_deploy_configs.pb.yml`

more examples:
`ansible-playbook -i inventory/MD build_and_deploy_configs.pb.yml -e ansible_python_interpreter=/Users/jalphonso/venv/bin/python`

Added Python CLI to build out yaml files. Still a WIP.

*Requires Python 3.6*

`python cli.py`
