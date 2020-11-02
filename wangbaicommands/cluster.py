"""
Compute alignments from the data.
"""

from lingpy.compare.partial import Partial
from lexibank_wangbai import Dataset
from lingpy import *
from lingrex.align import template_alignment
from lingrex.colex import find_bad_internal_alignments, find_colexified_alignments
from pyconcepticon import Concepticon
from cldfcatalog import Config

def run(args):

    ds = Dataset(args)
    args.log.info('[i] start analysis')
    part = Partial(ds.dir.joinpath('analysis', 'wordlist.tsv').as_posix())
    part.partial_cluster(method='sca', threshold=0.45, ref='cogids')
    part.add_cognate_ids('cogids', 'cogid', idtype='loose')
    args.log.info('[i] computed cognates')

    template_alignment(part, template='imnct', structure='structure',
            fuzzy=True, segments='tokens', ref='cogids')
    args.log.info('[i] computed alignments')

    alms = Alignments(part, ref='cogids')

    find_bad_internal_alignments(alms, ref='cogids', transcription='form')
    args.log.info('[i] discarded bad internal alignments')
    find_colexified_alignments(alms, cognates='cogids', ref='crossids')
    args.log.info('[i] identified cross-semantic cognates')
    template_alignment(alms, ref='crossids', template='imnct', structure='structure',
            fuzzy=True, segments='tokens')
    args.log.info('[i] re-aligned the data')
    alms.output(
            'tsv', 
            filename=ds.dir.joinpath('analysis','wordlist-aligned').as_posix(), 
            ignore='all', 
            prettify=False,
            subset=True,
            cols=[
                'doculect',
                'concept',
                'value',
                'form',
                'tokens',
                'cogids',
                'structure',
                'alignment',
                'crossids',
                'cogid'
                ]
            )
    args.log.info('[i] saved alignments to file')

    # export subset of cognates
    S = {0: [c for c in part.columns]}
    concepticon = Concepticon(Config.from_file().get_clone('concepticon'))
    concepts = set()
    for clist in ['Sagart-2019-250', 'Swadesh-1955-100', 'Swadesh-1952-200']:
        for concept in concepticon.conceptlists[clist].concepts.values():
            if concept.concepticon_id:
                concepts.add(concept.concepticon_id)
    for idx in part:
        if part[idx, 'concepticon'] in concepts:
            if part[idx, 'doculect'] != 'ProtoBai':
                S[idx] = part[idx]
    print(part.columns)
    wls = Wordlist(S)
    wls.output('tsv', filename=ds.dir.joinpath('analysis', 'wordlist-subset').as_posix(),
            subset=True,
            cols=[
                'doculect',
                'concept',
                'concepticon',
                'value',
                'form',
                'tokens',
                'cogids',
                'structure',
                'alignment',
                'cogid'
                ])
    wls.calculate('tree', ref='cogid', tree_calc='neighbor')
    print(wls.tree.asciiArt())
    args.log.info(' [i] wordlist has {0} concepts'.format(wls.height))
    wls.output('dst', filename=ds.dir.joinpath('analysis', 'wordlist-subset').as_posix())


