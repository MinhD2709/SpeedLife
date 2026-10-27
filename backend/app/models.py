from dataclasses import dataclass


@dataclass(frozen=True)
class Evidence:
    source_id: str
    filename: str
    page: int
    text: str


@dataclass(frozen=True)
class Point:
    text: str
    citation: Evidence


@dataclass
class CheatSheet:
    mode: str
    title: str
    points: list[Point]
    warnings: list[str]
    trace: list[str]
