from typing import Any, Dict, Set


# Errors
class ConstructionError(Exception):
  pass

# Parent Class Definition
class AdventureObject:
  def __init__(self, **data) -> None:
    self._data = data
    self._validate()
  
  # def __hash__(self) -> int:
  #   return hash(self.name)
  
  # def __eq__(self, __o: object) -> bool:
  #   return self._data == __o._data
  
  def __str__(self) -> str:
    return self._prefix + " " + self.name

  def __getattr__(self, attr) -> Any:
    if attr in self._required_attrs:
      return self._data[attr]
    else:
      return object.__getattr__(attr)
  
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
  
  def cmd(self, name: str, *args):
    def check(arg=None) -> str:
      return self.desc
    
    return locals()[name](*args)


class Room(AdventureObject):
  def __init__(self, **data) -> None:
    self._required_attrs = ["name", "desc", "clues"]
    self._prefix = "*"

    self._open = False
    self._unlocked = False

    super().__init__(**data)
  
  def __getitem__(self, key: str) -> Clue:
    for clue in self.clues:
      if clue.name == key: return clue
    raise KeyError(key)
  
  def __iter__(self):
    return iter(self.clues)
  
  def __str__(self) -> str:
    if self._open:
      return super().__str__() + "\n" + "\n".join([str(clue) for clue in self])
    else:
      return super().__str__()
  
  def cmd(self, name: str, *args):
    def take(clue_name: str) -> Clue:
      if self[clue_name].is_item:
        return self.pop(clue_name)
      else:
        return None
    
    return locals()[name](*args)
  
  def push(self, clue: Clue) -> Clue:
    self.clues.add(clue)
    return clue

  def pop(self, key: str) -> None:
    for clue in self.clues.copy():
      if clue.name == key:
        self.clues.remove(clue)
        return clue
  
  def open(self):
    self._open = True
  
  def unlock(self):
    self._unlocked = True
    return self


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


class TextAdventure(AdventureObject):
  def __init__(self, **data) -> None:
    self._required_attrs = ["locations"]

    super().__init__(**data)
  
  def cmd(self, name: str, *args):
    pass


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
    ).unlock()
  }
)

print(test_location["A Room"])
print()

test_location["A Room"].open()
print(test_location["A Room"])
print()

test_location["A Room"].cmd("take", "Stained Wall")
print(test_location["A Room"])
print()