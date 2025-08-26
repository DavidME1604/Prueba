# Git Workflow - CELEC Forecast Project

## 🌊 Git Flow Strategy

This project follows a **Git Flow branching strategy** for organized development and releases.

### Branch Structure

```
main (protected)
├── develop (protected)
    ├── feature/feature-name
    ├── feature/model-improvement
    └── hotfix/critical-bug-fix
```

### Branch Types

#### 🏠 Main Branches

- **`main`** - Production-ready code
  - Only accepts merges from `develop` or `hotfix/*`
  - Always deployable
  - Protected with branch rules

- **`develop`** - Integration branch for features
  - Default branch for development
  - Features are merged here first
  - Protected with branch rules

#### 🚀 Supporting Branches

- **`feature/*`** - New features or enhancements
  - Branch from: `develop`
  - Merge back to: `develop`
  - Naming: `feature/description` or `feature/issue-number`
  - Example: `feature/data-preprocessing`, `feature/mlflow-integration`

- **`hotfix/*`** - Critical production fixes
  - Branch from: `main`
  - Merge back to: `main` and `develop`
  - Naming: `hotfix/description`
  - Example: `hotfix/model-loading-error`

- **`release/*`** - Prepare releases
  - Branch from: `develop`
  - Merge back to: `main` and `develop`
  - Naming: `release/v1.0.0`

## 🔄 Workflow Process

### 1. Feature Development

```bash
# Start new feature
git checkout develop
git pull origin develop
git checkout -b feature/awesome-feature

# Work on feature
git add .
git commit -m "feat: implement awesome feature"
git push origin feature/awesome-feature

# Create Pull Request: feature/awesome-feature → develop
```

### 2. Code Review Process

1. **Create Pull Request** using the provided template
2. **Assign reviewers** (minimum 1 required)
3. **Run automated checks** (tests, linting)
4. **Address review feedback**
5. **Merge after approval**

### 3. Release Process

```bash
# Create release branch
git checkout develop
git checkout -b release/v1.2.0

# Finalize release (version bumps, changelog)
git commit -m "chore: prepare release v1.2.0"

# Merge to main
git checkout main
git merge release/v1.2.0
git tag -a v1.2.0 -m "Release version 1.2.0"

# Merge back to develop
git checkout develop
git merge release/v1.2.0
```

### 4. Hotfix Process

```bash
# Create hotfix from main
git checkout main
git checkout -b hotfix/critical-fix

# Fix the issue
git commit -m "fix: resolve critical production issue"

# Merge to main
git checkout main
git merge hotfix/critical-fix
git tag -a v1.2.1 -m "Hotfix version 1.2.1"

# Merge to develop
git checkout develop
git merge hotfix/critical-fix
```

## 🛡️ Branch Protection Rules

### Main Branch Protection

**Required settings for `main` branch:**

- [x] **Require pull request reviews before merging**
  - Required approving reviews: **1**
  - Require review from code owners
  - Dismiss stale PR approvals when new commits are pushed

- [x] **Require status checks to pass before merging**
  - Require branches to be up to date before merging
  - Status checks: `tests`, `lint`, `security-scan`

- [x] **Enforce restrictions**
  - Restrict pushes that create files larger than 100MB
  - No force pushes allowed
  - No deletions allowed

- [x] **Rules applied to administrators**

### Develop Branch Protection

**Required settings for `develop` branch:**

- [x] **Require pull request reviews before merging**
  - Required approving reviews: **1**
  - Allow specified actors to bypass required pull requests (maintainers only)

- [x] **Require status checks to pass before merging**
  - Status checks: `tests`, `lint`

- [x] **No force pushes allowed**

## 📋 Commit Convention

We follow **Conventional Commits** specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Commit Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements

### Examples

```bash
feat(model): add Random Forest hyperparameter tuning
fix(data): resolve CSV parsing issue for large datasets
docs(readme): update installation instructions
test(model): add unit tests for feature engineering
chore(deps): update pandas to version 2.0.0
```

## 🔍 Code Review Guidelines

### For Authors

- [ ] Ensure all tests pass
- [ ] Update documentation
- [ ] Follow coding standards
- [ ] Keep PRs focused and small
- [ ] Provide clear description
- [ ] Include test results/model metrics

### For Reviewers

- [ ] Check code quality and standards
- [ ] Verify tests cover new functionality
- [ ] Review security implications
- [ ] Validate model performance (if applicable)
- [ ] Ensure documentation is updated

## 🚀 GitHub Settings Configuration

### Repository Settings

1. **General Settings**
   ```
   Default branch: develop
   Allow merge commits: ✓
   Allow squash merging: ✓
   Allow rebase merging: ✗
   Automatically delete head branches: ✓
   ```

2. **Required Status Checks**
   - Create GitHub Actions for:
     - Python tests (`pytest`)
     - Code linting (`flake8`, `black`)
     - Security scanning
     - Model validation

3. **Collaborators and Teams**
   - Add team members with appropriate permissions
   - Assign code owners via `CODEOWNERS` file

## 📊 MLflow Integration

Special considerations for ML projects:

- **Model versioning** tracked in MLflow
- **Experiment tracking** for all model changes
- **Model approval process** before production deployment
- **Performance regression tests** in CI/CD

---

**Note:** Configure these settings in GitHub repository settings under "Branches" section.