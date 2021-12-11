from typing import Any
import re

# Errors
class ConstructionError(Exception):
  pass

# Parent Class Definition
class AdventureObject:
  def __init__(self, **data) -> None:
    self._data = data.copy()
    self._validate()

    self.is_default = False
  
  # def __hash__(self) -> int:
  #   return hash(self.name)
  
  # def __eq__(self, __o: object) -> bool:
  #   return self._data == __o._data
  
  def __str__(self) -> str:
    return "\n" + self._prefix + " " + self.get("name")
  
  # Validates the object against its own required attributes
  def _validate(self) -> None:
    if hasattr(self, "_required_attrs"):
      for attr in self._required_attrs:
        if not attr[0] in self._data:
          raise ConstructionError(f"{type(self).__name__} object missing attribute {attr[0]}")
        else:
          typ = type(self._data[attr[0]])
          if typ != attr[1]:
            raise ConstructionError(f"Invalid type for \"{attr[0]}\" attribute in {type(self).__name__} object (expected {str(attr[1].__name__)}, got {str(typ.__name__)})")
    
    if not hasattr(self, "_prefix"):
      self._prefix = ""
  
  def default(self):
    self.is_default = True
    return self

  def describe(self) -> None:
    print(self.get("desc"))
  
  def get(self, attr) -> Any:
    return self._data[attr]
  
  def id(self) -> str:
    return self.get("name").lower()
  
  def rename(self, name: str) -> None:
    self._data["name"] = name


class Clue(AdventureObject):
  def __init__(self, **data) -> None:
    self._required_attrs = [
      ("name", str),
      ("desc", str),
      ("is_item", bool)
    ]
    self._prefix = "  ~"

    super().__init__(**data)
  
  def __str__(self) -> str:
    return self._prefix + " " + self.get("name")

  def cmd(self, name: str, arg):
    def check(arg=None) -> str:
      return self.get("desc")
    
    return locals()[name](arg)


class Room(AdventureObject):
  def __init__(self, **data) -> None:
    self._required_attrs = [
      ("name", str),
      ("desc", str),
      ("clues", set)
    ]
    self._prefix = " *"

    self._open = False
    self._unlocked = False

    super().__init__(**data)
  
  def __getitem__(self, key: str) -> Clue:
    for clue in self.get("clues"):
      if clue.id() == key: return clue
    raise KeyError(key)
  
  def __iter__(self):
    return iter(self.get("clues"))
  
  def __str__(self) -> str:
    if self._open:
      return super().__str__() + "\n" + "\n".join([str(clue) for clue in self])
    else:
      return super().__str__()
  
  def push(self, clue: Clue) -> Clue:
    self.get("clues").add(clue)
    return clue

  def pop(self, key: str) -> None:
    for clue in self.get("clues").copy():
      if clue.get("name") == key:
        self.get("clues").remove(clue)
        return clue
  
  # Unopened rooms will not show their clues in the console display
  def open(self):
    self._open = True
    return self

  def close(self):
    self._open = False
    return self
  
  # Locked rooms cannot be opened until unlocked
  def unlock(self):
    self._unlocked = True
    return self


class Location(AdventureObject):
  def __init__(self, **data) -> None:
    self._required_attrs = [
      ("name", str),
      ("desc", str),
      ("rooms", set)
    ]
    self._prefix = "**"
    super().__init__(**data)
  
  def __getitem__(self, key: str) -> Room:
    for room in self.get("rooms"):
      if room.id() == key: return room
    raise KeyError(key)
  
  def __iter__(self):
    return iter(self.get("rooms"))
  
  def __str__(self) -> str:
    return super().__str__() + "\n" + "\n".join([str(room) for room in self]) + "\n"
  
  def get_default(self) -> Room:
    for room in self.get("rooms"):
      if room.is_default: return room


class TextAdventure(AdventureObject):
  def __init__(self, **data) -> None:
    self._required_attrs = [
      ("title", str),
      ("locations", set)
    ]

    super().__init__(**data)

    self._inventory: set = {}
    self._current_location = self.get_default()
    self._current_room = self._current_location.get_default().open()
  
  def __call__(self) -> Any:
    player_input = input("\n>> ")
    return super().__call__(*args, **kwds)

  def __getitem__(self, key: str) -> Location:
    for location in self.get("locations"):
      if location.id() == key: return location
    raise KeyError(key)
  
  def __str__(self) -> str:
    return str(self._current_location)

  # Parses a command and its argument into dict from given input text
  def _parse_cmd(self, cmd_str: str) -> dict:
    cmd_name = re.search("^[a-zA-Z]+", cmd_str)
    cmd_arg = re.search("(?<=[a-zA-Z]\\s)([a-zA-Z]+\\s*)+", cmd_str)

    return {
      "name": cmd_name,
      "arg": cmd_arg
    }

  def cmd(self, name: str, arg):
    def go(location_name: str) -> None:
      self._current_location = self[location_name]
      print(f"Going to {location_name}...")
    
    def enter(room_name: str) -> None:
      self._current_room.close()
      self._current_room = self._current_location[room_name].open()
      print(f"Entering {room_name}...")

    def take(clue_name: str) -> None:
      if self._current_room[clue_name].is_item:
        self._inventory.add(self._current_room.pop(clue_name))
    
    if name in locals():
      return locals()[name](arg)
    else:
      return None

  
  def get_default(self) -> Location:
    for location in self.get("locations"):
      if location.is_default: return location


test_location = Location(
  name="House",
  desc="Smells like a house.",
  rooms={
    Room(
      name="Hallway",
      desc="Just a regular old hallway",
      clues={
        Clue(
          name="Phone",
          desc="It's unplugged.",
          is_item=True
        ),
        Clue(
          name="Painting",
          desc="There's a painting of a smol doggo.",
          is_item=False
        )
      }
    ).unlock().default(),
    Room(
      name="Bedroom",
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

test_adv = TextAdventure(
  title="TITLE",
  locations={
    test_location.default()
  }
)

print(test_adv)
test_adv.cmd("enter", "bedroom")
print(test_adv)

# test_adv.cmd("")