from __future__ import annotations

from collections.abc import Iterable

from app.schemas.browser import UploadFieldDetection


class UploadDetectionService:
    _KEYWORDS: dict[str, tuple[str, ...]] = {
        "resume": ("resume", "cv", "curriculum vitae"),
        "cover_letter": ("cover letter", "covering letter"),
        "supporting_documents": ("supporting document", "additional document", "attachments"),
        "portfolio": ("portfolio", "work samples", "github"),
    }

    def detect_fields(self, page) -> list[UploadFieldDetection]:  # noqa: ANN001
        nodes = page.evaluate(
            """
            () => {
              const toText = (v) => (v || "").toString().trim();
              const controls = Array.from(document.querySelectorAll(
                'input[type="file"], button, [role="button"], [data-testid*="upload"], [class*="upload"], [aria-label*="upload"]'
              ));
              return controls.map((el, idx) => {
                const id = el.getAttribute("id");
                const name = el.getAttribute("name");
                const ariaLabel = toText(el.getAttribute("aria-label"));
                const placeholder = toText(el.getAttribute("placeholder"));
                const labelNode = id ? document.querySelector(`label[for="${id}"]`) : null;
                const parentLabel = el.closest("label");
                const labelText = toText(labelNode?.textContent || parentLabel?.textContent);
                const nearbyText = toText(el.closest("div,section,fieldset,form")?.textContent).slice(0, 220);
                const inputType = toText(el.getAttribute("type")).toLowerCase() || el.tagName.toLowerCase();
                const hidden = el.matches('input[type="file"][hidden], input[type="file"][style*="display: none"], input[type="file"][style*="visibility: hidden"]');
                const isDropZone = /drop|drag/.test((el.className || "").toString().toLowerCase()) || /drop|drag/.test(nearbyText.toLowerCase());
                const uploadCapability = isDropZone ? "drag_and_drop" : (inputType === "file" ? (hidden ? "hidden_input" : "standard") : "button_triggered");
                const selector =
                  id ? `#${CSS.escape(id)}` :
                  name ? `[name="${name.replaceAll('"', '\\"')}"]` :
                  `${el.tagName.toLowerCase()}:nth-of-type(${idx + 1})`;
                return {
                  selector,
                  inputType,
                  ariaLabel,
                  placeholder,
                  labelText,
                  nearbyText,
                  visible: !hidden,
                  uploadCapability,
                };
              });
            }
            """
        )
        if not isinstance(nodes, Iterable):
            return []

        detected: list[UploadFieldDetection] = []
        for idx, node in enumerate(nodes):
            if not isinstance(node, dict):
                continue
            field_type, confidence = self._classify(node)
            if field_type == "unknown":
                continue
            detected.append(
                UploadFieldDetection(
                    field_id=f"upload-{field_type}-{idx}",
                    field_type=field_type,
                    selector=str(node.get("selector", "")),
                    confidence=confidence,
                    visible=bool(node.get("visible", True)),
                    upload_capability=str(node.get("uploadCapability", "unknown")),
                    input_type=self._safe(node.get("inputType")),
                    nearby_text=self._safe(node.get("nearbyText")),
                )
            )
        return detected

    def _classify(self, node: dict) -> tuple[str, float]:
        haystack = " ".join(
            part.lower()
            for part in [
                self._safe(node.get("ariaLabel")),
                self._safe(node.get("placeholder")),
                self._safe(node.get("labelText")),
                self._safe(node.get("nearbyText")),
            ]
            if part
        )
        best = "unknown"
        score = 0.0
        for field_type, words in self._KEYWORDS.items():
            hits = sum(1 for word in words if word in haystack)
            if hits <= 0:
                continue
            next_score = round(0.55 + min(0.4, hits * 0.2), 2)
            if next_score > score:
                best = field_type
                score = next_score
        return best, score

    @staticmethod
    def _safe(value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None
