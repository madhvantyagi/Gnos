#!/usr/bin/env python3
"""Recreate GNOS's original quadratic-step figure for the Markdown PDF example."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main():
    root=Path(__file__).resolve().parents[3]
    path=root/'examples/lessons/gradient/steps.png'
    path.parent.mkdir(parents=True,exist_ok=True)
    x=np.linspace(-3.2,3.2,400)
    fig,axes=plt.subplots(1,2,figsize=(9.4,3.8),sharex=True,sharey=True)
    for ax,eta,color in zip(axes,[.2,1.2],['#157d83','#b44832']):
        start=2;end=start-eta*2*start
        ax.plot(x,x*x,color='#73838d',lw=1.7)
        ax.scatter([start],[start*start],color='#172c35',s=40,zorder=4)
        ax.scatter([end],[end*end],color=color,s=48,zorder=4)
        ax.annotate('',xy=(end,end*end),xytext=(start,start*start),
                    arrowprops=dict(arrowstyle='->',color=color,lw=2,connectionstyle='arc3,rad=-.2'))
        ax.annotate('start (2, 4)',(2,4),xytext=(8,10),textcoords='offset points',fontsize=9)
        ax.annotate(f'next ({end:.1f}, {end*end:.2f})',(end,end*end),xytext=(5,-20),textcoords='offset points',fontsize=9,color=color)
        ax.set_title(f'Learning rate {eta}',loc='left',fontsize=13,color='#172c35',pad=12)
        ax.set_xlabel('x');ax.set_xlim(-3.3,3.5);ax.set_ylim(-.5,11)
        ax.spines[['top','right']].set_visible(False);ax.grid(alpha=.12)
    axes[0].set_ylabel('f(x) = x²')
    fig.tight_layout(pad=2)
    fig.savefig(path,dpi=190,facecolor='white')
    plt.close(fig)
    print(path)


if __name__=='__main__':main()
