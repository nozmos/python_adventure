from typing import Any, Dict


# Errors
class MissingAttributeError(Exception):
  pass

class AdventureObject:
  def __init__(self, **data) -> None:
    self._data = data
    self._required_attrs = []
    self._validate()
  
  def _validate(self) -> None:
    for attr in self._required_attrs:
      if not attr in self._data:
        raise MissingAttributeError(f"Invalid {self.__name__}: missing attribute {attr}")


class Clue(AdventureObject):
  def __init__(self, **data) -> None:
    self._required_attrs = ["name"]
    super().__init__(**data)

    # self._required_attrs = ["name", ""]

    # for attr in ["name", "desc", "is_item"]:
    #   if not attr in self._data:
    #     self._data[attr] = None
  
  def __hash__(self) -> int:
    return hash(self._data)
  
  def __eq__(self, __o: object) -> bool:
    return self._data == __o._data

  # def __getattr__(self, attr) -> Any:
  #   if attr in self._data:
  #     return self._data[attr]
  #   else:
  #     object.__getattr__(attr)
  
  # def __setattr__(self, __name: str, __value: Any) -> None:
  #   if __name in self._data:
  #     self._data[__name] = __value


class Room:
  def __init__(self, **data) -> None:
    self._data = data


test_clue = Clue()