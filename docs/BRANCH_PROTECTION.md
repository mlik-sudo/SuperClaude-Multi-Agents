# Branch Protection Setup Guide

## 🔒 GitHub Branch Protection Configuration

### Step 1: Access Branch Protection Settings

1. Go to your repository: https://github.com/mlik-sudo/SuperClaude-Multi-Agents
2. Click **Settings** tab (top right)
3. In the left sidebar, click **Branches**
4. Click **Add branch protection rule**

### Step 2: Configure Branch Protection Rule

#### Branch Name Pattern
```
main
```

#### Protection Rules (Check these boxes)

##### ✅ Pull Request Requirements

- [x] **Require a pull request before merging**
  - [x] Require approvals: **1**
  - [x] Dismiss stale pull request approvals when new commits are pushed
  - [ ] Require review from Code Owners (optional - requires CODEOWNERS file)
  - [x] Require approval of the most recent reviewable push

##### ✅ Status Checks

- [x] **Require status checks to pass before merging**
  - [x] Require branches to be up to date before merging

  **Select these required status checks:**
  - `CI - Tests & Quality Checks / test (3.11)` ← Your CI workflow
  - `CI - Tests & Quality Checks / lint` ← Your linting
  - `CI - Tests & Quality Checks / build` ← Your build check
  - `Security Scanning / secrets-scan` ← Security check

##### ✅ Additional Protections

- [x] **Require conversation resolution before merging**
  *(All PR comments must be resolved)*

- [x] **Require signed commits** *(Recommended for security)*
  *(Ensures commits are cryptographically verified)*

- [x] **Require linear history** *(Optional but clean)*
  *(Prevents merge commits, enforces rebase)*

- [x] **Include administrators**
  *(Apply rules to admins too - best practice)*

##### ❌ Do NOT Enable (Keep Unchecked)

- [ ] **Allow force pushes** ← DANGER! Keep disabled
- [ ] **Allow deletions** ← DANGER! Keep disabled

### Step 3: Save Changes

Click **Create** or **Save changes** at the bottom

---

## 🔍 Verification

After setup, verify protection is active:

1. Go to **Settings** → **Branches**
2. You should see **main** listed under "Branch protection rules"
3. Try to push directly to main:
   ```bash
   git checkout main
   git commit --allow-empty -m "test"
   git push origin main
   ```
   ✅ Should be **rejected** with message:
   ```
   remote: error: GH006: Protected branch update failed for refs/heads/main.
   ```

---

## 📋 What This Means for Your Workflow

### Before (No Protection)
```bash
git checkout main
git commit -m "quick fix"
git push origin main
```
✅ Push succeeds immediately (DANGEROUS!)

### After (With Protection)
```bash
# 1. Create feature branch
git checkout -b feature/my-changes

# 2. Make changes and commit
git commit -m "feat: add feature"

# 3. Push feature branch
git push origin feature/my-changes

# 4. Create Pull Request on GitHub
# 5. Wait for CI checks to pass
# 6. Get review approval
# 7. Merge via PR (only way to update main)
```

---

## 🎯 Benefits

✅ **Code Quality**
- All code reviewed before merge
- CI tests must pass
- Linting must pass

✅ **Safety**
- No accidental force push
- No branch deletion
- History preserved

✅ **Collaboration**
- PR discussions documented
- Changes visible to team
- Review process enforced

✅ **Compliance**
- Audit trail of changes
- Signed commits (if enabled)
- Linear history (if enabled)

---

## 🚀 Alternative: GitHub CLI

If you prefer automation:

```bash
# Install GitHub CLI
brew install gh  # macOS
# or: sudo apt install gh  # Ubuntu

# Authenticate
gh auth login

# Create protection rule
gh api repos/mlik-sudo/SuperClaude-Multi-Agents/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["CI - Tests & Quality Checks / test (3.11)","CI - Tests & Quality Checks / lint"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
  --field restrictions=null \
  --field allow_force_pushes=false \
  --field allow_deletions=false
```

---

## 📄 CODEOWNERS File (Optional but Recommended)

Create `.github/CODEOWNERS` to automatically assign reviewers:

```
# SuperClaude Multi-Agents - Code Owners

# Default owner for everything
* @mlik-sudo

# Core orchestration
/core/ @mlik-sudo

# MCP components
/mcp/ @mlik-sudo

# Security-critical files
/SECURITY.md @mlik-sudo
/.github/workflows/ @mlik-sudo

# Configuration
/config/ @mlik-sudo
/.env.example @mlik-sudo

# Documentation (can be more permissive)
/docs/ @mlik-sudo
README.md @mlik-sudo
```

Then enable "Require review from Code Owners" in branch protection.

---

## 🔐 Signed Commits (Highly Recommended)

### Why?
- Cryptographically prove who made each commit
- Prevent commit impersonation
- GitHub displays "Verified" badge

### Setup GPG Signing

```bash
# 1. Generate GPG key
gpg --full-generate-key
# Choose: RSA, 4096 bits, no expiration

# 2. List keys
gpg --list-secret-keys --keyid-format=long
# Note the key ID (after sec rsa4096/)

# 3. Export public key
gpg --armor --export YOUR_KEY_ID

# 4. Add to GitHub
# Settings → SSH and GPG keys → New GPG key → Paste

# 5. Configure git
git config --global user.signingkey YOUR_KEY_ID
git config --global commit.gpgsign true

# 6. Test
git commit --allow-empty -m "test signed commit"
# Should show "Verified" on GitHub
```

---

## ⚠️ Common Issues & Solutions

### Issue 1: Can't merge PR - "Required status checks must pass"

**Solution:** Wait for CI to complete. Fix any failing tests.

### Issue 2: Can't merge PR - "Review required"

**Solution:**
- Ask teammate for review
- Or: Temporarily disable if you're solo (not recommended)

### Issue 3: Accidentally pushed to main before protection

**Solution:**
```bash
# If it's the latest commit, revert locally
git reset --soft HEAD~1

# Create proper PR
git checkout -b fix/proper-pr
git commit -m "feat: proper change via PR"
git push origin fix/proper-pr

# Then create PR on GitHub
```

---

## 📊 Monitoring

After setup, monitor:

1. **Pull Requests tab** - All changes visible
2. **Actions tab** - CI status for each PR
3. **Insights → Network** - Branch structure (should be clean)

---

## 🎓 Team Guidelines

Create `docs/PR_GUIDELINES.md`:

```markdown
# Pull Request Guidelines

## Creating a PR

1. Branch from `main`:
   \`\`\`bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature
   \`\`\`

2. Make changes and commit following conventions

3. Push and create PR

4. Ensure CI passes

5. Request review

6. Address feedback

7. Merge when approved

## PR Checklist

- [ ] Tests pass locally
- [ ] Code follows style guide (black, flake8)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if applicable)
- [ ] No merge conflicts
- [ ] CI checks pass
```

---

## ✅ Next Steps

1. **Now**: Go to GitHub Settings → Branches and configure protection
2. **Test**: Try to push directly to main (should fail)
3. **Practice**: Create a test PR to verify workflow
4. **Document**: Add PR guidelines to your docs
5. **Optional**: Set up GPG signing for verified commits

---

**Need help with any of these steps?** Let me know! 🚀
