"""Transform Garmin split export csv to editable table

After creation, please annotate __processed.xlsx table with your block and
condition structure.

Input: Garmin csv export file
Output: __processed.xlsx

"""


import warnings
import pandas as pd
import yaml
import os
import numpy as np
import string
import matplotlib as mpl
import git
from pathlib import Path

from argparse import ArgumentParser, RawDescriptionHelpFormatter,ArgumentDefaultsHelpFormatter

from selkietools.utils import helpers as hf
import selkietools.paths as pathfns

pd.options.mode.chained_assignment = None

class RawDefaultsFormatter(ArgumentDefaultsHelpFormatter, RawDescriptionHelpFormatter):
    pass

warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message="This pattern is interpreted as a regular expression"
)

parser = ArgumentParser(description=__doc__, formatter_class=RawDefaultsFormatter)
parser.add_argument('csvfile',help='path to file with Garmin-exported csv splits')
parser.add_argument('-N_cond',type=int,default=4,help='number of conditions to prepare template with')
parser.add_argument('-session_id',default='csvstem',help='if session == csvstem (default), it uses the pattern of csv naming')
parser.add_argument('-pathpath',default='default',help='file with the general path settings, default: SETTINGS/PATHS/general_paths.yml')
parser.add_argument('-outdir',default='default',help='where to write the toolbox-generated files to')
parser.add_argument('-outfile',default='processed',help='file to write preprocessed table to, \
                                                      if default it will write to outdir folder')
parser.add_argument('-debug', action='store_true',
                     help='drop into ipython right after parsing args, for interactive debugging')

args = parser.parse_args()

if args.debug:
    from IPython import embed; embed()

pdict = pathfns.load_settings(args.pathpath if args.pathpath != 'default' else None)

logger = hf.Logger('process_raw',log_dir=pdict.get('log_dir'))

csvfile = args.csvfile

if args.session_id == 'csvstem':
    session_id = Path(csvfile).stem
else:
    session_id = args.session_id

outdir = pathfns.resolve_dict_fallbacks(pdict,args,'outdir')
outfilename = pathfns.resolve_file(args.outfile, session_id, outdir)


logger.info('Reading csv %s',csvfile)

df = pd.read_csv(csvfile, sep=',')

logger.info('Adjusting format.')

if 'Intervals' in df.columns:
    convdict = pathfns.load_config('headENG', pdict)
elif 'Intervaller' in df.columns:
    convdict = pathfns.load_config('headSWE', pdict)
else:
    assert 0, 'unknown language, please adjust and write header conversions to config'



myvars = list(convdict.values())
df.rename(convdict, axis='columns', inplace=True)#rename
df = df.drop(labels=[col for col in df.columns if not col in myvars],axis=1)#remove unnecessary columns
df = df.drop(df[df['run_id'] == convdict['Summary_row']].index)

#adjust format of cells
time_cols = ['time', 'ctime', 'pace', 'pace_max']
int_cols = ['lengths','dist','swolf','hr_avg','hr_max','strokes']
for col in time_cols:
    df[col] = df[col].apply(hf.str_to_sec)
for col in int_cols:
    if type(df[col][0]) == type('teststr'):
        df[col] = df[col].apply(lambda x: x.replace(',',''))
        df[col] = df[col].apply(lambda x: int(x))

#separate overall rep time from lane-split times
myexp_full = '^(\d+)(?!.)'
myexp_split = '^(\d+)(.)(\d+)'
df_main = df[df.run_id.str.contains(myexp_full, regex=True,na=False)]
df_split = df[df.run_id.str.contains(myexp_split, regex=True,na=False)]



newcols = ['block','cond','usable']
df_main = df_main.reindex(columns = newcols+df_main.columns.tolist())
df_main['block'] = ''
df_main['cond'] = ''
df_main['usable'] = '+'

logger.info('Creating from templates.')

# create template xlsx specifying the conditions to append to output
N_cond = args.N_cond
cfg = pathfns.load_config('sheetspec', pdict)
cmap_cond = cfg['colormap_default']
ccdict = {key:['']*N_cond for key in cfg['columns_cond']}
ccdict['cond'] =  list(string.ascii_uppercase)[:N_cond]
ccdict['disp_color'] = ['default']*N_cond
ccdict['is_ref'] = [0]*N_cond
ccdict['pref_rank'] = [0]*N_cond

#coloring cells accordin got default
cdisp_index = list(ccdict.keys()).index('disp_color')

cmap = mpl.colormaps[cmap_cond]
condcolors = cmap(np.linspace(0.1,0.9,N_cond))
hex_colors = [mpl.colors.to_hex(col) for col in condcolors]
df_cond = pd.DataFrame.from_dict(ccdict, orient='columns')

# create template xlsx specifying the metadata to append to output
metafeaturelist = cfg['columns_meta']
metadict = {'feature':metafeaturelist,'value':['']*len(metafeaturelist)}
df_meta = pd.DataFrame.from_dict(metadict, orient='columns')

#setting up info sheet
repo = git.Repo(search_parent_directories=True)

infodict_ = {'srcfile':os.path.basename(csvfile),'session_id':session_id,\
             'githash': repo.head.object.hexsha}
infodict = {'property':list(infodict_.keys()),'value':list(infodict_.values())}
df_info = pd.DataFrame.from_dict(infodict)

writedirname = os.path.dirname(outfilename)
if not os.path.isdir(writedirname):
    logger.info('creating writedirectory %s', writedirname)
    os.makedirs(writedirname)

logger.info('writing preprocessed to %s\n PLEASE ANNOTATE!',outfilename)
with pd.ExcelWriter(outfilename, engine='xlsxwriter') as writer:
    for mydf,sname in zip([df_main, df_split,df_cond,df_meta,df_info],['summary','splits','cond_spec','metadata','info']):
        mydf.to_excel(writer, sheet_name=sname, index=False, na_rep='NaN')
        for col in mydf:
            clength = max(mydf[col].astype(str).map(len).max(), len(col))
            col_idx = mydf.columns.get_loc(col)
            writer.sheets[sname].set_column(col_idx, col_idx, clength)
    wb = writer.book
    sheet = writer.sheets['cond_spec']
    for cc,col in enumerate(hex_colors):
        colfmt = wb.add_format({'bg_color':col})
        sheet.write(cc+1, cdisp_index, df_cond.iat[cc, cdisp_index], colfmt)



