#!/usr/bin/env python3
"""
GitHub Catalogue Generator
Automatically inventory, categorize, and document GitHub repositories.

Usage:
    python3 github_catalogue.py [USERNAME] [OUTPUT_DIR]
    python3 github_catalogue.py diamitani ~/Desktop

Requirements:
    - gh CLI (authenticated)
    - python3.8+
"""

import subprocess
import json
import csv
import sys
import argparse
from pathlib import Path
from datetime import datetime

def run_git(args, check=True):
    """Run gh command and return result."""
    result = subprocess.run(
        ['gh'] + args,
        capture_output=True, text=True
    )
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result

def fetch_repos(owner, max_repos=1000, include_private=False):
    """Fetch repositories from GitHub."""
    print(f"🔍 Fetching repositories for {owner}...")
    
    fields = [
        'name', 'description', 'url', 'createdAt', 'pushedAt',
        'primaryLanguage', 'stargazersCount', 'forkCount',
        'isPrivate', 'isArchived', 'topics'
    ]
    
    result = run_git([
        'repo', 'list', owner,
        '--limit', str(max_repos),
        '--json', ','.join(fields)
    ])
    
    repos = json.loads(result.stdout)
    
    if not include_private:
        repos = [r for r in repos if not r.get('isPrivate', False)]
    
    print(f"✓ Found {len(repos)} repositories")
    return repos

def categorize_repo(name, description, topics):
    """Auto-categorize repository based on name and content."""
    name_lower = name.lower()
    desc_lower = (description or "").lower()
    topic_list = [t.lower() for t in (topics or [])]
    
    # AI/Agent skills
    if any(s in name_lower for s in ['-skill', 'skill-', 'agent-', '-agent']):
        return "AI Agent Skill"
    if 'ai' in name_lower or 'ai' in topic_list:
        return "AI/ML Project"
    
    # Applications
    if any(s in name_lower for s in ['app', 'mobile', 'react', 'vue', 'angular', 'flutter']):
        return "Application"
    if any(s in topic_list for s in ['app', 'mobile', 'react']):
        return "Application"
    
    # Backend/API
    if any(s in name_lower for s in ['api', 'backend', 'service', 'server']):
        return "Backend/API"
    if 'api' in topic_list:
        return "Backend/API"
    
    # Libraries
    if any(s in name_lower for s in ['lib', 'sdk', 'framework', 'package']):
        return "Library/Framework"
    if any(s in topic_list for s in ['library', 'sdk', 'framework']):
        return "Library/Framework"
    
    # Infrastructure
    if any(s in name_lower for s in ['infra', 'terraform', 'ansible', 'deploy', 'kubernetes', 'docker']):
        return "Infrastructure"
    if any(s in topic_list for s in ['infrastructure', 'terraform', 'devops']):
        return "Infrastructure"
    
    # Tools
    if any(s in name_lower for s in ['tool', 'cli', 'script', 'utility']):
        return "Developer Tool"
    if 'cli' in topic_list:
        return "Developer Tool"
    
    # Documentation/Sites
    if any(s in name_lower for s in ['website', 'web', 'landing', 'docs', 'site']):
        return "Website"
    if any(s in topic_list for s in ['website', 'documentation']):
        return "Website"
    
    # Templates/Demos
    if any(s in name_lower for s in ['template', 'example', 'demo', 'boilerplate', 'starter']):
        return "Template/Demo"
    
    return "Project/Other"

def calculate_staleness(last_push):
    """Calculate days since last push."""
    if not last_push:
        return 999
    try:
        last_date = datetime.fromisoformat(last_push.replace('Z', '+00:00'))
        return (datetime.now().astimezone() - last_date).days
    except:
        return 999

def analyze_repos(repos):
    """Add derived analysis fields."""
    for repo in repos:
        repo['category'] = categorize_repo(
            repo['name'],
            repo.get('description'),
            repo.get('topics', [])
        )
        repo['staleness_days'] = calculate_staleness(repo.get('pushedAt'))
        repo['language'] = repo.get('primaryLanguage', {}).get('name', 'N/A')
    return repos

def generate_markdown_report(repos, output_path, owner):
    """Generate Markdown report."""
    print("📝 Generating Markdown report...")
    
    # Group by category
    by_category = {}
    for repo in repos:
        by_category.setdefault(repo['category'], []).append(repo)
    
    # Sort categories by count
    categories = sorted(by_category.items(), key=lambda x: -len(x[1]))
    
    # Statistics
    total = len(repos)
    active = sum(1 for r in repos if r['staleness_days'] < 30)
    stale = sum(1 for r in repos if 30 <= r['staleness_days'] < 90)
    dormant = sum(1 for r in repos if r['staleness_days'] >= 90)
    archived = sum(1 for r in repos if r.get('isArchived', False))
    
    # Build report
    lines = [
        f"# GitHub Repository Catalogue",
        f"",
        f"**Owner:** [{owner}](https://github.com/{owner})",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Total Repositories:** {total}",
        f"",
        f"---",
        f"",
        f"## 📊 Summary Statistics",
        f"",
        f"| Category | Count | Percentage |",
        f"|----------|-------|------------|",
    ]
    
    for cat, items in categories:
        pct = len(items) / total * 100
        lines.append(f"| {cat} | {len(items)} | {pct:.1f}% |")
    
    lines.extend([
        f"",
        f"## 📈 Activity Analysis",
        f"",
        f"| Status | Count | Description |",
        f"|--------|-------|-------------|",
        f"| 🟢 Active (< 30 days) | {active} | Recent commits |",
        f"| 🟡 Stale (30-90 days) | {stale} | Needs attention |",
        f"| 🔴 Dormant (90+ days) | {dormant} | Archive candidate |",
    ])
    
    if archived > 0:
        lines.append(f"| ⚪ Archived | {archived} | Read-only |")
    
    lines.extend([
        f"",
        f"---",
        f"",
        f"## 📁 Repositories by Category",
        f"",
    ])
    
    for cat, items in categories:
        lines.extend([
            f"### {cat} ({len(items)})",
            f"",
            f"| Repository | Description | Language | Stars | Updated |",
            f"|------------|-------------|----------|-------|----------|",
        ])
        
        for repo in sorted(items, key=lambda x: x.get('stargazersCount', 0), reverse=True):
            desc = repo.get('description', '') or '-'
            if len(desc) > 40:
                desc = desc[:37] + '...'
            desc = desc.replace('|', '\\|').replace('\n', ' ')
            
            lang = repo['language']
            stars = repo.get('stargazersCount', 0)
            updated = repo.get('pushedAt', '-')[:10]
            url = repo['url']
            
            status = "🟢" if repo['staleness_days'] < 30 else "🟡" if repo['staleness_days'] < 90 else "🔴"
            
            lines.append(f"| {status} [{repo['name']}]({url}) | {desc} | {lang} | {stars} | {updated} |")
        
        lines.append("")
    
    lines.extend([
        f"---",
        f"",
        f"## 🏷️ Language Distribution",
        f"",
    ])
    
    by_language = {}
    for repo in repos:
        lang = repo['language'] or 'Unknown'
        by_language[lang] = by_language.get(lang, 0) + 1
    
    lines.append("| Language | Count |")
    lines.append("|----------|-------|")
    for lang, count in sorted(by_language.items(), key=lambda x: -x[1])[:10]:
        lines.append(f"| {lang} | {count} |")
    
    lines.append("")
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    return output_path

def generate_csv(repos, output_path):
    """Generate CSV report."""
    print("📊 Generating CSV report...")
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Name', 'Category', 'Description', 'URL', 'Language',
            'Stars', 'Forks', 'Topics', 'Created', 'Last Push',
            'Staleness (days)', 'Is Private', 'Is Archived'
        ])
        
        for repo in repos:
            writer.writerow([
                repo['name'],
                repo['category'],
                repo.get('description', ''),
                repo['url'],
                repo['language'],
                repo.get('stargazersCount', 0),
                repo.get('forkCount', 0),
                ', '.join(repo.get('topics', [])),
                repo.get('createdAt', '')[:10],
                repo.get('pushedAt', '')[:10],
                repo['staleness_days'],
                repo.get('isPrivate', False),
                repo.get('isArchived', False)
            ])
    
    return output_path

def generate_json(repos, output_path, owner):
    """Generate JSON report."""
    print("🔧 Generating JSON report...")
    
    data = {
        'metadata': {
            'owner': owner,
            'generated_at': datetime.now().isoformat(),
            'total_repos': len(repos),
            'tool': 'GitHub Catalogue Skill',
            'version': '1.0.0'
        },
        'summary': {
            'by_category': {},
            'by_language': {},
            'activity': {
                'active_last_30_days': sum(1 for r in repos if r['staleness_days'] < 30),
                'stale_30_to_90_days': sum(1 for r in repos if 30 <= r['staleness_days'] < 90),
                'dormant_over_90_days': sum(1 for r in repos if r['staleness_days'] >= 90)
            }
        },
        'repositories': repos
    }
    
    for repo in repos:
        cat = repo['category']
        data['summary']['by_category'][cat] = data['summary']['by_category'].get(cat, 0) + 1
        
        lang = repo['language']
        data['summary']['by_language'][lang] = data['summary']['by_language'].get(lang, 0) + 1
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    return output_path

def copy_to_cloud(paths):
    """Copy reports to cloud storage if available."""
    copied = []
    
    # Google Drive
    gdrive = list(Path.home().glob('Library/CloudStorage/GoogleDrive-*'))
    if gdrive:
        dest = gdrive[0] / 'My Drive' / 'GitHub Catalogue'
        dest.mkdir(parents=True, exist_ok=True)
        for path in paths:
            import shutil
            new_path = shutil.copy2(path, dest)
            copied.append(('Google Drive', new_path))
        print(f"☁️  Copied to Google Drive: {dest}")
    
    # iCloud
    icloud = Path.home() / 'Library/Mobile Documents/com~apple~CloudDocs/GitHub Catalogue'
    if icloud.parent.exists():
        icloud.mkdir(parents=True, exist_ok=True)
        for path in paths:
            import shutil
            new_path = shutil.copy2(path, icloud)
            copied.append(('iCloud', new_path))
        print(f"☁️  Copied to iCloud: {icloud}")
    
    return copied

def main():
    parser = argparse.ArgumentParser(description='GitHub Repository Catalogue Generator')
    parser.add_argument('username', nargs='?', help='GitHub username')
    parser.add_argument('output_dir', nargs='?', help='Output directory')
    parser.add_argument('--private', action='store_true', help='Include private repositories')
    parser.add_argument('--limit', type=int, default=1000, help='Max repos to fetch')
    parser.add_argument('--no-cloud', action='store_true', help='Skip cloud upload')
    
    args = parser.parse_args()
    
    # Get username
    if args.username:
        owner = args.username
    else:
        # Try to get from gh
        result = run_git(['api', 'user', '-q', '.login'], check=False)
        if result.returncode == 0:
            owner = result.stdout.strip()
        else:
            owner = input("GitHub username: ").strip()
    
    output_dir = Path(args.output_dir) if args.output_dir else Path.home() / 'Desktop'
    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Fetch and analyze
    repos = fetch_repos(owner, args.limit, args.private)
    repos = analyze_repos(repos)
    
    if not repos:
        print("No repositories found!")
        sys.exit(1)
    
    # Generate reports
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    md_path = output_dir / f"{owner}_github_catalogue_{timestamp}.md"
    csv_path = output_dir / f"{owner}_github_catalogue_{timestamp}.csv"
    json_path = output_dir / f"{owner}_github_catalogue_{timestamp}.json"
    
    generate_markdown_report(repos, md_path, owner)
    generate_csv(repos, csv_path)
    generate_json(repos, json_path, owner)
    
    print(f"\n{'='*60}")
    print(f"✅ Reports generated successfully!")
    print(f"{'='*60}")
    print(f"\n📄 Markdown: {md_path}")
    print(f"📊 CSV:      {csv_path}")
    print(f"🔧 JSON:     {json_path}")
    
    # Cloud upload
    if not args.no_cloud:
        copied = copy_to_cloud([md_path, csv_path, json_path])
        if copied:
            print(f"\n{'='*60}")
            print("Cloud sync complete")
    
    print(f"\n{'='*60}")
    print(f"Total: {len(repos)} repositories catalogued")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
