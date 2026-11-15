"""Assemble one offline HTML document from checked prose, models and records.

This is additional repository study material, separate from the journal submission.
The HTML contains its styles, SVG drawing code and reference data checked against saved source hashes.
"""
from pathlib import Path
import json
import sys
from lxml import html

MODULE=Path(__file__).resolve().parent
ROOT=MODULE/'src'
DEST=MODULE/'Additive_channels_interactive_guide.html'
sys.path.insert(0, str(ROOT))
from reference_integrity import SOURCE_BASE, validate_reference

BASE=SOURCE_BASE
CURRENT=BASE
LESSONS=[('counts','Expected reproduction','From counts to a conditional mean'),
 ('share','The linear share','Slope, curvature and variance'),
 ('population','Population variation','Narrowing, location and orientation'),
 ('selection','Selection','Frequency and reproductive weights'),
 ('estimation','Estimation','Measurements, fitting and uncertainty'),
 ('inheritance','Inheritance','Covariance across generations')]

home='''<article class="lesson active" id="home">
<div class="home-hero"><div><p class="eyebrow">Additional study material</p><h1>Additive channels</h1><p class="lead">How can a curved fitness relationship have a close linear description, and when can that description predict selection?</p><p>Start with the parents and their offspring counts. Follow the calculation through the population's genetic variation, reproductive contributions and inheritance.</p><p>This guide is additional repository material, separate from the paper and its numbered supplementary files. Six connected lessons use the examples and saved results from the additive-channels repository. Change a quantity to see its effect, then open the derivation when you want to follow the algebra.</p><div class="button-row"><a href="#counts" class="btn btn-primary">Begin with offspring counts →</a><a href="#selection" class="btn">Go to selection</a></div></div>
<figure class="home-figure"><div id="home-curve" class="chart"></div><div id="home-populations" class="chart"></div><div class="home-values"><span style="color:#216f96">Broad, on slope: 66.7%</span><span style="color:#237f75">Narrow, on slope: 95.2%</span><span style="color:#ae6029">Narrow, at peak: 0%</span></div><figcaption>One fixed quadratic log-fitness curve. The three normal populations differ in variance or mean. The percentages describe the variance explained by their population-fitted lines.</figcaption></figure></div>
<section class="home-claim"><h2>Fitness variation and reproductive contribution</h2><p>To describe variation in log expected fitness, we weight breeding values by how common they are. To calculate the mean among contributing parents, we also weight them by expected reproductive output. Predicting offspring requires an inheritance model.</p></section>
<div class="course-list">'''
entries=[
 ('counts','Expected reproduction and offspring counts','Keep zero counts, calculate a conditional mean and then take its logarithm.'),
 ('share','The linear share','Calculate the two variance components and distinguish a fitted line from a tangent.'),
 ('population','Changes in population variation','Use the same curve to compare narrowing the population, moving its mean and rotating covariance.'),
 ('selection','Reproductive weighting and selection','Work through the 97% fit and 50% overestimate, then change the parameters.'),
 ('estimation','Estimating the share from measurements','Inspect the simulated observations, fitted relationship and all 500 saved bootstrap refits.'),
 ('inheritance','Inheritance and changing genetic variation','Follow the covariance recursion and identify the assumptions needed for predictions across generations.')]
for i,(key,title,description) in enumerate(entries,1):
 home+=f'<a class="course-entry" href="#{key}"><span class="entry-top">LESSON {i:02d}</span><h2>{title}</h2><p>{description}</p></a>'
home+='''</div><details class="derivation"><summary>Notation used throughout the guide</summary><div><p>G is breeding-value variance in one trait and a covariance matrix in several traits. The local gradient is b and the Hessian is H. Stabilising curvature is written Γ = −H, or γ = −H for one trait. The linear share A<sub>g</sub> concerns a quadratic description of log expected output.</p><p>Use the Symbols button at any point for the remaining definitions. Matrix expressions preserve multiplication order; scalar expressions are labelled as one-trait calculations.</p></div></details>
<details><summary>Paper results and additional explanations</summary><div><p>The numerical records are stored in this file. A source manifest gives the file paths and SHA-256 hashes used to extract them. The controls calculate the stated mathematical examples; the estimation records are saved simulated results.</p><ul>
<li><a href="https://doi.org/10.64898/2026.03.21.713332">Ortiz-Barrientos and Cooper (2026), <em>Additive Channels in Curved Fitness Landscapes</em></a>: cite the paper for the scientific ideas and results. Record the repository version when reusing code or data.</li>
<li><a href="CURRENTtutorials/companion/companion.pdf">Short companion</a>: an additional account of the main argument and its assumptions.</li>
<li><a href="CURRENTtutorials/interactive/src/reference_sources.json">Source manifest</a>: file hashes identifying the exact numerical sources used here. Links beside each lesson open their current public paths.</li>
<li><a href="CURRENTdocs/VERSION_GUIDE.md">Reading versions 2 and 3</a>: changes between the preprint versions and the role of earlier material.</li>
<li><a href="CURRENTRESULTS.md">Paper reproduction and additional exposition</a>: the role and source of each calculation.</li>
<li><a href="CURRENTREPRODUCING.md">Reproduction instructions</a>: figures, simulations, estimation and document builds.</li>
</ul><p>The underlying methods also draw on these primary sources:</p><ul>
<li><a href="https://doi.org/10.1093/biomet/12.1-2.134">Isserlis (1918), Biometrika 12:134–139</a>: Gaussian product moments used in the variance decomposition.</li>
<li><a href="https://doi.org/10.1038/227520a0">Price (1970), Nature 227:520–521</a>: the covariance expression for the selection component of change.</li>
<li><a href="https://doi.org/10.1086/282718">Bulmer (1971), The American Naturalist 105:201–211</a>: selection-induced associations and changes in genetic variance. The specific covariance closure used here is stated separately in Lesson 6.</li>
</ul></div></details><p class="source-status">All observations displayed here are constructed or simulated. The final lesson separates mathematical results, numerical checks and questions for empirical work. The document works offline; external source links require an internet connection.</p><p class="print-note">The printed document contains all six lessons. Expanded derivations and code are included; open them before printing if you want the detailed version.</p></article>'''.replace('BASE',BASE).replace('CURRENT',CURRENT)

parts={}
for filename in ['lessons_1_3.html','lesson_5.html','lessons_4_6.html']:
 for article in html.fragments_fromstring((ROOT/filename).read_text()):
  if isinstance(article,str):continue
  parts[article.get('id')]=article
for article in parts.values():
 for table in article.xpath('.//table'):
  parent=table.getparent()
  if 'table-wrap' not in parent.get('class','').split():
   wrapper=html.Element('div',{'class':'table-wrap'})
   parent.replace(table,wrapper);wrapper.append(table)
 for link in article.xpath('.//a[starts-with(@href,"https://")]'):
  link.set('target','_blank');link.set('rel','noopener noreferrer')
content=home+'\n'.join(html.tostring(parts[k],encoding='unicode',method='html') for k,_,_ in LESSONS)

nav='<a href="#home" aria-current="page"><span class="nav-number">00</span><span>Overview<span class="nav-desc">The question and the reading order</span></span></a>'
for i,(key,label,desc) in enumerate(LESSONS,1):
 nav+=f'<a href="#{key}"><span class="nav-number">{i:02d}</span><span>{label}<span class="nav-desc">{desc}</span></span></a>'

symbols=[('Z or A','Breeding value in the original trait coordinates.'),('μ','Mean breeding value in the population.'),('X','Breeding value minus its population mean.'),('W','Recorded reproductive output, such as surviving offspring count.'),('W<sub>A</sub>','Expected reproductive output conditional on breeding value.'),('ℓ','Natural logarithm of W<sub>A</sub>.'),('b','Slope in one trait; gradient vector in several traits.'),('H','Curvature in one trait; Hessian matrix in several traits.'),('G','Breeding-value variance, or covariance matrix.'),('A<sub>g</sub>','Linear share of variance in the quadratic log-mean description.'),('Γ or γ','Stabilising curvature, equal to −H.'),('B','Fixed genic covariance baseline in the inheritance model.'),('ρ','Fraction of the selected departure from B retained after reproduction.'),('E','Environmental variance of the simulated height measurements.'),('κ','Strength of the fourth-order term in the separate curve comparison.')]
symbol_html=''.join(f'<dt>{key}</dt><dd>{text}</dd>' for key,text in symbols)
style=(ROOT/'base.css').read_text()+'\n'+(ROOT/'guide.css').read_text()
data=json.loads((ROOT/'scientific_reference.json').read_text())
validate_reference(data)
data_json=json.dumps(data,separators=(',',':'),ensure_ascii=False).replace('</','<\\/')
script='\n'.join((ROOT/file).read_text() for file in ['models.js','labs.js','navigation.js'])
document=f'''<!doctype html>
<html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Six offline lessons on additive channels: expected reproduction, Gaussian variance, population geometry, selection, estimation and inheritance."><meta name="theme-color" content="#eaf2f5"><title>Additive channels — interactive study guide</title><style>{style}</style></head>
<body><a class="skip-link" href="#main-content">Skip to lesson</a><div class="mobile-bar"><a href="#home">Additive channels</a><button class="btn btn-small" id="menu-button" type="button" aria-expanded="false" aria-controls="sidebar">Lessons</button></div>
<aside class="sidebar" id="sidebar"><a href="#home" class="brand"><span class="brand-mark">A</span><span>Additive channels<small>Fitness variation and selection</small></span></a><nav class="course-nav" id="course-nav" aria-label="Lessons">{nav}</nav><div class="sidebar-note"><p>Read the explanation first. Use a control to test a prediction. Open the derivation when you need the intermediate steps.</p><p id="course-progress-text">0 of 6 marked as read</p><div class="progress-track" aria-hidden="true"><div id="course-progress" class="progress-fill" style="width:0%"></div></div><p>Marking a lesson is optional and saved only in this browser.</p></div><div class="sidebar-note">Repository study guide<br>15 November 2026<br><a href="{BASE}README.md" target="_blank" rel="noopener noreferrer">Repository source</a></div></aside>
<main class="main" id="main-content" tabindex="-1"><div class="main-inner"><div class="page-tools"><span class="status-label">Six linked lessons · works offline</span><button class="btn" id="symbols-button" type="button">Symbols</button><button class="btn" id="math-toggle" type="button" aria-pressed="false">Show derivations</button><button class="btn" id="print-button" type="button">Print / save PDF</button><button class="btn" id="download-html" type="button">Download HTML</button></div><p class="no-js note">Enable JavaScript for the live controls. All lesson text and derivations remain readable below.</p><div id="app">{content}</div><footer class="site-footer">Additional repository guide prepared by Daniel Ortiz-Barrientos, based on the work with Mark Cooper. The <a href="{CURRENT}tutorials/interactive/src/reference_sources.json">source manifest</a> identifies the code and data by file hash. Calculations, saved simulated results and proposed empirical work are identified in the text.</footer></div></main>
<dialog id="symbols-dialog" aria-labelledby="symbols-title"><div class="dialog-head"><h2 id="symbols-title">Symbols</h2><button id="symbols-close" class="btn close-dialog" type="button" aria-label="Close symbols">×</button></div><dl class="symbol-list">{symbol_html}</dl></dialog>
<script id="scientific-reference" type="application/json">{data_json}</script><script>const SCIENTIFIC_REFERENCE=JSON.parse(document.getElementById('scientific-reference').textContent);\n{script}</script>
</body></html>'''
DEST.parent.mkdir(parents=True,exist_ok=True)
DEST.write_text(document)
print(f'Built {DEST} ({DEST.stat().st_size:,} bytes)')
