# Package Registry API Specifications

## Overview

This document provides comprehensive API specifications for implementing package registries compatible with PyPI (Python), npm (Node.js), and Cargo (Rust). Each registry has distinct patterns, but common architectural principles can be abstracted.

## 🐍 PyPI Simple Repository API (PEP 503)

### Specification Source
- **Primary**: [PEP 503 - Simple Repository API](https://peps.python.org/pep-0503/)
- **Implementation Reference**: [pypiserver](https://github.com/pypiserver/pypiserver)

### Required Endpoints

#### 1. Root Index
```
GET /simple/
```
- **Response**: HTML5 page with anchor elements for each project
- **Format**: `<a href="/simple/{normalized-name}/">{display-name}</a>`
- **Content-Type**: `text/html`

#### 2. Package Index
```
GET /simple/{package-name}/
```
- **Response**: HTML5 page with anchor elements for each package file
- **Format**: `<a href="../../packages/{filename}#{hash}">{filename}</a>`
- **Content-Type**: `text/html`

#### 3. File Download
```
GET /packages/{filename}
```
- **Response**: Package files (.whl, .tar.gz)
- **Content-Type**: `application/zip` (wheels), `application/gzip` (sdist)

### Package Name Normalization
```python
import re
def normalize_package_name(name):
    return re.sub(r"[-_.]+", "-", name).lower()
```

### HTML Format Requirements
- Must be valid HTML5 with proper `<!DOCTYPE html>`
- URLs ending in HTML pages must terminate with `/`
- Optional attributes:
  - `data-requires-python=">=3.8"` - Python version compatibility
  - `data-gpg-sig="true"` - GPG signature presence
- Hash fragments: `#sha256=abc123...` (recommended)

### Authentication
- Optional HTTP Basic Auth for publishing
- No authentication required for downloads

## 📦 npm Registry API

### Specification Source
- **Primary**: [npm Registry API](https://github.com/npm/registry/blob/main/docs/REGISTRY-API.md)
- **Implementation Reference**: [verdaccio](https://github.com/verdaccio/verdaccio)

### Required Endpoints

#### 1. Package Metadata
```
GET /{package}
```
- **Response**: Complete package metadata including all versions
- **Content-Type**: `application/json`

#### 2. Specific Version
```
GET /{package}/{version}
```
- **Response**: Metadata for specific version
- **Content-Type**: `application/json`

#### 3. Tarball Download
```
GET /{package}/-/{package}-{version}.tgz
```
- **Response**: Package tarball
- **Content-Type**: `application/gzip`

#### 4. Search (Optional)
```
GET /-/v1/search?text={query}&size={limit}&from={offset}
```
- **Response**: Search results with package metadata
- **Content-Type**: `application/json`

### Package Metadata Schema
```json
{
  "_id": "package-name",
  "name": "package-name",
  "description": "Package description",
  "versions": {
    "1.0.0": {
      "name": "package-name",
      "version": "1.0.0",
      "description": "Version description",
      "main": "index.js",
      "dependencies": {},
      "devDependencies": {},
      "peerDependencies": {},
      "dist": {
        "tarball": "http://registry.com/package/-/package-1.0.0.tgz",
        "shasum": "sha1-hash",
        "integrity": "sha512-hash"
      }
    }
  },
  "dist-tags": {
    "latest": "1.0.0"
  },
  "time": {
    "created": "2023-01-01T00:00:00.000Z",
    "modified": "2023-01-01T00:00:00.000Z",
    "1.0.0": "2023-01-01T00:00:00.000Z"
  }
}
```

### Scoped Packages
- Format: `@scope/package-name`
- URL encoding: `@scope%2Fpackage-name`

### Authentication
- Bearer token via `Authorization: Bearer <token>` header
- Required for publishing, optional for downloads

## 🦀 Cargo Registry API

### Specification Source
- **Primary**: [Cargo Registry Web API](https://doc.rust-lang.org/cargo/reference/registry-web-api.html)
- **Index Format**: [Cargo Registry Index](https://doc.rust-lang.org/cargo/reference/registry-index.html)
- **Implementation Reference**: [alexandrie](https://github.com/Hirevo/alexandrie)

### Required Endpoints

#### 1. Crate Search/List
```
GET /api/v1/crates?q={query}&per_page={limit}&page={page}
```
- **Response**: List of crates with search capability
- **Content-Type**: `application/json`

#### 2. Crate Metadata
```
GET /api/v1/crates/{crate}
```
- **Response**: Crate information and versions
- **Content-Type**: `application/json`

#### 3. Download Redirect
```
GET /api/v1/crates/{crate}/{version}/download
```
- **Response**: Redirect to actual .crate file
- **Status**: `302 Found`

#### 4. Publishing (Optional)
```
PUT /api/v1/crates/new
```
- **Request**: Multipart form with metadata and .crate file
- **Content-Type**: `multipart/form-data`
- **Authentication**: Required

### Registry Index Structure

The index is a Git repository with specific file organization:

```
config.json                 # Registry configuration
{first-char}/{name}         # 1-character names
{first-char}/{second-char}/{name}  # 2-character names
{first-char}/{first-char}/{name}   # 3+ character names (first two chars)
```

#### Index File Format
Each line contains a JSON object for one version:
```json
{"name":"serde","vers":"1.0.0","deps":[{"name":"serde_derive","req":"^1.0","features":[],"optional":false,"default_features":true,"target":null,"kind":"normal"}],"cksum":"abc123","features":{},"yanked":false,"v":2}
```

#### Configuration (config.json)
```json
{
  "dl": "https://registry.com/api/v1/crates/{crate}/{version}/download",
  "api": "https://registry.com/api/"
}
```

### Authentication
- API token via `Authorization: <token>` header
- Required for publishing and ownership management

## 🔄 Common Patterns and Abstractions

### Shared Architectural Elements

#### 1. File Serving Strategy
All registries separate API endpoints from file serving:
- **API Endpoints**: Dynamic content (JSON/HTML) with metadata
- **File Endpoints**: Static content with proper caching headers
- **CDN Support**: Files can be served from different domains/CDNs

#### 2. Content Negotiation
- **MIME Types**: Critical for client compatibility
- **Caching Headers**: `Cache-Control`, `ETag` for performance
- **Compression**: gzip encoding for responses

#### 3. Authentication Patterns
- **Stateless**: No server-side sessions
- **Token-based**: API keys or Bearer tokens
- **Optional Downloads**: Public registries allow anonymous downloads
- **Required Publishing**: All registries require auth for uploads

#### 4. Error Handling
Standard HTTP status codes:
- `200 OK` - Successful operation
- `302 Found` - Redirect (Cargo downloads)
- `400 Bad Request` - Invalid request format
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Package/version not found
- `500 Internal Server Error` - Server errors

### Package Naming Strategies

| Registry | Normalization | Case Sensitivity | Special Characters |
|----------|---------------|------------------|-------------------|
| PyPI     | `[-_.]+` → `-`, lowercase | Insensitive | `-`, `_`, `.` |
| npm      | No normalization | Sensitive | `-`, `_`, `@` (scopes) |
| Cargo    | No normalization | Insensitive | `-`, `_` |

### Checksum Validation

| Registry | Algorithm | Location | Format |
|----------|-----------|----------|---------|
| PyPI     | SHA256 | URL fragment | `#sha256=abc123` |
| npm      | SHA1/SHA512 | Metadata | `shasum`, `integrity` |
| Cargo    | SHA256 | Index | `cksum` field |

## 🎯 Implementation Recommendations

### Current PyPI Server Analysis

The existing implementation in `/src/goobits_cli/pypi_server.py` is **mostly PEP 503 compliant** but missing:

#### Required Enhancements:
1. **Hash Support**: Add SHA256 checksums to download URLs
2. **Metadata Attributes**: Support `data-requires-python` and `data-gpg-sig`
3. **Range Requests**: Support partial content downloads
4. **Proper Caching**: Add appropriate cache headers

#### Recommended Changes:
```python
def _serve_package_simple_page(self, package_name: str) -> None:
    # ... existing code ...
    for file_path in matching_files:
        # Calculate SHA256 hash
        sha256_hash = self._calculate_sha256(file_path)
        file_url = f"/{file_path.name}#sha256={sha256_hash}"

        # Add metadata attributes
        attrs = []
        if python_version := self._extract_python_version(file_path):
            attrs.append(f'data-requires-python="{python_version}"')

        attrs_str = " ".join(attrs)
        html_lines.append(f'<a href="{file_url}" {attrs_str}>{file_path.name}</a><br/>')
```

### Multi-Registry Architecture

For implementing multiple registry types:

```python
class RegistryHandler(ABC):
    @abstractmethod
    def handle_request(self, request: Request) -> Response:
        pass

class PyPIHandler(RegistryHandler):
    def handle_request(self, request: Request) -> Response:
        # PEP 503 implementation
        pass

class NpmHandler(RegistryHandler):
    def handle_request(self, request: Request) -> Response:
        # npm registry implementation
        pass

class CargoHandler(RegistryHandler):
    def handle_request(self, request: Request) -> Response:
        # Cargo registry implementation
        pass
```

### Performance Considerations

1. **Lazy Loading**: Only load package metadata when requested
2. **Caching**: Implement aggressive caching for static content
3. **Indexing**: Use databases for package search and metadata
4. **CDN Integration**: Serve files from CDN when possible

### Security Best Practices

1. **Input Validation**: Sanitize all package names and versions
2. **Rate Limiting**: Implement API rate limits
3. **Checksum Verification**: Always validate file integrity
4. **Authentication**: Use secure token management
5. **HTTPS Only**: Never serve registries over HTTP in production

## 🔍 Critical Implementation Gotchas

### PyPI
- Package names must be normalized in URLs but preserve original case in display
- HTML pages must end with `/`
- Hash fragments are optional but strongly recommended
- Support both `.whl` and `.tar.gz` formats

### npm
- Scoped packages require proper URL encoding (`@scope%2Fpackage`)
- Version metadata can be massive - implement streaming/pagination
- Tarball URLs must be absolute URLs, not relative paths
- `dist-tags` are critical for determining latest versions

### Cargo
- Index files use newline-delimited JSON (not JSON arrays)
- Git index requires precise file paths based on package name length
- Checksums must match `.crate` file contents exactly
- Yanked versions remain in index but marked as unavailable

### Universal
- HTTP caching headers are critical for performance
- Content-Type headers must be precise for client compatibility
- Authentication should be stateless (no server sessions)
- Error responses should include helpful diagnostic information

---

*Generated with comprehensive research of official specifications and real-world implementations.*