import asyncio
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi import HTTPException, UploadFile
from starlette.datastructures import Headers

from app.services import recorded_video_service as module
from app.services.recorded_video_service import RecordedVideoService


@pytest.fixture
def service(tmp_path, monkeypatch):
    monkeypatch.setattr(module, "settings", SimpleNamespace(upload_path=tmp_path))
    repository = Mock()
    repository.get_by_lesson.return_value = None
    repository.create.side_effect = lambda video: video
    repository.update.side_effect = lambda video, values: (video.__dict__.update(values), video)[1]
    service = RecordedVideoService(repository, Mock())
    service._get_lesson_for_owner = Mock(return_value=SimpleNamespace(id=uuid4()))
    return service


def upload(service, content=b"\x00\x00\x00\x18ftypisomvideo", filename="clip.mp4", mime="video/mp4"):
    file = UploadFile(BytesIO(content), filename=filename, headers=Headers({"content-type": mime}))
    return asyncio.run(service.upload_video(SimpleNamespace(id=uuid4()), uuid4(), uuid4(), file, " My video ", 12))


def test_local_upload_stores_generated_name_and_metadata(service, tmp_path):
    video = upload(service, filename="../../clip.mp4")
    assert video.title == "My video"
    assert video.duration_seconds == 12
    assert video.video_url.startswith("/uploads/videos/")
    assert len(list((tmp_path / "videos").iterdir())) == 1
    assert "clip" not in video.video_url


@pytest.mark.parametrize("content,filename,mime", [(b"", "x.mp4", "video/mp4"), (b"fake", "x.mp4", "video/mp4"), (b"anything", "x.exe", "video/mp4"), (b"anything", "x.mp4", "text/plain")])
def test_invalid_files_rejected_without_records(service, tmp_path, content, filename, mime):
    with pytest.raises(HTTPException):
        upload(service, content, filename, mime)
    service.repository.create.assert_not_called()
    assert not list(tmp_path.rglob("*.mp4"))


def test_size_limit_cleans_partial_file(service, tmp_path):
    service.MAX_VIDEO_BYTES = 10
    with pytest.raises(HTTPException) as error:
        upload(service)
    assert error.value.status_code == 413
    assert not list(tmp_path.rglob("*.mp4"))


def test_authorization_precedes_file_storage(service, tmp_path):
    service._get_lesson_for_owner.side_effect = HTTPException(status_code=403)
    with pytest.raises(HTTPException):
        upload(service)
    assert not list(tmp_path.iterdir())


def test_database_failure_removes_new_file(service, tmp_path):
    service.repository.create.side_effect = RuntimeError("DB failure")
    with pytest.raises(RuntimeError):
        upload(service)
    assert not list(tmp_path.rglob("*.mp4"))


def test_replacement_deletes_old_managed_file_after_save(service, tmp_path):
    original = upload(service)
    old_path = tmp_path / "videos" / original.video_url.rsplit("/", 1)[1]
    service.repository.get_by_lesson.return_value = original
    replacement = upload(service)
    assert not old_path.exists()
    assert (tmp_path / "videos" / replacement.video_url.rsplit("/", 1)[1]).exists()


def test_failed_replacement_preserves_old_file(service, tmp_path):
    original = upload(service)
    old_path = tmp_path / "videos" / original.video_url.rsplit("/", 1)[1]
    service.repository.get_by_lesson.return_value = original
    service.repository.update.side_effect = RuntimeError("DB failure")
    with pytest.raises(RuntimeError):
        upload(service)
    assert list((tmp_path / "videos").iterdir()) == [old_path]


@pytest.mark.parametrize("content,filename,mime", [(b"\x1a\x45\xdf\xa3webm", "x.webm", "video/webm"), (b"OggSvideo", "x.ogv", "video/ogg")])
def test_other_browser_video_formats(service, content, filename, mime):
    assert upload(service, content, filename, mime).video_url.endswith(filename[1:])


def test_delete_removes_managed_upload(service, tmp_path):
    video = upload(service)
    service.repository.get_by_lesson.return_value = video
    service.delete_video(SimpleNamespace(id=uuid4()), uuid4(), uuid4())
    assert not list(tmp_path.rglob("*.mp4"))


def test_cleanup_cannot_delete_unmanaged_paths(service, tmp_path):
    protected = tmp_path / "keep.mp4"
    protected.write_bytes(b"keep")
    service._remove_uploaded_file("/uploads/videos/../../keep.mp4")
    service._remove_uploaded_file("/uploads/keep.mp4")
    assert protected.read_bytes() == b"keep"


def test_multiple_uploads_append_without_replacing_primary(service, tmp_path, monkeypatch):
    resources = []
    repository = Mock()
    repository.create.side_effect = lambda resource: (resources.append(resource), resource)[1]
    monkeypatch.setattr(module, "ResourceRepository", lambda db: repository)
    primary = upload(service)
    service.repository.get_by_lesson.return_value = primary
    for name in ("first.mp4", "second.mp4"):
        file = UploadFile(BytesIO(b"\x00\x00\x00\x18ftypisomvideo"), filename=name, headers=Headers({"content-type": "video/mp4"}))
        asyncio.run(service.upload_video(SimpleNamespace(id=uuid4()), uuid4(), uuid4(), file, name, append=True))
    assert len(resources) == 2
    assert len(list((tmp_path / "videos").iterdir())) == 3
    assert resources[0].url != resources[1].url != primary.video_url
    assert all(resource.resource_type == "video/mp4" for resource in resources)
    service.repository.update.assert_not_called()


def test_failed_attachment_save_removes_only_new_file(service, tmp_path, monkeypatch):
    repository = Mock()
    repository.create.side_effect = RuntimeError("DB failure")
    monkeypatch.setattr(module, "ResourceRepository", lambda db: repository)
    primary = upload(service)
    file = UploadFile(BytesIO(b"\x00\x00\x00\x18ftypisomvideo"), filename="next.mp4", headers=Headers({"content-type": "video/mp4"}))
    with pytest.raises(RuntimeError):
        asyncio.run(service.upload_video(SimpleNamespace(id=uuid4()), uuid4(), uuid4(), file, "next", append=True))
    assert len(list((tmp_path / "videos").iterdir())) == 1
    assert (tmp_path / "videos" / primary.video_url.rsplit("/", 1)[1]).exists()
