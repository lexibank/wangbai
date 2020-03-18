"""
Compute partial cognates and alignments and create a wordlist.
"""

from lingpy import *
from lingpy.compare.partial import Partial
import pathlib
from lexibank_wangbai import Dataset

def run(args):

    ds = Dataset(args)
    part = Partial.from_cldf(str(ds.cldf_specs().metadata_path))
    part.partial_cluster(method='sca', threshold=0.45, ref='cogids')
    alms = Alignments(part, ref='cogids')
    alms.align()
    alms.output('tsv', filename='wordlist', ignore='all', prettify=False)
