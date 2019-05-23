class FabricError(Exception):
  """
  baseclass for all exceptions
  """
  pass


class InterfaceAlreadyExists(FabricError):
  def __init__(self, message):
    super().__init__(message)


class VlanAlreadyExists(FabricError):
  def __init__(self, message):
    super().__init__(message)


class UnEqualCorrespondingArgs(FabricError):
  def __init__(self, message):
    super().__init__(message)
