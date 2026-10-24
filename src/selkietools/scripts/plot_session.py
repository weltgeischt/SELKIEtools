import pandas as pd
import yaml
import re
import os
import sys
import numpy as np
import matplotlib.ticker as ticker
import openpyxl as oxl
from matplotlib import pyplot as plt
import matplotlib as mpl


#srcfile = '/home/weltgeischt/Dropbox/dc_paddles/dc_paddles_data/edited/KH_260928__edited.xlsx'
srcfile = '/home/weltgeischt/Dropbox/dc_paddles/dc_paddles_data/edited/KH_261002__edited.xlsx'
#srcfile = '/home/weltgeischt/Dropbox/dc_paddles/dc_paddles_data/edited/KH_260930__edited.xlsx'
srcfile = '/home/weltgeischt/Dropbox/dc_paddles/dc_paddles_data/edited/KH_261005__edited.xlsx'
srcfile = '/home/weltgeischt/Dropbox/dc_paddles/dc_paddles_data/edited/KH_261008__edited.xlsx'

codepath = '/home/weltgeischt/workspace/splitlab'

stylepath = os.path.join(pdict['settings']['mplstyle'])
plt.style.use(stylepath)

sys.path.append(codepath)
from splitlab.utils import dataclasses as dc
from splitlab.utils import helpers as hf
from splitlab.utils import loading_tools as ltools
from importlib import reload
reload(dc)

S = ltools.load_session(srcfile)

#prepare plotting and saving
reffn_rel = lambda vals,myrefval: (vals-myrefval)/myrefval*100
reffn_abs = lambda vals,myrefval: vals-myrefval

fformat = 'png'
basefigdir = '/home/weltgeischt/Dropbox/dc_paddles/dc_paddles_data/figures/per_session'
figdir = os.path.join(basefigdir,'%s_figs'%S.id,'attr_vs_blockrank')
def figsaver(fig, nametag, closeit=True):
    figname = os.path.join(figdir,'%s__%s.%s'%(S.id,nametag,fformat))
    fdir = os.path.dirname(figname)
    if not os.path.isdir(fdir): os.makedirs(fdir)
    fig.savefig(figname,bbox_inches='tight')
    if closeit: plt.close(fig)

label_dict = {'dur':'dur [s]',\
              'pos_in_block':'pos. in block',\
              'pace': 'pace [m:ss]',\
              'centerpace': 'center pace [m:ss]',\
              'strokes':'n strokes',
             'strokes_per_25':'N_strokes/25m',\
              'strokes_per_min': 'N_strokes/min'}

def plot_condlabels(ax,B):
    for cc, C in enumerate(B.conditions):
        showstr = '%s:ref' % (C.name) if C.is_ref else str(C.name)
        ax.text(1.01, 0.99 - cc * 0.1, showstr, ha='left', va='top', transform=ax.transAxes, color=C.color,
                fontweight='bold')


for I in S.intervals:
    I.get_pace_from_splits()#this avoids their rounding


yattrs = ['pace','centerpace','strokes_per_min','strokes_per_25']#[,'pace'],'dur',
for B in S.namedBlocks:
    TGs = [G for G in S.testgroups if G.block==B]
    refTG = [G for G in TGs if G.condition.is_ref][0]#todo allow for several testgroups then loop



    attrx = 'pos_in_block'#todo also check time etc
    xvals =  [[getattr(I,attrx) for I in G.intervals if I.is_usable] for G in TGs]

    clist = [G.condition.color for G in TGs]


    def label_make_plot(myxvals,myyvals,y_hint=None):
        f,ax = plt.subplots(figsize=(4,3))

        ax.set_title('%s block %s dist: %im' % (B.session.id, B.id, B.dist), fontsize=10)
        for col, xx, yy in zip(clist, myxvals,myyvals):
            ax.plot(xx, yy, color=col, marker='o', mec=col, mfc='none', mew=2, ms=10)

        plot_condlabels(ax, B)

        ax.xaxis.set_minor_locator(ticker.MultipleLocator(1.0))
        ax.grid(True,color='silver',which='both',linestyle=':')
        ax.set_xlabel(label_dict[attrx])
        if str(y_hint).count('pace'):
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(hf.seconds_to_min_sec))
            ax.yaxis.set_major_locator(ticker.MultipleLocator(1))

        return f,ax


    for attry in yattrs:
        yvals = [[getattr(I,attry) for I in G.intervals if I.is_usable] for G in TGs]
        f,ax = label_make_plot(xvals,yvals,y_hint=attry)
        ax.set_ylabel(label_dict[attry])
        if attry == 'strokes': ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        f.tight_layout()
        figsaver(f,'Block%s_%s'%(B.id,attry))

        #same referenced to ref
        refval = np.mean([getattr(I,attry) for I in refTG.intervals if I.is_usable])#todo make also form splits to get rid of first/last line artifacts
        #relative diff
        yvals_reffed = reffn_rel(yvals,refval)
        f,ax = label_make_plot(xvals,yvals_reffed)
        ax.set_ylabel('%s %%diff to ref' % attry)
        f.tight_layout()
        figsaver(f,'Block%s_%s_percdiff'%(B.id,attry))

        '''#abs-diff
        yvals_reffed = reffn_abs(yvals,refval)
        f,ax = label_make_plot(xvals,yvals_reffed)
        ax.set_ylabel('%s-%s_ref' %(attry,attry))
        f.tight_layout()
        figsaver(f,'Block%s_%s_absdiff'%(B.id,attry))'''

#summary
attrs = ['pace','centerpace','strokes_per_min','strokes_per_25']
jit_amp = 0.2
figdict = {}
for B in S.namedBlocks:
    TGs = [G for G in S.testgroups if G.block==B]
    ref_pos = [gg for gg,G in enumerate(TGs) if G.condition.is_ref][0]
    avg_mat =  np.vstack([[np.mean([getattr(I,myattr) for I in G.intervals if I.is_usable]) for G in TGs] for myattr in attrs])
    diff_mat = (avg_mat-avg_mat[:,ref_pos][:,None])/avg_mat[:,ref_pos][:,None]*100

    yvec = np.arange(len(attrs))
    f,ax = plt.subplots(figsize=(4,2))
    ax.set_title('%s block %s dist: %im' % (B.session.id, B.id, B.dist), fontsize=10)
    for cc,TG in enumerate(TGs):
        ax.plot(diff_mat[:,cc],yvec+np.random.uniform(-jit_amp,jit_amp,len(attrs)),'o', mec=TG.condition.color, mfc='none', mew=2, ms=6)

    for aa,attr in enumerate(attrs):
        #ax.axhline(aa, color='silver', zorder=-10,alpha=0.5)
        ax.axhspan(aa-jit_amp-0.1,aa+jit_amp+0.1,color='silver',zorder=-10,alpha=0.5,linewidth=0)
    ax.set_yticks(yvec)
    ax.set_yticklabels([label_dict[attr].replace(' [m:ss]','') for attr in attrs])
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1.0))
    ax.xaxis.set_major_locator(ticker.MultipleLocator(2))

    ax.grid(True, color='silver', which='both', linestyle=':')
    ax.set_xlabel('%diff to ref')
    ax.set_ylim([-0.5,len(attrs)-1+0.5])
    plot_condlabels(ax,B)
    f.tight_layout()
    figdict['Block%s_percdiff_summary'%(B.id)] = f
    #figsaver(f,'Block%s_percdiff_summary'%(B.id))

#ensure equal ylim
ylims = np.stack([f.axes[0].get_ylim() for f in figdict.values()]).T
for savestr,myfig in figdict.items():
    myfig.axes[0].set_ylim([ylims.min(),ylims.max()])
    figsaver(myfig,savestr)



#plot splits
mode_dict = {'': lambda x: x[:], '_skipBorders': lambda x: x[1:-1]}

for yattr in ['dur','strokes_per_min']:
    for B in S.namedBlocks:
        TGs = [G for G in S.testgroups if G.block==B]
        split_dict = {TG.id:[] for TG in TGs}
        for TG in TGs:
            for I in TG.intervals:
                #my_rest = I.rest_before
                if I.is_usable: split_dict[TG.id] += [[getattr(spl,yattr) for spl in I.splits]]
        max_n = np.max([len(vals) for vals in split_dict.values()])
        for mode_tag,modefn in mode_dict.items():
            f,axarr = plt.subplots(2,1,figsize=(3+1*max_n,2+1.5*max_n),sharey=True,sharex=True)
            f.suptitle('%s block %s dist: %im' % (B.session.id, B.id, B.dist), fontsize=10)
            for TG in TGs:
                splitlists = split_dict[TG.id]
                for ii,splitlist in enumerate(splitlists):
                    ax = axarr[ii]
                    ax.plot(modefn(np.arange(len(splitlist))),modefn(np.array(splitlist)),'o-',mfc='none',color=TG.condition.color)#[3:-1]
                    ax.text(0.01, 0.01, 'Interval%i'%(ii+1), ha='left', va='bottom', transform=ax.transAxes, color='k',
                            fontweight='normal')
                    ax.set_ylabel(label_dict[yattr])
                    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1.0))
                    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
                    ax.grid(True,color='silver',which='both',linestyle=':')

            axarr[-1].set_xlabel('split #')
            plot_condlabels(axarr[0],B)
            f.tight_layout()
            figsaver(f,'Block%s_%s_splits%s'%(B.id,yattr,mode_tag))