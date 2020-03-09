from juniper_datacenter_fabric.exceptions import exceptions
from juniper_datacenter_fabric.utils.unique import add_unique_vlan
from juniper_datacenter_fabric.utils.validate import validate_str, validate_int


def add_vlan(args, vc):
  def _add_vlan(vlan_id=None, vlan_name=None, vlan_description=None):
    vlan = validate_int("Enter vlan id: ", 1, 4094, cli_input=vlan_id)
    vlan_name = validate_str("Enter vlan name: ", cli_input=vlan_name, default="vlan."+str(vlan))
    vlan_descr = validate_str("Enter vlan description: ", cli_input=vlan_description, default="")
    vlan_yml = {
      'name': vlan_name,
      'id': vlan,
      'description': vlan_descr
    }
    add_unique_vlan(vc['vlans'], vlan_yml)
    vc['vlans'] = sorted(vc['vlans'], key=lambda x: x['id'])

  if args.vlan_id and args.vlan_name:
    if len(args.vlan_id) != len(args.vlan_name):
      raise exceptions.UnEqualCorrespondingArgs("If providing both vlan_id and vlan_name arguments, "
                                                "the number of ids and names must be equal")
    for idx, vlan_id in enumerate(args.vlan_id):
      _add_vlan(vlan_id, args.vlan_name[idx], args.vlan_description[idx])
  elif args.vlan_id:
    for vlan_id in args.vlan_id:
      _add_vlan(vlan_id)
  else:
    _add_vlan()


def delete_vlan(args, vc):
  def _delete_vlan(vlan_name=None):
    vlan = validate_str("Enter vlan name: ", cli_input=vlan_name)

    # check to see if vlan is in use on any hosts
    if vlan in vlan_on_hosts:
      raise exceptions.VlanInUse(f"vlan named {vlan} is in use on one or more hosts. "
                                 f"Please remove the vlan from all hosts first")

    # check to see if vlan exists in fabric before removing it
    existing_vlans = [v['name'] for v in vc['vlans']]
    if vlan not in existing_vlans:
      raise exceptions.VlanDoesNotExist(f"Vlan named {vlan} does not exist in fabric {vc['fabric_name']}")
    vc['vlans'][:] = [x for x in vc['vlans'] if x['name'] != vlan]

  # build list of vlans in use by hosts
  vlan_on_hosts = set()
  for host in vc['host_interfaces']:
    if 'vlan' in host:
      for vlan in host['vlan']:
        vlan_on_hosts.add(vlan)

  if args.vlan_name:
    for vlan_name in args.vlan_name:
      _delete_vlan(vlan_name)
  else:
    _delete_vlan()
