from typing import Any


# Errors
class ConstructionError(Exception):
  pass

# Parent Class Definition
class AdventureObject:
  def __init__(self, **data) -> None:
    self._data = data
    self._validate()
  
  def __hash__(self) -> int:
    return hash(self.name)
  
  def __eq__(self, __o: object) -> bool:
    return self._data == __o._data

  def __getattr__(self, attr) -> Any:
    if attr[0] != "_":
      return self._data[attr]
    else:
      object.__getattr__(attr)
  
  def _validate(self) -> None:
    if hasattr(self, "_required_attrs"):
      missing_attrs = []
      for attr in self._required_attrs:
        if not attr in self._data:
          missing_attrs.append(attr)
      if len(missing_attrs) > 0:
        raise ConstructionError(f"{type(self).__name__} object missing required attributes {str(missing_attrs)}")


class Clue(AdventureObject):
  def __init__(self, **data) -> None:
    self._required_attrs = ["name", "desc", "is_item"]
    super().__init__(**data)


class Room(AdventureObject):
  def __init__(self, **data) -> None:
    self._required_attrs = ["name", "desc", "clues"]
    super().__init__(**data)
  
  def __getitem__(self, key) -> Clue:
    return self.clues[key]
  
  # def __iter__(self) 


test_clue = Clue(name="CLUE_NAME", desc="CLUE_DESC", is_item=True)

test_room = Room(
  name="ROOM_NAME",
  desc="ROOM_DESC",
  clues={
    "clue 1": Clue(name="clue 1", desc="the first clue", is_item=True)
  }
)

print(test_room["clue 1"].desc)