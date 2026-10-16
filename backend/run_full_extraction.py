from pathlib import Path
from app.ai.extraction.full_runner import FullRunner

pdfs = sorted(str(p) for p in Path("ai_data/raw").rglob("*.pdf"))

print("Found", len(pdfs), "PDFs")

if len(pdfs) != 221:
    raise RuntimeError(f"Expected 221 PDFs, found {len(pdfs)}")

runner = FullRunner(
    output_dir="ai_data/reports/full_extraction"
)

result = runner.process(pdfs)

print("Completed:", result["completed"])
print("Failed:", result["failed"])
