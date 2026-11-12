"""Draw a physical map and slice, then distinguish them from a fitness projection."""
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Arc, Polygon
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.backends.backend_pdf import PdfPages
from geometry import (ROOT, GRADIENT_NORM, PEAK_DISTANCE, PRINCIPAL_VARIANCES, rotation, datasets)
from pathlib import Path
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.labelsize':8.2,'axes.linewidth':.6,
                     'xtick.labelsize':7.4,'ytick.labelsize':7.4,'pdf.fonttype':42,'svg.fonttype':'none'})
ink='#19343c'; teal='#006a72'; pale='#c9dddd'; slate='#576e74'; amber='#b14f28'; rule='#cbd6d8'; violet='#70508c'
cmap=LinearSegmentedColormap.from_list('surface',['#fcfaf3','#e7ede0','#b4d2bb'])
data=datasets(); W,HFIG=9.,7.25
def ftxt(fig,x,y,txt,size=9,col=ink,bold=False,**kw):
    artist=fig.text(x,y,txt,fontsize=size,color=col,fontweight='bold' if bold else 'normal',va='center',**kw)
    # Outline mathematics so PowerPoint does not need the STIX private-use glyphs.
    if '$' in txt:
        from matplotlib.patheffects import Normal
        artist.set_path_effects([Normal()])
    return artist
def divider(fig,y):
    fig.add_artist(plt.Line2D([.052,.967],[y,y],transform=fig.transFigure,color=rule,lw=.65))
def clean(ax):
    for k in ['top','right']:ax.spines[k].set_visible(False)
    for k in ['left','bottom']:ax.spines[k].set_color('#91a6a7')
    ax.tick_params(colors=slate,length=2.4,pad=3)
def entry(fig,number,title,subtitle):
    ftxt(fig,.052,.956,number,8.3,teal,True)
    ftxt(fig,.052,.905,title,20,ink,True)
    ftxt(fig,.052,.851,subtitle,10,slate)
    divider(fig,.82)
def note(fig,y,t):ftxt(fig,.052,y,t,9.2)
def finish(fig,name,book):
    dest=ROOT/'figures';dest.mkdir(exist_ok=True)
    fig.savefig(dest/(name+'.svg'),facecolor='white')
    fig.savefig(dest/(name+'.png'),dpi=205,facecolor='white')
    book.savefig(fig,facecolor='white');plt.close(fig)
def rotated(book):
    fig=plt.figure(figsize=(W,HFIG));entry(fig,'01   /   GEOMETRY IN TRAIT SPACE','What changes when the breeding-value cloud turns?',
        'The surface, population mean and two principal variances stay fixed. Only the direction of genetic variation changes.')
    xs=[.064,.382,.700]; titles=['Towards the peak','Oblique to the slope','Across the slope']
    angles=[0,45,90]; z=np.random.default_rng(20261111).standard_normal((225,2))*np.sqrt(PRINCIPAL_VARIANCES)
    tt=np.linspace(0,2*np.pi,220); ell=np.column_stack((np.cos(tt),np.sin(tt)))*np.sqrt(PRINCIPAL_VARIANCES)*np.sqrt(-2*np.log(.1))
    x=np.linspace(-1.17,1.24,150);y=np.linspace(-1.15,1.15,150);u,v=np.meshgrid(x,y)
    landscape=-.4*((u-PEAK_DISTANCE)**2+v*v)
    for j,(x0,name,a) in enumerate(zip(xs,titles,angles)):
        d=data['rotations'][str(a)]; r=rotation(a)
        ftxt(fig,x0,.777,f'{a}°   {name}',11.5,ink,True)
        ax=fig.add_axes([x0,.487,.255,.259]);ax.set_aspect('equal')
        ax.contourf(u,v,landscape,levels=np.linspace(-2.65,0,55),cmap=cmap,extend='both')
        ax.contour(u,v,landscape,levels=[-2,-1.6,-1.2,-.85,-.55,-.31,-.14,-.04],colors='#8aa792',linewidths=.58)
        P=z@r.T; e=ell@r.T
        ax.scatter(*P.T,c=ink,s=2.6,alpha=.53,lw=0)
        ax.plot(*e.T,color=teal,lw=1.45)
        ax.plot([-r[0,0]*1.02,r[0,0]*1.02],[-r[1,0]*1.02,r[1,0]*1.02],':',color=teal,lw=1.05)
        ax.plot(0,0,'o',mfc='white',mec=ink,ms=4.2);ax.plot(PEAK_DISTANCE,0,'+',color=ink,mew=1.4,ms=8)
        ax.set(xlim=(x[0],x[-1]),ylim=(y[0],y[-1]),xticks=[-1,0,1],yticks=[-1,0,1])
        ax.set_xlabel('Towards the peak');clean(ax)
        if j==0:ax.set_ylabel('Across the slope')
        # Slice along the long axis. The fitted plane has the gradient at the mean
        # but its population intercept is LOWER than the tangent's intercept.
        sec=fig.add_axes([x0+.013,.211,.243,.155]);t=np.linspace(-1.02,1.02,200)
        f=GRADIENT_NORM*r[0,0]*t-.4*t*t; p=GRADIENT_NORM*r[0,0]*t-.4*PRINCIPAL_VARIANCES.sum()
        sec.axhline(0,color=rule,lw=.6);sec.axvline(0,color=rule,lw=.6)
        sec.fill_between(t,f,p,color='#d9e7e4',alpha=.85)
        sec.plot(t,f,c=teal,lw=2);sec.plot(t,p,c=amber,ls='--',lw=1.6)
        sec.set(xlim=(-1.03,1.03),ylim=(-1.3,.82),xticks=[-1,0,1],yticks=[-1,0,.5]);clean(sec)
        if j==0:sec.set_ylabel('Relative log fitness')
        sec.set_xlabel('Distance along the long axis')
        ftxt(fig,x0+.008,.119,rf'$\mathcal{{A}}_g$ = {d["Ag"]:.3f}',15,teal,True)
    ftxt(fig,.052,.408,'Side view along the long axis',10.5,ink,True)
    ftxt(fig,.443,.408,'Solid: fitness surface    ·    Dashed: fitted plane',8.5,slate)
    divider(fig,.085)
    note(fig,.056,'Dots are equally weighted parents. The ellipse contains 90% of the model population; + marks the fitness peak.')
    ftxt(fig,.052,.023,'The index uses both traits. At 90° the slice is flat to first order, but the cloud still has some width towards the peak.',8.5,slate)
    finish(fig,'rotating_breeding_value_cloud',book)
def projection(book):
    fig=plt.figure(figsize=(W,HFIG))
    entry(fig,'02   /   GEOMETRY OF THE VARIANCE SHARE','What does the angle measure?',
          'Each triangle divides variation in log fitness into the part described by a plane and the part left by curvature.')
    xx=[.064,.300,.536,.772]; names=['Broad, on slope','Narrow, on slope','Narrow, at peak','Broad, farther away']
    for j,(key,name,x0) in enumerate(zip('ABCD',names,xx)):
        d=data['comparison_cases'][key]; ag=d['Ag']; X=np.sqrt(ag); Y=np.sqrt(1-ag)
        ftxt(fig,x0,.77,key+'   '+name,10.1,ink,True)
        ax=fig.add_axes([x0,.49,.183,.231]); ax.set_aspect('equal');ax.axis('off')
        th=np.linspace(0,np.pi/2,150);ax.plot(np.cos(th),np.sin(th),color=rule,lw=1)
        ax.plot([0,1.025],[0,0],color=rule,lw=.8);ax.plot([0,0],[0,1.025],color=rule,lw=.8)
        ax.fill([0,X,X],[0,0,Y],color='#e8f1ee')
        ax.plot([0,X],[0,0],color=teal,lw=3.5,solid_capstyle='butt')
        ax.plot([X,X],[0,Y],color=amber,lw=2,ls='--')
        ax.plot([0,X],[0,Y],color=ink,lw=1.7 if key!='C' else 1.0, ls=':' if key=='C' else '-')
        ax.plot(X,Y,'o',c=ink,ms=3.4);ax.add_patch(Arc((0,0),.39,.39,theta1=0,theta2=d['angle'],color=slate,lw=.9))
        ax.set(xlim=(-.045,1.07),ylim=(-.05,1.07))
        ftxt(fig,x0+.002,.473,f'Angle  {d["angle"]:.1f}°',9,slate)
        ftxt(fig,x0+.002,.428,rf'$\mathcal{{A}}_g$ = {ag:.3f}',14.5,teal,True)
    ftxt(fig,.052,.384,'Base: linear SD     |     Height: curvature SD     |     Diagonal: total SD, scaled to 1 in every panel.',9,slate)
    ftxt(fig,.052,.349,r'The squared base length gives the index: $\mathcal{A}_g=\cos^2(\psi)$. Here $\psi$ is a projection angle, not the tilt of the fitness surface.',8.7,ink)
    divider(fig,.326)
    ftxt(fig,.052,.293,'Now weight the same parents by their expected offspring',12.2,ink,True)
    # Means in case B are near zero on the same scale used for D. Print each length.
    ax=fig.add_axes([.25,.105,.43,.148]); ax.spines[['top','right','left']].set_visible(False)
    for row,key in [(1,'B'),(0,'D')]:
        d=data['comparison_cases'][key]; c,p=[np.linalg.norm(d[k]) for k in ['curved_shift','plane_shift']]
        ax.plot([0,p],[row,row],color=rule,lw=2);ax.plot(c,row,'D',c=teal,ms=6);ax.plot(p,row,'^',c=amber,ms=6)
        ftxt(fig,.052,.105+.148*(row+.5)/2,'B   Narrow cloud' if key=='B' else 'D   Broad cloud',9.3,ink,True)
        ftxt(fig,.707,.105+.148*(row+.5)/2, f'{c:.3f}  /  {p:.3f}    (+{100*(p/c-1):.0f}%)',10.5,ink,True)
    ax.set(xlim=(-.03,3.02),ylim=(-.5,1.5),xticks=[0,1,2,3],yticks=[]);clean(ax);ax.spines['left'].set_visible(False);ax.set_xlabel('Distance moved by the mean parental breeding value')
    ftxt(fig,.707,.255,'Surface  /  plane',8.8,slate)
    ftxt(fig,.052,.024,'B and D have the same triangle. Their offspring-weighted means move different distances, in the same trait units.',8.8,slate)
    finish(fig,'fitness_projection_angles',book)
if __name__=='__main__':
    dest=ROOT/'figures';dest.mkdir(exist_ok=True)
    with PdfPages(dest/'geometry_of_additive_channels.pdf') as book:rotated(book);projection(book)
