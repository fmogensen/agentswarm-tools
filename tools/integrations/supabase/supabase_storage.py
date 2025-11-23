"""
Supabase Storage Tool

Upload, download, and manage files in Supabase Storage buckets.
Supports public/private buckets, file transformations, and CDN URLs.
"""

from typing import Any, Dict, List, Optional, Literal
from pydantic import Field
import os
import json
import base64

from shared.base import BaseTool
from shared.errors import ValidationError, APIError, AuthenticationError, ResourceNotFoundError


class SupabaseStorage(BaseTool):
    """
    Manage files in Supabase Storage buckets.

    This tool provides complete file storage operations including upload, download,
    delete, list, and URL generation. Supports public/private buckets, file
    transformations, and CDN delivery.

    Args:
        action: Storage action - 'upload', 'download', 'delete', 'list', 'get_url', 'create_bucket'
        bucket_name: Name of the storage bucket
        file_path: Path to file in bucket (for upload/download/delete/get_url)
        local_path: Local file path (for upload/download)
        content: File content as base64 string (alternative to local_path for upload)
        content_type: MIME type of the file (e.g., 'image/png', 'application/pdf')
        public: Whether bucket/file is public (default: False)
        transform: Image transformation options (width, height, quality, format)
        expires_in: URL expiration time in seconds (for signed URLs, default: 3600)
        prefix: Filter files by prefix (for list action)
        limit: Maximum number of files to list (default: 100)
        offset: Offset for pagination (default: 0)

    Returns:
        Dict containing:
            - success (bool): Whether the operation was successful
            - action (str): Action performed
            - file_path (str): Path to file in bucket
            - url (str): Public or signed URL (for get_url action)
            - files (list): List of files (for list action)
            - metadata (dict): Tool execution metadata

    Example:
        >>> # Upload file
        >>> tool = SupabaseStorage(
        ...     action="upload",
        ...     bucket_name="avatars",
        ...     file_path="users/user123.png",
        ...     local_path="/path/to/avatar.png",
        ...     content_type="image/png",
        ...     public=True
        ... )
        >>> result = tool.run()
        >>> print(result['url'])

        >>> # Get signed URL
        >>> tool = SupabaseStorage(
        ...     action="get_url",
        ...     bucket_name="documents",
        ...     file_path="reports/2025-q4.pdf",
        ...     expires_in=3600
        ... )
        >>> result = tool.run()
        >>> print(result['url'])

        >>> # List files
        >>> tool = SupabaseStorage(
        ...     action="list",
        ...     bucket_name="uploads",
        ...     prefix="images/",
        ...     limit=50
        ... )
        >>> result = tool.run()
        >>> for file in result['files']:
        ...     print(f"{file['name']}: {file['size']} bytes")
    """

    # Tool metadata
    tool_name: str = "supabase_storage"
    tool_category: str = "integrations"

    # Required parameters
    action: Literal["upload", "download", "delete", "list", "get_url", "create_bucket"] = Field(
        ...,
        description="Storage action to perform",
    )
    bucket_name: str = Field(
        ...,
        description="Name of the storage bucket",
        min_length=1,
        max_length=63,
    )

    # Optional parameters
    file_path: Optional[str] = Field(
        None,
        description="Path to file in bucket",
    )
    local_path: Optional[str] = Field(
        None,
        description="Local file path for upload/download",
    )
    content: Optional[str] = Field(
        None,
        description="File content as base64 string",
    )
    content_type: Optional[str] = Field(
        None,
        description="MIME type of the file",
    )
    public: bool = Field(
        False,
        description="Whether bucket/file is public",
    )
    transform: Optional[Dict[str, Any]] = Field(
        None,
        description="Image transformation options (width, height, quality, format)",
    )
    expires_in: int = Field(
        3600,
        description="URL expiration time in seconds for signed URLs",
        ge=1,
        le=604800,  # Max 7 days
    )
    prefix: Optional[str] = Field(
        None,
        description="Filter files by prefix",
    )
    limit: int = Field(
        100,
        description="Maximum number of files to list",
        ge=1,
        le=1000,
    )
    offset: int = Field(
        0,
        description="Offset for pagination",
        ge=0,
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute the storage operation."""
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()
            return {
                "success": True,
                "action": self.action,
                **result,
                "metadata": {
                    "tool_name": self.tool_name,
                    "bucket": self.bucket_name,
                    "file_path": self.file_path,
                },
            }
        except Exception as e:
            raise APIError(
                f"Storage operation failed: {e}",
                tool_name=self.tool_name,
                api_name="supabase_storage",
            )

    def _validate_parameters(self) -> None:
        """Validate input parameters based on action."""
        # Validate action-specific requirements
        if self.action in ["upload", "download", "delete", "get_url"]:
            if not self.file_path:
                raise ValidationError(
                    f"File path required for {self.action} action",
                    tool_name=self.tool_name,
                    field="file_path",
                )

        if self.action == "upload":
            if not self.local_path and not self.content:
                raise ValidationError(
                    "Either local_path or content required for upload",
                    tool_name=self.tool_name,
                    field="local_path",
                )

            if self.local_path and self.content:
                raise ValidationError(
                    "Cannot specify both local_path and content",
                    tool_name=self.tool_name,
                    field="local_path",
                )

        if self.action == "download":
            if not self.local_path:
                raise ValidationError(
                    "Local path required for download action",
                    tool_name=self.tool_name,
                    field="local_path",
                )

        # Validate bucket name
        if not self.bucket_name or not self.bucket_name.strip():
            raise ValidationError(
                "Bucket name cannot be empty",
                tool_name=self.tool_name,
                field="bucket_name",
            )

        # Validate transform options if provided
        if self.transform:
            valid_keys = ["width", "height", "quality", "format", "resize"]
            for key in self.transform.keys():
                if key not in valid_keys:
                    raise ValidationError(
                        f"Invalid transform option: {key}. Valid: {valid_keys}",
                        tool_name=self.tool_name,
                        field="transform",
                    )

    def _should_use_mock(self) -> bool:
        """Check if mock mode is enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        result = {"success": True, "action": self.action}

        if self.action == "upload":
            result["file_path"] = self.file_path
            result["url"] = f"https://mock-supabase.co/storage/v1/object/{self.bucket_name}/{self.file_path}"
            result["size"] = 1024

        elif self.action == "download":
            result["file_path"] = self.file_path
            result["local_path"] = self.local_path
            result["size"] = 2048
            result["content_type"] = self.content_type or "application/octet-stream"

        elif self.action == "delete":
            result["file_path"] = self.file_path
            result["message"] = f"File {self.file_path} deleted"

        elif self.action == "get_url":
            if self.public:
                result["url"] = f"https://mock-supabase.co/storage/v1/object/public/{self.bucket_name}/{self.file_path}"
            else:
                result["url"] = f"https://mock-supabase.co/storage/v1/object/sign/{self.bucket_name}/{self.file_path}?token=mock_token_12345"
            result["expires_in"] = self.expires_in if not self.public else None

        elif self.action == "list":
            result["files"] = [
                {
                    "name": f"file_{i}.txt",
                    "id": f"mock_file_{i}",
                    "created_at": "2025-11-23T10:00:00Z",
                    "updated_at": "2025-11-23T10:00:00Z",
                    "size": 1024 * (i + 1),
                    "metadata": {"content_type": "text/plain"},
                }
                for i in range(min(self.limit, 3))
            ]
            result["count"] = len(result["files"])

        elif self.action == "create_bucket":
            result["bucket_name"] = self.bucket_name
            result["public"] = self.public
            result["message"] = f"Bucket {self.bucket_name} created"

        result["metadata"] = {
            "tool_name": self.tool_name,
            "bucket": self.bucket_name,
            "mock_mode": True,
        }

        return result

    def _process(self) -> Dict[str, Any]:
        """Process storage operation with Supabase."""
        # Get Supabase credentials
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise AuthenticationError(
                "Missing SUPABASE_URL or SUPABASE_KEY environment variables",
                tool_name=self.tool_name,
                api_name="supabase",
            )

        # Import Supabase client
        try:
            from supabase import create_client, Client
        except ImportError:
            raise APIError(
                "Supabase SDK not installed. Run: pip install supabase",
                tool_name=self.tool_name,
                api_name="supabase",
            )

        # Create client
        try:
            supabase: Client = create_client(supabase_url, supabase_key)
        except Exception as e:
            raise AuthenticationError(
                f"Failed to create Supabase client: {e}",
                tool_name=self.tool_name,
                api_name="supabase",
            )

        # Execute action
        if self.action == "upload":
            return self._upload(supabase)
        elif self.action == "download":
            return self._download(supabase)
        elif self.action == "delete":
            return self._delete(supabase)
        elif self.action == "get_url":
            return self._get_url(supabase)
        elif self.action == "list":
            return self._list_files(supabase)
        elif self.action == "create_bucket":
            return self._create_bucket(supabase)
        else:
            raise ValidationError(
                f"Unknown action: {self.action}",
                tool_name=self.tool_name,
            )

    def _upload(self, supabase: Any) -> Dict[str, Any]:
        """Upload file to bucket."""
        try:
            # Read file content
            if self.local_path:
                with open(self.local_path, "rb") as f:
                    file_content = f.read()
            else:
                # Decode base64 content
                file_content = base64.b64decode(self.content)

            # Upload file
            options = {}
            if self.content_type:
                options["content_type"] = self.content_type

            response = supabase.storage.from_(self.bucket_name).upload(
                self.file_path, file_content, options
            )

            # Get public URL if bucket is public
            url = None
            if self.public:
                url = supabase.storage.from_(self.bucket_name).get_public_url(self.file_path)

            return {
                "file_path": self.file_path,
                "url": url,
                "size": len(file_content),
            }

        except FileNotFoundError:
            raise ResourceNotFoundError(
                f"Local file not found: {self.local_path}",
                tool_name=self.tool_name,
            )
        except Exception as e:
            raise APIError(
                f"Upload failed: {e}",
                tool_name=self.tool_name,
                api_name="supabase_storage",
            )

    def _download(self, supabase: Any) -> Dict[str, Any]:
        """Download file from bucket."""
        try:
            # Download file
            response = supabase.storage.from_(self.bucket_name).download(self.file_path)

            # Save to local path
            with open(self.local_path, "wb") as f:
                f.write(response)

            return {
                "file_path": self.file_path,
                "local_path": self.local_path,
                "size": len(response),
            }

        except Exception as e:
            raise APIError(
                f"Download failed: {e}",
                tool_name=self.tool_name,
                api_name="supabase_storage",
            )

    def _delete(self, supabase: Any) -> Dict[str, Any]:
        """Delete file from bucket."""
        try:
            supabase.storage.from_(self.bucket_name).remove([self.file_path])

            return {
                "file_path": self.file_path,
                "message": f"File {self.file_path} deleted",
            }

        except Exception as e:
            raise APIError(
                f"Delete failed: {e}",
                tool_name=self.tool_name,
                api_name="supabase_storage",
            )

    def _get_url(self, supabase: Any) -> Dict[str, Any]:
        """Get public or signed URL for file."""
        try:
            if self.public:
                # Get public URL
                url = supabase.storage.from_(self.bucket_name).get_public_url(self.file_path)

                # Apply transformations if specified
                if self.transform:
                    query_params = []
                    for key, value in self.transform.items():
                        query_params.append(f"{key}={value}")
                    url += "?" + "&".join(query_params)

                return {
                    "url": url,
                    "expires_in": None,
                }
            else:
                # Create signed URL
                response = supabase.storage.from_(self.bucket_name).create_signed_url(
                    self.file_path, self.expires_in
                )

                return {
                    "url": response["signedURL"],
                    "expires_in": self.expires_in,
                }

        except Exception as e:
            raise APIError(
                f"URL generation failed: {e}",
                tool_name=self.tool_name,
                api_name="supabase_storage",
            )

    def _list_files(self, supabase: Any) -> Dict[str, Any]:
        """List files in bucket."""
        try:
            options = {
                "limit": self.limit,
                "offset": self.offset,
            }

            if self.prefix:
                options["prefix"] = self.prefix

            response = supabase.storage.from_(self.bucket_name).list(
                path=self.prefix or "", options=options
            )

            files = []
            for item in response:
                files.append(
                    {
                        "name": item.get("name"),
                        "id": item.get("id"),
                        "created_at": item.get("created_at"),
                        "updated_at": item.get("updated_at"),
                        "size": item.get("metadata", {}).get("size", 0),
                        "metadata": item.get("metadata", {}),
                    }
                )

            return {
                "files": files,
                "count": len(files),
            }

        except Exception as e:
            raise APIError(
                f"List files failed: {e}",
                tool_name=self.tool_name,
                api_name="supabase_storage",
            )

    def _create_bucket(self, supabase: Any) -> Dict[str, Any]:
        """Create new storage bucket."""
        try:
            supabase.storage.create_bucket(self.bucket_name, {"public": self.public})

            return {
                "bucket_name": self.bucket_name,
                "public": self.public,
                "message": f"Bucket {self.bucket_name} created",
            }

        except Exception as e:
            raise APIError(
                f"Create bucket failed: {e}",
                tool_name=self.tool_name,
                api_name="supabase_storage",
            )


if __name__ == "__main__":
    # Test the tool
    print("Testing SupabaseStorage...")
    print("=" * 60)

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Upload file
    print("\n1. Testing file upload...")
    tool = SupabaseStorage(
        action="upload",
        bucket_name="avatars",
        file_path="users/user123.png",
        content=base64.b64encode(b"fake image data").decode(),
        content_type="image/png",
        public=True,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"File path: {result.get('file_path')}")
    print(f"URL: {result.get('url')}")
    print(f"Size: {result.get('size')} bytes")
    assert result.get("success") == True
    assert "url" in result

    # Test 2: Get public URL
    print("\n2. Testing get public URL...")
    tool = SupabaseStorage(
        action="get_url",
        bucket_name="avatars",
        file_path="users/user123.png",
        public=True,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"URL: {result.get('url')}")
    print(f"Expires: {result.get('expires_in')}")
    assert result.get("success") == True
    assert result.get("url") is not None

    # Test 3: Get signed URL
    print("\n3. Testing get signed URL...")
    tool = SupabaseStorage(
        action="get_url",
        bucket_name="documents",
        file_path="reports/2025-q4.pdf",
        public=False,
        expires_in=7200,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Signed URL: {result.get('url')[:60]}...")
    print(f"Expires in: {result.get('expires_in')} seconds")
    assert result.get("success") == True
    assert result.get("expires_in") == 7200

    # Test 4: List files
    print("\n4. Testing list files...")
    tool = SupabaseStorage(
        action="list", bucket_name="uploads", prefix="images/", limit=50, offset=0
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Files found: {result.get('count')}")
    for file in result.get("files", []):
        print(f"  - {file.get('name')}: {file.get('size')} bytes")
    assert result.get("success") == True
    assert "files" in result

    # Test 5: Delete file
    print("\n5. Testing delete file...")
    tool = SupabaseStorage(
        action="delete", bucket_name="temp", file_path="uploads/old_file.txt"
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Message: {result.get('message')}")
    assert result.get("success") == True

    # Test 6: Create bucket
    print("\n6. Testing create bucket...")
    tool = SupabaseStorage(
        action="create_bucket", bucket_name="new-bucket", public=False
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Bucket: {result.get('bucket_name')}")
    print(f"Public: {result.get('public')}")
    assert result.get("success") == True

    # Test 7: Download file
    print("\n7. Testing download file...")
    tool = SupabaseStorage(
        action="download",
        bucket_name="backups",
        file_path="db/backup-2025-11-23.sql",
        local_path="/tmp/backup.sql",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Downloaded to: {result.get('local_path')}")
    print(f"Size: {result.get('size')} bytes")
    assert result.get("success") == True

    # Test 8: Image transformation
    print("\n8. Testing image transformation...")
    tool = SupabaseStorage(
        action="get_url",
        bucket_name="images",
        file_path="photos/landscape.jpg",
        public=True,
        transform={"width": 800, "height": 600, "quality": 80, "format": "webp"},
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Transformed URL: {result.get('url')}")
    assert result.get("success") == True

    # Test 9: Error handling - missing file_path
    print("\n9. Testing error handling (missing file_path)...")
    try:
        tool = SupabaseStorage(action="download", bucket_name="test")
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except ValidationError as e:
        print(f"Correctly caught error: {e.message}")

    # Test 10: Error handling - upload without content
    print("\n10. Testing error handling (upload without content)...")
    try:
        tool = SupabaseStorage(
            action="upload", bucket_name="test", file_path="file.txt"
        )
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except ValidationError as e:
        print(f"Correctly caught error: {e.message}")

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
