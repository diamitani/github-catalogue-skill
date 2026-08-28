# GitHub Catalogue Skill

Automatically inventory, categorize, and document your GitHub repositories with intelligent analysis.

## What It Does

- 📊 **Fetches** all repositories from a GitHub account
- 🏷️ **Categorizes** repos by type (AI skill, app, library, tool, etc.)
- 📈 **Analyzes** activity, staleness, and importance
- 📝 **Generates** organized reports (Markdown, CSV, JSON)
- ☁️ **Exports** to cloud storage

## Installation

### Hermes Agent

```bash
# Copy to skills directory
cp -r github-catalogue-skill ~/.hermes/skills/github-catalogue

# Use it
skill_view(name='github-catalogue')
```

### Claude Code

```
@ github-catalogue-skill/SKILL.md
```

### Manual

```bash
# Requires: gh CLI, python3, jq
python3 github_catalogue.py [USERNAME] [OUTPUT_DIR]
```

## Quick Start

```bash
# Run with defaults (fetches your repos)
python3 github_catalogue.py

# Specify user and output
python3 github_catalogue.py diamitani ~/Desktop

# Full catalogue with metadata
python3 github_catalogue.py --full --include-private
```

## Generated Reports

| Format | File | Use Case |
|--------|------|----------|
| Markdown | `{USER}_github_catalogue_{DATE}.md` | Human-readable report |
| CSV | `{USER}_github_catalogue_{DATE}.csv` | Spreadsheet import, analysis |
| JSON | `{USER}_github_catalogue_{DATE}.json` | API consumption, backup |

## Example Output

### Summary Table
```markdown
| Category | Count | % |
|----------|-------|---|
| AI Agent Skill | 45 | 51% |
| Application | 22 | 25% |
| Developer Tool | 12 | 14% |
| Library/Framework | 9 | 10% |
```

### Repository Detail
```markdown
| Repository | Description | Language | Stars | Updated |
|------------|-------------|----------|-------|---------|
| [context_engine-skill](...) | Context management | Python | 12 | 2024-08-15 |
```

## Configuration

Edit patterns in `categorize_repo()` function to customize classification:

```python
def categorize_repo(name, description, topics):
    if "my-custom-pattern" in name.lower():
        return "Custom Category"
    # ...
```

## Requirements

- **GitHub CLI** (`gh`) - authenticated
- **Python 3.8+**
- **jq** (optional, for validation)

## Authentication

The skill uses your existing `gh` CLI authentication:

```bash
# Check auth status
gh auth status

# Login if needed
gh auth login
```

## Cloud Storage

Reports automatically sync if detected:

- **Google Drive**: `~/Library/CloudStorage/GoogleDrive-*/`
- **iCloud**: `~/Library/Mobile Documents/`
- **Dropbox**: `~/Dropbox/` (if exists)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "gh not found" | Install GitHub CLI: `brew install gh` |
| "not logged in" | Run `gh auth login` |
| API rate limit | Use `--limit 100` to reduce calls |
| Large repo count | Increase `--limit` or paginate |

## License

MIT
