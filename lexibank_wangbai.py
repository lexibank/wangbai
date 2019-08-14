from __future__ import unicode_literals, print_function
from collections import OrderedDict, defaultdict

import attr
from clldutils.misc import slug
from clldutils.path import Path
from clldutils.text import split_text, strip_brackets
from pylexibank.dataset import NonSplittingDataset as BaseDataset
from pylexibank.dataset import Concept, Language

from lingpy import *
from tqdm import tqdm

@attr.s
class HConcept(Concept):
    Chinese_Gloss = attr.ib(default=None)
    Page = attr.ib(default=None)
@attr.s
class HLanguage(Language):
    ChineseName = attr.ib(default=None)
    SubGroup = attr.ib(default=None)
    Family = attr.ib(default='Sino-Tibetan')
    Location = attr.ib(default=None)
    Pinyin = attr.ib(default=None)
    Source_ID = attr.ib(default=None)
    Latitude = attr.ib(default=None)
    Longitude = attr.ib(default=None)
    DialectGroup = attr.ib(default=None)


class Dataset(BaseDataset):
    id = 'wangbai'
    dir = Path(__file__).parent
    concept_class = HConcept
    language_class = HLanguage
    
    def clean_form(self, item, form):
        return form.strip().replace(' ', '_')

    def cmd_download(self, **kw):
        pass

    def cmd_install(self, **kw):

        wl = Wordlist(self.dir.joinpath('raw', 'wang-wordlist.tsv').as_posix())
        with self.cldf as ds:
            for concept in self.concepts:#tlist.concepts.values():
                ds.add_concept(
                        ID=concept['NUMBER'],
                        Name=concept['ENGLISH'],
                        Page=concept['PAGE'],
                        Chinese_Gloss=concept['CHINESE'], #.attributes['chinese'],
                        Concepticon_ID=concept['CONCEPTICON_ID'], #.concepticon_id,
                        Concepticon_Gloss=concept['CONCEPTICON_GLOSS'] #.concepticon_gloss
                        )
            ds.add_languages()
            langs = {language['Source_ID']: language['ID'] for language in
                    self.languages}
            ds.add_sources(*self.raw.read_bib())
            errors = []
            for idx in tqdm(wl, desc='cldfify'):
                
                try:
                    ds.add_form_with_segments(
                       Language_ID=langs[wl[idx, 'doculect']],
                       Parameter_ID=wl[idx, 'glossid'], 
                       Value=wl[idx, 'value'],
                       Form=wl[idx, 'form'],
                       Segments=wl[idx, 'tokens'],
                       Source=['Wang2004'],
                       #Loan=wl[idx, 'borrowing']
                       )
                except:
                    errors += [(idx, wl[idx, 'doculect'], wl[idx, 'value'])]
            for line in errors:
                print(line[0], '\t', line[1], '\t', line[2])



