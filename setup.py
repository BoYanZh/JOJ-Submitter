import os
import re
from typing import List

from setuptools import find_packages, setup


def get_version(package: str) -> str:
    """
    Return package version as listed in `__version__` in `__main__.py`.
    """
    path = os.path.join(package, "__main__.py")
    main_py = open(path, "r", encoding="utf8").read()
    match = re.search("__version__ = ['\"]([^'\"]+)['\"]", main_py)
    if match is None:
        return "0.0.0"
    return match.group(1)


def get_long_description() -> str:
    """
    Return the README.
    """
    return open("README.md", "r", encoding="utf8").read()


def get_packages(package: str) -> List[str]:
    """
    Return root package and all sub-packages.
    """
    return [
        dirpath
        for dirpath, dirnames, filenames in os.walk(package)
        if os.path.exists(os.path.join(dirpath, "__init__.py"))
    ]


def get_install_requires() -> List[str]:
    return open("requirements.txt").read().splitlines()


setup(
    name="joj-submitter",
    version=get_version("joj_submitter"),
    url="https://github.com/BoYanZh/JOJ-Submitter",
    license="MIT",
    description="Submit your work to JOJ via cli.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="SJTU JI Tech",
    author_email="bomingzh@sjtu.edu.cn",
    maintainer="BoYanZh",
    maintainer_email="bomingzh@sjtu.edu.cn",
    packages=find_packages(),
    python_requires=">=3.6",
    entry_points={"console_scripts": ["joj-submit=joj_submitter:main"]},
    project_urls={
        "Bug Reports": "https://github.com/BoYanZh/JOJ-Submitter/issues",
        "Source": "https://github.com/BoYanZh/JOJ-Submitter",
    },
    install_requires=[
        "beautifulsoup4>=4.9.3",
        "pydantic>=1.8.1",
        "requests>=2.25.1",
        "typer[all]>=0.3.2",
    ],
)
