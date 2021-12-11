from typing import Any, Dict, Set


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
  
  def __str__(self) -> str:
    return self._prefix + " " + self.name

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
    if not hasattr(self, "_prefix"):
      self._prefix = ""
  
  def describe(self) -> None:
    print(self.desc)


class Clue(AdventureObject):
  def __init__(self, **data) -> None:
    self._required_attrs = ["name", "desc", "is_item"]
    self._prefix = "~"
    super().__init__(**data)


class Room(AdventureObject):
  def __init__(self, **data) -> None:
    self._required_attrs = ["name", "desc", "clues"]
    self._prefix = "*"
    super().__init__(**data)
  
  def __getitem__(self, key: str) -> Clue:
    for clue in self.clues:
      if clue.name == key: return clue
    raise KeyError(key)
  
  def __iter__(self):
    return iter(self.clues)
  
  # def __str__(self) -> str:
  #   return super().__str__() + "\n" + "\n".join([str(clue) for clue in self])
  
  def add(self, clue: Clue) -> None:
    self.clues.add(clue)

  def remove(self, key: str) -> None:
    for clue in self.clues.copy():
      if clue.name == key:
        self.clues.remove(clue)


class Location(AdventureObject):
  def __init__(self, **data) -> None:
    self._required_attrs = ["name", "desc", "rooms"]
    self._prefix = "**"
    super().__init__(**data)
  
  def __getitem__(self, key: str) -> Clue:
    for room in self.rooms:
      if room.name == key: return room
    raise KeyError(key)
  
  def __iter__(self):
    return iter(self.rooms)
  
  def __str__(self) -> str:
    return super().__str__() + "\n" + "\n".join([str(room) for room in self])


test_location = Location(
  name="A House",
  desc="Smells like a house.",
  rooms={
    Room(
      name="A Room",
      desc="Looks like a room. Smells like one too.",
      clues={
        Clue(
          name="Old Key",
          desc="A Key. Looks old.",
          is_item=True
        ),
        Clue(
          name="Stained Wall",
          desc="There's a stain on the wall.",
          is_item=False
        )
      }
    )
  }
)

print(test_location)
# for room in test_location:
#   print(room)
#   for clue in room:
#     print(clue)