#!/bin/bash
# Safe Cleanup Step 2: Create and verify filter patterns
# This script creates the patterns file for git-filter-repo

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_error() { echo -e "${RED}✗ $1${NC}"; }
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }

echo "========================================"
echo "SAFE CLEANUP - STEP 2: Filter Patterns"
echo "========================================"
echo ""

# Check state from step 1
if [ ! -f "/tmp/cleanup-state.txt" ]; then
    print_error "Step 1 not completed. Run safe-cleanup-step1.sh first"
    exit 1
fi

source /tmp/cleanup-state.txt
print_success "Loaded state from Step 1"
print_info "Backup location: $BACKUP_DIR"

# Create comprehensive filter patterns
cat > .git-filter-patterns << 'EOF'
# Virtual Environments - NEVER belong in git
venv/
env/
ENV/
test_env/
test_venv/
.venv/
.env/
virtualenv/
.virtualenv/

# Python Cache - compiled files
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.py[cod]
*$py.class

# Test Outputs - generated files
test-*-out/
test_*_out/
test-*-output/
test_*_release/
test_frameworks/
test_results/
test-results/

# Node.js - dependencies
node_modules/
.npm/
.yarn/

# Build Artifacts
build/
dist/
*.egg-info/
.eggs/
target/
*.so
*.dylib
*.dll

# IDE and Editor
.idea/
.vscode/
*.swp
*.swo
*~
.DS_Store
Thumbs.db

# Coverage and Testing
.coverage
.coverage.*
htmlcov/
.tox/
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Logs
*.log
logs/
pip-log.txt
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Environment files with potential secrets
.env
.env.*
*.env

# Package locks (library project)
package-lock.json
yarn.lock
Pipfile.lock

# Temporary and backup files
*.tmp
*.bak
*.backup
.~*

# Generated CLI files in src
src/test_cli/
src/testcli/
src/test_python_cli/
src/nodejs_test_cli/
src/complexcli/

# Ad-hoc test scripts
test_*.py
!src/tests/**/test_*.py
EOF

print_success "Created .git-filter-patterns"

echo ""
echo "========================================"
echo "PATTERN VERIFICATION"
echo "========================================"
echo ""

# Show what will be removed
print_info "Analyzing what will be removed..."

# Count files matching patterns
REMOVE_COUNT=0
KEEP_COUNT=0

# Create temporary test lists
git ls-files > /tmp/all-files.txt

# Check each pattern
while IFS= read -r pattern; do
    # Skip comments and empty lines
    [[ "$pattern" =~ ^#.*$ ]] && continue
    [[ -z "$pattern" ]] && continue
    
    # Count matches (handling both file and directory patterns)
    if [[ "$pattern" == */ ]]; then
        # Directory pattern
        COUNT=$(git ls-files | grep -c "^${pattern%/}/" || true)
    else
        # File pattern
        COUNT=$(git ls-files | grep -c "$pattern" || true)
    fi
    
    if [ "$COUNT" -gt 0 ]; then
        REMOVE_COUNT=$((REMOVE_COUNT + COUNT))
        printf "  %-30s %5d files\n" "$pattern" "$COUNT"
    fi
done < .git-filter-patterns

TOTAL_FILES=$(git ls-files | wc -l)
KEEP_COUNT=$((TOTAL_FILES - REMOVE_COUNT))

echo ""
print_warning "Summary:"
echo "  Total files in repository: $TOTAL_FILES"
echo "  Files to be removed: $REMOVE_COUNT"
echo "  Files to keep: $KEEP_COUNT"
echo "  Reduction: $(( (REMOVE_COUNT * 100) / TOTAL_FILES ))%"

echo ""
echo "========================================"
echo "CRITICAL FILES CHECK"
echo "========================================"
echo ""

# Check that important files will be kept
CRITICAL_FILES=(
    "goobits.yaml"
    "README.md"
    "pyproject.toml"
    "src/goobits_cli/__init__.py"
    "src/goobits_cli/main.py"
    "src/tests/conftest.py"
)

print_info "Verifying critical files will be preserved:"
for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        # Check if file would be removed
        WOULD_REMOVE=false
        while IFS= read -r pattern; do
            [[ "$pattern" =~ ^#.*$ ]] && continue
            [[ -z "$pattern" ]] && continue
            
            if echo "$file" | grep -q "$pattern"; then
                WOULD_REMOVE=true
                break
            fi
        done < .git-filter-patterns
        
        if [ "$WOULD_REMOVE" = true ]; then
            print_error "$file would be removed!"
        else
            print_success "$file will be kept"
        fi
    fi
done

echo ""
echo "========================================"
echo "DRY RUN OPTION"
echo "========================================"
echo ""
echo "You can now do a dry run to see what would be removed:"
echo ""
echo "  git filter-repo --paths-from-file .git-filter-patterns --invert-paths --dry-run"
echo ""
echo "Or proceed to Step 3 for the actual cleanup:"
echo ""
print_info "Next step: Run ./scripts/safe-cleanup-step3.sh"
print_warning "This will perform the actual cleanup!"
echo ""

# Update state
cat >> /tmp/cleanup-state.txt << EOF
REMOVE_COUNT=$REMOVE_COUNT
KEEP_COUNT=$KEEP_COUNT
TOTAL_FILES=$TOTAL_FILES
EOF

print_success "Ready for Step 3"