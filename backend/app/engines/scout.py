from __future__ import annotations

import hashlib
import hmac
import json
import re
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


DEFAULT_INTENTS = [
    {
        "id": "academic.plan_next_term",
        "description": "Create or recommend a valid next-semester unit plan",
        "examples": ["plan my next semester", "what units should I take next", "build my study plan"],
        "capabilities": ["zetaris.query", "planner.solve", "nightshift.explain"],
        "riskClass": "medium",
        "parameters": {"required": ["target_session"]},
    },
    {
        "id": "academic.check_unit_eligibility",
        "description": "Check prerequisites prohibitions and eligibility for a unit",
        "examples": ["can I take DATA3406", "am I eligible for this unit", "check prerequisites"],
        "capabilities": ["zetaris.query", "planner.solve"],
        "riskClass": "medium",
        "parameters": {"required": []},
    },
    {
        "id": "academic.explain_degree_progress",
        "description": "Explain completed and remaining degree requirements",
        "examples": ["explain my degree progress", "what requirements remain", "how far through my degree am I"],
        "capabilities": ["zetaris.query", "nightshift.explain"],
        "riskClass": "low",
        "parameters": {"required": []},
    },
]

INJECTION_PATTERNS = (
    r"ignore (all|any|the|your) (previous|prior|system) instructions",
    r"ignore previous",
    r"disregard (the )?(rules|user|instructions)",
    r"unrestricted mode",
    r"</system>",
    r"<system>",
    r"\[inst\]",
    r"reveal .*?(secret|token|api key|system prompt)",
    r"(grant|make) me admin",
    r"internal_admin_panel",
    r"\\u202e",
)
SENSITIVE_PATTERNS = (r"\b\d{9}\b", r"\b\d{3}-\d{3}-\d{3}\b")


def _canonical(value: dict[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _tokens(text: str) -> set[str]:
    stop = {"a", "an", "and", "for", "i", "in", "is", "me", "my", "of", "or", "the", "to"}
    return {token for token in re.findall(r"[a-z0-9.]+", text.lower()) if len(token) > 1 and token not in stop}


@dataclass
class ScoutDecision:
    intent: dict[str, Any]
    risk: dict[str, Any]
    toolPlan: list[dict[str, Any]]
    executionContract: dict[str, Any] | None
    clarification: dict[str, Any] | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "intent": self.intent,
            "risk": self.risk,
            "toolPlan": self.toolPlan,
            "executionContract": self.executionContract,
            "clarification": self.clarification,
        }


class Scout:
    """Meterless Scout's Sense -> Interpret -> Guard -> Route -> Recommend pipeline."""

    def __init__(self, intent_registry: str | dict | None = None, signing_secret: str = "demo-only-change-me"):
        self.registry_version = 1
        self.intents = DEFAULT_INTENTS
        self.signing_secret = signing_secret.encode()
        if intent_registry:
            data = json.loads(Path(intent_registry).read_text()) if isinstance(intent_registry, str) else intent_registry
            self.registry_version = int(data.get("registryVersion", data.get("version", 1)))
            self.intents = data.get("intents", data if isinstance(data, list) else DEFAULT_INTENTS)

    def _score(self, prompt: str, intent: dict[str, Any]) -> float:
        prompt_tokens = _tokens(prompt)
        examples = " ".join([intent.get("description", ""), *intent.get("examples", [])])
        intent_tokens = _tokens(examples)
        overlap = len(prompt_tokens & intent_tokens)
        lexical = overlap / max(1, min(4, len(prompt_tokens)))
        phrase_bonus = 0.0
        for example in intent.get("examples", []):
            if example.lower() in prompt.lower():
                phrase_bonus = 0.45
                break
        return min(1.0, lexical * 0.7 + phrase_bonus)

    def decide(self, *, prompt: str, surface: str = "chat", context: dict | None = None, user: dict | None = None) -> ScoutDecision:
        started = time.perf_counter()
        candidates = sorted(
            ({"intent": item, "score": self._score(prompt, item)} for item in self.intents),
            key=lambda item: item["score"],
            reverse=True,
        )
        winner = candidates[0]
        score = round(winner["score"], 4)
        intent = {
            "primary": winner["intent"].get("id", "GENERAL"),
            "parameters": {"target_session": (context or {}).get("target_session")},
            "references": [],
            "confidence": score,
            "alternates": [
                {"intent": item["intent"].get("id"), "score": round(item["score"], 4)} for item in candidates[1:3]
            ],
        }

        flags: list[str] = []
        if any(re.search(pattern, prompt, re.I) for pattern in INJECTION_PATTERNS):
            flags.append("prompt_injection")
        if any(re.search(pattern, prompt) for pattern in SENSITIVE_PATTERNS):
            flags.append("sensitive_identifier_redacted")
        if "prompt_injection" in flags:
            return ScoutDecision(intent, {"level": "block", "flags": flags, "reason": "Prompt injection detected."}, [], None, None)

        close_tie = len(candidates) > 1 and score < 0.8 and score >= 0.55 and score - candidates[1]["score"] <= 0.05
        if score < 0.55 or close_tie:
            options = [item["intent"].get("id", "GENERAL") for item in candidates[:3]]
            return ScoutDecision(
                intent,
                {"level": "medium", "flags": flags},
                [],
                None,
                {"question": "What kind of academic planning help do you want?", "options": options},
            )

        capabilities = list(winner["intent"].get("capabilities", []))
        tool_plan = [{"tool": capability, "input": intent["parameters"]} for capability in capabilities]
        now = datetime.now(UTC)
        unsigned = {
            "contractId": uuid.uuid4().hex,
            "traceId": uuid.uuid4().hex,
            "intent": intent,
            "risk": {
                "level": winner["intent"].get("riskClass", "low"),
                "flags": flags,
                "redactions": ["student_identifier"] if "sensitive_identifier_redacted" in flags else [],
                "approvals": ["user-confirm"] if (context or {}).get("confirmed") else [],
            },
            "toolPlan": tool_plan,
            "modelProfile": {"provider": "meterless", "profile": "configured-runtime-route"},
            "scope": {"user": (user or {}).get("id", "local-user"), "surface": surface, "capabilities": capabilities},
            "issuedAt": now.isoformat(),
            "expiresAt": (now + timedelta(minutes=5)).isoformat(),
            "registryVersion": self.registry_version,
            "policyPackVersion": "unipilot-1",
            "signedBy": "scout",
            "latencyMs": round((time.perf_counter() - started) * 1000, 3),
        }
        signature = hmac.new(self.signing_secret, _canonical(unsigned), hashlib.sha256).hexdigest()
        contract = {**unsigned, "signature": signature}
        return ScoutDecision(intent, unsigned["risk"], tool_plan, contract, None)

    def verify(self, contract: dict[str, Any]) -> bool:
        signature = contract.get("signature", "")
        unsigned = {key: value for key, value in contract.items() if key != "signature"}
        expected = hmac.new(self.signing_secret, _canonical(unsigned), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return False
        return datetime.fromisoformat(contract["expiresAt"]) > datetime.now(UTC)


def _cli() -> None:
    payload = json.loads(sys.stdin.read())
    options = payload.get("options", {})
    scout = Scout(options.get("intentRegistry"), options.get("signingSecret", "demo-only-change-me"))
    action = payload.get("action", "decide")
    if action == "classify":
        decision = scout.decide(prompt=payload["input"]["prompt"], surface=payload["input"].get("surface", "chat"))
        print(json.dumps({"candidates": [decision.intent]}))
        return
    print(json.dumps(scout.decide(**payload["input"]).as_dict()))


if __name__ == "__main__":
    _cli()
