from colorama import Fore, Style


class FabricError(Exception):
  """
  baseclass for all exceptions
  """

  def __init__(self, message):
    message = f"{Fore.RED}" + message + f"{Style.RESET_ALL}"
    super().__init__(message)


class InterfaceAlreadyExists(FabricError):
  def __init__(self, message):
    super().__init__(message)


class VlanAlreadyExists(FabricError):
  def __init__(self, message):
    super().__init__(message)


class VlanDoesNotExist(FabricError):
  def __init__(self, message):
    super().__init__(message)


class VlanInUse(FabricError):
  def __init__(self, message):
    super().__init__(message)


class UnEqualCorrespondingArgs(FabricError):
  def __init__(self, message):
    super().__init__(message)


class HostAlreadyExists(FabricError):
  def __init__(self, message):
    super().__init__(message)


class HostDoesNotExist(FabricError):
  def __init__(self, message):
    super().__init__(message)
