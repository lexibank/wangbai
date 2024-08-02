import attr
from clldutils.misc import slug
from clldutils.path import Path
from lingpy import *
from pylexibank import Concept, Language
from pylexibank import progressbar
from pylexibank.dataset import Dataset as BaseDataset


@attr.s
class CustomConcept(Concept):
    Chinese_Gloss = attr.ib(default=None)
    Page = attr.ib(default=None)


@attr.s
class CustomLanguage(Language):
    ChineseName = attr.ib(default=None)
    SubGroup = attr.ib(default=None)
    Family = attr.ib(default="Sino-Tibetan")
    Location = attr.ib(default=None)
    Pinyin = attr.ib(default=None)
    Source_ID = attr.ib(default=None)
    Latitude = attr.ib(default=None)
    Longitude = attr.ib(default=None)
    DialectGroup = attr.ib(default=None)


class Dataset(BaseDataset):
    id = "wangbai"
    dir = Path(__file__).parent
    writer_options = dict(keep_languages=False, keep_parameters=False)

    concept_class = CustomConcept
    language_class = CustomLanguage

    def cmd_makecldf(self, args):

        wl = Wordlist(self.raw_dir.joinpath("wang-wordlist.tsv").as_posix())
        concepts = {}
        for concept in self.conceptlists[0].concepts.values():
            idx = "{0}_{1}".format(concept.number, slug(concept.english))
            args.writer.add_concept(
                ID=idx,
                Name=concept.english,
                Page=concept.attributes["page"],
                Chinese_Gloss=concept.attributes["chinese"],
                Concepticon_ID=concept.concepticon_id,
                Concepticon_Gloss=concept.concepticon_gloss,
            )
            concepts[concept.number] = idx
        languages = args.writer.add_languages(lookup_factory="Source_ID")
        args.writer.add_sources()

        errors = []
        for idx in progressbar(wl, desc="cldfify"):
            if wl[idx, "form"] == "tree + skin":
                dct = wl.get_dict(col=wl[idx, "doculect"])
                idxA, idxB = dct["tree"][0], dct["skin"][0]
                wl[idx, "form"] = wl[idxA, "form"] + wl[idxB, "form"]
            if wl[idx, "form"] == "female+brother":
                dct = wl.get_dict(col=wl[idx, "doculect"])
                idxA, idxB = dct["woman"][0], dct["younger brother"][0]
                wl[idx, "form"] = wl[idxA, "form"] + wl[idxB, "form"]
            if wl[idx, "form"] == "water":
                dct = wl.get_dict(col=wl[idx, "doculect"])
                wl[idx, "form"] = wl[dct["water"][0], "form"]
            if wl[idx, "form"] == "trɚ+group":
                dct = wl.get_dict(col=wl[idx, "doculect"])
                wl[idx, "form"] = wl[dct["water"][0], "form"]

            if wl[idx, "form"] not in [
                "di3+wag",
                "ɣɯ2+year",
                "trɚ+group",
                "paddy+field",
                "njoŋ1+brother",
                "ji5+fragrant",
                "5",
            ]:
                try:
                    args.writer.add_form(
                        Language_ID=languages[wl[idx, "doculect"]],
                        Parameter_ID=concepts[wl[idx, "glossid"]],
                        Value=wl[idx, "value"],
                        Form=self.lexemes.get(wl[idx, "form"], wl[idx, "form"]),
                        Source=["Wang2004b"],
                    )
                except:
                    errors += [(idx, wl[idx, "doculect"], wl[idx, "value"])]
        for line in errors:
            print(line[0], "\t", line[1], "\t", line[2])

        # We explicitly remove the ISO column since none of the languages in
        # this dataset have an ISO code.
        args.writer.cldf["LanguageTable"].tableSchema.columns = [
            col
            for col in args.writer.cldf["LanguageTable"].tableSchema.columns
            if col.name != "ISO639P3code"
        ]
