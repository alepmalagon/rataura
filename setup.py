from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="rataura",
    version="0.1.0",
    author="Alejandro Perez Malagon",
    author_email="your.email@example.com",
    description="A Discord bot for EVE Online using Livekit and LLM function tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alepmalagon/rataura",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "rataura=rataura.__main__:main",
        ],
    },
)
