"""
Compute correspondence patterns from the data.
"""

from lingpy.compare.partial import Partial
from lexibank_wangbai import Dataset
from lingrex.copar import CoPaR
from lingpy import *
from lingpy.algorithm import misc

def run (args):

    ds = Dataset(args)
    args.log.info('[i] start analysis')
    cop = CoPaR(
            ds.dir.joinpath('analysis', 'wordlist-aligned.tsv').as_posix(),
            ref='crossids',
            fuzzy=True,
            transcription='form',
            structure='structure',
            segments='tokens'
            )

    # write all alignments down to file
    table = []
    pid = 1
    all_taxa = ['ProtoBai']+[t for t in cop.cols if t != 'ProtoBai']
    for cogid, msa in cop.msa['crossids'].items(): 
        # select the alignments
        idxs, taxa, strucs, widxs = [], [], [], []
        for i, (idx, doc) in enumerate(zip(msa['ID'], msa['taxa'])):
            if doc in taxa:
                pass
            else:
                idxs += [idx]
                taxa += [doc]
                widx = cop[idx, 'crossids'].index(cogid)
                widxs += [widx]
                strucs += [
                        class2tokens(
                            basictypes.lists(cop[idx, 'structure']).n[widx],
                            cop[idx, 'alignment'].n[widx])]
        if len(taxa) >= 3:
            consensus = [[x for x in col if x != '-'][0] for col in
                    misc.transpose(strucs)]
            for i, cons in enumerate(consensus):
                table += [[
                    str(pid),
                    cons,
                    "1",
                    ]]
                for taxon in all_taxa:
                    if taxon in taxa:
                        tidx = taxa.index(taxon)
                        idx = idxs[tidx]
                        widx = widxs[tidx]
                        reflex = cop[idx, 'alignment'].n[widx][i]
                    else:
                        reflex = 'Ø'
                    table[-1] += [reflex]
                table[-1] += ['{0}:{1}'.format(cogid, i)]
                pid += 1
        
    with open(ds.dir.joinpath('analysis', 'alignments.tsv').as_posix(), 'w') as f:
        f.write('\t'.join([
            'ID',
            'STRUCTURE',
            'FREQUENCY',
            ]+all_taxa+['COGNATESETS'])+'\n')
        for line in table:
            f.write('\t'.join(line)+'\n')
    args.log.info('[i] exported all alignments')
    args.log.info('[i] loaded the wordlist')
    cop.get_sites(minrefs=3, structure='structure')
    args.log.info('[i] retrieved the sites')
    cop.cluster_sites()
    args.log.info('[i] clustered the sites')
    cop.sites_to_pattern()
    cop.add_patterns()
    args.log.info('[i] computed the patterns')
    cop.write_patterns(
            ds.dir.joinpath('analysis', 'correspondence-patterns.tsv').as_posix(),
            proto='ProtoBai'
            )
    cop.output(
            'tsv', 
            filename=ds.dir.joinpath('analysis', 'wordlist-correspondences').as_posix(), 
            prettify=False
            )
    args.log.info('[i] wrote patterns to file')
    

        
