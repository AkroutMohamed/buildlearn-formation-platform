from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from app.ai.acquisition.validator import DocumentValidator, ValidationResult


_PDF_MAGIC = b"%PDF-1.4\n%test content here for testing purposes\n"


class TestDocumentValidator:
    def test_compute_hash_is_deterministic(self):
        assert DocumentValidator.compute_hash(b"hello") == DocumentValidator.compute_hash(b"hello")
        assert DocumentValidator.compute_hash(b"hello") != DocumentValidator.compute_hash(b"world")

    def test_validate_url_empty_returns_error(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        result = validator.validate_url("")
        assert result.document_url == ""
        assert result.error == "Empty URL"
        assert result.is_pdf is False

    def test_validate_url_http_error(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.headers = {"Content-Type": "text/html"}

        with patch.object(validator._session, "head", return_value=mock_response):
            result = validator.validate_url("https://example.com/doc.pdf")

        assert result.http_status == 404
        assert result.is_pdf is False
        assert "404" in result.error

    def test_validate_url_invalid_content_type(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/html"}

        with patch.object(validator._session, "head", return_value=mock_response):
            result = validator.validate_url("https://example.com/doc.pdf")

        assert result.http_status == 200
        assert result.content_type == "text/html"
        assert result.is_pdf is False
        assert "Content-Type" in result.error

    def test_validate_url_valid_pdf(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/pdf"}

        with patch.object(validator._session, "head", return_value=mock_response):
            result = validator.validate_url("https://example.com/doc.pdf")

        assert result.http_status == 200
        assert result.content_type == "application/pdf"
        assert result.is_pdf is True
        assert result.error is None

    def test_validate_and_download_valid_pdf(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.iter_content = lambda chunk_size: [_PDF_MAGIC]

        with patch.object(validator._session, "get", return_value=mock_response):
            result = validator.validate_and_download("https://example.com/test.pdf", "gypsobat")

        assert result.is_pdf is True
        assert result.downloadable is True
        assert result.content_hash is not None
        assert result.file_path is not None
        assert Path(result.file_path).exists()
        saved_content = Path(result.file_path).read_bytes()
        assert saved_content[:5] == _PDF_MAGIC[:5]

    def test_validate_and_download_not_pdf_content(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.iter_content = lambda chunk_size: [b"<html>not a pdf</html>"]

        with patch.object(validator._session, "get", return_value=mock_response):
            result = validator.validate_and_download("https://example.com/page.html", "gypsobat")

        assert result.is_pdf is False
        assert result.downloadable is False
        assert "Content-Type" in result.error

    def test_validate_and_download_invalid_magic_bytes(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.iter_content = lambda chunk_size: [b"Not a PDF file at all!!!"]

        with patch.object(validator._session, "get", return_value=mock_response):
            result = validator.validate_and_download("https://example.com/bad.pdf", "gypsobat")

        assert result.is_pdf is False
        assert "magic" in result.error.lower()

    def test_validate_and_download_http_error(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.iter_content = lambda chunk_size: []

        with patch.object(validator._session, "get", return_value=mock_response):
            result = validator.validate_and_download("https://example.com/missing.pdf", "gypsobat")

        assert result.http_status == 404
        assert result.downloadable is False
        assert result.error is not None

    def test_validate_and_download_existing_file_same_hash(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)

        first_response = MagicMock()
        first_response.status_code = 200
        first_response.headers = {"Content-Type": "application/pdf"}
        first_response.iter_content = lambda chunk_size: [_PDF_MAGIC]
        first_response.content = _PDF_MAGIC

        with patch.object(validator._session, "get", return_value=first_response):
            result1 = validator.validate_and_download("https://example.com/doc.pdf", "gypsobat")

        assert Path(result1.file_path).exists()

        second_response = MagicMock()
        second_response.status_code = 200
        second_response.headers = {"Content-Type": "application/pdf"}
        second_response.iter_content = lambda chunk_size: [_PDF_MAGIC]
        second_response.content = _PDF_MAGIC

        with patch.object(validator._session, "get", return_value=second_response):
            result2 = validator.validate_and_download("https://example.com/doc.pdf", "gypsobat")

        assert result2.content_hash == result1.content_hash
        assert result2.file_path == result1.file_path

    def test_validate_url_redirect_follows(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.url = "https://example.com/final.pdf"

        with patch.object(validator._session, "head", return_value=mock_response) as mock_head:
            result = validator.validate_url("https://example.com/redirect.pdf")
            assert mock_head.call_args.kwargs["allow_redirects"] is True

    def test_validation_result_defaults(self):
        result = ValidationResult(document_url="https://example.com/test.pdf")
        assert result.document_url == "https://example.com/test.pdf"
        assert result.http_status is None
        assert result.is_pdf is False
        assert result.downloadable is False
        assert result.content_hash is None
        assert result.error is None

    def test_default_download_dir_resolved_once(self):
        validator = DocumentValidator()
        expected = Path(__file__).resolve().parent.parent.parent / "ai_data" / "raw"
        assert validator.download_dir.resolve() == expected.resolve()

    def test_default_download_dir_is_under_backend(self):
        validator = DocumentValidator()
        backend_dir = Path(__file__).resolve().parent.parent.parent
        assert "backend" in backend_dir.parts
        assert validator.download_dir.resolve() == (backend_dir / "ai_data" / "raw").resolve()

    def test_validate_url_encodes_spaces(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/pdf"}

        with patch.object(validator._session, "head", return_value=mock_response) as mock_head:
            result = validator.validate_url("https://example.com/path with spaces/file.pdf")

        assert result.is_pdf is True
        called_url = mock_head.call_args.args[0]
        assert "%20" in called_url

    def test_validate_and_download_encodes_spaces(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.iter_content.return_value = [_PDF_MAGIC + b"content"]

        with patch.object(validator._session, "get", return_value=mock_response) as mock_get:
            result = validator.validate_and_download("https://example.com/path with spaces/file.pdf", "test")

        assert result.is_pdf is True
        called_url = mock_get.call_args.args[0]
        assert "%20" in called_url
