"""Produce the two teaching figures. Run calculate.py first, or use the supplied CSV."""
from pathlib import Path
import json,gzip
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap,Normalize
from matplotlib.lines import Line2D
from matplotlib import patheffects as fx
from matplotlib.ticker import FuncFormatter
mpl.rcParams.update({'pdf.fonttype':42,'svg.fonttype':'none','font.family':'DejaVu Sans','font.size':8,'axes.unicode_minus':True,'axes.linewidth':.55,'axes.labelcolor':'#233a40','xtick.color':'#4d6061','ytick.color':'#4d6061','svg.hashsalt':'cloudgenetics2026'})
R=Path(__file__).resolve().parents[1]; D=R/'data'; O=R/'figures';O.mkdir(exist_ok=True)
results=json.loads((D/'results.json').read_text());public=results['cloud'];obs=results['tutorial']
INK='#19363D'; MUT='#4C6265'; TEAL='#006B70'; RUST='#A04329'; GRP='#7A285F'; GRAY='#38494C'; RULE='#BFCDCA'; WHITE='#FFFFFF'
cmap=LinearSegmentedColormap.from_list('landscape',['#F9F7F1','#EFEADC','#DBDFD3','#B5D3C6','#83B7AC'])
def page(w,h):
 f=plt.figure(figsize=(w/72,h/72),facecolor='white')
 def t(x,y,s,size=8,col=INK,weight='normal',ha='left'):
  return f.text(x/w,1-y/h,s,fontsize=size,color=col,weight=weight,va='center',ha=ha)
 def box(x,y,ww,hh):return f.add_axes([x/w,1-(y+hh)/h,ww/w,hh/h])
 def line(x,y,x2,y2,col=RULE,lw=.55):
  f.add_artist(Line2D([x/w,x2/w],[1-y/h,1-y2/h],color=col,lw=lw,transform=f.transFigure))
 return f,t,box,line
def trim(ax):
 for k in ['top','right']:ax.spines[k].set_visible(False)
 for k in ['bottom','left']:ax.spines[k].set_color('#8A9998');ax.spines[k].set_linewidth(.55)
 ax.tick_params(length=2.5,width=.55,pad=2,labelsize=7.7)
def save(f,stem):
 for ext in ['pdf','png','svg']:f.savefig(O/(stem+'.'+ext),dpi=245,facecolor='white')
 plt.close(f)
def signed(v):return f'{v:+.2f}'.replace('-','−')
def cloud():
 p=public
 x=np.genfromtxt(D/'parent_cloud.csv.gz',names=True,delimiter=',')
 zs=np.stack((x['z1'],x['z2']),axis=1)
 mask=x['displayed'].astype(bool);grp=x['group_below_minus_1SD'].astype(bool);X=zs[mask];g=grp[mask]
 M=np.asarray(p['sample_mean']);s=np.asarray(p['sample_sd']);b=np.asarray(p['b']);H=np.asarray(p['H']);beta=np.asarray(p['fitted_plane_coefficients'])
 cen=np.asarray(p['mean_shifts_sd']);means=np.asarray(p['shift_lengths'])
 cols=[GRAY,TEAL,RUST]
 fig,t,axbox,line=page(555,367)
 head=['Count parents','Count expected offspring','Use the linear prediction']
 sub=['Each parent has the same weight.','Area shows relative expected offspring.','Area shows relative predicted offspring.']
 grouptext=['of parents','of expected output','of predicted output']
 ext=[-4.65,3.55,-3.45,3.45];aa,bb=np.meshgrid(np.linspace(ext[0],ext[1],160),np.linspace(ext[2],ext[3],140))
 grid=M+np.stack([aa,bb],axis=-1)*s
 field=(grid-M)@b+.5*(np.einsum('...i,ij,...j->...',grid,H,grid)-M@H@M)
 plane=(grid-M)@beta[1:]
 norm=Normalize(-3,2,clip=True);levels=np.arange(-3,2.01,.5)
 for j,px in enumerate([38,215,392]):
  t(px-11,12,'ABC'[j],11,cols[j],'bold');t(px+2,12,head[j],10.5,INK,'bold')
  t(px-11,27,sub[j],7.7,MUT)
  ax=axbox(px,41,154,135);ax.set_xlim(ext[:2]);ax.set_ylim(ext[2:]);ax.set_aspect('equal',adjustable='box')
  F=field if j<2 else plane
  ax.contourf(aa,bb,F,levels=levels,cmap=cmap,norm=norm,extend='both',antialiased=False,zorder=0)
  ax.contour(aa,bb,F,levels=levels,colors='#829C8F',linewidths=.46,linestyles='solid',zorder=1)
  ax.axvline(-1,ls=(0,(2,2)),lw=.85,color=GRP,zorder=2)
  wr=[x['equal_weight'],x['curved_weight'],x['plane_weight']][j][mask]*len(x)
  for group,col in [(False,GRAY),(True,GRP)]:
   wh=(g==group);ax.scatter(X[wh,0],X[wh,1],s=3.0*wr[wh],c=col,alpha=.75 if group else .56,edgecolors='none',zorder=3)
  # The two first maps share the true fitness surface; markers are means over ALL 20,000 parents.
  ax.scatter([0],[0],s=39,marker='o',facecolor='white',edgecolor=INK,linewidths=1.25,zorder=7)
  if j:
   ax.plot([0,cen[j,0]],[0,cen[j,1]],lw=1.9,color='white',zorder=6)
   ax.scatter([cen[j,0]],[cen[j,1]],marker='D' if j==1 else '^',s=43,facecolor=cols[j],edgecolor='white',linewidths=1,zorder=8)
  if j==0:
   ax.annotate('Below −1 SD',xy=(-2.3,-2.35),ha='center',fontsize=6.8,color=GRP,
               path_effects=[fx.withStroke(linewidth=2,foreground='#F2F2E8')])
  ax.set_xticks([-4,-2,0,2]);ax.set_yticks([-2,0,2]);trim(ax)
  if j:ax.set_yticklabels([])
  else:ax.set_ylabel('Trait 2 breeding value (SD)',fontsize=8,labelpad=4)
  # The small row underneath preserves the denominator of each percentage.
  t(px+74,212,f"{p['group_shares'][j]:.1%} {grouptext[j]}",9,GRP,'bold',ha='center')
 t(290,197,'Trait 1 breeding value (SD from the starting mean)',8.5,ha='center')
 t(285,227,'Purple: trait 1 below −1 SD. The same 600 parents are shown; all 20,000 determine the percentages and means.',7.6,MUT,ha='center')
 line(15,237,541,237)
 # Magnification allows readers to see the selected means without confusing movement of a mean with movement of individual parents.
 t(16,249,'D',10,TEAL,'bold');t(30,249,'Where does the parental mean end up?',10,INK,'bold')
 zoom=axbox(19,260,100,68);zoom.set_xlim(-.72,.1);zoom.set_ylim(-.095,.70);zoom.set_aspect('equal');zoom.axis('off')
 for j in [2,1]:
  zoom.plot([0,cen[j,0]],[0,cen[j,1]],color=cols[j],lw=1.4,ls='--' if j==2 else '-',zorder=3 if j==1 else 2)
 for j,mark in [(0,'o'),(1,'D'),(2,'^')]:
  zoom.scatter(*cen[j],s=34,marker=mark,facecolor='white' if j==0 else cols[j],edgecolor=INK if j==0 else 'white',lw=.75,zorder=8)
 zoom.text(-.065,-.064,'Start',ha='right',va='center',color=MUT,fontsize=7)
 t(117,269,'Distance from starting mean',7.6,MUT)
 for j,yy,lab in [(1,286,'Curved surface'),(2,303,'Linear plane')]:
  t(117,yy,lab,8.4,cols[j]);t(211,yy,f'{means[j]:.2f}',10,cols[j],'bold',ha='right')
 t(117,320,'Distance uses both traits in SD units.',7.1,MUT)
 line(262,246,262,322)
 t(276,253,'What the plane gets wrong',9.6,INK,'bold')
 t(276,272,f"The plane explains {p['r2_sample_plane']:.1%} of variation in log expected output.",8)
 t(276,287,'It gives too much weight to parents with low trait 1 values.',8)
 t(276,305,f"It overestimates the distance the mean shifts by {p['relative_overestimate']:.0%}.",8.3,RUST,'bold')
 line(15,332,541,332)
 t(16,347,'Map colour: log expected output relative to the starting mean',7.3,MUT)
 cb=axbox(279,341,115,7)
 from matplotlib.colorbar import ColorbarBase
 cs=ColorbarBase(cb,cmap=cmap,norm=norm,orientation='horizontal',boundaries=levels,ticks=[-3,-2,-1,0,1,2],spacing='proportional')
 cs.outline.set_visible(False);cs.ax.tick_params(labelsize=6.4,pad=1,length=2,width=.4)
 t(407,347,'Darker = more expected offspring.',7.1,MUT)
 save(fig,'parental_weighting')
def counts():
 p=obs; tab=np.genfromtxt(D/'observed_data.csv',names=True,delimiter=','); truth=np.genfromtxt(D/'simulation_truth.csv',names=True,delimiter=',')
 a=truth['true_breeding_value'];k=tab['offspring'];z=(a-p['initial_mean'])/p['initial_sd'];g=z>1
 fig,t,box,line=page(526,253)
 t(13,15,'A   Count offspring for each parent',11,INK,'bold');t(13,32,'Saved observations from the one-trait teaching example.',8,MUT)
 t(281,15,'B   Weight the same parents',10.5,INK,'bold')
 t(281,32,'High group: breeding value above +1 SD.',8,MUT)
 ax=box(42,55,202,137);ox=np.linspace(-3.3,3.3,200);xx=ox*p['initial_sd']+p['initial_mean'];bet=p['fitted_line']
 ax.axvline(1,ls=(0,(3,2)),color=GRP,lw=.7)
 for group,col in [(False,GRAY),(True,GRP)]:
  wh=(g==group);ax.scatter(z[wh],k[wh],s=4.3,c=col,edgecolor='none',alpha=.35 if not group else .60,zorder=3)
 ax.plot(ox,np.exp(np.log(4)+.7*xx-.35*xx**2),color=TEAL,lw=1.7,label='Curved model',zorder=4)
 ax.plot(ox,np.exp(bet[0]+bet[1]*xx),color=RUST,lw=1.4,ls='--',label='Line on log scale',zorder=4)
 ax.set(xlim=(min(-3.4,z.min()-.1),max(3.4,z.max()+.1)),ylim=(-.45,max(k)+1),xticks=[-3,-2,-1,0,1,2,3],xlabel='Breeding value for height (SD)',ylabel='Surviving offspring (number)')
 trim(ax);ax.legend(frameon=False,fontsize=7,loc='upper left',handlelength=1.5);ax.xaxis.label.set_size(8);ax.yaxis.label.set_size(8)
 t(281,55,'Weight',7.6,MUT,'bold');t(438,55,'Group share',7.6,MUT,'bold',ha='right');t(515,55,'Mean (SD)',7.6,MUT,'bold',ha='right');line(281,64,515,64)
 for idx,yy,name,col in [(0,82,'One per parent',GRAY),(3,105,'Counted offspring',INK),(1,128,'Curved model',TEAL),(2,151,'Line on log scale',RUST)]:
  t(281,yy,name,8.6,col);t(438,yy,f"{p['group_shares'][idx]:.1%}",9,col,'bold',ha='right');t(515,yy,'0.00' if not idx else signed(p['means_sd'][idx]),9,col,'bold',ha='right')
 t(281,178,f"{p['group_n']} of {p['n']} parents belong to the high group.",8.7,GRP,'bold');t(281,194,f"They produced {p['offspring_from_group']} of {p['total_offspring']:,} recorded offspring.",8.7,GRP,'bold')
 line(13,221,514,221);t(13,236,'Each dot is a parent. All 88 parents with zero offspring remain in the population and contribute zero to the count-weighted mean.',7.3,MUT)
 save(fig,'tutorial_cloud_recorded_offspring')
if __name__=='__main__':cloud();counts()
