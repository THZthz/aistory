import os
from enum import Enum, unique


def PATH(path: str) -> str:
    """
    Return the source directory of the project.
    :param path:
    :return:
    """
    return '../' + path


@unique
class Memories(Enum):
    Observation = 0
    Reflection = 1
    Plan = 2

    def __str__(self):
        return f'{self.name.lower()}'

