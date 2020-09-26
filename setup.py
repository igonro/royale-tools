"""Setup configuration file."""
from setuptools import find_packages, setup

MODULE_NAME = "royale-tools"
PACKAGE_NAME = "royale-tools"
VERSION = "0.1"

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description="Clash Royale tools for clan management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/igonro/royale-tools",
    author="Iago GR",
    author_email="igonro@gmail.com",
    packages=find_packages(),
    platforms="any",
    python_requires=">=3.7",
)
