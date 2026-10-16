from __future__ import annotations

import json
import sys
import os
from pathlib import Path

sys.path.insert(0, os.getcwd())

import fitz

from app.ai.extraction.full_runner import FullRunner, DocumentResult


def _make_pdf(path: Path, text: str = "Test content") -> None:
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 80), text, fontsize=11)
    doc.save(str(path))
    doc.close()


class TestFreshProcessing:
    def test_processes_pdf_creates_json_and_markdown(self, tmp_path):
        pdf = tmp_path / "test.pdf"
        _make_pdf(pdf, "Fresh processing test content")

        output_dir = tmp_path / "reports" / "full_extraction"
        runner = FullRunner(output_dir=output_dir)
        result = runner.process([str(pdf)])

        assert result["completed"] == 1
        assert result["failed"] == 0

        json_file = output_dir.glob("test_*.json")
        md_file = output_dir.glob("test_*.md")
        assert len(list(json_file)) == 1
        assert len(list(md_file)) == 1

        doc = json.loads(list(output_dir.glob("test_*.json"))[0].read_text())
        assert doc["document_id"].startswith("full-")
        assert doc["file_name"] == "test.pdf"
        assert doc["extraction_status"] == "success"
        assert len(doc["pages"]) >= 1

        md = list(output_dir.glob("test_*.md"))[0].read_text()
        assert "# Document:" in md
        assert "Fresh processing test content" in md

        manifest = json.loads(output_dir.joinpath("manifest.json").read_text())
        assert manifest["total"] == 1
        assert manifest["completed"] == 1

    def test_manifest_contains_document_entry(self, tmp_path):
        pdf = tmp_path / "doc.pdf"
        _make_pdf(pdf)

        output_dir = tmp_path / "reports" / "full_extraction"
        runner = FullRunner(output_dir=output_dir)
        runner.process([str(pdf)])

        manifest = runner.manifest
        entry = manifest["documents"].get(str(pdf))
        assert entry is not None
        assert entry["status"] == "completed"
        assert entry["output_json"].startswith("doc_") and entry["output_json"].endswith(".json")
        assert entry["output_markdown"].startswith("doc_") and entry["output_markdown"].endswith(".md")
        assert entry["document_id"] is not None


class TestFilenameCollision:
    def test_same_basename_different_dirs_get_separate_outputs(self, tmp_path):
        dir1 = tmp_path / "emtop"
        dir2 = tmp_path / "gypsobat"
        dir1.mkdir()
        dir2.mkdir()
        pdf1 = dir1 / "doc.pdf"
        pdf2 = dir2 / "doc.pdf"
        _make_pdf(pdf1, "First doc content")
        _make_pdf(pdf2, "Second doc content")

        output_dir = tmp_path / "reports" / "full_extraction"
        runner = FullRunner(output_dir=output_dir)
        result = runner.process([str(pdf1), str(pdf2)])

        assert result["completed"] == 2
        assert result["failed"] == 0

        json_files = sorted(output_dir.glob("doc_*.json"))
        md_files = sorted(output_dir.glob("doc_*.md"))
        assert len(json_files) == 2, f"Expected 2 JSON files, got {len(json_files)}"
        assert len(md_files) == 2, f"Expected 2 MD files, got {len(md_files)}"

        for jf, mf in zip(json_files, md_files):
            doc = json.loads(jf.read_text())
            assert doc["extraction_status"] == "success"
            assert jf.exists() and mf.exists()

    def test_same_basename_resume_skips_independently(self, tmp_path):
        dir1 = tmp_path / "dir_a"
        dir2 = tmp_path / "dir_b"
        dir1.mkdir()
        dir2.mkdir()
        pdf1 = dir1 / "doc.pdf"
        pdf2 = dir2 / "doc.pdf"
        _make_pdf(pdf1, "A")
        _make_pdf(pdf2, "B")

        output_dir = tmp_path / "reports" / "full_extraction"
        runner = FullRunner(output_dir=output_dir)
        runner.process([str(pdf1), str(pdf2)])

        runner2 = FullRunner(output_dir=output_dir)
        result = runner2.process([str(pdf1), str(pdf2)])
        assert result["completed"] == 0
        assert result["failed"] == 0
        assert len(runner2.results) == 0

        assert len(list(output_dir.glob("doc_*.json"))) == 2


class TestResumeSkip:
    def test_skips_already_completed_on_resume(self, tmp_path):
        pdf = tmp_path / "skip.pdf"
        _make_pdf(pdf, "Resume test")

        output_dir = tmp_path / "reports" / "full_extraction"
        runner = FullRunner(output_dir=output_dir)
        result1 = runner.process([str(pdf)])
        assert result1["completed"] == 1

        runner2 = FullRunner(output_dir=output_dir)
        result2 = runner2.process([str(pdf)])
        assert result2["completed"] == 0
        assert result2["failed"] == 0

        assert len(runner2.results) == 0

    def test_resumes_with_new_and_skips_existing(self, tmp_path):
        pdf1 = tmp_path / "first.pdf"
        pdf2 = tmp_path / "second.pdf"
        _make_pdf(pdf1, "First doc")
        _make_pdf(pdf2, "Second doc")

        output_dir = tmp_path / "reports" / "full_extraction"
        runner = FullRunner(output_dir=output_dir)
        runner.process([str(pdf1)])

        runner2 = FullRunner(output_dir=output_dir)
        result = runner2.process([str(pdf1), str(pdf2)])

        assert result["completed"] == 1
        assert result["failed"] == 0
        assert len(list(output_dir.glob("second_*.json"))) == 1
        assert len(list(output_dir.glob("second_*.md"))) == 1


class TestFailureContinues:
    def test_missing_file_recorded_and_continues(self, tmp_path):
        pdf_good = tmp_path / "good.pdf"
        _make_pdf(pdf_good, "Good content")

        output_dir = tmp_path / "reports" / "full_extraction"
        runner = FullRunner(output_dir=output_dir)
        result = runner.process([
            "/nonexistent/file.pdf",
            str(pdf_good),
        ])

        assert result["completed"] == 1
        assert result["failed"] == 1

        assert len(list(output_dir.glob("good_*.json"))) == 1
        assert len(list(output_dir.glob("good_*.md"))) == 1

        failed_entry = runner.manifest["documents"].get("/nonexistent/file.pdf")
        assert failed_entry is not None
        assert failed_entry["status"] == "failed"
        assert failed_entry["error"] is not None

    def test_partial_extraction_recorded_as_failed_continues(self, tmp_path):
        pdf = tmp_path / "empty.pdf"
        doc = fitz.open()
        doc.new_page()
        doc.save(str(pdf))
        doc.close()

        pdf_good = tmp_path / "good.pdf"
        _make_pdf(pdf_good, "Good content")

        output_dir = tmp_path / "reports" / "full_extraction"
        runner = FullRunner(output_dir=output_dir)
        result = runner.process([str(pdf), str(pdf_good)])

        assert result["completed"] == 1
        assert result["failed"] == 1

        assert len(list(output_dir.glob("good_*.json"))) == 1
        assert len(list(output_dir.glob("good_*.md"))) == 1


class TestAtomicManifest:
    def test_manifest_valid_after_single_process(self, tmp_path):
        pdf = tmp_path / "atomic.pdf"
        _make_pdf(pdf)

        output_dir = tmp_path / "reports" / "full_extraction"
        runner = FullRunner(output_dir=output_dir)
        runner.process([str(pdf)])

        manifest_path = output_dir / "manifest.json"
        assert manifest_path.exists()
        data = json.loads(manifest_path.read_text())
        assert "documents" in data
        assert "completed" in data
        assert "failed" in data

    def test_manifest_valid_after_multiple_processes(self, tmp_path):
        pdf1 = tmp_path / "a.pdf"
        pdf2 = tmp_path / "b.pdf"
        _make_pdf(pdf1)
        _make_pdf(pdf2)

        output_dir = tmp_path / "reports" / "full_extraction"
        runner = FullRunner(output_dir=output_dir)
        runner.process([str(pdf1)])
        runner.process([str(pdf2)])

        manifest = json.loads(output_dir.joinpath("manifest.json").read_text())
        assert manifest["total"] == 2
        assert manifest["completed"] == 2
        assert "a.pdf" in str(manifest["documents"])
        assert "b.pdf" in str(manifest["documents"])

    def test_no_temp_files_left_after_manifest_write(self, tmp_path):
        pdf = tmp_path / "clean.pdf"
        _make_pdf(pdf)

        output_dir = tmp_path / "reports" / "full_extraction"
        runner = FullRunner(output_dir=output_dir)
        runner.process([str(pdf)])

        temp_files = list(output_dir.glob("*.tmp"))
        assert len(temp_files) == 0
