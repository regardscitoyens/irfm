import os
from setuptools import setup


BASE_DIR = os.path.dirname(__file__)


def read_text(fname):
    with open(os.path.join(BASE_DIR, fname)) as f:
        return f.read()


def read_requirements(fname):
    with open(os.path.join(BASE_DIR, fname)) as f:
        lines = f.read().splitlines()
        return [line
                for line in lines
                if bool(line and not line.startswith('#'))]


setup(
    name="irfm",
    version="0.0.1",
    author="Nicolas Joyard",
    author_email="joyard.nicolas@gmail.com",
    description="",
    license="AGPLv3+",
    keywords="",
    url="https://git.regardscitoyens.org/regardscitoyens/irfm",
    packages=['irfm'],
    long_description=read_text('README.md'),
    install_requires=read_requirements('requirements.txt'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
    ],
    entry_points='''
        [console_scripts]
        irfm=irfm.cli:manager.run
    '''
)
