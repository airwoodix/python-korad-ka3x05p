# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name="PyKoradKA",
    description="KORAD KA Series Remote Control V2.0 Python Interface",
    author="Etienne Wodey",
    author_email="wodey@iqo.uni-hannover.de",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    install_requires=["pyserial", "six>=1.10"],
    packages=["koradKA"])
