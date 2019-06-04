from lib.exceptions import exceptions


def add_unique_interface(interface_list, new_interface):
  for d in interface_list:
    if d['name'] == new_interface['name']:
      raise exceptions.InterfaceAlreadyExists(
        f"Cannot add new host {new_interface['tag']} "
        f"because interface {new_interface['name']} "
        f"already exists for host {d['tag']}"
      )
  interface_list.append(new_interface)


def add_unique_vlan(vlan_list, new_vlan):
  for d in vlan_list:
    if d['id'] == new_vlan['id']:
      raise exceptions.VlanAlreadyExists(
        f"Cannot add new vlan {new_vlan['name']} "
        f"for vlan id {new_vlan['id']} because "
        f"vlan already exists with name {d['name']}"
      )
  vlan_list.append(new_vlan)


def host_is_unique_or_error(host_list, new_host, fabric):
  for d in host_list:
    if d['tag'] == new_host:
      raise exceptions.HostAlreadyExists(
          f"Host {new_host} already exists in "
          f"Fabric {fabric}.\nIf this is another "
          f"group of interfaces for the same host,\n"
          f"then just ensure the tag (hostname) is unique "
          f"when adding thru this tool.\ni.e. hostname-eth1 "
          f"or hostname-mgmt or hostname-data"
      )
  return True


def is_list_unique(l):
  seen = set()
  return not any(i in seen or seen.add(i) for i in l)
