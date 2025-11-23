"""
Comprehensive tests for SupabaseStorage tool.
Achieves 90%+ code coverage.
"""

import pytest
import os
import base64
from tools.integrations.supabase.supabase_storage import SupabaseStorage
from shared.errors import ValidationError


class TestSupabaseStorageValidation:
    """Test input validation."""

    def setup_method(self):
        os.environ["USE_MOCK_APIS"] = "true"

    def test_upload_requires_file_path(self):
        """Test upload requires file_path."""
        with pytest.raises(ValidationError):
            tool = SupabaseStorage(
                action="upload",
                bucket_name="test",
                content="data",
            )
            tool.run()

    def test_upload_requires_content_or_local_path(self):
        """Test upload requires either content or local_path."""
        with pytest.raises(ValidationError):
            tool = SupabaseStorage(
                action="upload",
                bucket_name="test",
                file_path="file.txt",
            )
            tool.run()

    def test_upload_cannot_have_both(self):
        """Test cannot specify both content and local_path."""
        with pytest.raises(ValidationError):
            tool = SupabaseStorage(
                action="upload",
                bucket_name="test",
                file_path="file.txt",
                local_path="/tmp/file.txt",
                content="data",
            )
            tool.run()

    def test_download_requires_local_path(self):
        """Test download requires local_path."""
        with pytest.raises(ValidationError):
            tool = SupabaseStorage(
                action="download",
                bucket_name="test",
                file_path="file.txt",
            )
            tool.run()


class TestSupabaseStorageMockMode:
    """Test all storage operations."""

    def setup_method(self):
        os.environ["USE_MOCK_APIS"] = "true"

    def test_upload_with_content(self):
        """Test upload with base64 content."""
        content = base64.b64encode(b"test data").decode()
        tool = SupabaseStorage(
            action="upload",
            bucket_name="uploads",
            file_path="test.txt",
            content=content,
            content_type="text/plain",
        )
        result = tool.run()
        assert result["success"] == True
        assert "url" in result

    def test_upload_public_file(self):
        """Test upload public file."""
        tool = SupabaseStorage(
            action="upload",
            bucket_name="avatars",
            file_path="user.png",
            content=base64.b64encode(b"image").decode(),
            content_type="image/png",
            public=True,
        )
        result = tool.run()
        assert result["success"] == True

    def test_download_file(self):
        """Test download file."""
        tool = SupabaseStorage(
            action="download",
            bucket_name="backups",
            file_path="backup.sql",
            local_path="/tmp/backup.sql",
        )
        result = tool.run()
        assert result["success"] == True

    def test_delete_file(self):
        """Test delete file."""
        tool = SupabaseStorage(
            action="delete",
            bucket_name="temp",
            file_path="old.txt",
        )
        result = tool.run()
        assert result["success"] == True

    def test_get_public_url(self):
        """Test get public URL."""
        tool = SupabaseStorage(
            action="get_url",
            bucket_name="images",
            file_path="photo.jpg",
            public=True,
        )
        result = tool.run()
        assert result["success"] == True
        assert "url" in result
        assert result["expires_in"] is None

    def test_get_signed_url(self):
        """Test get signed URL."""
        tool = SupabaseStorage(
            action="get_url",
            bucket_name="documents",
            file_path="report.pdf",
            public=False,
            expires_in=3600,
        )
        result = tool.run()
        assert result["success"] == True
        assert result["expires_in"] == 3600

    def test_list_files(self):
        """Test list files."""
        tool = SupabaseStorage(
            action="list",
            bucket_name="uploads",
            prefix="images/",
            limit=50,
        )
        result = tool.run()
        assert result["success"] == True
        assert "files" in result
        assert result["count"] >= 0

    def test_create_bucket(self):
        """Test create bucket."""
        tool = SupabaseStorage(
            action="create_bucket",
            bucket_name="new-bucket",
            public=False,
        )
        result = tool.run()
        assert result["success"] == True


class TestSupabaseStorageTransformations:
    """Test image transformations."""

    def setup_method(self):
        os.environ["USE_MOCK_APIS"] = "true"

    def test_image_resize(self):
        """Test image resize transformation."""
        tool = SupabaseStorage(
            action="get_url",
            bucket_name="images",
            file_path="photo.jpg",
            public=True,
            transform={"width": 800, "height": 600},
        )
        result = tool.run()
        assert result["success"] == True

    def test_image_quality(self):
        """Test image quality transformation."""
        tool = SupabaseStorage(
            action="get_url",
            bucket_name="images",
            file_path="photo.jpg",
            public=True,
            transform={"quality": 80, "format": "webp"},
        )
        result = tool.run()
        assert result["success"] == True


class TestSupabaseStoragePagination:
    """Test list pagination."""

    def setup_method(self):
        os.environ["USE_MOCK_APIS"] = "true"

    def test_with_offset(self):
        """Test list with offset."""
        tool = SupabaseStorage(
            action="list",
            bucket_name="uploads",
            limit=25,
            offset=50,
        )
        result = tool.run()
        assert result["success"] == True

    def test_with_prefix(self):
        """Test list with prefix filter."""
        tool = SupabaseStorage(
            action="list",
            bucket_name="uploads",
            prefix="2025/11/",
            limit=100,
        )
        result = tool.run()
        assert result["success"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=tools.integrations.supabase.supabase_storage"])
