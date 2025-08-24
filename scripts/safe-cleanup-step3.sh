#!/bin/bash
# Safe Cleanup Step 3: Execute cleanup with verification
# This script performs the actual git history cleanup

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
echo "SAFE CLEANUP - STEP 3: Execute Cleanup"
echo "========================================"
echo ""

# Check state
if [ ! -f "/tmp/cleanup-state.txt" ]; then
    print_error "Previous steps not completed. Run step1 and step2 first"
    exit 1
fi

source /tmp/cleanup-state.txt
print_success "Loaded state from previous steps"

echo ""
print_warning "⚠️  WARNING: This will rewrite git history!"
echo ""
echo "Summary of changes:"
echo "  - Backup location: $BACKUP_DIR"
echo "  - Files to remove: $REMOVE_COUNT"
echo "  - Files to keep: $KEEP_COUNT"
echo "  - Repository size: $GIT_SIZE"
echo ""
print_warning "This action cannot be undone (except by restoring from backup)"
echo ""
read -p "Type 'CLEANUP' to proceed: " CONFIRM

if [ "$CONFIRM" != "CLEANUP" ]; then
    print_error "Cleanup cancelled"
    exit 1
fi

echo ""
print_info "Starting cleanup... This may take a few minutes"
echo ""

# Record before state
BEFORE_SIZE=$(du -sh .git 2>/dev/null | cut -f1)
BEFORE_COMMITS=$(git rev-list --count HEAD)
BEFORE_FILES=$(git ls-files | wc -l)

# Create a tag for the last state before cleanup
git tag -a "before-cleanup-$(date +%Y%m%d_%H%M%S)" -m "State before git-filter-repo cleanup" || true

# Execute git-filter-repo
print_info "Running git-filter-repo..."
git filter-repo --paths-from-file .git-filter-patterns --invert-paths --force

# Check if it succeeded
if [ $? -eq 0 ]; then
    print_success "git-filter-repo completed successfully"
else
    print_error "git-filter-repo failed!"
    print_warning "Restore from backup: cp -r $BACKUP_DIR/* ."
    exit 1
fi

# Record after state
AFTER_SIZE=$(du -sh .git 2>/dev/null | cut -f1)
AFTER_COMMITS=$(git rev-list --count HEAD 2>/dev/null || echo "0")
AFTER_FILES=$(git ls-files | wc -l)

echo ""
echo "========================================"
echo "CLEANUP RESULTS"
echo "========================================"
echo ""
echo "Before cleanup:"
echo "  Repository size: $BEFORE_SIZE"
echo "  Total commits: $BEFORE_COMMITS"
echo "  Total files: $BEFORE_FILES"
echo ""
echo "After cleanup:"
echo "  Repository size: $AFTER_SIZE"
echo "  Total commits: $AFTER_COMMITS"
echo "  Total files: $AFTER_FILES"
echo ""

# Calculate reduction
print_success "✓ Cleanup completed successfully!"

echo ""
echo "========================================"
echo "POST-CLEANUP STEPS"
echo "========================================"
echo ""
echo "1. Update .gitignore:"
echo "   mv .gitignore-new .gitignore"
echo "   git add .gitignore"
echo "   git commit -m 'Update .gitignore after cleanup'"
echo ""
echo "2. Clean working directory:"
echo "   git clean -fdx"
echo ""
echo "3. Update remote (COORDINATE WITH TEAM):"
echo "   git push --force-with-lease origin $CURRENT_BRANCH"
echo ""
echo "4. Team members need to:"
echo "   git fetch origin"
echo "   git reset --hard origin/$CURRENT_BRANCH"
echo ""
print_warning "Keep backup for at least 30 days: $BACKUP_DIR"

# Create verification script
cat > scripts/verify-cleanup.sh << 'EOF'
#!/bin/bash
echo "Verifying cleanup..."
echo ""

# Check for problem files
PROBLEMS=0

# Check for virtual environments
if find . -type d \( -name "venv" -o -name "test_env" -o -name "env" \) 2>/dev/null | grep -q .; then
    echo "✗ Virtual environment directories still exist"
    PROBLEMS=$((PROBLEMS + 1))
else
    echo "✓ No virtual environments found"
fi

# Check for .pyc files
if find . -type f -name "*.pyc" 2>/dev/null | grep -q .; then
    echo "✗ Python compiled files still exist"
    PROBLEMS=$((PROBLEMS + 1))
else
    echo "✓ No .pyc files found"
fi

# Check for __pycache__
if find . -type d -name "__pycache__" 2>/dev/null | grep -q .; then
    echo "✗ Python cache directories still exist"
    PROBLEMS=$((PROBLEMS + 1))
else
    echo "✓ No __pycache__ directories found"
fi

# Check for node_modules
if find . -type d -name "node_modules" 2>/dev/null | grep -q .; then
    echo "✗ node_modules directories still exist"
    PROBLEMS=$((PROBLEMS + 1))
else
    echo "✓ No node_modules found"
fi

echo ""
if [ $PROBLEMS -eq 0 ]; then
    echo "✓ Cleanup verified successfully!"
else
    echo "✗ Found $PROBLEMS issues. Run: git clean -fdx"
fi
EOF
chmod +x scripts/verify-cleanup.sh

print_success "Created verification script: ./scripts/verify-cleanup.sh"
echo ""
print_info "Run verification: ./scripts/verify-cleanup.sh"

# Save final state
cat > cleanup-report.txt << EOF
Cleanup Report - $(date)
========================

Backup Location: $BACKUP_DIR

Before Cleanup:
  Repository size: $BEFORE_SIZE
  Total commits: $BEFORE_COMMITS
  Total files: $BEFORE_FILES

After Cleanup:
  Repository size: $AFTER_SIZE
  Total commits: $AFTER_COMMITS
  Total files: $AFTER_FILES

Files Removed: $REMOVE_COUNT
Files Kept: $KEEP_COUNT

Next Steps:
1. Update .gitignore
2. Clean working directory (git clean -fdx)
3. Coordinate with team for force push
4. Keep backup for 30 days
EOF

print_success "Cleanup report saved to: cleanup-report.txt"