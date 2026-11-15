"""Export the figure pair to PowerPoint. Text is native and plots are editable SVG graphics.
Requires python-pptx, matplotlib, Pillow and Inkscape (for the PNG compatibility preview).
"""
from pathlib import Path
import tempfile,subprocess,re,math,xml.etree.ElementTree as E
from lxml import etree as ET
from pptx import Presentation
from pptx.util import Pt
from pptx.enum.text import MSO_ANCHOR,MSO_AUTO_SIZE,PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn
from pptx.opc.package import Part
from pptx.opc.packuri import PackURI
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from PIL import ImageFont
from matplotlib.font_manager import findfont,FontProperties
root=Path(__file__).resolve().parents[1]; svg_ns='http://www.w3.org/2000/svg'
def export(stem):
    file=root/'figures'/(stem+'.svg');doc=ET.parse(str(file));w,h=map(float,doc.getroot().attrib['viewBox'].split()[-2:]);sc=1.55
    def dim(x):return Pt(x*sc)
    ppt=Presentation();ppt.slide_width=dim(w);ppt.slide_height=dim(h);sl=ppt.slides.add_slide(ppt.slide_layouts[6])
    labels=doc.xpath('//*[local-name()="text"]')
    for t in labels:t.getparent().remove(t)
    with tempfile.TemporaryDirectory() as td:
        tmp=Path(td);svg=tmp/'drawing.svg';svg.write_bytes(ET.tostring(doc,encoding='UTF-8',xml_declaration=True))
        png=tmp/'drawing.png';subprocess.run(['inkscape',str(svg),'--export-dpi=170','--export-filename='+str(png)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        im=sl.shapes.add_picture(str(png),0,0,width=dim(w),height=dim(h));im.name="Vector figure: contours, individuals and means"
        part=Part(PackURI('/ppt/media/plot.svg'),'image/svg+xml',sl.part.package,svg.read_bytes())
        rid=sl.part.relate_to(part,RT.IMAGE)
        blip=im._element.xpath('.//a:blip')[0]
        el=ET.SubElement(blip,qn('a:extLst'));ext=ET.SubElement(el,qn('a:ext'),uri='{96DAC541-7B7A-43D3-8B79-37D633B846F1}')
        v=ET.SubElement(ext,'{http://schemas.microsoft.com/office/drawing/2016/SVG/main}svgBlip');v.set(qn('r:embed'),rid)
    for t in labels:
        st=dict((p.split(':',1)[0].strip(),p.split(':',1)[1].strip()) for p in t.attrib['style'].split(';') if ':' in p)
        fs=float(st['font-size'].replace('px',''));bold=st.get('font-weight')=='700';c=st.get('fill','#000000')
        text=''.join(t.itertext());font=ImageFont.truetype(findfont(FontProperties(family='DejaVu Sans',weight='bold' if bold else 'normal')),round(fs*100))
        tw=font.getlength(text)/100;th=fs*1.34; x,y=float(t.attrib['x']),float(t.attrib['y']);ang=float(re.search(r'rotate\(([-.0-9]+)',t.attrib.get('transform','rotate(0)'))[1])
        dx={'start':tw/2,'end':-tw/2,'middle':0}[st.get('text-anchor','start')];dy=-fs*.35;rad=math.radians(ang)
        cx=x+dx*math.cos(rad)-dy*math.sin(rad);cy=y+dx*math.sin(rad)+dy*math.cos(rad)
        shape=sl.shapes.add_textbox(dim(cx-(tw+fs)/2),dim(cy-th/2),dim(tw+fs),dim(th));shape.name=text[:220];shape.rotation=ang%360
        tf=shape.text_frame;tf.word_wrap=False;tf.auto_size=MSO_AUTO_SIZE.NONE;tf.vertical_anchor=MSO_ANCHOR.MIDDLE
        tf.margin_top=tf.margin_bottom=tf.margin_left=tf.margin_right=0;p=tf.paragraphs[0];p.alignment=PP_ALIGN.CENTER;p.space_before=p.space_after=Pt(0)
        run=p.add_run();run.text=text;run.font.name='DejaVu Sans';run.font.bold=bold;run.font.size=dim(fs);run.font.color.rgb=RGBColor.from_string(c[1:].upper())
    ppt.core_properties.title=stem;ppt.save(root/'figures'/(stem+'.pptx'))
if __name__=='__main__':
 for s in ['parental_weighting','tutorial_cloud_recorded_offspring']:export(s)
