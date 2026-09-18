---
name: github-catalogue-skill
description: >
  Automatically inventory GitHub repositories, categorize them, and generate organized catalogue reports with analysis Use this skill when working with github catalogue skill tasks or workflows.
---

# GitHub Catalogue Skill

Automatically inventory, categorize, and document GitHub repositories with intelligent analysis and organized reporting.

## Purpose

This skill enables AI agents to:
1. **Inventory** all repositories from a GitHub account
2. **Categorize** repos by type, language, and purpose
3. **Analyze** commit activity, staleness, and importance
4. **Generate** organized reports (Markdown, CSV, JSON)
5. **Export** to cloud storage (Google Drive, iCloud, etc.)

## Trigger Conditions

Invoke this skill when user asks:
- "Catalogue my GitHub repos"
- "Inventory my repositories"
- "Analyze my GitHub account"
- "Create a report of all my repos"
- "Organize my GitHub projects"

## Execution Flow

```
User Intent
    ↓
[1] Fetch all repos via GitHub API
    ↓
[2] Categorize (AI/Skill, App, Tool, Library, etc.)
    ↓
[3] Analyze (activity, size, language, staleness)
    ↓
[4] Generate reports (Markdown + CSV + JSON)
    ↓
[5] Optional: Upload to cloud storage
    ↓
Return organized catalogue to user
```

## Tool Requirements

| Tool | Purpose |
|------|---------|
| `gh` CLI | List repositories, get metadata |
| `curl`/`gh api` | Fetch detailed repo data |
| `jq` | Parse JSON responses |
| `python3` | Generate reports, analysis |
| `rclone` | Upload to cloud storage (optional) |

## Command Reference

### List All Repositories
```bash
gh repo list {OWNER} --limit {MAX} --json "name,description,url,createdAt,pushedAt,primaryLanguage,stargazersCount,forkCount,isPrivate,topics"
```

### Get Repo Details
```bash
gh api repos/{OWNER}/{REPO} --jq '{...}'
```

### Get Recent Commits (activity)
```bash
gh api repos/{OWNER}/{REPO}/commits?per_page=1 --jq '.[0].commit.committer.date'
```

## Categorization Rules

Auto-detect category based on name/content:

| Pattern | Category |
|---------|----------|
| `-skill`, `skill-` | AI Agent Skill |
| `ai-`, `-ai` | AI/ML Project |
| `app-`, `-app`, `mobile` | Application |
| `api-`, `-api`, `backend` | Backend/API |
| `lib-`, `-lib`, `sdk` | Library/Framework |
| `tool-`, `-tool`, `cli` | Developer Tool |
| `web-`, `-web`, `site` | Website |
| `demo`, `example`, `template` | Template/Demo |
| `infra`, `deploy`, `terraform` | Infrastructure |
| `doc`, `guide`, `wiki` | Documentation |

## Report Templates

### Markdown Report Structure
```markdown
# GitHub Repository Catalogue

**Account:** {OWNER}
**Generated:** {DATE}
**Total Repos:** {COUNT}

## Summary Statistics
| Category | Count | % of Total |
|----------|-------|------------|
...

## Repository Details

### Category: {CATEGORY}
| Repo | Description | Stars | Language | Updated |
|------|-------------|-------|----------|---------|
...

## Activity Analysis
- Active (last 30 days): X repos
- Stale (6+ months): Y repos
- Archived: Z repos
```

## Python Report Generator

```python
#!/usr/bin/env python3
"""GitHub Catalogue Report Generator"""

import json
import csv
from datetime import datetime
from pathlib import Path

def categorize_repo(name, description, topics):
    """Auto-categorize repo based on signals."""
    name_lower = name.lower()
    desc_lower = (description or "").lower()
    
    if "skill" in name_lower or "ai-" in name_lower:
        return "AI Agent Skill"
    elif any(t in name_lower for t in ["app", "mobile", "react", "vue"]):
        return "Application"
    elif any(t in name_lower for t in ["api", "backend", "service"]):
        return "Backend/API"
    elif any(t in name_lower for t in ["lib", "sdk", "framework"]):
        return "Library/Framework"
    elif any(t in name_lower for t in ["tool", "cli", "script"]):
        return "Developer Tool"
    elif any(t in name_lower for t in ["website", "web", "landing"]):
        return "Website"
    elif any(t in name_lower for t in ["infrastructure", "terraform", "deploy"]):
        return "Infrastructure"
    else:
        return "Project/Other"

def calculate_staleness(last_push):
    """Calculate staleness in days."""
    if not last_push:
        return 999
    last_date = datetime.fromisoformat(last_push.replace('Z', '+00:00'))
    return (datetime.now().astimezone() - last_date).days

def generate_markdown_report(repos, output_path, owner):
    """Generate organized Markdown report."""
    # Categorize
    categorized = {}
    for repo in repos:
        cat = categorize_repo(repo['name'], repo.get('description'), repo.get('topics', []))
        categorized.setdefault(cat, []).append(repo)
    
    # Build report
    report = f"""# GitHub Repository Catalogue

**Owner:** {owner}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Total Repositories:** {len(repos)}

## Summary Statistics

| Category | Count | % |
|----------|-------|---|
"""
    for cat, items in sorted(categorized.items(), key=lambda x: -len(x[1])):
        pct = len(items) / len(repos) * 100
        report += f"| {cat} | {len(items)} | {pct:.1f}% |\n"
    
    report += f"""

## Activity Overview

| Status | Count | Description |
|--------|-------|-------------|
| Active (< 30 days) | {sum(1 for r in repos if calculate_staleness(r.get('pushedAt')) < 30)} | Recent activity |
| Stale (30-90 days) | {sum(1 for r in repos if 30 <= calculate_staleness(r.get('pushedAt')) < 90)} | Needs attention |
| Dormant (90+ days) | {sum(1 for r in repos if calculate_staleness(r.get('pushedAt')) >= 90)} | Archive candidate |

## Repositories by Category

"""
    for cat, items in sorted(categorized.items(), key=lambda x: -len(x[1])):
        report += f"### {cat} ({len(items)})\n\n"
        report += "| Repository | Description | Language | Stars | Updated |\n"
        report += "|------------|-------------|----------|-------|---------|\n"
        for repo in sorted(items, key=lambda x: x.get('stargazersCount', 0), reverse=True):
            desc = (repo.get('description') or "")[:40] + "..." if len(repo.get('description') or "") > 43 else (repo.get('description') or "-")
            lang = repo.get('primaryLanguage', {}).get('name', '-')
            stars = repo.get('stargazersCount', 0)
            updated = repo.get('pushedAt', '-')[:10]
            report += f"| [{repo['name']}]({repo['url']}) | {desc} | {lang} | {stars} | {updated} |\n"
        report += "\n"
    
    with open(output_path, 'w') as f:
        f.write(report)
    return output_path

def generate_csv(repos, output_path):
    """Generate CSV for spreadsheet import."""
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Category', 'Description', 'URL', 'Language', 
                        'Stars', 'Forks', 'Created', 'Last Push', 'Is Private'])
        for repo in repos:
            writer.writerow([
                repo['name'],
                categorize_repo(repo['name'], repo.get('description'), repo.get('topics', [])),
                repo.get('description', ''),
                repo['url'],
                repo.get('primaryLanguage', {}).get('name', ''),
                repo.get('stargazersCount', 0),
                repo.get('forkCount', 0),
                repo.get('createdAt', '')[:10],
                repo.get('pushedAt', '')[:10],
                repo.get('isPrivate', False)
            ])
    return output_path

def generate_json(repos, output_path, owner):
    """Generate JSON with full metadata."""
    data = {
        'generated_at': datetime.now().isoformat(),
        'owner': owner,
        'total_repos': len(repos),
        'repositories': [
            {
                **repo,
                'category': categorize_repo(repo['name'], repo.get('description'), repo.get('topics', [])),
                'staleness_days': calculate_staleness(repo.get('pushedAt'))
            }
            for repo in repos
        ]
    }
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    return output_path
```

## Execution Script

```python
#!/usr/bin/env python3
"""GitHub Catalogue - Main execution"""

import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime

REPORT_GENERATOR = '''
{Paste the Python report generator code here}
'''

def main():
    owner = sys.argv[1] if len(sys.argv) > 1 else input("GitHub username: ")
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.home() / "Desktop"
    
    # Fetch repos
    print(f"Fetching repositories for {owner}...")
    result = subprocess.run(
        ['gh', 'repo', 'list', owner, '--limit', '1000', 
         '--json', 'name,description,url,createdAt,pushedAt,primaryLanguage,stargazersCount,forkCount,isPrivate,topics'],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return
    
    repos = json.loads(result.stdout)
    print(f"Found {len(repos)} repositories")
    
    # Generate reports
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    md_path = output_dir / f"{owner}_github_catalogue_{timestamp}.md"
    csv_path = output_dir / f"{owner}_github_catalogue_{timestamp}.csv"
    json_path = output_dir / f"{owner}_github_catalogue_{timestamp}.json"
    
    # Save report generator
    generator_path = output_dir / f"report_generator_{timestamp}.py"
    with open(generator_path, 'w') as f:
        f.write(REPORT_GENERATOR)
    
    # Run generation
    print("Generating reports...")
    exec(compile(REPORT_GENERATOR, '<string>', 'exec'))
    
    generate_markdown_report(repos, md_path, owner)
    generate_csv(repos, csv_path)
    generate_json(repos, json_path, owner)
    
    print(f"\nReports generated:")
    print(f"  Markdown: {md_path}")
    print(f"  CSV:      {csv_path}")
    print(f"  JSON:     {json_path}")
    
    # Upload to Google Drive if available
    if (Path.home() / 'Library/CloudStorage/GoogleDrive-*').exists():
        print("\nUploading to Google Drive...")
        for f in [md_path, csv_path, json_path]:
            subprocess.run(['cp', str(f), str(Path.home() / 'Desktop')])
        print("Copied to Desktop for cloud sync")

if __name__ == '__main__':
    main()
```

## Cloud Storage Integration

### Google Drive (macOS)
```bash
# Destination path
"$HOME/Library/CloudStorage/GoogleDrive-{EMAIL}/My Drive/GitHub Catalogue/"
```

### iCloud
```bash
"$HOME/Library/Mobile Documents/com~apple~CloudDocs/GitHub Catalogue/"
```

## Output Files

| File | Format | Purpose |
|------|--------|---------|
| `{USER}_github_catalogue_{DATE}.md` | Markdown | Human-readable report |
| `{USER}_github_catalogue_{DATE}.csv` | CSV | Spreadsheet/analysis |
| `{USER}_github_catalogue_{DATE}.json` | JSON | Machine-readable data |
| `report_generator_{DATE}.py` | Python | Reusable script |

## Usage Examples

### Basic Usage
```
@github-catalogue-skill
Catalogue my GitHub repos
```

### With Custom Output
```
@github-catalogue-skill
Inventory repos for user "acmecorp" and save to ~/projects/analysis/
```

### Include Archived/Private
```
@github-catalogue-skill
Full catalogue including private and archived repos
```

## CLI Command

Once skill is installed, run via:

```bash
# Interactive
python3 ~/.hermes/skills/github-catalogue/github_catalogue.py

# With args
python3 ~/.hermes/skills/github-catalogue/github_catalogue.py diamitani ~/Desktop
```

## Extension Points

1. **Custom categorization rules** - Add patterns to `categorize_repo()`
2. **Additional analytics** - Code complexity, dependency analysis
3. **Visualization** - Generate graphs/charts (PNG/SVG)
4. **Comparisons** - Track catalogue changes over time
5. **Auto-archival** - Suggest repos to archive based on staleness

## Validation

Verify report completeness:
- [ ] All repos accounted for (compare with `gh repo list --limit 9999 | wc -l`)
- [ ] Categories sum to total
- [ ] Dates parsed correctly (ISO 8601)
- [ ] Links are clickable in Markdown
- [ ] CSV opens correctly in spreadsheet

## Metadata

```json
{
  "skill_version": "1.0.0",
  "requires_auth": true,
  "language": "python",
  "external_deps": ["gh CLI", "jq"],
  "output_formats": ["markdown", "csv", "json"],
  "estimated_runtime": "30-60s per 100 repos"
}
```
