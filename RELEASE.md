# Release Instructions for Goobits CLI

## Prerequisites

1. Ensure you have PyPI account and are added as maintainer
2. Configure PyPI trusted publishing for this GitHub repository:
   - Go to https://pypi.org/manage/account/publishing/
   - Add a new trusted publisher
   - Enter GitHub repository details:
     - Owner: [your-github-username]
     - Repository: goobits-cli
     - Workflow: publish.yml
     - Environment: pypi

## Release Process

### 1. Update Version

Edit `pyproject.toml`:
```toml
version = "1.0.0"  # Update to new version
```

### 2. Update Changelog

Add release notes to `CHANGELOG.md`:
```markdown
## [1.0.0] - 2024-XX-XX
### Added
- Initial production release
- Multi-language CLI generation (Python, Node.js, TypeScript, Rust)
- Universal template system
- Enhanced error messages
- Validation command
```

### 3. Commit Changes

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "Release v1.0.0"
git push origin main
```

### 4. Create and Push Tag

```bash
git tag v1.0.0
git push origin v1.0.0
```

This will trigger the GitHub Actions workflow which will:
1. Run all tests across Python 3.8-3.12
2. Build the distribution packages
3. Publish to PyPI using trusted publishing (no password needed!)
4. Create a GitHub release with artifacts

### 5. Verify Release

After ~5 minutes, verify the release:
```bash
pip install goobits-cli==1.0.0
goobits --version
```

Check PyPI page: https://pypi.org/project/goobits-cli/

## Manual Release (If GitHub Actions Fails)

### Build Locally

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Install build tools
pip install --upgrade build twine

# Build the package
python -m build

# Check the distribution
twine check dist/*
```

### Upload to PyPI

```bash
# Upload to TestPyPI first (optional)
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ goobits-cli

# Upload to PyPI
twine upload dist/*
```

## Post-Release

1. Announce the release on social media
2. Update documentation if needed
3. Start development on next version:
   ```bash
   # Update version in pyproject.toml to next dev version
   version = "1.1.0.dev0"
   ```

## Troubleshooting

### "Package already exists" Error
- The version already exists on PyPI
- Increment the version number and try again

### GitHub Actions Fails on Tests
- Check test logs in Actions tab
- Fix failing tests before release
- Can bypass with manual release if needed

### Trusted Publishing Not Working
- Ensure the PyPI project is configured to trust the GitHub repo
- Check that workflow name matches exactly: `publish.yml`
- Verify environment name matches: `pypi`

## Version Numbering

Follow semantic versioning:
- **Major** (1.0.0): Breaking changes
- **Minor** (1.1.0): New features, backwards compatible
- **Patch** (1.0.1): Bug fixes only

For pre-releases:
- Alpha: `1.0.0a1`
- Beta: `1.0.0b1`
- Release Candidate: `1.0.0rc1`