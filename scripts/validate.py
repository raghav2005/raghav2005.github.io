#!/usr/bin/env python3
"""Check rendered content coverage, local destinations, metadata, and PDF download."""
from html.parser import HTMLParser
from pathlib import Path
import json
from content import load_content
from urllib.parse import urlsplit,unquote

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'dist'
class Document(HTMLParser):
    def __init__(self,text):
        super().__init__(); self.ids=set(); self.links=[]; self.h1=0; self.text=[]; self.title=False; self.description=False; self.canonical=False
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:
            assert a['id'] not in self.ids, f'Duplicate id: {a["id"]}'
            self.ids.add(a['id'])
        if tag=='h1': self.h1+=1
        if tag=='title': self.title=True
        if tag=='meta' and a.get('name')=='description': self.description=bool(a.get('content'))
        if tag=='link' and a.get('rel')=='canonical': self.canonical=True
        for attr in ['href','src']:
            if attr in a: self.links.append(a[attr])
    def handle_data(self,data): self.text.append(data)

docs={p:Document(p.read_text()) for p in OUT.rglob('*.html')}
for path,doc in docs.items():
    raw=path.read_text()
    assert '{{' not in raw and '}}' not in raw, f'Template leak in {path}'
    assert doc.h1==1 and doc.title and doc.description and doc.canonical, f'Metadata or heading issue in {path}'
    for link in doc.links:
        parts=urlsplit(link)
        assert parts.scheme in ['', 'https','mailto'], f'Unexpected URL scheme: {link}'
        if parts.scheme or parts.netloc: continue
        target=OUT/unquote(parts.path).lstrip('/') if parts.path else path
        if target.is_dir(): target=target/'index.html'
        assert target.exists(), f'Broken local destination from {path}: {link}'
        if parts.fragment: assert unquote(parts.fragment) in docs[target].ids, f'Broken anchor: {link}'
cv=load_content()
home=' '.join(docs[OUT/'index.html'].text)
projects=' '.join(docs[OUT/'projects/index.html'].text)
for role in cv['experiences']:
    for bullet in role['bullets']: assert bullet in home, f'Missing experience bullet: {bullet}'
for project in cv['projects']:
    for bullet in project['bullets']: assert bullet in projects, f'Missing project bullet: {bullet}'
for skill in cv['skills']: assert skill['items'] in home, f'Missing skill group: {skill}'
for school in cv['education']: assert school['qualification'] in home, f'Missing education: {school}'
for line in cv['leadership']: assert line in home, f'Missing leadership: {line}'
writing=json.loads((ROOT/'data/writing.json').read_text())
assert len(writing)==len({p['url'] for p in writing}), 'Duplicate writing URLs'
for post in writing: assert post['url'] in docs[OUT/'writing/index.html'].links, f'Missing article: {post}'
for award in cv['awards']:
    assert award['result'] in home and award['title'] in home, f'Missing award: {award}'
for hobby in cv['hobbies']:
    assert hobby['description'] in home, f'Missing hobby: {hobby}'
for path,doc in docs.items():
    assert all(url == 'mailto:'+cv['contact']['emailTarget'] for url in doc.links if url.startswith('mailto:')), f'Wrong email target in {path}'
    assert 'raghavawasthi@me.com' not in path.read_text(), f'Old email remains in {path}'
    assert cv['contact']['emailTarget'] not in ' '.join(doc.text), f'Tagged email exposed in display text in {path}'
assert cv['contact']['emailDisplay'] in home
pdf=(OUT/'resume.pdf').read_bytes()
assert pdf.startswith(b'%PDF-'), 'Invalid résumé PDF'
assert ('mailto:'+cv['contact']['emailTarget']).encode() in pdf, 'PDF email target missing'
assert b'mailto:raghavawasthi@me.com' not in pdf, 'PDF old email target remains'

print(f'Validated {len(docs)} pages, {len(cv["experiences"])} roles, {len(cv["projects"])} CV projects, all skills/education/leadership, {len(writing)} articles, and all local links.')
