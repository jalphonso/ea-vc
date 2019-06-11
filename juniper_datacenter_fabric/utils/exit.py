from colorama import Fore, Style
import sys


def exit(msg):
  print(f"{Fore.RED}{msg}\nQuitting{Style.RESET_ALL}")
  sys.exit(1)
