from enum import Enum


class EnumWithLowerCaseNames(Enum):
    def __str__(self):
        return self.name.lower()