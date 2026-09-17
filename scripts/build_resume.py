"""Generate the portfolio résumé from exactly the same content as the website."""
from html import escape
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, PageBreak,
)

INK = colors.HexColor('#202838')
MUTED = colors.HexColor('#505d70')
ACCENT = colors.HexColor('#254fa8')
STYLES = {
    'name': ParagraphStyle('name',fontName='Helvetica-Bold',fontSize=27,leading=31,textColor=INK,spaceAfter=7),
    'contact': ParagraphStyle('contact',fontName='Helvetica',fontSize=9,leading=14,textColor=ACCENT,spaceAfter=3),
    'section': ParagraphStyle('section',fontName='Helvetica-Bold',fontSize=12,leading=16,textColor=ACCENT,spaceBefore=13,spaceAfter=8,keepWithNext=True),
    'heading': ParagraphStyle('heading',fontName='Helvetica-Bold',fontSize=10,leading=14,textColor=INK,spaceBefore=9,spaceAfter=2,keepWithNext=True),
    'meta': ParagraphStyle('meta',fontName='Helvetica',fontSize=9,leading=12,textColor=MUTED,spaceAfter=5,keepWithNext=True),
    'body': ParagraphStyle('body',fontName='Helvetica',fontSize=9.3,leading=13,textColor=INK,spaceAfter=5),
    'bullet': ParagraphStyle('bullet',fontName='Helvetica',fontSize=9.3,leading=13,textColor=INK,leftIndent=11,firstLineIndent=-9,spaceAfter=5),
}

def text(value):
    # Standard PDF fonts and simple punctuation keep extraction portable.
    for old,new in [('’',"'"),('‘',"'"),('“','"'),('”','"'),('—',' - '),('–','-'),('×','x'),('\u00a0',' ')]: value=value.replace(old,new)
    return escape(value,quote=True)

def paragraph(value,style='body'): return Paragraph(value,STYLES[style])
def link(url,label): return f'<link href="{escape(url,quote=True)}" color="#254fa8">{text(label)}</link>'

def build_resume(data,destination):
    destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
    story=[]
    def section(title): story.append(paragraph(text(title),'section'))
    def bullet(value): story.append(paragraph('&#8226; '+text(value),'bullet'))
    def footer(canvas,doc):
        canvas.saveState();w,h=A4
        canvas.setStrokeColor(colors.HexColor('#d7dce5'));canvas.line(42,35,w-42,35)
        canvas.setFillColor(MUTED);canvas.setFont('Helvetica',8)
        canvas.drawString(42,22,'Raghav Awasthi | Portfolio resume')
        canvas.drawRightString(w-42,22,f'{doc.page}')
        canvas.restoreState()
    story.append(paragraph(text(data['name']),'name'))
    contact=data['contact']
    story.append(paragraph(link('mailto:'+contact['emailTarget'],contact['emailDisplay'])+'  |  '+link('https://raghav2005.github.io/','raghav2005.github.io'),'contact'))
    story.append(paragraph(link('https://github.com/raghav2005','github.com/raghav2005')+'  |  '+link('https://www.linkedin.com/in/raghavawasthi2005','linkedin.com/in/raghavawasthi2005'),'contact'))
    section('Education')
    for school in data['education']:
        story.append(paragraph('<b>'+text(school['name'])+'</b> | '+text(school['dates'])))
        story.append(paragraph(text(school['qualification'])))
    section('Experience')
    for role in data['experiences']:
        title=text(role['role'])+' | '+text(role['company'])
        meta=text(role['dates'])+(' | '+text(role['location']) if role['location'] else '')
        story.append(paragraph(title,'heading'));story.append(paragraph(meta,'meta'))
        for value in role['bullets']: bullet(value)
    story.append(PageBreak());section('Projects')
    for project in data['projects']:
        title=link(project['url'],project['name']) if project.get('url') else text(project['name'])
        story.append(paragraph(title,'heading'))
        meta=text(project['technology'])+(' | '+text(project['dates']) if project['dates'] else '')
        story.append(paragraph(meta,'meta'))
        for value in project['bullets']: bullet(value)
    story.append(PageBreak());section('Technical Skills')
    for skill in data['skills']: story.append(paragraph('<b>'+text(skill['category'])+':</b> '+text(skill['items'])))
    section('Awards and Distinctions')
    for award in data['awards']:
        bullet(f'{award["title"]}: {award["result"]} ({award["year"]}). {award["description"]}')
    section('Open Source, Teaching, and Leadership')
    for value in data['leadership']: bullet(value)
    section('Writing and Press')
    story.append(paragraph(link('https://qpg.hashnode.dev/','Quantum Proximity Gateway project journal')+' | '+link('https://ucldevs.hashnode.dev/vscode-to-emacs-the-beginning-why','VSCode to Emacs - UCL Devs')))
    story.append(paragraph(link('https://gulfnews.com/friday/art-people/ai-and-ethics-go-together-1.2315026',"'AI and ethics go together' - Gulf News, 2022")))
    section('Interests')
    for hobby in data['hobbies']: story.append(paragraph('<b>'+text(hobby['category'])+':</b> '+text(hobby['description'])))
    document=SimpleDocTemplate(str(destination),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=38,bottomMargin=48,title='Raghav Awasthi - Portfolio Resume',author='Raghav Awasthi',subject='Experience, projects, awards, and interests',pageCompression=1)
    document.build(story,onFirstPage=footer,onLaterPages=footer)
