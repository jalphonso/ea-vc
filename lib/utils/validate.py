import re
import sys
from netaddr import IPAddress, IPNetwork
from netaddr.core import AddrFormatError
from getpass import getpass


def validate_input(prompt, input_type=str, input_min=None, input_max=None, cli_input=None, default=None, choices=None):
  max_tries = 5
  tries = 0
  if default is not None:
    if default is False:
      print_default = 'n'
    elif default is True:
      print_default = 'y'
    else:
      print_default = default
    prompt = prompt + "[" + str(print_default) + "]: "
  while True and tries < max_tries:
    if cli_input is None:
      if input_type == "password":
        passwd = getpass(prompt).strip()
        if passwd:
          passwd_confirm = getpass("Confirm your password: ").strip()
          if passwd == passwd_confirm:
            user_input = passwd
            break
          else:
            print("Passwords do not match, please try again...")
            continue
        else:
          print("Password cannot be blank, please try again...")
          continue
      else:
        user_input = input(prompt).strip()
    else:
      user_input = cli_input
      cli_input = None
    if input_type == bool and type(user_input) == bool:
      break
    elif not user_input:
      if default is None:
        print("Input cannot be blank, please try again")
      else:
        user_input = default
        break
    elif input_type == int:
      try:
        user_input = int(user_input)
      except ValueError:
        print("Input needs to be an integer, please try again")
        tries += 1
        continue
      if input_min and input_max and input_min < input_max:
        if user_input < input_min or user_input > input_max:
          print(f"Input needs to between {input_min} and {input_max}, please try again")
        else:
          break
      elif input_min and user_input < input_min:
        print(f"Input needs to be greater than or equal to {input_min}, please try again")
      elif input_max and user_input > input_max:
        print(f"Input needs to be less than or equal to {input_max}, please try again")
      else:
        break
    elif input_type == bool:
      bool_char = user_input.lower()
      if bool_char == 'y' or bool_char == 'yes':
        user_input = True
        break
      elif bool_char == 'n' or bool_char == 'no':
        user_input = False
        break
      else:
        print(f"Input needs to be yes/no or y/n, please try again")
    elif input_type == list:
      if user_input in choices:
        break
      else:
        print(f"Selection must be one of the following {choices}")
    elif input_type == 'IPAddress':
      try:
        if len(user_input.split('.')) != 4:
          raise ValueError("Not a properly formatted IP Address x.x.x.x")
        user_input = IPAddress(user_input)
        break
      except (ValueError, AddrFormatError) as e:
        print(e)
    elif input_type == 'IPNetwork':
      try:
        if len(user_input.split('.')) != 4 or '/' not in user_input:
          raise ValueError("Not a properly formatted IP/CIDR x.x.x.x/x")
        user_input = IPNetwork(user_input)
        break
      except (ValueError, AddrFormatError) as e:
        print(e)
    elif input_type == 'Interface':
      if re.match(r"(ge|xe|et)-0/0/(\d|[0-4]\d|5[0-1])$", user_input):
        break
      else:
        print("Interface format must be <type>-0/0/x where type is ge, xe, or et")
        print("5120 model supported range is from 0/0/0 thru 0/0/51 for hosts")
    else:
      break
    tries += 1
  if tries == max_tries:
    print("Reached maximum attempts to validate input, quitting...")
    sys.exit(1)
  return user_input
