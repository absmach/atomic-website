"""Adapt the approved offline press index for the existing Atomic website."""
from pathlib import Path
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
from PIL import Image
import shutil,json,hashlib,os,re,subprocess,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent.parent
KIT=Path(os.environ['PRESS_KIT_DIR']).resolve()
SITE=ROOT
PUBLIC='/assets/press/'+KIT.name.removeprefix('atomic-press-kit-')+'/'
ASSETS=SITE/'dist'/PUBLIC.lstrip('/')
RELEASE='https://github.com/absmach/atomic-website/releases/download/press-kit-2026-11-03/'
STAGE=Path(os.environ['PRESS_RELEASE_STAGE']).resolve()
ASSETS.mkdir(parents=True,exist_ok=True);STAGE.mkdir(parents=True,exist_ok=True)

def copy_local(relative):
 target=ASSETS/relative;target.parent.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(KIT/relative,target)
 return PUBLIC+relative

def release_asset(relative):
 name=('raw-' if relative.startswith('03-screenshots/raw/') else '')+Path(relative).name
 if relative.startswith(('04-portraits/','03-screenshots/')):
  source=Path(relative);name=source.stem+'-'+KIT.name.removeprefix('atomic-press-kit-')+source.suffix
  if relative.startswith('03-screenshots/raw/'):name='raw-'+name
 target=STAGE/name
 shutil.copyfile(KIT/relative,target)
 return RELEASE+name

def preview(relative):
 source=KIT/relative
 name=source.stem+'.webp';target=ASSETS/'previews'/name;target.parent.mkdir(exist_ok=True)
 im=Image.open(source);im.thumbnail((1920,1920));im.convert('RGB').save(target,'WEBP',quality=92,method=6)
 return PUBLIC+'previews/'+name,im.size

archive=KIT.with_suffix('.zip');shutil.copyfile(archive,STAGE/archive.name)
(STAGE/(archive.name+'.sha256')).write_text(hashlib.sha256(archive.read_bytes()).hexdigest()+'  '+archive.name+'\n')
soup=BeautifulSoup((KIT/'index.html').read_text(),'html.parser')
main=soup.main;main.name='div';main['class']=['press-catalog']
intro=main.find('header');intro.name='section';intro['class']=['press-intro'];intro['aria-labelledby']='press-title';intro.h1['id']='press-title'
contact=main.find('footer');contact.name='section';contact['class']=['press-contact'];contact['id']='press-contact'
for a in main.find_all('a',href=True):
 href=a['href']
 if urlsplit(href).scheme or href.startswith('#'):continue
 if href.startswith(('03-screenshots/','04-portraits/')):a['href']=release_asset(href)
 else:a['href']=copy_local(href)
 if 'button' in a.get('class',[]):a['class'].append('button-secondary')
 if href.endswith('START-HERE.txt'):a.string='ZIP contents'

for img in main.find_all('img'):
 src=img['src']
 if src.startswith(('03-screenshots/','04-portraits/')):
  img['src'],size=preview(src);img['loading']='lazy';img['decoding']='async'
 else:
  img['src']=copy_local(src)
  if src.endswith('.svg'):
   svg=ET.parse(KIT/src).getroot();box=list(map(float,svg.attrib['viewBox'].split()));size=(round(box[2]),round(box[3]))
  else:size=Image.open(KIT/src).size
 img['width'],img['height']=map(str,size)

for video in main.find_all('video'):
 video['src']=copy_local(video['src']);video['preload']='none';video['playsinline']=''
 if video.get('poster'):video['poster'],_=preview(video['poster'])
 else:raise ValueError('Video needs an explicit matching poster: '+video['src'])
 for track in video.find_all('track'):track['src']=copy_local(track['src'])

download=soup.new_tag('a',href=RELEASE+archive.name,attrs={'class':'button button-primary press-download'})
download.string=f'Download complete kit · ZIP, {round(archive.stat().st_size/1e6)} MB'
intro.find('a',class_='button').insert_before(download)
def page_count(relative):
 info=subprocess.check_output(['pdfinfo',str(KIT/relative)],text=True)
 return int(re.search(r'Pages:\s+(\d+)',info)[1])
book_pages=page_count('01-documents/00-complete-press-book.pdf')
book_link=intro.find('a',class_='button-secondary')
book_link.string=f'Read the press book · PDF, {(KIT/"01-documents/00-complete-press-book.pdf").stat().st_size/1e6:.1f} MB'
book_link['class']=['button','button-primary']
download['class']=['button','button-secondary','press-download']
download.insert_before(book_link.extract())
contact_link=intro.find('a',href='mailto:drasko@absmach.eu')
contact_link['class']=['press-contact-link']
intro.find_all('p')[-1].string=os.getenv('PRESS_UPDATED_LABEL','Updated 2 November 2026 · Paris, France')
nav=soup.new_tag('nav',attrs={'class':'press-sections','aria-label':'Press kit sections'})
sections=[('documents','Documents'),('logos','Logos'),('screenshots','Screenshots'),('video','Video'),('people','People'),('social','Social artwork')]
for h2,(slug,label) in zip(main.find_all('h2'),sections):
 h2['id']=slug;a=soup.new_tag('a',href='#'+slug);a.string=label;nav.append(a)
intro.insert_after(nav)
for el in main.find_all(class_=True):
 el['class']=['press-'+c if c in ['grid','gallery','links','logo-show'] else c for c in el['class']]

# Provide accurate, explicit context for the downloadable images.
gallery=main.find('div',class_='press-gallery')
gallery.find_previous_sibling('p').string='Browse the product views below. Download a presentation PNG or its clean capture for editorial use. All screens show local sample apps and data; the builder conversation is staged and comments are drafts.'
for p in gallery.find_all('p'):
 if p.find('a'):
  for a in p.find_all('a'):a['class']=['press-file-link']

# Match the editorial story while retaining every downloadable product view.
figures={Path(f.find('a')['href']).stem.removesuffix('-'+KIT.name.removeprefix('atomic-press-kit-')):f for f in gallery.find_all('figure',recursive=False)}
story=[
 ('start','Start with your idea.','Describe an idea or explore a working template.', ['01-home','02-templates','03-template-preview']),
 ('build','Build in conversation.','Keep the brief, the conversation and the working preview together.', ['04-builder']),
 ('shape','Shape it together.','Explore screens, refine the appearance and give feedback in context.', ['05-canvas','06-theme','07-element','08-collaboration','15-responsive']),
 ('publish','Review. Publish. Manage.','Review versions, publish the app and manage projects and access.', ['12-versions','13-dashboard','09-applications','14-salon-app']),
 ('monitor','See what is happening.','Inspect preview requests, building-session usage and account billing.', ['16-monitoring','17-usage','10-billing']),
 ('source','Your code, in view.','Browse app files on every plan. Download source code on Builder or Pro.', ['11-source'])]
assert set(figures)=={name for _,_,_,names in story for name in names}
gallery_intro=gallery.find_previous_sibling('p')
gallery_intro.string='View the screenshots and download each image directly. All screens show local sample apps and data; the builder conversation is staged and comments are drafts.'
for _,_,_,names in story:
 for name in names:gallery.append(figures[name].extract())
doc_grid=main.find(id='documents').find_next_sibling('div')
for article in doc_grid.find_all('article',recursive=False):
 href=article.find('a')['href']
 if '/01-product-overview.' in href:article.p.string='Six illustrated chapters, from your first idea to source access.'
document_intro=soup.new_tag('p');document_intro.string='Download individual documents as PDF, editable Word or plain text.'
main.find(id='documents').insert_after(document_intro)

shutil.copytree(KIT/'02-logos',ASSETS/'02-logos',dirs_exist_ok=True)
(SITE/'content/press.html').write_text(str(main)+'\n')
(ASSETS/'ASSET-CREDITS.txt').write_text((KIT/'ASSET-CREDITS.txt').read_text())
manifest={'release_tag':'press-kit-2026-11-03','archive':archive.name,'archive_bytes':archive.stat().st_size,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'release_files':[{'name':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(STAGE.iterdir()) if p.is_file()]}
(STAGE.parent/'website-release-manifest.json').write_text(json.dumps(manifest,indent=2))
print(f'Prepared the approved visual index; {len(manifest["release_files"])} release attachments; {sum(p.stat().st_size for p in ASSETS.rglob("*") if p.is_file())/1e6:.1f} MB of website assets.')
