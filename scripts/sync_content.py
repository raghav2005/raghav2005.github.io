#!/usr/bin/env python3
"""Import public content. No TeX execution, scraping private files, or third-party deps."""
import argparse
import email.utils
import html
import json
from pathlib import Path
import re
import shutil
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

def download(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'raghav2005-portfolio/1.0'})
    with urllib.request.urlopen(request, timeout=40) as response:
        return response.read()

def argument(text, pos):
    while pos < len(text) and text[pos].isspace(): pos += 1
    if pos >= len(text) or text[pos] != '{': raise ValueError(f'Expected TeX argument at {pos}')
    start, depth = pos + 1, 1
    pos += 1
    while pos < len(text):
        if text[pos] == '\\': pos += 2; continue
        if text[pos] == '{': depth += 1
        if text[pos] == '}':
            depth -= 1
            if depth == 0: return text[start:pos], pos + 1
        pos += 1
    raise ValueError('Unclosed TeX argument')

def commands(text, name, count):
    for match in re.finditer(r'\\' + re.escape(name) + r'\b', text):
        pos = match.end(); args = []
        for _ in range(count):
            value, pos = argument(text, pos); args.append(value)
        yield args, pos, match.start()

def plain(text):
    for name, count, selected in [('href', 2, 1), ('textbf', 1, 0), ('textit', 1, 0), ('emph', 1, 0)]:
        matches = list(commands(text, name, count))
        for args, end, start in reversed(matches): text = text[:start] + args[selected] + text[end:]
    for old, new in [(r'\%', '%'), (r'\&', '&'), (r'\_', '_'), (r'\#', '#'), ('~', ' ')]: text = text.replace(old, new)
    text = re.sub(r'\s+', ' ', text).strip()
    if '\\' in text: raise ValueError(f'Unsupported TeX in content: {text}')
    return text

def bullet_list(text):
    match = re.search(r'\\begin\{resumeBullets\}(.*?)\\end\{resumeBullets\}', text, re.S)
    if not match: raise ValueError('Missing resumeBullets block')
    return [plain(v) for v in re.split(r'\\item\b', match.group(1))[1:]]

def parse_resume(content, education):
    experiences=[]; projects=[]
    for args, end, _ in commands(content, 'resumeExperience', 4):
        experiences.append(dict(zip(['role', 'dates', 'company', 'location'], map(plain, args)), bullets=bullet_list(content[end:])))
    for args, end, _ in commands(content, 'resumeProject', 3):
        links=list(commands(args[0], 'href', 2))
        projects.append(dict(zip(['name', 'technology', 'dates'], map(plain, args)), url=links[0][0][0] if links else None, bullets=bullet_list(content[end:])))
    skills=[{'category':plain(args[0]),'items':plain(args[1])} for args,_,_ in commands(content,'resumeSkill',2)]
    schools=[]
    for m in re.finditer(r'\\textbf\{(.*?)\}\\hfill (.*?)\\\\\[\dpt\]\s*\\textit\{(.*?)\}\\hfill ([^\n]+)',education):
        date=re.sub(r'\\\\\[\dpt\]$', '', m[4])
        schools.append(dict(zip(['name','location','qualification','dates'],map(plain,[m[1],m[2],m[3],date]))))
    leadership=bullet_list(content.split(r'\section{Open Source and Leadership}',1)[1])
    if not experiences or not projects or not skills or not schools: raise ValueError('Incomplete CV import')
    return dict(name='Raghav Awasthi',experiences=experiences,projects=projects,skills=skills,education=schools,leadership=leadership)

def write_json(path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')

def sync_blogs(rss, sitemap):
    path=ROOT/'data/writing.json'
    existing=json.loads(path.read_text()) if path.exists() else []
    posts={x['url']:x for x in existing}
    for item in ET.fromstring(rss).findall('./channel/item'):
        url=item.findtext('link'); title=item.findtext('title')
        old=posts.get(url,{})
        posts[url]={**old,'title':re.sub(r'^\d{2}/\d{2}/\d{2}\s*-\s*','',title),'url':url,'date':email.utils.parsedate_to_datetime(item.findtext('pubDate')).date().isoformat(),'publication':'Quantum Proximity Gateway','summary':old.get('summary') or html.unescape(item.findtext('description') or '')}
    urls={x.text for x in ET.fromstring(sitemap).iter() if x.tag.endswith('}loc') and x.text}
    expected={u for u in urls if re.search(r'qpg\.hashnode\.dev/\d',u)}
    missing=expected-posts.keys()
    if missing: raise ValueError('Blog archive needs older posts not in RSS: '+', '.join(sorted(missing)))
    posts['https://ucldevs.hashnode.dev/vscode-to-emacs-the-beginning-why']={
        'title':'VSCode to Emacs — the Beginning: Why?', 'url':'https://ucldevs.hashnode.dev/vscode-to-emacs-the-beginning-why',
        'date':'2023-12-10','publication':'UCL Devs','summary':'Why I switched to Emacs: keyboard-first development, customisation, Org mode, and the joys of a steeper learning curve.','readMinutes':7}
    write_json(path, sorted(posts.values(),key=lambda x:x['date'],reverse=True))
    print(f'Writing: {len(posts)} articles; all {len(expected)} QPG sitemap posts covered.')

def main():
    p=argparse.ArgumentParser(); p.add_argument('--cv-dir',type=Path); p.add_argument('--remote',action='store_true'); p.add_argument('--rss',type=Path); p.add_argument('--sitemap',type=Path); a=p.parse_args()
    if a.cv_dir:
        cv=a.cv_dir
        content=(cv/'master-resume/content.tex').read_text(); education=(cv/'shared/education.tex').read_text()
        source={'repository':'https://github.com/raghav2005/cv','path':'master-resume/content.tex','revision':'local-working-copy'}
    elif a.remote:
        commit=json.loads(download('https://api.github.com/repos/raghav2005/cv/commits/main'))['sha']
        base=f'https://raw.githubusercontent.com/raghav2005/cv/{commit}/'
        content=download(base+'master-resume/content.tex').decode(); education=download(base+'shared/education.tex').decode()
        source={'repository':'https://github.com/raghav2005/cv','path':'master-resume/content.tex','revision':commit}
    else: p.error('Choose --cv-dir or --remote')
    result=parse_resume(content,education); result['source']=source
    # Validate all imports before overwriting committed snapshots.
    rss=a.rss.read_bytes() if a.rss else download('https://qpg.hashnode.dev/rss.xml')
    sitemap=a.sitemap.read_bytes() if a.sitemap else download('https://qpg.hashnode.dev/sitemap.xml')
    sync_blogs(rss,sitemap)
    write_json(ROOT/'data/resume.json',result)
    print(f'CV: {len(result["experiences"])} roles, {len(result["projects"])} projects, {len(result["skills"])} skill groups, {len(result["education"])} schools.')

if __name__=='__main__': main()
