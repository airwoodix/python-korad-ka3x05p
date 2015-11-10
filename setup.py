# -*- coding: utf-8 -*-

from setuptools import setup


def read_version():
    from koradKA2 import __version__
    return __version__


setup(
    name="PyKoradKA2",
    description="KORAD KA Series Remote Control V2.0 Python Interface",
    author="Etienne Wodey",
    author_email="wodey@iqo.uni-hannover.de",
    version=read_version(),
    install_requires=["decorator"],
    packages=["koradKA2"])
