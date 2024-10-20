from enum import Enum


class EnumWithLowerCaseNames(Enum):
    def __str__(self):
        return self.name.lower()

    @classmethod
    def from_string(cls, value: str):
        try:
            return cls[value.upper()]
        except KeyError:
            raise ValueError(f"{value} is not a valid {cls.__name__}")