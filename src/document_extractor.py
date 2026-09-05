from __future__ import annotations
import csv, io, re
from datetime import datetime

PATTERNS = {
 "order_id": r"(?:order\s*(?:id|number|#))\s*[:#-]?\s*([A-Z0-9-]{4,})",
 "transaction_id": r"(?:transaction\s*(?:id|number|#)|txn\s*id)\s*[:#-]?\s*([A-Z0-9-]{4,})",
 "tracking_number": r"(?:tracking\s*(?:id|number|#))\s*[:#-]?\s*([A-Z0-9-]{4,})",
 "payment_amount": r"(?:amount|total|paid)\s*[:\-]?\s*(?:INR|Rs\.?|₹)?\s*([\d,]+(?:\.\d{1,2})?)",
 "delivery_status": r"delivery\s*status\s*[:\-]?\s*(delivered|failed|returned|pending|in transit)",
 "order_date": r"order\s*date\s*[:\-]?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
 "delivery_date": r"delivery\s*date\s*[:\-]?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
 "refund_date": r"refund\s*date\s*[:\-]?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
 "refund_amount": r"refund\s*amount\s*[:\-]?\s*(?:INR|Rs\.?|₹)?\s*([\d,]+(?:\.\d{1,2})?)",
}

def extract_text(name: str, data: bytes) -> tuple[str, str | None]:
    ext = name.lower().rsplit(".", 1)[-1]
    try:
        if ext in {"txt", "csv"}: return data.decode("utf-8", errors="replace"), None
        if ext == "pdf":
            import fitz
            doc = fitz.open(stream=data, filetype="pdf")
            text = "\n".join(page.get_text() for page in doc)
            return text, None if text.strip() else "PDF contains no extractable text; OCR may be required."
        if ext in {"png", "jpg", "jpeg"}:
            try:
                import pytesseract
                from PIL import Image
                return pytesseract.image_to_string(Image.open(io.BytesIO(data))), None
            except Exception:
                return "", "OCR unavailable or image unreadable; enter fields manually."
        return "", "Unsupported file type."
    except Exception as exc:
        return "", f"Extraction failed: {exc}"

def extract_fields(text: str) -> dict:
    out = {}
    for field, pattern in PATTERNS.items():
        match = re.search(pattern, text, re.I)
        if match: out[field] = match.group(1).strip()
    return out

