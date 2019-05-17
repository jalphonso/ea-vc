# Render Jinja2 Template and push to device via Ansible

Builds EVPN configs and pushes to devices

`ansible-playbook -i inventory/MD build_and_deploy_configs.pb.yml`

more examples:
`ansible-playbook -i inventory/MD build_and_deploy_configs.pb.yml -e ansible_python_interpreter=/Users/jalphonso/venv/bin/python`

Added Python CLI to build out yaml files. Still a WIP.

*Requires Python 3.6*

## Initialize switch with command line options
```
python initialize_switch.py -h
usage: initialize_switch.py [-h] [--hostname <hostname>] [--node_id <node_id>]
                            [--mgmt_ip <mgmt_ip>]

Initialize yaml file for device

optional arguments:
  -h, --help            show this help message and exit
  --hostname <hostname>
                        provide hostname of device
  --node_id <node_id>   provide node id (must be unique per VC) 0 or 1
  --mgmt_ip <mgmt_ip>   provide mgmt_ip in CIDR format x.x.x.x/x
(venv3) jalphonso-mbp:ea-vc jalphonso$ python initialize_switch.py --hostname test0 --node_id 0 --mgmt_ip 192.168.254.27/24
Ansible yaml file creator assistant
```

## Initialize switch interactively
```
python initialize_switch.py
Enter hostname for device: test1
Ansible yaml file creator assistant
Enter node id (must be unique per VC) 0 or 1: 1
Enter management IP in CIDR format x.x.x.x/x: 192.168.254.28/24
```

## Manage VC with command line options
```
python manage_vc.py -o add_vlan --vlan_id 40 50 60 70 80
python manage_vc.py -o delete_host --hostname testdev2
python manage_vc.py -o delete_vlan --vlan_id 40 50

python manage_vc.py -o add_host --vlan_id 100 200 300 --interface xe-2/0/1 xe-2/0/2 --interface_description "testdev4" --hostname testdev4 --jumbo --trunk --lag --ae 5 --ae_description testdev4 --lacp --lacp_active
Ansible operation assistant
Cannot add new host testdev4 because interface xe-2/0/1 already exists for host testdev3
Please fix and try again, Quitting...

python manage_vc.py -o add_host --vlan_id 100 200 300 --interface xe-2/0/3 xe-2/0/4 --interface_description "testdev4" --hostname testdev4 --jumbo --trunk --lag --ae 5 --ae_description testdev4 --lacp --lacp_active
Ansible operation assistant
Cannot add new host testdev4 because interface ae5 already exists for host testdev3
Please fix and try again, Quitting...

python manage_vc.py -o add_host --vlan_id 100 200 300 --interface xe-2/0/3 xe-2/0/4 --interface_description "testdev4" --hostname testdev4 --jumbo --trunk --lag --ae 6 --ae_description testdev4 --lacp --lacp_active
Ansible operation assistant
```

## Manage VC interactively
```
python manage_vc.py
Ansible operation assistant
select operation(s) to run from list
['add_host', 'delete_host', 'add_vlan', 'delete_vlan', 'push_changes']
Type operation you want to run: add_vlan
Enter vlan id: 1234
Do you want to add another one? (y or n): [n]:
```
