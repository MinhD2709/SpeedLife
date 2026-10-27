from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


UnitStatus = Literal["completed", "current", "credited", "failed", "unknown"]


class StudentUnit(BaseModel):
    code: str
    status: UnitStatus = "completed"
    mark: float | None = Field(default=None, ge=0, le=100)
    credit_points: int = Field(default=6, ge=0, le=24)
    source_document: str | None = None
    page: int | None = Field(default=None, ge=1)

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        value = value.strip().upper()
        if len(value) != 8 or not value[:4].isalpha() or not value[4:].isdigit():
            raise ValueError("Use a unit code such as DATA2001.")
        return value


class StudentRecord(BaseModel):
    degree: str = "Bachelor of Advanced Computing"
    major: str = "Computational Data Science"
    handbook_year: int = 2026
    units: list[StudentUnit] = Field(default_factory=list)


class DocumentSummary(BaseModel):
    filename: str
    pages: int
    units_found: int


class RecordExtractionResponse(BaseModel):
    record: StudentRecord
    documents: list[DocumentSummary]
    warnings: list[str]
    confirmation_required: bool = True


class PlanRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=1000)
    confirmed: bool
    record: StudentRecord
    target_session: Literal["Semester 1", "Semester 2"]
    target_credit_points: int = Field(default=24, ge=6, le=24, multiple_of=6)
    pace: Literal["balanced", "accelerated"] = "balanced"
    interests: list[str] = Field(default_factory=list, max_length=8)


class RequirementGroup(BaseModel):
    any_of: list[str]
    minimum_mark: float | None = None


class CatalogUnit(BaseModel):
    code: str
    title: str
    credit_points: int = 6
    level: int
    requirement_group: str
    core: bool = False
    sessions: list[str]
    prerequisites: list[RequirementGroup] = Field(default_factory=list)
    corequisites: list[RequirementGroup] = Field(default_factory=list)
    prohibitions: list[str] = Field(default_factory=list)
    assumed_knowledge: str | None = None
    source_url: str
    handbook_year: int = 2026

    @field_validator("sessions", "prerequisites", "corequisites", "prohibitions", mode="before")
    @classmethod
    def decode_zetaris_json(cls, value):
        if isinstance(value, str):
            import json

            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return [part.strip() for part in value.split(",") if part.strip()]
        return value


class PlanUnit(BaseModel):
    code: str
    title: str
    credit_points: int
    requirement_group: str
    reason: str
    source_url: str


class ExcludedUnit(BaseModel):
    code: str
    title: str
    reason: str


class OutlookTerm(BaseModel):
    session: str
    units: list[str]
    note: str = "Indicative only; re-check offerings and rules before enrolment."


class EvidenceLink(BaseModel):
    label: str
    url: str


class Clarification(BaseModel):
    question: str
    options: list[str]


class PlanResponse(BaseModel):
    status: Literal["complete", "clarification"]
    clarification: Clarification | None = None
    next_term: list[PlanUnit] = Field(default_factory=list)
    excluded: list[ExcludedUnit] = Field(default_factory=list)
    outlook: list[OutlookTerm] = Field(default_factory=list)
    narrative: str = ""
    evidence: list[EvidenceLink] = Field(default_factory=list)
    trace: list[str] = Field(default_factory=list)
    contract_id: str | None = None
    intent: str | None = None
