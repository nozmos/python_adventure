from typing import Dict


class Clue:
  def __init__(self, **data) -> None:
    self.data = data
    self.name = data.name
    self.desc = data.desc
    self.is_item = data.is_item
  
  def __hash__(self) -> int:
    return hash((self.name, self.desc, self.is_item))
  
  def __eq__(self, __o: object) -> bool:
    return (self.name, self.desc, self.is_item) == (__o.name, __o.desc, __o.is_item)

  def __getattr__(self, attr) -> Any:
    if attr in self.data:
      return self.data[attr]
    else:
      object.__getattr__(attr)


# class Room:
#   def __init__(self, name: str, desc: str, clues: Dict={}) -> None:
#     self.name = name
#     self.desc = desc
#     self.clues = clues.copy()
