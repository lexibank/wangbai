from setuptools import setup, find_packages
import json


with open("metadata.json", encoding="utf-8") as fp:
    metadata = json.load(fp)


setup(
    name="lexibank_wangbai",
    description=metadata["title"],
    license=metadata.get("license", ""),
    url=metadata.get("url", ""),
    py_modules=["lexibank_wangbai"],
    packages=find_packages(where="."),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "lexibank.dataset": ["wangbai=lexibank_wangbai:Dataset"],
        "cldfbench.commands": ["wangbai=wangbaicommands"],
    },
    install_requires=["pylexibank>=3.0"],
    extras_require={"wangbai": ["sinopy", "lingrex", "python-igraph"], "test":
                    ["pytest-cldf"]},
)
