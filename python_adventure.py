from typing import Any
import re

# Errors
class ConstructionError(Exception):
  pass

# AdventureObject definition (Base Class)
class AdventureObject:
  def __init__(self, **data) -> None:
    self._data = data.copy()
    self._validate()
  
  # def __hash__(self) -> int:
  #   return hash(self.name)
  
  # def __eq__(self, __o: object) -> bool:
  #   return self._data == __o._data
  
  # def __str__(self) -> str:
  #   return "\n" + self._prefix + " " + self.get("name")
    
  # def describe(self, detailed=False) -> None:
  #   print()
  #   print(self.get("prefix") + self.get("name"))
  #   if detailed: print(self.get("desc"))
  
  def __repr__(self) -> str:
    return str(self._data)

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
    
    if not hasattr(self, "prefix"):
      self.set("prefix", "")
  
  # setters and getters
  def get(self, attr) -> Any:
    return self._data[attr]
  
  def set(self, attr, value) -> None:
    self._data[attr] = value
  
  # other base functions

  def id(self) -> str:
    return self.get("name").lower()
  
  def rename(self, name: str) -> None:
    self.set("name", name)


class Clue(AdventureObject):
  def __init__(self, **data) -> None:
    self._required_attrs = [
      ("name", str),
      ("desc", str),
      ("is_item", bool)
    ]

    super().__init__(**data)

    self.set("prefix", "~ ")
    self.set("actions", {})
  
  # def __str__(self) -> str:
  #   return self._prefix + " " + self.get("name")

  def cmd(self, name: str, arg):
    def check(arg=None) -> str:
      return self.get("desc")
    
    if name in locals():
      return locals()[name](arg)
    else:
      return self.get("actions")[name](arg)
  
  # def action(self, cmd_name, *cmd_action: tuple):
  #   exec(f"""def {cmd_name}():\n\t""")

  #   new_action = locals()[cmd_name]

  #   return new_action
  
  def on(self, cmd_name: str, *cmd_actions: str):
    if cmd_name in self.get("actions"):
      print(f"Action '{cmd_name}' already defined.")
    else:
      create_action = f"def {cmd_name}(arg=None):\n\t" + "\n".join(cmd_actions)
      exec(create_action)
      self.get("actions")[cmd_name] = locals()[cmd_name]
    
    return self


class Room(AdventureObject):
  def __init__(self, **data) -> None:
    self._required_attrs = [
      ("name", str),
      ("desc", str),
      ("clues", dict)
    ]

    super().__init__(**data)

    self.set("prefix", "* ")

    self.set("is_default", False)
    self.set("is_open", False)
    self.set("is_locked", False)
  
  def __getitem__(self, key: str) -> Clue:
    return self.get("clues")[key]
  
  def __iter__(self):
    return iter(self.get("clues").values())
  
  # def __str__(self) -> str:
  #   if self._open:
  #     return super().__str__() + "\n" + "\n".join([str(clue) for clue in self])
  #   else:
  #     return super().__str__()
  
  def default(self):
    self.set("is_default", True)
    return self
  
  # def describe(self, detailed=False) -> None:
  #   super().describe(detailed)

  #   for clue in self:
  #     print(clue.get("name"))

  def push(self, clue: Clue) -> Clue:
    self.get("clues").add(clue)
    return clue

  def pop(self, key: str) -> None:
    return self.get("clues").pop(key, None)
  
  # Unopened rooms will not show their clues in the console display
  def open(self):
    self.set("is_open", True)
    return self

  def close(self):
    self.set("is_open", False)
    return self
  
  # Locked rooms cannot be opened until unlocked
  def lock(self):
    self.set("is_locked", True)
    return self

  def unlock(self):
    self.set("is_locked", False)
    return self


class Location(AdventureObject):
  def __init__(self, **data) -> None:
    self._required_attrs = [
      ("name", str),
      ("desc", str),
      ("rooms", dict)
    ]

    super().__init__(**data)

    self.set("prefix", "** ")
    self.set("is_default", False)
  
  def __getitem__(self, key: str) -> Room:
    return self.get("rooms")[key]
  
  def __iter__(self):
    return iter(self.get("rooms").values())
  
  # def __str__(self) -> str:
  #   return super().__str__() + "\n" + "\n".join([str(room) for room in self]) + "\n"
  
  def default(self):
    self.set("is_default", True)
    return self
  
  def get_default(self) -> Room:
    for room in self:
      if room.get("is_default"): return room

  # def describe(self, detailed=False) -> None:
  #   super().describe(detailed)

  #   for room in self:
  #     room.describe()
    
  #   print()


class TextAdventure(AdventureObject):
  def __init__(self, **data) -> None:
    self._required_attrs = [
      ("title", str),
      ("locations", dict)
    ]

    super().__init__(**data)

    self.set("inventory", {})
    self.set_default_location()
    self.set_default_room()
  
  def __call__(self) -> Any:
    player_cmd = self._parse_cmd(input("\n>> "))

    self.cmd(player_cmd["name"], player_cmd["arg"])

    print(self)

    return self()

  def __getitem__(self, key: str) -> Location:
    return self.get("locations")[key]
  
  def __iter__(self):
    return iter(self.get("locations").values())
  
  # def __str__(self) -> str:
  #   return "\n".join([str(location) for location in self]) + "\n"

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
      self.set("current_location", self[location_name])
      self.set_default_room()
      print(f"Going to {location_name}...")
    
    def enter(room_name: str) -> None:
      location_name = self.get("current_location").id()
      self.get("current_room").close()
      self.set("current_room", self[location_name][room_name])
      self.get("current_room").open()

      print(f"Entering {room_name}...")

    def take(clue_name: str) -> None:
      room = self.get("current_room")
      if room[clue_name].get("is_item"):
        self.get("inventory")[clue_name] = room.pop(clue_name)
    
    if name in locals():
      return locals()[name](arg)
    else:
      return None
  
  def get_default_location(self) -> Location:
    for location in self:
      if location.get("is_default"): return location
  
  def get_default_room(self) -> Room:
    for room in self.get("current_location"):
      if room.get("is_default"): return room

  def set_default_location(self) -> None:
    self.set("current_location", self.get_default_location())
  
  def set_default_room(self) -> None:
    self.set("current_room", self.get_default_room())


# clues
cl_old_key = Clue(
  name="Old Key",
  desc="A Key. Looks old.",
  is_item=True
)
cl_stained_wall = Clue(
  name="Stained Wall",
  desc="There's a stain on the wall.",
  is_item=False
)
cl_painting = Clue(
  name="Painting",
  desc="There's a painting of a smol doggo.",
  is_item=False
)
cl_phone = Clue(
  name="Phone",
  desc="It's unplugged.",
  is_item=True
)
cl_dumpster = Clue(
  name="Dumpster",
  desc="For some reason, it's locked.",
  is_item=False
)
cl_snowglobe = Clue(
  name="Snowglobe",
  desc="\'For Melinda\' is engraved on its plaque.",
  is_item=True
)

# rooms
rm_hallway = Room(
  name="Hallway",
  desc="Just a regular old hallway",
  clues={
    cl_phone.id(): cl_phone,
    cl_painting.id(): cl_painting
  }
)
rm_bedroom = Room(
  name="Bedroom",
  desc="Looks like a room. Smells like one too.",
  clues={
    cl_old_key.id(): cl_old_key,
    cl_stained_wall.id(): cl_stained_wall
  }
)
rm_dark_alley = Room(
  name="Dark Alley",
  desc="Well lit, despite the name.",
  clues={
    cl_dumpster.id(): cl_dumpster,
    cl_snowglobe.id(): cl_snowglobe
  }
)

# locations
ln_house = Location(
  name="House",
  desc="Smells like a house.",
  rooms={
    rm_hallway.id(): rm_hallway.default(),
    rm_bedroom.id(): rm_bedroom.lock()
  }
)
ln_street = Location(
  name="Street",
  desc="Looks dark, but it's midday.",
  rooms={
    rm_dark_alley.id(): rm_dark_alley.default()
  }
)

# text adventure
test_adv = TextAdventure(
  title="TITLE",
  locations={
    ln_house.id(): ln_house.default(),
    ln_street.id(): ln_street
  }
)


cl_old_key.on("eat", "print('ate the key')")
cl_old_key.cmd("eat", "")