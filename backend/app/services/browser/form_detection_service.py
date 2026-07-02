from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from app.schemas.browser import DetectedFormField


@dataclass(frozen=True)
class FieldDefinition:
    field_type: str
    keywords: tuple[str, ...]


class FormDetectionService:
    _FIELD_DEFINITIONS: tuple[FieldDefinition, ...] = (
        FieldDefinition("first_name", ("first name", "firstname", "given name", "givenname")),
        FieldDefinition("last_name", ("last name", "lastname", "surname", "family name")),
        FieldDefinition("full_name", ("full name", "name", "legal name")),
        FieldDefinition("email", ("email", "e-mail")),
        FieldDefinition("phone_number", ("phone", "mobile", "telephone", "contact number")),
        FieldDefinition("address", ("address", "street")),
        FieldDefinition("city", ("city", "town")),
        FieldDefinition("state", ("state", "province", "region")),
        FieldDefinition("country", ("country",)),
        FieldDefinition("postal_code", ("postal", "zip", "pincode")),
        FieldDefinition("date_of_birth", ("date of birth", "dob", "birth date", "birthday")),
        FieldDefinition("linkedin_url", ("linkedin",)),
        FieldDefinition("github_url", ("github",)),
        FieldDefinition("portfolio_url", ("portfolio", "website", "personal site")),
        FieldDefinition("highest_qualification", ("highest qualification", "highest degree", "qualification")),
        FieldDefinition("university", ("university", "college", "institution")),
        FieldDefinition("graduation_year", ("graduation year", "passing year", "year of graduation")),
        FieldDefinition("current_company", ("current company", "employer")),
        FieldDefinition("current_role", ("current role", "current title", "designation")),
        FieldDefinition("experience", ("experience", "years of experience")),
        FieldDefinition("skills", ("skills", "technologies", "core skills")),
        FieldDefinition("notice_period", ("notice period", "notice")),
        FieldDefinition("current_salary", ("current salary", "ctc", "compensation current")),
        FieldDefinition("expected_salary", ("expected salary", "salary expectation", "desired salary")),
        FieldDefinition("work_authorization", ("work authorization", "authorized to work", "visa status")),
        FieldDefinition("willing_to_relocate", ("relocate", "willing to relocate")),
        FieldDefinition("resume_upload", ("resume upload", "attach resume", "upload resume", "resume")),
        FieldDefinition(
            "cover_letter_upload",
            ("cover letter upload", "attach cover letter", "upload cover letter", "cover letter"),
        ),
    )

    def detect_fields(self, page) -> list[DetectedFormField]:  # noqa: ANN001
        nodes = page.evaluate(
            """
            () => {
              const controls = Array.from(document.querySelectorAll("input, textarea, select"));
              return controls.map((el, idx) => {
                const inputType = (el.getAttribute("type") || el.tagName || "").toLowerCase();
                const id = el.getAttribute("id");
                const name = el.getAttribute("name");
                const placeholder = el.getAttribute("placeholder");
                const ariaLabel = el.getAttribute("aria-label");
                const required = el.hasAttribute("required") || el.getAttribute("aria-required") === "true";
                const labelNode = id ? document.querySelector(`label[for="${id}"]`) : null;
                const parentLabel = el.closest("label");
                const labelText = (labelNode?.textContent || parentLabel?.textContent || "").trim();
                const nearby = (el.closest("div,fieldset,section,form")?.textContent || "").trim().slice(0, 160);
                const selector =
                  id ? `#${CSS.escape(id)}` :
                  name ? `[name="${name.replaceAll('"', '\\"')}"]` :
                  `${el.tagName.toLowerCase()}:nth-of-type(${idx + 1})`;
                return {
                  selector,
                  label: labelText || null,
                  placeholder: placeholder || null,
                  name: name || null,
                  ariaLabel: ariaLabel || null,
                  nearbyText: nearby || null,
                  inputType,
                  required,
                  tagName: el.tagName.toLowerCase(),
                };
              });
            }
            """
        )
        if not isinstance(nodes, Iterable):
            return []

        detected: list[DetectedFormField] = []
        for idx, node in enumerate(nodes):
            if not isinstance(node, dict):
                continue
            field_type, confidence = self._classify(node)
            if field_type == "unknown":
                continue
            detected.append(
                DetectedFormField(
                    field_id=f"{field_type}-{idx}",
                    field_type=field_type,
                    selector=str(node.get("selector", "")),
                    label=self._safe(node.get("label")),
                    placeholder=self._safe(node.get("placeholder")),
                    input_name=self._safe(node.get("name")),
                    input_type=self._safe(node.get("inputType")),
                    required=bool(node.get("required", False)),
                    confidence=confidence,
                )
            )
        return detected

    def _classify(self, node: dict) -> tuple[str, float]:
        text_parts = [
            self._safe(node.get("label")),
            self._safe(node.get("placeholder")),
            self._safe(node.get("name")),
            self._safe(node.get("ariaLabel")),
            self._safe(node.get("nearbyText")),
        ]
        haystack = " ".join(part.lower() for part in text_parts if part)
        input_type = (self._safe(node.get("inputType")) or "").lower()

        # Strong first-pass type-based heuristics.
        if input_type == "email":
            return "email", 0.98
        if input_type in {"tel"}:
            return "phone_number", 0.96
        if input_type == "date":
            return "date_of_birth", 0.9
        if input_type == "url":
            if "linkedin" in haystack:
                return "linkedin_url", 0.95
            if "github" in haystack:
                return "github_url", 0.95
            return "portfolio_url", 0.82
        if input_type == "file":
            if "cover" in haystack:
                return "cover_letter_upload", 0.92
            return "resume_upload", 0.92

        best_match = "unknown"
        best_score = 0.0
        for definition in self._FIELD_DEFINITIONS:
            score = self._keyword_score(haystack, definition.keywords)
            if score > best_score:
                best_match = definition.field_type
                best_score = score
        return best_match, best_score

    @staticmethod
    def _keyword_score(haystack: str, keywords: tuple[str, ...]) -> float:
        if not haystack:
            return 0.0
        hits = sum(1 for keyword in keywords if keyword in haystack)
        if hits == 0:
            return 0.0
        ratio = min(1.0, hits / max(1, len(keywords)))
        return round(0.55 + ratio * 0.4, 2)

    @staticmethod
    def _safe(value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None
