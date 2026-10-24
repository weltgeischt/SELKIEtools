import pandas as pd
import openpyxl as oxl
import numpy as np
import re
import yaml
from . import dataclasses as dc


def load_session(srcfile):
    dflist = [pd.read_excel(srcfile, sheet_name=key) for key in ['summary', 'splits', 'cond_spec', 'metadata', 'info']]
    [df_main, df_split, df_cond, df_meta, df_info] = dflist

    for colname in ['block', 'cond']:
        df_main[colname] = df_main[colname].fillna('na')

    dictlist = df_main.to_dict(orient='records')
    for mydict in dictlist:
        mydict['block_id'] = str(mydict['block'])
        mydict['cond_id'] = str(mydict['cond'])
        mydict['dur'] = float(mydict['time'])
        for key in ['block', 'cond', 'time']:
            mydict.pop(key)

    allIntervals = [dc.Interval(**mydict) for mydict in dictlist]
    idx_row = df_info.index[df_info['property'] == 'session_id'][0]
    sessionid = df_info['value'][idx_row]
    S = dc.Session(sessionid)
    S.set_intervals(allIntervals)
    for I in allIntervals: I.set_session(S)

    #making subintervals
    dictlist_splits = df_split.to_dict(orient='records')
    for mydict in dictlist_splits:
        mydict['dur'] = float(mydict['time'])
        for key in ['time']:
            mydict.pop(key)

    allSplits = [dc.Split(**mydict) for mydict in dictlist_splits]

    #setting splits to intervals and intervals to splits
    for I in allIntervals:
        my_splits = [spl for spl in allSplits if spl.intnum == I.run_id]
        I.set_splits(my_splits)
        for spl in my_splits:
            spl.set_parent_interval(I)

    #
    Blocks = [dc.Block(bid) for bid in df_main['block'].unique()]
    for B in Blocks: B.set_session(S)
    S.set_blocks(Blocks)

    #make condition objects, with colors!!!
    Conds = [dc.Condition(cid) for cid in df_main['cond'].unique()]
    for C in Conds: C.set_session(S)
    S.set_conditions(Conds)
    df_cond['notes'] = df_cond['notes'].fillna('na')
    conddict0 = df_cond.to_dict(orient='index')
    conddict = {vals['cond']: {subkey: subvals for subkey, subvals in vals.items() if not subkey == 'cond'} for vals in
                conddict0.values()}  #a dict of dicts
    for mydict in conddict.values():
        mydict['name'] = str(mydict['disp_cond'])
        mydict.pop('disp_cond')

    #read color
    color_idx = np.where(df_cond.columns == 'disp_color')[0][0]
    wb = oxl.load_workbook(srcfile)
    try:
        sheet = wb['cond_spec']
        hex_cols = ['#' + sheet.cell(ii, color_idx + 1).fill.start_color.rgb[2:] for ii in np.arange(len(conddict)) + 2]
    finally:
        wb.close()

    #set colors
    for hexcol, mydict in zip(hex_cols, conddict.values()):
        if mydict['disp_color'] == 'default':
            mydict['color'] = hexcol
        else:
            mydict['color'] = mydict['disp_color']

    #fill conditions #todo put this in a settings
    na_color = 'grey'
    na_dict = {'is_ref': 0, 'pref_rank': np.nan, 'disp_color': 'default', 'name': 'na', 'color': na_color,
               'isnamed': False}

    for C in Conds:
        if C.id in conddict:
            mydict = conddict[C.id]
            mydict['isnamed'] = True
            C.set_features_fromdict(mydict)
        elif C.id not in conddict:
            C.set_features_fromdict(na_dict)

    S.get_set_testgroups(attr1='block', attr2='condition')

    for B in S.namedBlocks: B.get_dist()

    return S