# action plugin for Ansible 2.x
from ansible.plugins.action import ActionBase

class ActionModule(ActionBase):
    def _qfx5(self, task_vars, hostname, result):
        interface_types = ['host_interfaces', 'fabric_interfaces']
        allowed_ports = {"0": None, "4": None, "8": None, "12": None,
                        "16": None, "20": None, "24": None, "28": None,
                        "32": None, "36": None, "40": None, "44": None, 
                        "48": None, "49": None, "50": None, "51": None }
        allowed_ports_list = list(allowed_ports.keys())
        for interface_type in interface_types:
            try:
                for interface in task_vars['hostvars'][hostname][interface_type]:
                    [p_name, pic, port] = interface['name'].split('/')
                    [p_name, fpc] = p_name.split('-')

                    # get port group number
                    if port in allowed_ports_list:
                        port_group = port
                    elif str(int(int(port) / 4) * 4) in allowed_ports_list:
                        port_group = str(int(int(port) / 4) * 4)
                    else:
                        result['failed'] = True
                        result['msg'] = "Invalid port number " + interface['name']
                        return result

                    #print("port: " + port + " port group: " + port_group + " speed: " + interface['speed'])
                    if allowed_ports[port_group] is None:
                        allowed_ports[port_group] = interface['speed']
                    elif allowed_ports[port_group] == interface['speed']:
                        continue
                    else:
                        result['failed'] = True
                        result['msg'] = "Invalid chassis speed: Port group " + fpc + "/" + pic + "/" + port_group + " on " + hostname + " has both " + allowed_ports[port_group] + " and " + interface['speed'] + "."
                        return result
            except:
                continue
        return result
    def _qfx10(self, task_vars, hostname, result):
        interface_types = ['dc_interfaces', 'fabric_interfaces']
        allowed_ports = {"1": None, "5": None, "7": None, "11": None,
                        "13": None, "17": None, "19": None, "23": None,
                        "25": None, "29": None, "31": None, "35": None, 
                        "37": None, "41": None, "43": None, "47": None,
                        "49": None, "53": None, "55": None, "59": None,
                        "61": None, "65": None, "67": None, "71": None}
        allowed_ports_list = list(allowed_ports.keys())
        for interface_type in interface_types:
            try:
                for interface in task_vars['hostvars'][hostname][interface_type]:
                    [p_name, pic, port] = interface['name'].split('/')
                    [p_name, fpc] = p_name.split('-')

                    # only certain ports are allowed to be 100G ports
                    if interface['speed'] == "100g" and not port in allowed_ports_list:
                        result['failed'] = True
                        result['msg'] = "Port " + interface['name'] +" is not a valid 100g port"
                        return result

                    # get port group number
                    if port in allowed_ports_list:
                        port_group = port
                    elif str(int(port) - 1) in allowed_ports_list:
                        port_group = str(int(port) - 1)
                    elif str(int(port) + 1) in allowed_ports_list:
                        port_group = str(int(port) + 1)
                    elif str(int(port) + 2) in allowed_ports_list:
                        port_group = str(int(port) + 2)
                    else:
                        result['failed'] = True
                        result['msg'] = "Invalid port number " + interface['name']
                        return result

                    if allowed_ports[port_group] is None:
                        allowed_ports[port_group] = interface['speed']
                    elif allowed_ports[port_group] == interface['speed']:
                        continue
                    else:
                        result['failed'] = True
                        result['msg'] = "Invalid chassis speed: Port group " + fpc + "/" + pic + "/" + port_group + " has both " + allowed_ports[port_group] + " and " + interface['speed'] + "."
                        return result
            except:
                continue
        return result
    def run (self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()
        result = super(ActionModule, self).run(tmp, task_vars)
        result['changed'] = False
        result['failed'] = False

        inventory_hostname = task_vars.get('inventory_hostname')

        if 'qfx5' in task_vars['hostvars'][inventory_hostname]['platform'].lower():
            self._qfx5(task_vars, inventory_hostname, result)
        elif 'qfx10' in task_vars['hostvars'][inventory_hostname]['platform'].lower():
            self._qfx10(task_vars, inventory_hostname, result)

    
        return result

