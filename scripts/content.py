"""Combine the CV source with explicitly supplied portfolio-only additions."""
from copy import deepcopy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_content():
    cv = json.loads((ROOT / 'data/resume.json').read_text())
    profile = json.loads((ROOT / 'data/profile.json').read_text())
    result = deepcopy(cv)
    # If a portfolio addition later moves into the master CV, prefer the CV entry.
    existing_roles = {(x['company'].casefold(), x['role'].casefold()) for x in result['experiences']}
    result['experiences'] += [r for r in profile['earlierExperience'] if (r['company'].casefold(), r['role'].casefold()) not in existing_roles]
    for project in result['projects']:
        project.update(profile['projectEnhancements'].get(project['name'], {}))
    existing_projects = {p['name'] for p in result['projects']}
    result['projects'] += [p for p in profile['earlierProjects'] if p['name'] not in existing_projects]
    result['leadership'] = [entry for line in cv['leadership'] for entry in profile['leadershipReplacements'].get(line, [line])]
    for entries in profile['leadershipReplacements'].values():
        result['leadership'] += [entry for entry in entries if entry not in result['leadership']]
    result['awards'] = profile['awards']
    result['hobbies'] = profile['hobbies']
    result['contact'] = profile['contact']
    links = json.loads((ROOT / 'data/links.json').read_text())
    for project in result['projects']:
        project['url'] = project.get('url') or links['projects'].get(project['name'], {}).get('url')
    return result
