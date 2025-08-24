#!/bin/bash
# Safe Cleanup Step 1: Pre-flight checks and backup
# This script performs all safety checks before any cleanup

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "========================================"
echo "SAFE CLEANUP - STEP 1: Pre-flight Checks"
echo "========================================"
echo ""

# Function to print colored output
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }

# Check 1: Verify we're in the right directory
if [ ! -f "goobits.yaml" ]; then
    print_error "Not in project root directory (goobits.yaml not found)"
    exit 1
fi
print_success "In correct project directory"

# Check 2: Check for uncommitted changes
UNCOMMITTED=$(git status --porcelain | wc -l)
if [ "$UNCOMMITTED" -gt 0 ]; then
    print_warning "You have $UNCOMMITTED uncommitted changes:"
    git status --short
    echo ""
    read -p "Do you want to stash these changes? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git stash push -m "Pre-cleanup stash $(date +%Y%m%d_%H%M%S)"
        print_success "Changes stashed"
    else
        print_error "Please commit or stash changes before proceeding"
        exit 1
    fi
fi
print_success "Working directory clean"

# Check 3: Check current branch
CURRENT_BRANCH=$(git branch --show-current)
print_info "Current branch: $CURRENT_BRANCH"

# Check 4: Check repository size
GIT_SIZE=$(du -sh .git 2>/dev/null | cut -f1)
WORK_SIZE=$(du -sh . 2>/dev/null | cut -f1)
print_info "Repository size: $GIT_SIZE (git) / $WORK_SIZE (total)"

# Check 5: Count problem files
echo ""
echo "Analyzing repository contents..."
VENV_COUNT=$(find . -type f -path "*/venv/*" -o -path "*/test_env/*" -o -path "*/env/*" 2>/dev/null | wc -l)
PYC_COUNT=$(find . -type f -name "*.pyc" 2>/dev/null | wc -l)
PYCACHE_COUNT=$(find . -type d -name "__pycache__" 2>/dev/null | wc -l)
NODE_COUNT=$(find . -type f -path "*/node_modules/*" 2>/dev/null | wc -l)

print_warning "Found problematic files:"
echo "  - Virtual environment files: $VENV_COUNT"
echo "  - Compiled Python files (.pyc): $PYC_COUNT"
echo "  - Python cache directories: $PYCACHE_COUNT"
echo "  - Node modules files: $NODE_COUNT"

# Check 6: Check for git filter-repo
if ! command -v git-filter-repo &> /dev/null; then
    print_warning "git-filter-repo not installed"
    echo "Install with: pip install git-filter-repo"
    echo "Or on Mac: brew install git-filter-repo"
    exit 1
fi
print_success "git-filter-repo is installed"

# Check 7: Create backup directory name
BACKUP_DIR="../workspace-backup-$(date +%Y%m%d_%H%M%S)"
print_info "Backup will be created at: $BACKUP_DIR"

echo ""
echo "========================================"
echo "BACKUP CREATION"
echo "========================================"
echo ""
echo "This will create a complete backup of the repository."
echo "Backup location: $BACKUP_DIR"
echo ""
read -p "Create backup now? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_error "Backup cancelled"
    exit 1
fi

# Create backup
print_info "Creating backup... (this may take a minute)"
cp -r . "$BACKUP_DIR"
print_success "Backup created at: $BACKUP_DIR"

# Verify backup
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
print_success "Backup size: $BACKUP_SIZE"

# Create restore script in backup
cat > "$BACKUP_DIR/restore.sh" << 'EOF'
#!/bin/bash
# Restore script - run from backup directory
echo "This will restore the repository from this backup"
read -p "Target directory (../workspace): " TARGET
TARGET=${TARGET:-../workspace}
if [ -d "$TARGET" ]; then
    echo "Target exists. Remove it first."
    exit 1
fi
cp -r . "$TARGET"
echo "Restored to $TARGET"
EOF
chmod +x "$BACKUP_DIR/restore.sh"
print_success "Restore script created in backup"

echo ""
echo "========================================"
echo "SAFETY CHECKLIST"
echo "========================================"
echo ""
print_success "✓ Working directory verified"
print_success "✓ Repository backed up to: $BACKUP_DIR"
print_success "✓ git-filter-repo available"
print_success "✓ Problem files identified"
echo ""
print_info "Next step: Run ./scripts/safe-cleanup-step2.sh"
print_info "This will create the filter patterns file"
echo ""
print_warning "IMPORTANT: Keep the backup until cleanup is verified!"

# Save state for next step
cat > /tmp/cleanup-state.txt << EOF
BACKUP_DIR=$BACKUP_DIR
CURRENT_BRANCH=$CURRENT_BRANCH
GIT_SIZE=$GIT_SIZE
VENV_COUNT=$VENV_COUNT
PYC_COUNT=$PYC_COUNT
EOF

print_success "State saved for next step"