from __future__ import unicode_literals, print_function
from collections import OrderedDict, defaultdict

import attr
from clldutils.misc import slug
from clldutils.path import Path
from clldutils.text import split_text, strip_brackets
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank import Concept, Language
from pylexibank import progressbar
from pylexibank import FormSpec

from lingpy import *

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
    #form_spec = FormSpec(
    

    def cmd_makecldf(self, args):

        wl = Wordlist(self.raw_dir.joinpath('wang-wordlist.tsv').as_posix())
        for concept in self.conceptlists[0].concepts.values():
            args.writer.add_concept(
                    ID=concept.number,
                    Name=concept.english,
                    Page=concept.attributes['page'],
                    Chinese_Gloss=concept.attributes['chinese'],
                    Concepticon_ID=concept.concepticon_id,
                    Concepticon_Gloss=concept.concepticon_gloss
                    )
        args.writer.add_languages()
        languages = {language['Source_ID']: language['ID'] for language in
                self.languages}
        args.writer.add_sources()
        errors = []
        for idx in progressbar(wl, desc='cldfify'):
            
            try:
                args.writer.add_form_with_segments(
                   Language_ID=languages[wl[idx, 'doculect']],
                   Parameter_ID=wl[idx, 'glossid'], 
                   Value=wl[idx, 'value'],
                   Form=wl[idx, 'form'],
                   Segments=wl[idx, 'tokens'],
                   Source=['Wang2004b'],
                   )
            except:
                errors += [(idx, wl[idx, 'doculect'], wl[idx, 'value'])]
        for line in errors:
            print(line[0], '\t', line[1], '\t', line[2])



