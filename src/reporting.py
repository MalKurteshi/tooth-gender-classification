"""Generate a portable report about the active model without retraining it."""

from datetime import datetime, timezone
from html import escape
from pathlib import Path


def generate_report(predictor, output):
    metadata = predictor.metadata
    rows = "".join(
        f"<tr><th>{escape(str(key))}</th><td>{escape(str(value))}</td></tr>"
        for key, value in metadata.items()
    )
    content = f"""<!doctype html><html lang="en"><meta charset="utf-8">
<title>Tooth Gender Classification — Model Report</title>
<style>body{{font:16px system-ui;max-width:900px;margin:40px auto;padding:20px}}th,td{{text-align:left;vertical-align:top;padding:10px;border-bottom:1px solid #ddd}}table{{border-collapse:collapse}}</style>
<h1>Tooth Gender Classification</h1><p>Active model report · {datetime.now(timezone.utc).isoformat()}</p>
<p>Cross-validation scores describe internal validation. No independent test accuracy is available for this pipeline.</p>
<table>{rows}</table></html>"""
    Path(output).write_text(content, encoding="utf-8")
    return Path(output)
