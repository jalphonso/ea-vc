from lib.exceptions import exceptions


def add_unique_interface(interface_list, new_interface):
  for d in interface_list:
    if d['name'] == new_interface['name']:
      raise exceptions.InterfaceAlreadyExists(f"Cannot add new host {new_interface['tag']} "
                                              f"because interface {new_interface['name']} "
                                              f"already exists for host {d['tag']}")
  interface_list.append(new_interface)


def add_unique_vlan(vlan_list, new_vlan):
  for d in vlan_list:
    if d['id'] == new_vlan['id']:
      raise exceptions.VlanAlreadyExists(f"Cannot add new vlan {new_vlan['name']} "
                                         f"for vlan id {new_vlan['id']} because "
                                         f"vlan already exists with name {d['name']}")
  vlan_list.append(new_vlan)
