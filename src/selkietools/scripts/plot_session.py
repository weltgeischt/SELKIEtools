"""Plot session data.

Genarates plot that compare conditions, blocks, and splits.

Input: edited splits table (__processed.xlsx)
Output: figures in folder named according to session id.

"""

import pandas as pd
import yaml
import os
import numpy as np
import matplotlib.ticker as ticker
import openpyxl as oxl
from matplotlib import pyplot as plt
import matplotlib as mpl
from argparse import ArgumentParser, RawDescriptionHelpFormatter,ArgumentDefaultsHelpFormatter

from selkietools.utils import helpers as hf
from selkietools.utils import loading_tools as ltools
import selkietools.paths as pathfns

class RawDefaultsFormatter(ArgumentDefaultsHelpFormatter, RawDescriptionHelpFormatter):
    pass


parser = ArgumentParser(description=__doc__, formatter_class=RawDefaultsFormatter)
parser.add_argument('src',help='path to session file or just session id, if the session file is saved in outdir as specified by general_paths.yml')
parser.add_argument('-figdir',default='default',help='directory where to save the figures')
parser.add_argument('-fformat',default='default',help='figure format for example chunk psds')
parser.add_argument('-pathpath',default='default',help='file with the general path settings, default: SETTINGS/PATHS/general_paths.yml')
parser.add_argument('-outdir',default='default',help='where to write the toolbox-generated files to')
parser.add_argument('-outfile',default='processed',help='file to write preprocessed table to, \
                                                      if default it will write to outdir folder')
parser.add_argument('-plot_splits',default=1,type=int,\
                    help='also create plots for individual splits')

parser.add_argument('-debug', action='store_true',
                     help='drop into ipython right after parsing args, for interactive debugging')

args = parser.parse_args()


hf.maybe_embed(args)#drop to ipython if debug



pdict = pathfns.load_settings(args.pathpath if args.pathpath != 'default' else None)

logger = hf.Logger('plot_session',log_dir=pdict.get('log_dir'))

fformat, basefigdir,outdir = pathfns.resolve_dict_fallbacks(pdict,args,['fformat','figdir','outdir'])

if os.path.isfile(args.src):
    srcfile = args.src
else:
    srcfile = pathfns.resolve_file('processed', args.src, outdir)
logger.info('Plotting session data for file %s',srcfile)


plt.style.use(pdict['settings']['mplstyle'])


S = ltools.load_session(srcfile)

#prepare plotting and saving
reffn_rel = lambda vals,myrefval: (vals-myrefval)/myrefval*100
reffn_abs = lambda vals,myrefval: vals-myrefval

figdir = os.path.join(basefigdir,'%s_figs'%S.id)
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
              'strokes_per_min': 'N_strokes/min',\
              'stroke_len':'strokelen [m]',\
              'stroke_len_c':'strokelen_c [m]'}

def plot_condlabels(ax,B,y_dist=0.1):
    for cc, C in enumerate(B.conditions):
        showstr = '%s:ref' % (C.name) if C.is_ref else str(C.name)
        ax.text(1.01, 0.99 - cc * y_dist, showstr, ha='left', va='top', transform=ax.transAxes, color=C.color,
                fontweight='bold')


for I in S.intervals:
    I.get_pace_from_splits()#this avoids Garmins strange rounding


yattrs = ['pace','centerpace','strokes_per_min']#[,'pace'],'dur',
attrx = 'pos_in_block'
for B in S.namedBlocks:
    TGs = [G for G in S.testgroups if G.block==B]
    if len(TGs) == 1: continue
    refTG = [G for G in TGs if G.condition.is_ref][0]#todo allow for several testgroups then loop

    xvals =  [[getattr(I,attrx) for I in G.intervals if I.is_usable] for G in TGs]

    clist = [G.condition.color for G in TGs]
    #print(clist)
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
        figsaver(f,os.path.join('blk%s','Block%s_%s')%(B.id,B.id,attry))

        #same referenced to ref
        refval = np.mean([getattr(I,attry) for I in refTG.intervals if I.is_usable])#todo make also form splits to get rid of first/last line artifacts
        #relative diff
        yvals_reffed = reffn_rel(yvals,refval)
        f,ax = label_make_plot(xvals,yvals_reffed)
        ax.set_ylabel('%s %%diff to ref' % attry)
        f.tight_layout()
        figsaver(f,os.path.join('blk%s','Block%s_%s_percdiff')%(B.id,B.id,attry))


############################################
#summary per block
attrs = ['pace','centerpace','strokes_per_min','stroke_len_c']
yvec = np.arange(len(attrs))
jit_amp = 0.2
figdict = {}
for B in S.namedBlocks:
    TGs = [G for G in S.testgroups if G.block==B]
    ref_pos = [gg for gg,G in enumerate(TGs) if G.condition.is_ref][0]
    avg_mat =  np.vstack([[np.mean([getattr(I,myattr) for I in G.intervals if I.is_usable]) for G in TGs] for myattr in attrs])
    diff_mat = (avg_mat-avg_mat[:,ref_pos][:,None])/avg_mat[:,ref_pos][:,None]*100
    jit_step = jit_amp*2/len(TGs)
    f,ax = plt.subplots(figsize=(4,2))
    ax.set_title('%s block %s dist: %im' % (B.session.id, B.id, B.dist), fontsize=10)
    for cc,TG in enumerate(TGs):
        ax.plot(diff_mat[:,cc],yvec-jit_amp+jit_step*(cc+0.5),'o', mec=TG.condition.color, mfc='none', mew=2, ms=6)
        #np.random.uniform(-jit_amp,jit_amp,len(attrs))
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
    plot_condlabels(ax,B,y_dist=0.2)
    f.tight_layout()
    figdict[os.path.join('blk%s','Block%s_percdiff_summary')%(B.id,B.id)] = f


#ensure equal xlim
xlims = np.stack([f.axes[0].get_xlim() for f in figdict.values()]).T
lowx,highx = np.array([xlims.min(),xlims.max()])
#extent x to have at least one 2 in it.
if lowx > -2 and highx < 2:
    if abs(lowx) >= abs(highx):lowx = -2
    else: highx = 2
myxlim = np.array([lowx, highx])
for savestr,myfig in figdict.items():
    myfig.axes[0].set_xlim(myxlim)
    figsaver(myfig,savestr)

############################################
#summary - compare all blocks
unique_conds = list(dict.fromkeys(G.condition for G in S.testgroups if not G.condition.id=='na'))
comp_blocks = [B for B in S.namedBlocks if len(B.conditions)>1]

attrs = ['pace','centerpace','strokes_per_min','stroke_len_c']
yvec = np.arange(len(attrs))
jit_amp = 0.2
f, ax = plt.subplots(figsize=(6, 3.5))
ax.set_title('%s block %s dist: %im' % (B.session.id, B.id, B.dist), fontsize=10)

for bb,B in enumerate(comp_blocks):
    TGs = [G for G in S.testgroups if G.block==B]
    ref_pos = [gg for gg,G in enumerate(TGs) if G.condition.is_ref][0]
    avg_mat =  np.vstack([[np.mean([getattr(I,myattr) for I in G.intervals if I.is_usable]) for G in TGs] for myattr in attrs])
    diff_mat = (avg_mat-avg_mat[:,ref_pos][:,None])/avg_mat[:,ref_pos][:,None]*100
    jit_step = jit_amp*2/len(TGs)
    for cc,TG in enumerate(TGs):
        xvals = diff_mat[:,cc]
        yvals = yvec-jit_amp+jit_step*(bb+0.5)
        #np.random.uniform(-jit_amp,jit_amp,len(attrs))
        for xx, yy in zip(xvals, yvals):
            if not cc==ref_pos:
                ax.plot(xx, yy, 'o', mec='none', mfc='none', mew=0, ms=10, alpha=0)  # lazy way of getting a suitable xylim
                ax.text(xx, yy, B.id, color=TG.condition.color, ha='center', va='center', transform=ax.transData, \
                        fontsize=12, fontweight='bold')
for cc, C in enumerate(unique_conds):
    showstr = '%s:ref' % (C.name) if C.is_ref else str(C.name)
    ax.text(1.01, 0.99 - cc * 0.1, showstr, ha='left', va='top', transform=ax.transAxes, color=C.color,
            fontweight='bold')
for bb,B in enumerate(comp_blocks):
    ax.text(1.01, 0.99 - cc*0.1-bb * 0.1-0.1, '%s:%im' % (B.id, B.dist), ha='left', va='top', \
            transform=ax.transAxes, color='k',
            fontweight='bold')
Cref = [cond for cond in S.conditions if cond.is_ref][0]
for aa,attr in enumerate(attrs):
    #ax.axhline(aa, color='silver', zorder=-10,alpha=0.5)
    ax.axhspan(aa-jit_amp-0.1,aa+jit_amp+0.1,color='silver',zorder=-12,alpha=0.5,linewidth=0)
    ax.plot(0, aa, 'o', mec='none',mfc=Cref.color,mew=0,ms=10,zorder=-10)
ax.set_yticks(yvec)
ax.set_yticklabels([label_dict[attr].replace(' [m:ss]','') for attr in attrs])
ax.xaxis.set_minor_locator(ticker.MultipleLocator(1.0))
ax.xaxis.set_major_locator(ticker.MultipleLocator(2))

ax.grid(True, color='silver', which='both', linestyle=':')
ax.set_xlabel('%diff to ref')
ax.set_ylim([-0.5,len(attrs)-1+0.5])
f.tight_layout()
figsaver(f, os.path.join('blkcompare', 'summary_percdiff'))


##############################
#pair-wise correlations
var_pairs = [('stroke_len','pace'),('stroke_len_c','centerpace'),('strokes_per_min','pace'),('stroke_len','strokes_per_min')]

for B in S.namedBlocks:
    TGs = [G for G in S.testgroups if G.block==B]
    if len(TGs) == 1: continue
    for var_pair in var_pairs:
        xattr,yattr = var_pair
        f, ax = plt.subplots(figsize=(4, 3))
        ax.set_title('%s block %s dist: %im' % (B.session.id, B.id, B.dist), fontsize=10)
        for G in TGs:
            col = G.condition.color
            myintervals = [I for I in G.intervals if I.is_usable]
            xvals,yvals,posvals = np.vstack([[getattr(I,xattr), getattr(I,yattr),I.pos_in_block] \
                                            for I in myintervals]).T
            for posval, xx, yy in zip(posvals, xvals, yvals):
                #ax.plot(xx, yy, color=col, marker='o', mec=col, mfc='none', mew=2, ms=10)
                ax.plot(xx, yy,'o', mec='none', mfc='none', mew=0, ms=10,alpha=0)#lazy way of getting a suitable xylim
                ax.text(xx,yy,int(posval),color=col,ha='center',va='center',transform=ax.transData,\
                        fontsize=12,fontweight='bold')
        plot_condlabels(ax, B)
        ax.set_xlabel(label_dict[xattr])
        ax.set_ylabel(label_dict[yattr])
        ax.grid(True, color='silver', which='both', linestyle=':')
        if yattr.count('pace'):
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(hf.seconds_to_min_sec))
            ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
        if xattr.count('pace'):
            ax.xaxis.set_major_formatter(ticker.FuncFormatter(hf.seconds_to_min_sec))
            ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
        f.tight_layout()
        figsaver(f,os.path.join('blk%s','Block%s_varcorr_%s_vs_%s')%(B.id,B.id,yattr,xattr))

##############################
#block comparisons --> pairwise correlations
var_pairs = [('stroke_len','pace'),('stroke_len_c','centerpace'),('strokes_per_min','pace'),('stroke_len','strokes_per_min')]
for var_pair in var_pairs:
    xattr, yattr = var_pair
    f, ax = plt.subplots(figsize=(4, 3))
    ax.set_title('%s block compare'%S.id)
    for bb,B in enumerate(S.namedBlocks):
        TGs = [G for G in S.testgroups if G.block==B]

        for G in TGs:
            col = G.condition.color
            myintervals = [I for I in G.intervals if I.is_usable]
            xvals,yvals,posvals = np.vstack([[getattr(I,xattr), getattr(I,yattr),I.pos_in_block] \
                                            for I in myintervals]).T
            for posval, xx, yy in zip(posvals, xvals, yvals):
                #ax.plot(xx, yy, color=col, marker='o', mec=col, mfc='none', mew=2, ms=10)
                ax.plot(xx, yy,'o', mec='none', mfc='none', mew=0, ms=10,alpha=0)#lazy way of getting a suitable xylim
                ax.text(xx,yy,B.id,color=col,ha='center',va='center',transform=ax.transData,\
                        fontsize=12,fontweight='bold')
        ax.text(1.01, 0.99 - bb * 0.1, '%s:%im'%(B.id,B.dist), ha='left', va='top', \
                transform=ax.transAxes, color='k',
                fontweight='bold')
    for cc, C in enumerate(unique_conds):
        showstr = '%s:ref' % (C.name) if C.is_ref else str(C.name)
        ax.text(1.01, 0.99 - cc * 0.1-bb*0.1-0.1, showstr, ha='left', va='top', transform=ax.transAxes, color=C.color,
                fontweight='bold')
    ax.set_xlabel(label_dict[xattr])
    ax.set_ylabel(label_dict[yattr])
    ax.grid(True, color='silver', which='both', linestyle=':')
    if yattr.count('pace'):
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(hf.seconds_to_min_sec))
        #ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
    if xattr.count('pace'):
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(hf.seconds_to_min_sec))
        #ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    f.tight_layout()
    figsaver(f,os.path.join('blkcompare','varcorr_%s_vs_%s')%(yattr,xattr))

################################################
#plot splits
if args.plot_splits == 1:
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
                #figsaver(f,'Block%s_%s_splits%s'%(B.id,yattr,mode_tag))
                figsaver(f, os.path.join('blk%s', 'Block%s_%s_splits%s') % (B.id, B.id, yattr,mode_tag))
