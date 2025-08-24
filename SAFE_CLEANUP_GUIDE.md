# 🛡️ Safe Git Repository Cleanup Guide

## ⚠️ Current Situation
- **Repository Size**: 355MB (should be ~50MB)
- **Total Files**: ~14,000 (91% shouldn't be tracked)
- **Problem**: Virtual environments, compiled files, and test outputs in git history

## ✅ Safe 3-Step Cleanup Process

I've created a **safe, reversible** cleanup process with multiple safety checks:

### 📁 Scripts Created
1. `scripts/safe-cleanup-step1.sh` - Pre-flight checks & backup
2. `scripts/safe-cleanup-step2.sh` - Create filter patterns
3. `scripts/safe-cleanup-step3.sh` - Execute cleanup

## 🚀 Step-by-Step Instructions

### Step 1: Pre-flight Checks & Backup
```bash
./scripts/safe-cleanup-step1.sh
```
This will:
- ✓ Verify you're in the correct directory
- ✓ Check for uncommitted changes
- ✓ Create a complete backup (with restore script)
- ✓ Verify git-filter-repo is installed
- ✓ Count problematic files

**Safety**: Creates timestamped backup with restore capability

### Step 2: Create Filter Patterns
```bash
./scripts/safe-cleanup-step2.sh
```
This will:
- ✓ Create `.git-filter-patterns` file
- ✓ Show exactly what will be removed
- ✓ Verify critical files will be preserved
- ✓ Calculate size reduction estimate

**Safety**: No changes made yet, just analysis

### Step 3: Execute Cleanup (⚠️ Irreversible)
```bash
./scripts/safe-cleanup-step3.sh
```
This will:
- ⚠️ Require typing "CLEANUP" to confirm
- ✓ Tag current state before cleanup
- ✓ Run git-filter-repo
- ✓ Show before/after statistics
- ✓ Create verification script

**Safety**: Requires explicit confirmation, creates tag

## 🔍 What Gets Removed

### Definitely Remove (High Confidence)
- `venv/`, `test_env/`, `env/` - Virtual environments
- `__pycache__/`, `*.pyc` - Compiled Python files
- `node_modules/` - Node dependencies
- `test-*-out/` - Test outputs
- `.mypy_cache/`, `.pytest_cache/` - Tool caches

### Probably Remove (Medium Confidence)
- `package-lock.json`, `yarn.lock` - Lock files (library project)
- `*.log` - Log files
- `.coverage`, `htmlcov/` - Coverage reports

## 🎯 Expected Results

### Before Cleanup
- Repository: 355MB
- Files: ~14,000
- History: 230 commits

### After Cleanup (Estimated)
- Repository: ~50MB (86% reduction)
- Files: ~1,200 (91% reduction)
- History: 230 commits (preserved)

## ⚡ Quick Option (Less Safe)

If you're confident and have good backups:
```bash
# One-line cleanup (after backup!)
git filter-repo --paths-from-file .git-filter-patterns --invert-paths --force
```

## 🔄 Recovery Options

### If Something Goes Wrong

#### Option 1: Restore from Backup
```bash
cd ../workspace-backup-[timestamp]
./restore.sh
```

#### Option 2: Reset to Remote
```bash
git fetch origin
git reset --hard origin/main
```

#### Option 3: Clone Fresh
```bash
cd ..
git clone [repository-url] workspace-fresh
```

## 👥 Team Coordination

After cleanup, team members need to:
```bash
# Option 1: Reset their local copies
git fetch origin
git reset --hard origin/main

# Option 2: Fresh clone (cleanest)
git clone [repository-url] workspace-new
```

## 📋 Post-Cleanup Checklist

After successful cleanup:

1. **Update .gitignore**
   ```bash
   mv .gitignore-new .gitignore
   git add .gitignore
   git commit -m "Update .gitignore after repository cleanup"
   ```

2. **Clean Working Directory**
   ```bash
   git clean -fdx  # Removes all untracked files
   ```

3. **Verify Cleanup**
   ```bash
   ./scripts/verify-cleanup.sh
   ```

4. **Push Changes** (coordinate with team)
   ```bash
   git push --force-with-lease origin main
   ```

5. **Document for Team**
   - Send cleanup notice
   - Share new clone instructions
   - Update CI/CD if needed

## 🚨 Warning Signs to Stop

STOP the cleanup if:
- Backup fails or is incomplete
- git-filter-repo not installed
- Team members actively working
- CI/CD pipeline running
- Unsure about any step

## 💡 Best Practices Going Forward

1. **Never track**:
   - Virtual environments
   - Compiled files (.pyc, __pycache__)
   - Dependencies (node_modules)
   - IDE configurations
   - Test outputs

2. **Use .gitignore**:
   - Add patterns BEFORE creating files
   - Use templates (github.com/github/gitignore)
   - Review regularly

3. **Regular Maintenance**:
   - Check repository size monthly
   - Run `git clean -fdx` regularly
   - Audit tracked files quarterly

## 📞 Support

If you need help:
1. Don't proceed if unsure
2. Keep the backup
3. Test on a clone first
4. Ask team members for review

## ✅ Ready to Proceed?

Start with Step 1:
```bash
./scripts/safe-cleanup-step1.sh
```

The process is designed to be:
- **Safe**: Multiple checkpoints
- **Reversible**: Until Step 3
- **Verified**: Shows what will happen
- **Documented**: Clear audit trail

Remember: **When in doubt, don't proceed!**