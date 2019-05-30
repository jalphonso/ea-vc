from collections.abc import Mapping

def update(d, u):
  """
  Merges dictionary with update dictionary preserving adjacent key/value pairs
  """
  for k, v in u.items():
    if d.get(k) is not None:
      if isinstance(v, Mapping):
          d[k] = update(d.get(k, {}), v)
    else:
      d[k] = v
  return d
