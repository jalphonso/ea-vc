from netaddr import IPAddress
from ruamel.yaml.scalarstring import DoubleQuotedScalarString as dq


class Host(object):
  """
  Host class represents yaml config for host
  """

  def __init__(self, vgw_local_index, mgmt_default_gw):
    self.system_interfaces = []
    self.mgmt_interfaces = []
    self.vgw_local_index = vgw_local_index
    self.mgmt_default_gw = mgmt_default_gw

  def __repr__(self):
    return str(self.host)

  def __str__(self):
    return self.__repr__()

  @property
  def mgmt_default_gw(self):
    return self._mgmt_default_gw

  @mgmt_default_gw.setter
  def mgmt_default_gw(self, mgmt_default_gw):
    if type(mgmt_default_gw) == IPAddress:
      self._mgmt_default_gw = mgmt_default_gw

  @property
  def vgw_local_index(self):
    return self._vgw_local_index

  @vgw_local_index.setter
  def vgw_local_index(self, last_octet):
    if last_octet < 2 or last_octet > 254: raise Exception("vgw must be between 2 and 254 inclusive")
    self._vgw_local_index = last_octet

  def add_system_interface(self, **kwargs):
    new_interface = kwargs
    self.system_interfaces.append(new_interface)

  def add_mgmt_interface(self, **kwargs):
    new_interface = kwargs
    self.mgmt_interfaces.append(new_interface)

  def initialize_underlay(self, asn):
    self.underlay = {
      'asn': dq(asn),
      'neighbors': []
    }

  def initialize_overlay(self, asn, local_ip):
    self.overlay = {
      'local_ip': local_ip,
      'asn': dq(asn),
      'neighbors': []
    }

  def add_underlay_neighbor(self, **kwargs):
    new_neighbor = kwargs
    self.underlay['neighbors'].append(new_neighbor)

  def add_overlay_neighbor(self, **kwargs):
    new_neighbor = kwargs
    self.overlay['neighbors'].append(new_neighbor)

  @property
  def bgp(self):
    self._bgp = {
      'underlay': self.underlay,
      'overlay': self.overlay
    }
    return self._bgp

  @property
  def host(self):
    self._host = {
      'vgw_local_index': self.vgw_local_index,
      'bgp': self.bgp,
      'mgmt_interface': self.mgmt_interfaces,
      'mgmt_default_gw': str(self.mgmt_default_gw),
      'system_interfaces': self.system_interfaces
    }
    return self._host
