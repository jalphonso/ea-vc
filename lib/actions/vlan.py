from lib.exceptions import exceptions
from lib.utils.unique import add_unique_vlan
from lib.utils.validate import validate_input


def add_vlan(args, vc):
  def _add_vlan(vlan_id=None, vlan_name=None):
    vlan = validate_input("Enter vlan id: ", int, 1, 4094, cli_input=vlan_id)
    vlan_name = validate_input("Enter vlan name: ", cli_input=vlan_name, default="vlan."+str(vlan))
    vlan_yml = {
      'name': vlan_name,
      'id': vlan
    }
    add_unique_vlan(vc['vlans'], vlan_yml)
    vc['vlans'] = sorted(vc['vlans'], key=lambda x: x['id'])

  if args.vlan_id and args.vlan_name:
    if len(args.vlan_id) != len(args.vlan_name):
      raise exceptions.UnEqualCorrespondingArgs("If providing both vlan_id and vlan_name arguments, "
                                                "the number of ids and names must be equal")
    for idx, vlan_id in enumerate(args.vlan_id):
      _add_vlan(vlan_id, args.vlan_name[idx])
  elif args.vlan_id:
    for vlan_id in args.vlan_id:
      _add_vlan(vlan_id)
  else:
    _add_vlan()


def delete_vlan(args, vc):
  def _delete_vlan(vlan_id):
    vlan = validate_input("Enter vlan id: ", int, 1, 4094, cli_input=vlan_id)
    vc['vlans'][:] = [x for x in vc['vlans'] if x['id'] != vlan]

  if args.vlan_id:
    for vlan_id in args.vlan_id:
      _delete_vlan(vlan_id)
  else:
    _delete_vlan(None)
