import enum


class NoteCategory(str, enum.Enum):
    STICK = "stick"
    SMALL = "small"
    BIG = "big"
