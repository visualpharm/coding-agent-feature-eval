import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.text import Text
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'charts';OUT.mkdir(exist_ok=True)
d=json.loads((ROOT/'data/experiment-data.json').read_text());runs=d['runs']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':15,'text.color':'#252525','axes.labelcolor':'#252525','xtick.color':'#252525','ytick.color':'#252525','svg.fonttype':'none'})
fig,ax=plt.subplots(figsize=(16,9),facecolor='white');fig.subplots_adjust(left=.07,right=.97,top=.79,bottom=.14)
fig.text(.07,.935,'Which agent is the best subagent?',fontsize=29,weight='bold',va='center')
colors={'Anthropic':'#db7549','Z.ai':'#2563eb','OpenAI':'#171717'}
handles=[Line2D([],[],marker='o',linestyle='',color=c,markersize=8,label=n) for n,c in colors.items()]
fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(.062,.9),frameon=False,ncol=3,handletextpad=.4,columnspacing=1.8)
ax.set_xlim(0,1.5);ax.set_ylim(6,10)
ax.set_xticks([0,.25,.5,.75,1,1.25,1.5],['$0','$0.25','$0.50','$0.75','$1.00','$1.25','$1.50'])
ax.set_yticks([6,7,8,9,10]);ax.tick_params(length=0,pad=12)
for s in ['top','left','right']:ax.spines[s].set_visible(False)
ax.spines['bottom'].set_color('#aaa');ax.grid(axis='y',color='#e5e5e5',lw=.8);ax.set_axisbelow(True)
ax.text(0,1.035,'Score out of 10 ↑',transform=ax.transAxes,fontsize=16)
ax.set_xlabel('Estimated subscription dollars per task',labelpad=22,fontsize=17)
frontier=[r for r in runs if not any(o['sub_usd']<=r['sub_usd'] and o['score']>=r['score'] and (o['sub_usd']<r['sub_usd'] or o['score']>r['score']) for o in runs)]
frontier.sort(key=lambda r:r['sub_usd'])
assert [r['id'] for r in frontier]==['codex-astra-low','glm-zcode','glm-claude-code','fable-low']
# Shape-preserving cubic Hermite guide through observed nondominated points.
xp=np.array([r['sub_usd'] for r in frontier]);yp=np.array([r['score']/2 for r in frontier])
h=np.diff(xp);delta=np.diff(yp)/h
m=np.zeros(len(xp));m[0]=delta[0];m[-1]=delta[-1]
for i in range(1,len(xp)-1):
 w1=2*h[i]+h[i-1];w2=h[i]+2*h[i-1]
 m[i]=0 if delta[i-1]*delta[i]<=0 else (w1+w2)/(w1/delta[i-1]+w2/delta[i])
for i,dv in enumerate(delta):
 if dv==0:m[i]=m[i+1]=0;continue
 norm=np.hypot(m[i]/dv,m[i+1]/dv)
 if norm>3:m[i]=3*m[i]/norm;m[i+1]=3*m[i+1]/norm
xx=[];yy=[]
for i in range(len(h)):
 t=np.linspace(0,1,120)
 y=(2*t**3-3*t**2+1)*yp[i]+(t**3-2*t**2+t)*h[i]*m[i]+(-2*t**3+3*t**2)*yp[i+1]+(t**3-t**2)*h[i]*m[i+1]
 assert np.all(np.diff(y)>=-1e-10)
 assert abs(y[0]-yp[i])<1e-10 and abs(y[-1]-yp[i+1])<1e-10
 xx.extend(xp[i]+t*h[i]);yy.extend(y)
ax.plot(xx,yy,color='#a8a8a8',lw=1.4,zorder=2)
ax.text(.61,9.38,'Pareto frontier',color='#555',fontsize=14,va='bottom')
labels={
'fable-low':('Fable 5.1 low · Claude Code',(-13,5),'right','bottom'),
'opus-low':('Opus 5 low · Claude Code',(13,0),'left','center'),
'glm-claude-code':('GLM 5.3 · Claude Code',(12,32),'left','bottom'),
'glm-zcode':('GLM 5.3 · ZCode',(12,-12),'left','top'),
'sonnet-medium':('Sonnet 5 medium · Claude Code',(12,0),'left','center'),
'codex-astra-low':('GPT-6 Astra low · Codex',(12,-12),'left','top')}
anns=[]
for r in runs:
 family='Anthropic' if r['model'].startswith('claude') else 'Z.ai' if r['model'].startswith('glm') else 'OpenAI'
 x,y=r['sub_usd'],r['score']/2
 ax.scatter([x],[y],s=105,color=colors[family],edgecolors='none',zorder=5)
 name,offset,ha,va=labels[r['id']]
 anns.append(ax.annotate(f'{name}\n${x:.2f} · {y:g}/10',(x,y),xytext=offset,textcoords='offset points',ha=ha,va=va,fontsize=14,linespacing=1.45,zorder=6))
fig.canvas.draw();renderer=fig.canvas.get_renderer();boxes=[Text.get_window_extent(a,renderer) for a in anns]
assert not [(i,j) for i,a in enumerate(boxes) for j,b in enumerate(boxes) if i<j and a.overlaps(b)]
assert all(fig.bbox.contains(b.x0,b.y0) and fig.bbox.contains(b.x1,b.y1) for b in boxes)
for ext in ['png','svg','pdf']:fig.savefig(OUT/f'best-subagent.{ext}',dpi=200,facecolor='white',metadata={'Title':'Which agent is the best subagent?'})
(OUT/'verification.json').write_text(json.dumps({'points':6,'score_domain':[6,10],'cost_scale':'linear','label_overlaps':0,'label_connectors':0,'point_outlines':0,'pareto_curve':'Monotone visual guide through observed frontier points, not measured intermediate results','pareto_ids':[r['id'] for r in frontier]},indent=2))
print('PNG, SVG, PDF exported; six labels and Pareto frontier verified.')
