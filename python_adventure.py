from typing import Any, Union
import re

HELP = """
# COMMANDS (case-insensitive) #

help          - display help menu
quit          - quit game
go [place]    - go to a location or room
check [clue]  - investigate a clue
take [clue]   - take a clue if possible
map           - see available locations
where am I    - see available rooms
look around   - investigate current room"""

# Errors
class ConstructionError(Exception):
  pass

# AdventureObject definition (Base Class)
class AdventureObject:
  def __init__(self, **data) -> None:
    self._data = data.copy()
    self._validate()
  
  # def __hash__(self) -> int:
  #   return hash(self._data.values())
  
  def __eq__(self, __o: object) -> bool:
    return self.id() == __o.id()
    # for key in self._data:
    #   if key not in __o._data:
    #     print(f"key not found in target object: {key}")
    #     return False
    #   if type(self._data[key]) != dict:
    #     if self._data[key] != __o._data[key]:
    #       print(f"value mismatch in target object: {key}")
    #       return False
    # return True
  
  # def __str__(self) -> str:
  #   return "\n" + self._prefix + " " + self.get("name")
  
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
  
  # used for key indexing
  def id(self) -> str:
    return self.get("name").lower()
  
  def rename(self, name: str) -> None:
    self.set("name", name)
  
  def describe(self, is_current=False, include_details=False) -> str:
    current = " (current)" if is_current else ""
    details = "\n" + self.get("desc") if include_details else ""
    return self.get("prefix") + self.get("name") + current + details


class Clue(AdventureObject):
  def __init__(self, **data) -> None:
    self._required_attrs = [
      ("name", str),
      ("desc", str),
      ("is_item", bool)
    ]

    super().__init__(**data)

    self.set("prefix", "~ ")
    # self.set("actions", [])
  
  # def __str__(self) -> str:
  #   return self._prefix + " " + self.get("name")

  # def cmd(self, name: str, arg):
  #   def check(arg=None) -> str:
  #     return self.get("desc")
    
  #   if name in locals():
  #     return locals()[name](arg)
  #   else:
  #     return self.get("actions")[name](arg)
  
  # def action(self, cmd_name, *cmd_action: tuple):
  #   exec(f"""def {cmd_name}():\n\t""")

  #   new_action = locals()[cmd_name]

  #   return new_action
  
  # def on(self, cmd_name: str, *cmd_actions: str):
  #   if cmd_name in self.get("actions"):
  #     print(f"Action '{cmd_name}' already defined.")
  #   else:
  #     create_action = f"def {cmd_name}(arg=None):\n\t" + "\n".join(cmd_actions)
  #     exec(create_action)
  #     self.get("actions")[cmd_name] = locals()[cmd_name]
    
  #   return self

  def unlocks_room(self, room_id: str):
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
    clues = self.get("clues")
    if key in clues:
      return clues[key]
    else:
      return None
  
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
    self.get("clues")[clue.id()] = clue
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
  
  def describe(self, is_current=False, include_details=False, include_clues=False) -> str:
    output = super().describe(is_current, include_details)

    if not include_clues:
      return output
    else:
      clue_names = [clue.get("prefix") + clue.get("name") for clue in self]
      return output + "\n\n" + "\n".join(clue_names)



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
    rooms = self.get("rooms")
    if key in rooms:
      return rooms[key]
    else:
      return None
  
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
  
  def push(self, room: Room) -> Room:
    self.get("rooms")[room.id()] = room
    return room

  def describe(self, is_current=False, include_details=False, include_rooms=False) -> str:
    output = super().describe(is_current, include_details)

    if not include_rooms:
      return output
    else:
      room_names = [room.get("name") for room in self]
      return output + "\n\n" + "\n".join(room_names)


class TextAdventure(AdventureObject):
  def __init__(self, **data) -> None:
    self._required_attrs = [
      ("title", str),
      ("locations", dict)
    ]

    super().__init__(**data)

    self.set("inventory", {})
    self.set("actions", {})
    self.update_default_location()
    self.update_default_room()
  
  def __call__(self, display_help=False) -> Any:
    if display_help:
      print(self.cmd("help"))

    player_cmd = self._parse_cmd(input("\n>> "))
    cmd = self.cmd(player_cmd["name"], player_cmd["arg"])

    if player_cmd["name"] == "quit":
      quit()
    elif player_cmd is not None and cmd is not None:
      print(cmd)
    else:
      print("Invalid command. Type 'help' for a list of valid commands.")

    return self()

  def __getitem__(self, key: str) -> Location:
    locations = self.get("locations")
    if key in locations:
      return locations[key]
    else:
      return None
  
  def __iter__(self):
    return iter(self.get("locations").values())
  
  # def __str__(self) -> str:
  #   return "\n".join([str(location) for location in self]) + "\n"

  # Parses a command and its argument into dict from given input text
  def _parse_cmd(self, cmd_str: str) -> dict:
    cmd_name = re.search("^[a-zA-Z]+", cmd_str)
    cmd_arg = re.search("(?<=[a-zA-Z]\\s)([a-zA-Z]+\\s*)+", cmd_str)

    if cmd_name is not None:
      cmd_arg = "" if cmd_arg is None else cmd_arg.group()
      return {
        "name": cmd_name.group().lower(),
        "arg": cmd_arg.lower()
      }
    else:
      return {
        "name": None,
        "arg": None
      }

  def cmd(self, name: str, arg=None) -> str:
    # def _init(arg=None) -> None:
    #   for cmd_name in locals():
    #     self.get("actions").append(cmd_name)
    
    def quit(arg=None) -> str:
      return "Exiting..."
    
    def help(arg=None) -> str:
      return HELP
    
    def map(arg=None) -> str:

      location_names = []
      for location in self:
        if location.id() == self.get("current_location").id():
          location_names.append(location.describe(is_current=True))
        else:
          location_names.append(location.describe())
      
      return "\n".join(location_names)
    
    def where(arg=None) -> str:
      location = self.get('current_location')

      room_names = []
      for room in self[location.id()]:
        if room.id() == self.get("current_room").id():
          room_names.append(room.describe(is_current=True))
        else:
          room_names.append(room.describe())
      
      return location.describe(include_details=True) + "\n\n" + "\n".join(room_names)

    def look(arg=None) -> str:
      room = self.get("current_room")
      clue_names = [clue.describe() for clue in room]
      
      return room.describe(include_details=True) + "\n\n" + "\n".join(clue_names)

    def bag(arg=None) -> str:
      if len(self.get("inventory")) == 0:
        return "Your bag is empty."
      else:
        item_names = [item.describe() for item in self.get("inventory").values()]
        return "\n".join(item_names)

    def check(clue_name: str) -> str:
      room = self.get("current_room")
      clue = None

      if clue_name in room.get("clues"):
        clue = room[clue_name]
      elif clue_name in self.get("inventory"):
        clue = self.get("inventory")[clue_name]
      
      if clue is not None:
        return clue.get("desc")
      else:
        return "You see no clues of that description."

    def go(place_name: str) -> str:
      current_location = self.get("current_location")
      current_room = self.get("current_room")

      if place_name == current_location.id() or place_name == current_room.id():
        return "You are already at that location."

      elif place_name in current_location.get("rooms"):
        location_name = current_location.id()
        room = self[location_name][place_name]

        if room.get("is_locked"):
          return f"The {place_name} is locked."

        # self.get("current_room").close()
        self.set("current_room", room)
        # self.get("current_room").open()

        return f"Entering {place_name}..."
      
      elif place_name in self.get("locations"):
        self.set("current_location", self[place_name])
        self.update_default_room()

        return f"Travelling to {place_name}..."
      
      else:
        return "That location does not exist."

    def take(clue_name: str) -> str:
      room = self.get("current_room")
      clue = room[clue_name]
      
      if clue is not None:
        if clue.get("is_item"):
          self.get("inventory")[clue_name] = room.pop(clue_name)
        
          return f"You take the {clue_name}."
        else:
          return f"You can't find a way to take the {clue_name}."
      else:
        return "You can't find a clue with that name."
        
    def use(clue_name: str) -> str:
      if clue_name not in self.get("inventory"):
        return "You don't have any clues of that name in your inventory."
      
      if clue_name not in self.get("actions"):
        return "You don't think you can use this."
      
      action = self.get("actions")[clue_name]

      action_requires_clue = action["requires"]["clue"]
      action_requires_room = action["requires"]["room"]
      action_creates_clue = action["creates"]["clue"]
      action_creates_room = action["creates"]["room"]
      action_unlocks_room = action["unlocks"]["room"]
      action_location_id = action["creates"]["in_location"]
      action_room_id = action["creates"]["in_room"]

      success = False

      if not action_requires_clue and not action_requires_room:
        success = True
      
      if action_requires_clue and not action_requires_room:
        if action_requires_clue.id() in self.get("inventory"):
          success = True
      
      if action_requires_room and not action_requires_clue:
        if action_requires_room.id() == self.get("current_room").id():
          success = True
      
      if action_requires_clue and action_requires_room:
        if action_requires_clue.id() in self.get("inventory") and action_requires_room.id() == self.get("current_room").id():
          success = True
      
      if success:
        if action_creates_clue:
          self[action_location_id][action_room_id].push(action_creates_clue)
        if action_creates_room:
          self[action_location_id].push(action_creates_room)
        if action_unlocks_room:
          action_unlocks_room.unlock()
      
      return action[success]

    if name in locals() and name[0] != "_":
      return locals()[name](arg)
    else:
      return None
  
  # Default location / room getters and updaters
  def get_default_location(self) -> Location:
    for location in self:
      if location.get("is_default"): return location
  
  def get_default_room(self) -> Room:
    for room in self.get("current_location"):
      if room.get("is_default"): return room

  def update_default_location(self) -> None:
    self.set("current_location", self.get_default_location())
  
  def update_default_room(self) -> None:
    self.set("current_room", self.get_default_room())
  
  def add_action(self,
    use_clue_id: str,
    requires_clue: Clue,
    requires_room: Room,
    creates_clue: Clue,
    creates_room: Room,
    unlocks_room: Room,
    in_location_id: str,
    in_room_id: str,
    success_message: str,
    default_message: str) -> None:

    action = {
      "requires": {
        "clue": False,
        "room": False
      },
      "creates": {
        "clue": False,
        "room": False,
        "in_room": None,
        "in_location": None
      },
      "unlocks": {
        "room": False
      },
      True: success_message,
      False: default_message
    }

    if requires_clue is not None:
      action["requires"]["clue"] = requires_clue
    
    if requires_room is not None:
      action["requires"]["room"] = requires_room
    
    if creates_clue is not None:
      action["creates"]["clue"] = creates_clue
      action["creates"]["in_location"] = in_location_id
      action["creates"]["in_room"] = in_room_id
    
    if creates_room is not None:
      action["creates"]["room"] = creates_room
      action["creates"]["in_location"] = in_location_id
      action["creates"]["in_room"] = in_room_id
    
    if unlocks_room is not None:
      action["unlocks"]["room"] = unlocks_room
    
    self.get("actions")[use_clue_id] = action

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
cl_note = Clue(
  name="Note",
  desc="A small note, in the shape of a key.",
  is_item=True
)

# rooms
rm_hallway = Room(
  name="Hallway",
  desc="Just a regular old hallway.",
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
ln_street_2 = Location(
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

test_adv.add_action(
  "phone",
  None,
  None,
  cl_note,
  None,
  None,
  "street",
  "dark alley",
  "Despite being unplugged, the phone works because it's a mobile phone. Someone on the other end says 'I've left a note for you somewhere.' Before you can reply, they hang up.",
  ""
)
test_adv.add_action(
  "note",
  cl_note,
  rm_hallway,
  None,
  None,
  rm_bedroom,
  None,
  None,
  "You hear a door unlock upstairs.",
  "After some fiddling, you come to the conclusion that this item won't work here."
)

test_adv(True)