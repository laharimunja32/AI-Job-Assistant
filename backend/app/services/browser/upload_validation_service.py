from __future__ import annotations

from pathlib import Path

from app.schemas.browser import UploadValidationResult


class UploadValidationService:
    _DEFAULT_ACCEPTED = (".pdf", ".doc", ".docx", ".rtf", ".txt")

    def validate(self, page, selector: str, file_path: str) -> UploadValidationResult:  # noqa: ANN001
        result = UploadValidationResult(accepted=True, accepted_file_types=list(self._DEFAULT_ACCEPTED))
        path = Path(file_path)
        if not path.exists():
            result.accepted = False
            result.validation_error = "Document file does not exist on disk"
            return result

        result.max_file_size_mb = 10.0
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > result.max_file_size_mb:
            result.accepted = False
            result.validation_error = f"File too large ({size_mb:.1f}MB > {result.max_file_size_mb}MB)"

        if path.suffix.lower() not in self._DEFAULT_ACCEPTED:
            result.accepted = False
            result.validation_error = f"Unsupported file type: {path.suffix}"

        attrs = page.locator(selector).first.evaluate(
            """
            el => ({
              accept: (el.getAttribute("accept") || "").toLowerCase(),
              multiple: el.hasAttribute("multiple"),
            })
            """
        )
        if isinstance(attrs, dict):
            accept = str(attrs.get("accept", "")).strip()
            result.multiple_allowed = bool(attrs.get("multiple", False))
            if accept:
                accepted_file_types = [token.strip() for token in accept.split(",") if token.strip()]
                result.accepted_file_types = accepted_file_types
                if not self._matches_accept(path.name, accept):
                    result.accepted = False
                    result.validation_error = f"File does not match accepted types: {accept}"
        return result

    def verify_upload(self, page, selector: str, filename: str) -> tuple[bool, list[str]]:  # noqa: ANN001
        messages: list[str] = []
        try:
            page.wait_for_timeout(700)
            node = page.locator(selector).first
            input_value = node.input_value(timeout=1500)
            if input_value and filename.lower() in input_value.lower():
                return True, messages
            visible_name = page.evaluate(
                """
                (f) => {
                  const text = document.body?.innerText || "";
                  return text.toLowerCase().includes((f || "").toLowerCase());
                }
                """,
                filename,
            )
            if visible_name:
                return True, messages
            messages.append("Uploaded filename not visible yet")
            return False, messages
        except Exception as exc:  # pragma: no cover
            return False, [f"Upload verification failed: {exc}"]

    @staticmethod
    def _matches_accept(filename: str, accept_value: str) -> bool:
        suffix = Path(filename).suffix.lower()
        allowed = [part.strip().lower() for part in accept_value.split(",") if part.strip()]
        if not allowed:
            return True
        for token in allowed:
            if token.startswith(".") and suffix == token:
                return True
            if token == "application/pdf" and suffix == ".pdf":
                return True
            if token in {"application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"} and suffix in {".doc", ".docx"}:
                return True
            if token == "text/plain" and suffix == ".txt":
                return True
        return False
