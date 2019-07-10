import os
import sys
from os.path import join
import json
import pandas as pd
import re
import copy

DATA_COLS=['Datetime', 'beaconid', 'edgenodeid', 'rssi',
               'realx', 'realy']
POS_COLS=['Datetime', 'realx', 'realy']
EDGE_COLS=['beaconid', 'edgenodeid', 'gamma', 'bias', 'edge_x', 'edge_y', 'edge_z']
# Datetime is always include in wide
WIDE_COLS=['beaconid', 'realx', 'realy']

def package_datasets(ds_all, dirname=''):
    """
    Use to package datasets from dataobject objects
    This is not a dictionary of train, valid, test...
    """
    ds_all = copy.deepcopy(ds_all)
    assert dirname != '', "dirname required"
    package_dataset(ds_all['ds_train_um'], dirname=join('.', dirname, 'train'))
    package_dataset(ds_all['ds_valid_um'], dirname=join('.', dirname, 'valid'))
    package_dataset(ds_all['ds_test_um'], dirname=join('.', dirname, 'test'))

def package_dataset(ds, dirname=''):
    """
    This packages one of train, valid and test
    """
    assert dirname != '', "dirname required"
    import pyrfc3339 as rfc3339

    os.makedirs(dirname)
    ds.edges[EDGE_COLS].to_csv(join(dirname, 'edges.csv'), index=False)
# unused
#    ds.beacons.to_csv(join(dirname, 'beacons.csv'), **shared_cfg)

    for c in ds.chunks:
        fr_data = c.data.iloc[0]
        date = fr_data['Datetime']
        bid = fr_data['beaconid']
        fname = '{date}_{bid}'.format(
                date=date.strftime('%Y-%m-%dT%H-%M-%S-%f'), bid=bid)

        def _to_csv(data, suffix):
            data = data.copy()
            data['Datetime'] = data['Datetime'].apply(lambda dt: rfc3339.generate(dt, microseconds=True))
            data.to_csv(join(dirname, fname + suffix), index=False)

        _to_csv(c.data[DATA_COLS], "_data.csv")
        _to_csv(c.pos[POS_COLS], "_pos.csv")
        c.com = c.com.drop('magneticField', axis=1)
        _to_csv(c.com, "_com.csv")
        c.acc = c.acc.rename({'realx': 'accx', 'realy': 'accy', 'realz': 'accz'}, axis=1)
        _to_csv(c.acc, "_acc.csv")
        
        # Wide format
        d = c.data[DATA_COLS]
        d.pivot('Datetime', 'edgenodeid', 'rssi')
        dt = d.set_index('Datetime')
        dt = dt[WIDE_COLS]
        p = d.pivot('Datetime', 'edgenodeid', 'rssi')
        dt[['edge_' + str(n) for n in p.columns]] = p
        wide = dt.groupby(level=0).first().reset_index()
        _to_csv(wide, "_data_wide.csv")

        with open(join(dirname, fname + ".cfg"), 'w') as f:
            cfg = {k: v for k, v in c.cfg.items() if k not in ['SubmissionDatetime', 'ReceiveDatetime', 
                'Experiment Name', 'Configuration File']}
            json.dump(cfg, f, indent=4, sort_keys=True)

match_prefix = re.compile(r'.*/(?P<prefix>\S+_\d+)_data.csv')

def unpackage_datasets(dirname, dataobject_format=False):
    """
    This function unpackages all sub packages, (i.e. train, valid, test)
    You should use this function if you want everything
    args:
        dirname: directory path that has the train, valid, test folders in it
        dataobject_format: used for dataobject format
    """
    with open(join(dirname, 'room-data.json')) as f:
        lm = json.load(f)['Landmarks']
    res = {s: unpackage_dataset(join(dirname, s), dataobject_format) for s in ['train', 'valid', 'test']}
    res['landmarks'] = lm
    return res

def unpackage_dataset(dirname, dataobject_format=False):
    """
    unpackage_dataset loads data that has been packaged by
    package_dataset
    args:
        dirname: folder which contains all .csv files
        dataobject_format: flag to put data in a more useful format
    """
    if dataobject_format:
        import dataobject
    dof = dataobject_format
    datasetname = os.path.split(dirname)[-1]
    res = []

    # Edges and beacons file
    edges = pd.read_csv(join(dirname, 'edges.csv'))
#    beacons = pd.read_csv(join(dirname, 'beacons.csv'))
    
    def _read_csv(prefix, extension):
        return pd.read_csv(join(dirname, prefix + extension), parse_dates=True, infer_datetime_format=True)

    files = os.listdir(dirname)
    files = map(lambda f: join(dirname, f), files)
    files = filter(lambda f: os.path.isfile(f) and f.endswith("_data.csv"), files)

    for cfile in files:
        prefix = match_prefix.search(cfile).group('prefix')
        with open(join(dirname, prefix+'.cfg')) as f:
            cfg = json.load(f)
            pos = _read_csv(prefix, '_pos.csv')
            com = _read_csv(prefix, '_com.csv')
            data = _read_csv(prefix, '_data.csv')
            acc = _read_csv(prefix, '_acc.csv')
            wide = _read_csv(prefix, '_data_wide.csv')
        if dof:
            c = dataobject.Chunk(prefix=prefix,
                    pos=pos,
                    com=com,
                    data=data,
                    acc=acc,
                    cfg=cfg, processed=True)
            c.wide = wide
        else:
            c = {'pos': pos,
                 'com': com,
                 'data': data,
                 'acc': acc,
                 'wide': wide,
                 'cfg': cfg,
                 'prefix': prefix}

        res.append(c)
    if dof:
        ds = dataobject.Dataset(datasetname=datasetname, chunks=res, experimentname=prefix)
        ds.edges = edges
        #ds.beacons = beacons
        ds.chunks = ds._chunks
    else:
        ds = {'chunks': res,
              'edges': edges,
             }
    return ds

