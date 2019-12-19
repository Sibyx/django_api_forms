import datetime
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Artist:
    name: str = ""
    members: int = 0
    genres: List[str] = field(default_factory=list)


@dataclass
class Song:
    title: str = ""
    duration: datetime.timedelta = None


@dataclass
class Album:
    title: str = ""
    year: int = 0
    artist: Artist = Artist()
    songs: List[Song] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
