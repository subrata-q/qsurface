import pathlib

from setuptools import find_packages, setup

directory = pathlib.Path(__file__).parent

README = (directory / "README.md").read_text()


setup(
    name="qsurface",
    version="0.2.0",
    description="Surface code simulations and visualizations (forked from watermarkhu/qsurface)",
    long_description=README,
    long_description_content_type="text/markdown",
    license="BSD-3",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.8+",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*"]),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "matplotlib>=3.5.0",
        "networkx>=2.5",
        "pandas>=1.2.0",
        "scipy>=1.6.0",
        "pptree>=3.1",
        "numpy>=1.19.0",
        "drawsvg",
        "cairosvg",
    ],
    entry_points={
        "console_scripts": [
            "qsurface=qsurface.__main__:main",
            "qsurface-getblossomv=qsurface.decoders.mwpm:get_blossomv",
        ],
    },
)
