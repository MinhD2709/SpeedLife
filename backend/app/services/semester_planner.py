from __future__ import annotations

from dataclasses import dataclass

from app.models import CatalogUnit, ExcludedUnit, OutlookTerm, PlanUnit, StudentRecord


@dataclass
class PlannerResult:
    selected: list[PlanUnit]
    excluded: list[ExcludedUnit]
    outlook: list[OutlookTerm]


def _completed(record: StudentRecord) -> tuple[set[str], dict[str, float | None]]:
    units = {unit.code for unit in record.units if unit.status in {"completed", "credited"}}
    marks = {unit.code: unit.mark for unit in record.units if unit.code in units}
    return units, marks


def _group_satisfied(group, completed: set[str], marks: dict[str, float | None]) -> bool:
    for code in group.any_of:
        if code not in completed:
            continue
        if group.minimum_mark is None or (marks.get(code) is not None and marks[code] >= group.minimum_mark):
            return True
    return False


def _ineligibility(
    unit: CatalogUnit,
    completed: set[str],
    marks: dict[str, float | None],
    session: str,
    selected_codes: set[str],
) -> str | None:
    if unit.code in completed:
        return "Already completed or credited."
    if session not in unit.sessions:
        return f"Not listed in the curated {session} offering set."
    blocked = sorted(set(unit.prohibitions) & (completed | selected_codes))
    if blocked:
        return "Prohibited by completed unit(s): " + ", ".join(blocked) + "."
    missing = [" or ".join(group.any_of) for group in unit.prerequisites if not _group_satisfied(group, completed, marks)]
    if missing:
        return "Missing prerequisite group(s): " + "; ".join(missing) + "."
    return None


def _rank(
    unit: CatalogUnit,
    interests: list[str],
    unlock_counts: dict[str, int],
    pace: str,
) -> tuple[int, int, int, int, str]:
    interest_text = " ".join(interests).lower()
    interest_match = int(any(word and word in (unit.title + " " + unit.code).lower() for word in interest_text.split()))
    unlocks = unlock_counts.get(unit.code, 0)
    if pace == "accelerated":
        return (0 if unit.core else 1, -unlocks, -interest_match, unit.level, unit.code)
    return (0 if unit.core else 1, -interest_match, -unlocks, unit.level, unit.code)


def _corequisites_satisfied(
    unit: CatalogUnit,
    completed: set[str],
    marks: dict[str, float | None],
    selected_codes: set[str],
) -> tuple[bool, list[str]]:
    missing: list[str] = []
    for group in unit.corequisites:
        completed_match = _group_satisfied(group, completed, marks)
        concurrent_match = group.minimum_mark is None and bool(set(group.any_of) & selected_codes)
        if not completed_match and not concurrent_match:
            missing.append(" or ".join(group.any_of))
    return not missing, missing


def _build_term(
    catalog: list[CatalogUnit],
    record: StudentRecord,
    session: str,
    credit_limit: int,
    interests: list[str],
    pace: str,
) -> tuple[list[PlanUnit], list[ExcludedUnit]]:
    completed, marks = _completed(record)
    unlock_counts: dict[str, int] = {}
    for later_unit in catalog:
        for group in [*later_unit.prerequisites, *later_unit.corequisites]:
            for code in group.any_of:
                unlock_counts[code] = unlock_counts.get(code, 0) + 1
    selected: list[PlanUnit] = []
    excluded: list[ExcludedUnit] = []
    for unit in sorted(catalog, key=lambda item: _rank(item, interests, unlock_counts, pace)):
        selected_codes = {item.code for item in selected}
        problem = _ineligibility(unit, completed, marks, session, selected_codes)
        if problem:
            excluded.append(ExcludedUnit(code=unit.code, title=unit.title, reason=problem))
            continue
        if sum(item.credit_points for item in selected) + unit.credit_points > credit_limit:
            excluded.append(ExcludedUnit(code=unit.code, title=unit.title, reason="Would exceed the selected credit-point load."))
            continue
        reason = (
            f"Required {unit.requirement_group}; rules pass and it unlocks {unlock_counts.get(unit.code, 0)} later option(s)."
            if unit.core
            else f"Eligible {unit.requirement_group} matching the remaining major structure and stated interests."
        )
        selected.append(
            PlanUnit(
                code=unit.code,
                title=unit.title,
                credit_points=unit.credit_points,
                requirement_group=unit.requirement_group,
                reason=reason,
                source_url=unit.source_url,
            )
        )

    # Corequisites may be taken concurrently, so validate them only after the
    # tentative term is assembled. Iterate because removing one unit can make a
    # second unit's corequisite group unsatisfied.
    catalog_by_code = {unit.code: unit for unit in catalog}
    while True:
        selected_codes = {item.code for item in selected}
        invalid: list[tuple[PlanUnit, list[str]]] = []
        for item in selected:
            valid, missing = _corequisites_satisfied(catalog_by_code[item.code], completed, marks, selected_codes)
            if not valid:
                invalid.append((item, missing))
        if not invalid:
            break
        invalid_codes = {item.code for item, _ in invalid}
        selected = [item for item in selected if item.code not in invalid_codes]
        for item, missing in invalid:
            excluded.append(
                ExcludedUnit(
                    code=item.code,
                    title=item.title,
                    reason="Missing corequisite group(s): " + "; ".join(missing) + ".",
                )
            )
    return selected, excluded


def make_plan(
    catalog: list[CatalogUnit],
    record: StudentRecord,
    target_session: str,
    credit_limit: int,
    interests: list[str],
    pace: str = "balanced",
) -> PlannerResult:
    selected, excluded = _build_term(catalog, record, target_session, credit_limit, interests, pace)
    simulated = record.model_copy(deep=True)
    from app.models import StudentUnit

    simulated.units.extend(StudentUnit(code=item.code, status="completed") for item in selected)
    next_session = "Semester 2" if target_session == "Semester 1" else "Semester 1"
    later, _ = _build_term(catalog, simulated, next_session, credit_limit, interests, pace)
    outlook = [OutlookTerm(session=next_session, units=[item.code for item in later])]
    return PlannerResult(selected=selected, excluded=excluded[:10], outlook=outlook)
