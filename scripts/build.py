#!/usr/bin/env python3
"""Build a complete static portfolio with Python's standard library."""
from datetime import date
from html import escape
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist'
CV=json.loads((ROOT/'data/resume.json').read_text())
WRITING=json.loads((ROOT/'data/writing.json').read_text())
LINKS=json.loads((ROOT/'data/links.json').read_text())
ARROW='<span class="arrow" aria-hidden="true">↗</span>'
def e(v): return escape(str(v),quote=True)
def render(template,values):
    for key,value in values.items(): template=template.replace('{{'+key+'}}',str(value))
    return template

def visual(kind):
    if kind=='cache': return '''<div class="project-visual cache-visual" role="img" aria-label="Walrus Cache benchmark: average latency 85 milliseconds without cache, 20.5 milliseconds with cache. 4.2 times retrieval throughput on 100,000 requests."><div class="visual-top"><span>WALRUS / CACHE BENCHMARK</span><span class="visual-tag">Rust</span></div><div class="benchmark"><div class="bar-row"><span>Baseline</span><div class="bar-track"><div class="bar"></div></div><span>85.0 ms</span></div><div class="bar-row"><span>Cached</span><div class="bar-track"><div class="bar bar-fast" style="width:24.12%"></div></div><span>20.5 ms</span></div><div class="bench-bottom"><strong>4.2×</strong><span>retrieval throughput · 100k requests</span></div></div></div>'''
    return '''<div class="project-visual gateway-visual" role="img" aria-label="Quantum Proximity Gateway architecture: BLE proximity, face verification, and USB keyboard authentication."><div class="visual-top"><span>QUANTUM PROXIMITY GATEWAY</span><span class="visual-tag" style="color:#233881;border-color:#aebbe8">IBM × UCL</span></div><div class="gateway-flow"><div class="gateway-node"><strong>01</strong><span>Proximity</span></div><span class="flow-line"></span><div class="gateway-node"><strong>02</strong><span>Identity</span></div><span class="flow-line"></span><div class="gateway-node"><strong>03</strong><span>Access</span></div></div><div class="visual-footer"><span>ESP32 → Raspberry Pi → Pico</span><span>Edge to cloud</span></div></div>'''

def featured():
    cards=[]
    items=[('cache','Systems · UCL dissertation','Walrus Cache CDN','A lifecycle-aware, two-tier Rust cache for the Walrus decentralised storage network.','https://github.com/raghav2005/Walrus-Cache-CDN-FYP','walrus-cache-cdn'),('gateway','Hardware · Security · IBM × UCL','Quantum Proximity Gateway','Walk up. Verify. Get to work. Multi-factor authentication that connects proximity sensing with facial recognition.','https://github.com/proximity-gateway/main','quantum-proximity-gateway')]
    for kind,category,title,desc,url,slug in items:
        cards.append(f'<article class="project-card">{visual(kind)}<div class="project-caption"><span class="label">{e(category)}</span><h3><a href="/projects/#{slug}">{e(title)}</a></h3><p>{e(desc)}</p><div class="inline-links"><a href="/projects/#{slug}">Explore project {ARROW}</a><a href="{url}">Source code {ARROW}</a></div></div></article>')
    return ''.join(cards)

def page(path,title,description,content):
    target=OUT/path;target.parent.mkdir(parents=True,exist_ok=True)
    url='https://raghav2005.github.io/'+str(path).removesuffix('index.html')
    document=render((ROOT/'src/layout.html').read_text(),dict(TITLE=e(title),DESCRIPTION=e(description),CANONICAL=url,YEAR=date.today().year,CONTENT=content,PROJECTS_CURRENT='aria-current="page"' if str(path)=='projects/index.html' else '',WRITING_CURRENT='aria-current="page"' if str(path)=='writing/index.html' else ''))
    target.write_text(document)

def bullets(items): return '<ul class="bullets">'+''.join(f'<li>{e(item)}</li>' for item in items)+'</ul>'

def section_heading(index,title,link=''):
    return f'<div class="section-heading"><div><span class="index">{e(index)}</span><h2>{e(title)}</h2></div>{link}</div>'

def writing_list(posts,descriptions=False):
    rows=[]
    for post in posts:
        dt=date.fromisoformat(post['date'])
        read=f' · {post["readMinutes"]} min read' if post.get('readMinutes') else ''
        desc=f'<p>{e(post["summary"])}</p>' if descriptions else ''
        rows.append(f'<a class="writing-item" href="{e(post["url"])}"><time datetime="{post["date"]}">{dt.strftime("%d %b %Y")}</time><div><span class="label">{e(post["publication"]+read)}</span><h3>{e(post["title"])}</h3>{desc}</div>{ARROW}</a>')
    return '<div class="writing-list">'+''.join(rows)+'</div>'

def contact():
    return f'<section class="contact"><div class="shell contact-inner"><div><h2>Have something in mind?</h2><p>Let’s talk about systems, AI, security, or what you’re building.</p></div><a class="button" href="mailto:raghavawasthi@me.com">raghavawasthi@me.com {ARROW}</a></div></section>'

def home_sections():
    rows=[]
    for role in CV['experiences']:
        extra=''
        if len(role['bullets'])>2:
            extra=f'<details><summary>More about this role<span class="sr-only"> at {e(role["company"])}</span></summary>{bullets(role["bullets"][2:])}</details>'
        rows.append(f'<article class="experience-row"><div class="experience-meta"><h3>{e(role["company"])}</h3><span class="dates">{e(role["dates"])}</span><span class="location">{e(role["location"])}</span></div><div class="experience-body"><h3>{e(role["role"])}</h3>{bullets(role["bullets"][:2])}{extra}</div></article>')
    experience='<section class="section shell" id="experience">'+section_heading('02 / Experience','From research to real systems.')+''.join(rows)+'</section>'
    contributions=''.join(f'<article class="contribution"><span class="label">{e(c["language"])}</span><h3>{e(c["name"])}</h3><p>{e(c["description"])}</p><a class="text-link" href="{e(c["url"])}">Merged contribution {ARROW}</a></article>' for c in LINKS['contributions'])
    opensource='<section class="section shell">'+section_heading('03 / Open source','Small changes. Shared impact.')+'<div class="contribution-grid">'+contributions+'</div></section>'
    writing='<section class="section shell" id="writing">'+section_heading('04 / Writing','Notes from the build.',f'<a class="text-link" href="/writing/">All {len(WRITING)} articles {ARROW}</a>')+writing_list(WRITING[:2]+[WRITING[-1]])+'</section>'
    education=''.join(f'<article class="education"><span class="label">{e(s["dates"])} · {e(s["location"])}</span><h3>{e(s["name"])}</h3><p>{e(s["qualification"])}</p></article>' for s in CV['education'])
    skills=''.join(f'<div class="skill"><h3>{e(s["category"])}</h3><p>{e(s["items"])}</p></div>' for s in CV['skills'])
    leadership=''.join(f'<p>{e(item)}</p>' for item in CV['leadership'])
    about=f'''<section class="section shell" id="about"><div class="about-grid"><div class="about-copy"><span class="index">05 / A little more about me</span><h2>Curiosity, all the way down.</h2><p>I’m a software engineer and a First Class Computer Science graduate from UCL. My work spans the layers of computing: storage and distributed systems, machine learning, and the security that holds them together.</p><p>I enjoy understanding how things work, then making them work better — whether that means writing a Rust cache, investigating security telemetry, or teaching someone to program.</p><div class="leadership">{leadership}</div><div class="inline-links"><a href="https://github.com/raghav2005/programming-tutor-25-26">Teaching materials {ARROW}</a><a href="/resume.pdf">Full résumé {ARROW}</a></div></div><div>{education}</div></div><div class="skills">{skills}</div><aside class="press"><div><span class="label">In the press</span><p>Gulf News · 2022</p></div><div><h3>‘AI and ethics go together’</h3><p>A conversation about early AI projects, tackling misinformation, and the connection between computer science and philosophy.</p></div><a class="text-link" href="https://gulfnews.com/friday/art-people/ai-and-ethics-go-together-1.2315026">Read the interview {ARROW}</a></aside></section>'''
    return experience+opensource+writing+about+contact()

def projects_page():
    rows=[]
    for n,project in enumerate(CV['projects'],1):
        info=LINKS['projects'].get(project['name'],{})
        slug=info.get('slug',f'project-{n}')
        url=project.get('url') or info.get('url')
        links=f'<a href="{e(url)}">Source code {ARROW}</a>' if url else ''
        if info.get('writing'): links+=f'<a href="{e(info["writing"])}">Project journal {ARROW}</a>'
        rows.append(f'<article class="project-detail" id="{e(slug)}"><div><span class="label">{n:02d} / {e(info.get("category","Project"))}</span><span class="dates">{e(project["dates"])}</span><p class="technology">{e(project["technology"])}</p></div><div><h2>{e(info.get("title",project["name"]))}</h2>{bullets(project["bullets"])}<div class="inline-links">{links}</div></div></article>')
    extras=''.join(f'<article class="extra-project"><span class="label">{e(p["category"])}</span><h3>{e(p["name"])}</h3><p>{e(p["description"])}</p><p class="technology">{e(p["technology"])}</p><a class="text-link" href="{e(p["url"])}">View on GitHub {ARROW}</a></article>' for p in LINKS['additionalProjects'])
    return f'<header class="page-head shell"><span class="eyebrow">Projects & experiments</span><h1>Built to find out<em>.</em></h1><p>From decentralised storage and edge authentication to AI, developer tools, and post-quantum cryptography. A selection of things I’ve built and explored.</p></header><div class="shell">{"".join(rows)}</div><section class="section shell">{section_heading("Beyond the résumé","More on my workbench.")}<div class="extra-grid">{extras}</div><a class="back-link" href="https://github.com/raghav2005?tab=repositories">Explore all repositories {ARROW}</a></section>'+contact()

def writing_page():
    return f'<header class="page-head shell"><span class="eyebrow">Field notes / {len(WRITING):02d} articles</span><h1>Learning in public<em>.</em></h1><p>Build logs from Quantum Proximity Gateway, the problems we ran into along the way, and a detour into the world of Emacs.</p><div class="archive-note"><a href="https://qpg.hashnode.dev/">Quantum Proximity Gateway {ARROW}</a><a href="https://ucldevs.hashnode.dev/vscode-to-emacs-the-beginning-why">UCL Devs {ARROW}</a></div></header><section class="archive-content shell" aria-label="All articles">{writing_list(WRITING,True)}</section>'+contact()

def main():
    OUT.mkdir(exist_ok=True)
    shutil.copytree(ROOT/'public',OUT,dirs_exist_ok=True)
    shutil.copyfile(ROOT/'src/style.css',OUT/'style.css')
    current=next((r for r in CV['experiences'] if 'Present' in r['dates']),None)
    note=f'Currently <strong>{e(current["role"])} at {e(current["company"])}</strong>' if current else 'Software engineering · Applied AI · Security'
    home=render((ROOT/'src/home.html').read_text(),dict(CURRENT_ROLE=note,FEATURED_PROJECTS=featured(),HOME_SECTIONS=home_sections()))
    page(Path('index.html'),'Raghav Awasthi — Software Engineer','Software engineer working across backend systems, applied AI, and security. UCL Computer Science, First Class Honours. Projects, experience, and writing.',home)
    page(Path('projects/index.html'),'Projects — Raghav Awasthi','Projects in distributed systems, AI, edge authentication, developer tools, and post-quantum cryptography by Raghav Awasthi.',projects_page())
    page(Path('writing/index.html'),'Writing — Raghav Awasthi','All Quantum Proximity Gateway build logs, plus writing on Emacs for UCL Devs, by Raghav Awasthi.',writing_page())
    page(Path('404.html'),'Page not found — Raghav Awasthi','This page could not be found.',f'<section class="page-head shell"><span class="eyebrow">404 / A wrong turn</span><h1>Nothing here<em>.</em></h1><p>The page may have moved. You can find my work, projects, and writing back at the start.</p><a class="back-link" href="/">Back to the homepage {ARROW}</a></section>')
    (OUT/'.nojekyll').touch()
    (OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://raghav2005.github.io/sitemap.xml\n')
    (OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>https://raghav2005.github.io/{p}</loc></url>' for p in ['', 'projects/', 'writing/'])+'</urlset>')
    print('Built portfolio in dist/')

if __name__=='__main__': main()
