# SupabaseStorage

File upload, download, and CDN management for Supabase Storage.

## Overview

Manage files in Supabase Storage buckets with support for public/private files, signed URLs, image transformations, and batch operations.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | str | Yes | upload, download, delete, list, get_url, create_bucket |
| `bucket_name` | str | Yes | Storage bucket name |
| `file_path` | str | Optional | Path to file in bucket |
| `local_path` | str | Optional | Local file path |
| `content` | str | Optional | File content as base64 |
| `content_type` | str | Optional | MIME type |
| `public` | bool | No | Public bucket/file (default: False) |
| `transform` | dict | Optional | Image transformations |
| `expires_in` | int | No | URL expiration in seconds (default: 3600) |
| `prefix` | str | Optional | Filter files by prefix |
| `limit` | int | No | Max files to list (default: 100) |
| `offset` | int | No | Pagination offset |

## Examples

### Upload File

```python
from tools.integrations.supabase import SupabaseStorage
import base64

# Upload from base64 content
with open("avatar.png", "rb") as f:
    content = base64.b64encode(f.read()).decode()

tool = SupabaseStorage(
    action="upload",
    bucket_name="avatars",
    file_path="users/user123.png",
    content=content,
    content_type="image/png",
    public=True
)
result = tool.run()
print(f"Uploaded: {result['url']}")
```

### Get URL

```python
# Public URL
tool = SupabaseStorage(
    action="get_url",
    bucket_name="avatars",
    file_path="users/user123.png",
    public=True
)
result = tool.run()

# Signed URL (private files)
tool = SupabaseStorage(
    action="get_url",
    bucket_name="documents",
    file_path="report.pdf",
    public=False,
    expires_in=3600  # 1 hour
)
result = tool.run()
```

### Image Transformation

```python
# Resize and optimize image
tool = SupabaseStorage(
    action="get_url",
    bucket_name="images",
    file_path="photo.jpg",
    public=True,
    transform={
        "width": 800,
        "height": 600,
        "quality": 80,
        "format": "webp"
    }
)
result = tool.run()
```

### List Files

```python
# List all files in bucket
tool = SupabaseStorage(
    action="list",
    bucket_name="uploads",
    prefix="2025/11/",
    limit=100,
    offset=0
)
result = tool.run()

for file in result['files']:
    print(f"{file['name']}: {file['size']} bytes")
```

### Download File

```python
# Download to local file
tool = SupabaseStorage(
    action="download",
    bucket_name="backups",
    file_path="db/backup.sql",
    local_path="/tmp/backup.sql"
)
result = tool.run()
```

## Use Cases

### User Avatars

```python
# Upload avatar
upload = SupabaseStorage(
    action="upload",
    bucket_name="avatars",
    file_path=f"users/{user_id}.png",
    content=avatar_base64,
    public=True
)
result = upload.run()
avatar_url = result['url']

# Get optimized version
optimized = SupabaseStorage(
    action="get_url",
    bucket_name="avatars",
    file_path=f"users/{user_id}.png",
    public=True,
    transform={"width": 200, "height": 200}
)
url = optimized.run()['url']
```

### Document Management

```python
# Upload private document
upload = SupabaseStorage(
    action="upload",
    bucket_name="documents",
    file_path=f"contracts/{contract_id}.pdf",
    content=pdf_base64,
    public=False
)
result = upload.run()

# Generate signed URL for download
signed = SupabaseStorage(
    action="get_url",
    bucket_name="documents",
    file_path=f"contracts/{contract_id}.pdf",
    expires_in=1800  # 30 minutes
)
download_url = signed.run()['url']
```

### Backup Storage

```python
# Upload backup
backup = SupabaseStorage(
    action="upload",
    bucket_name="backups",
    file_path=f"db/{date}/backup.sql",
    local_path="/tmp/backup.sql"
)
result = backup.run()

# List all backups
list_tool = SupabaseStorage(
    action="list",
    bucket_name="backups",
    prefix="db/",
    limit=50
)
backups = list_tool.run()
```

---

**Version:** 1.0.0
