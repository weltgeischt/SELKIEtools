import numpy as np

class FeatureEnabler():

    def set_feature(self,featurename,featureval):
        setattr(self,featurename,featureval)

    def set_features_fromdict(self, featuredict):
        for key, value in featuredict.items():
            setattr(self, key, value)

class Session(FeatureEnabler):
    def __init__(self,id):
        self.id = id

    def set_blocks(self,blocklist):
        self.blocks = blocklist

    def set_conditions(self,condlist):
        self.conditions = condlist

    def set_intervals(self,intervallist):
        self.intervals = intervallist

    def find_unique_pairs(self,attr1='block',attr2='condition'):
        block_cond_pairs = np.vstack([[getattr(I,attr1).id, getattr(I,attr2).id] for I in self.intervals])
        u_pairs = np.unique(block_cond_pairs, axis=0)
        u_pairs_obj = [([B for B in getattr(self,attr1+'s') if B.id == pair[0]][0], [C for C in getattr(self,attr2+'s') if C.id == pair[1]][0])
                       for pair in u_pairs] # 's' a very foolish way of doing plurals ;)
        return u_pairs_obj

    def get_set_testgroups(self,attr1='block',attr2='condition'):

        upairs = self.find_unique_pairs(attr1=attr1,attr2=attr2)

        Testgroups = [TestGroup(pair[0],pair[1]) for pair in upairs]

        self.testgroups = Testgroups

    @property
    def namedBlocks(self):
       return [B for B in self.blocks if not B.id == 'na']


class Block(FeatureEnabler):
    def __init__(self,id):
        self.id = id

    def set_session(self,S):
        self.session = S

    @property
    def intervals(self):
        return [I for I in self.session.intervals if I.block == self]

    @property
    def tstart(self):
        return self.intervals[0].tstart

    @property
    def tstop(self):
        return self.intervals[-1].tstop

    @property
    def rest_before(self):
        return self.intervals[0].rest_before

    @property
    def rest_after(self):
        return self.intervals[-1].rest_after

    @property
    def interval_dists(self):
        return np.array([I.dist for I in self.intervals])


    def get_dist(self):
        '''should just be done for named blocks with same distance structure'''

        udists = np.unique(self.interval_dists)
        distcounts = np.array([np.sum(self.interval_dists == udist) for udist in udists])

        block_dist = udists[np.argmax(distcounts)]

        self.bad_intervals = [I for I in self.intervals if not I.dist == block_dist ]
        for I in self.intervals:
            if I in self.bad_intervals: setattr(I,'bad_dist',True)
        else: setattr(I,'bad_dist',False)

        if len(udists) > 1:
            print('WARNING program interval adjustment from splits')
            self.adjust_bad_intervals_fromsplits()

        self.dist = block_dist

    def adjust_bad_intervals_fromsplits(self):
        print('todo adjust bad intervals from splits!')


    @property
    def n_intervals(self):
        return len(self.intervals)


    @property
    def conditions(self):
        conditions = []
        for I in self.intervals:
            if not I.condition in conditions:
                conditions += [I.condition]
        return conditions


class Condition(FeatureEnabler):

    def __init__(self,id):
        self.id =  id

    def set_session(self,S):
        self.session = S

    @property
    def intervals(self):
        return [I for I in self.session.intervals if I.condition == self]

    @property
    def n_intervals(self):
        return len(self.intervals)

class Interval(FeatureEnabler):

    def __init__(self,**kwargs):
        self.set_features_fromdict(kwargs)


    def set_session(self,S):
        self.session = S

    def get_pace_from_splits(self):
        cumdur = np.sum([spl.dur for spl in self.splits])
        cumdist = np.sum([spl.dist for spl in self.splits])
        self.pace = cumdur/cumdist * 100

    @property
    def centerpace(self):
        cumdur = np.sum([spl.dur for spl in self.splits[1:-1]])
        cumdist = np.sum([spl.dist for spl in self.splits[1:-1]])
        return cumdur/cumdist * 100

    @property
    def stroke_len(self):
        return self.dist/self.strokes

    @property
    def stroke_len_c(self):
        cumdist = np.sum([spl.dist for spl in self.splits[1:-1]])
        cumstrokes = np.sum([spl.strokes for spl in self.splits[1:-1]])

        return cumdist/cumstrokes



    @property
    def id(self):
        return 'B%s__C%i__I%i'%(self.block.id,self.cond.id,self.run_id)

    @property
    def is_usable(self):
        return True if not self.usable == '-' else False

    def set_splits(self,splitlist):
        self.splits = splitlist

    @property
    def tstop(self):
        return self.ctime

    @property
    def tstart(self):
        return self.ctime-self.dur

    @property
    def idx_in_sess(self):
        return [ii for ii,iobj in enumerate(self.session.intervals) if iobj==self][0]

    @property
    def predecessor(self):
        return None if self.idx_in_sess == 0 else self.session.intervals[self.idx_in_sess-1]

    @property
    def follower(self):
        return None if self.idx_in_sess == len(self.session.intervals) else self.session.intervals[self.idx_in_sess+1]

    @property
    def rest_before(self):
        return self.tstart - self.predecessor.tstop

    @property
    def rest_after(self):
        return self.follower.tstart - self.tstop

    @property
    def pos_in_block(self):
        return [ii for ii, iobj in enumerate(self.block.intervals) if iobj == self][0]

    @property
    def block(self):
        return [B for B in self.session.blocks if B.id == self.block_id][0]

    @property
    def condition(self):
        return [C for C in self.session.conditions if C.id == self.cond_id][0]

    @property
    def n_splits(self):
        return len(self.splits)

    @property
    def color(self):
        return self.condition.color


    @property
    def strokes_per_25(self):
        return self.strokes/self.dist*25

    @property
    def strokes_per_min(self):
        return self.strokes/self.dur*60



class Split(FeatureEnabler):
    def __init__(self,**intidict):
        self.set_features_fromdict(intidict)
        if hasattr(self,'run_id'):
            self.intnum, self.relnum = [int(val) for val in str(self.run_id).split('.')]

    def set_parent_interval(self,intervalobj):
        self.parent = intervalobj

    @property
    def tstop(self):
        return self.ctime

    @property
    def tstart(self):
        return self.ctime-self.dur

    @property
    def strokes_per_min(self):
        return self.strokes/self.dur*60.

    @property
    def stroke_len(self):
        return self.dist/self.strokes

class TestGroup(FeatureEnabler):

    def __init__(self,blockobject,condobject):
        self.block = blockobject
        self.condition = condobject

    @property
    def id(self):
        return '%s_%s'%(self.block.id,self.condition.id)

    @property
    def intervals(self):
        return [interval for interval in self.block.intervals if interval.condition ==self.condition]

    @property
    def n_intervals(self):
        return len(self.intervals)



