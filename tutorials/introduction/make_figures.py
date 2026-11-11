"""Draw the teaching examples from their stated parameters. Run from any directory."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
out=Path(__file__).resolve().parent/'figures'
out.mkdir(exist_ok=True)
blue,orange,green,ink='#265a76','#b45528','#247368','#21383e'
plt.rcParams.update({'font.size':11,'axes.spines.right':False,'axes.spines.top':False,'pdf.fonttype':42,'axes.labelcolor':ink,'text.color':ink,'axes.edgecolor':'#708388'})
def save(f,name):
    f.savefig(out/(name+'.png'),dpi=180,bbox_inches='tight',facecolor='white')
    f.savefig(out/(name+'.pdf'),bbox_inches='tight',facecolor='white')
    plt.close(f)
def linefig():
    return plt.subplots(figsize=(7.4,3.3),layout='constrained')
# Two normals on the same exactly quadratic conditional log mean; densities are in their own panel.
fig,axs=plt.subplots(2,2,figsize=(8.6,4.4),sharex=True,sharey='row',height_ratios=[2.1,1],layout='constrained')
x=np.linspace(-2.7,2.7,321)
for j,G in enumerate([1,.25]):
    a,d=axs[:,j]
    a.plot(x,x-.5*x*x,color=blue,label='Quadratic log mean')
    a.plot(x,x-G/2,color=orange,ls='--',label='Fitted line')
    a.scatter([0],[-G/2],s=17,color=orange,zorder=3)
    a.set_title(f'Variance = {G:g}     Linear share = {1/(1+G/2):.3f}',fontsize=12)
    d.fill_between(x,np.exp(-x*x/(2*G))/np.sqrt(2*np.pi*G),color=green,alpha=.45)
    d.set_xlabel('Breeding value (centred)')
axs[0,0].set_ylabel('Log expected output');axs[1,0].set_ylabel('Density')
axs[0,0].legend(loc='lower right',fontsize=8,frameon=False)
save(fig,'fig02_two_populations')
# What is measured and what is fitted? Exact synthetic group means; no logs of counts.
fig,a=linefig()
groups=[[0,1,2,1],[0,2,2,4],[2,3,5,6]]
for j,counts in enumerate(groups):
    a.scatter(j+np.array([-.11,-.04,.04,.11]),counts,s=44,color=blue,label='Observed offspring counts' if j==0 else None)
a.plot(range(3),np.mean(groups,axis=1),'o--',mfc='white',mec=orange,color=orange,label='Mean within group')
a.set(xticks=[0,1,2],xlabel='Breeding-value group',ylabel='Offspring per plant',ylim=(-.25,6.6))
a.legend(frameon=False,loc='upper left')
save(fig,'fig01_offspring_counts')
# Exact selected-parent comparison, not a simulation.
fig,a=linefig()
a.barh([1,0],[4/3,2],height=.42,color=[green,orange]);a.set(yticks=[1,0],yticklabels=['With curvature','Ignoring curvature'],xlabel='Shift in mean breeding value among selected parents',xlim=(0,2.4))
for y,v,lab in [(1,4/3,'4/3'),(0,2,'2')]:a.text(v+.05,y,lab,va='center')
save(fig,'fig03_parental_shift')
