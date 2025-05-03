"""
Setup script for EVE Wiggin.
"""

from setuptools import setup, find_packages

setup(
    name="eve_wiggin",
    version="0.1.0",
    description="Strategic Analysis Tool for EVE Online Faction Warfare",
    author="alepmalagon",
    author_email="",
    url="https://github.com/alepmalagon/rataura",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "rataura",  # Add rataura as a dependency
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
