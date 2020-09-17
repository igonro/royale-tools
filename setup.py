"""Setup configuration file."""
from pathlib import Path

from setuptools import find_namespace_packages, setup

MODULE_NAME = "royale-tools"
PACKAGE_NAME = "royale-tools"
VERSION = "0.1"

requirements_path = Path(__file__).resolve().parent / "requirements.txt"
with open(requirements_path, "r") as f:
    install_requires = f.read().splitlines()

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description="Clash Royale tools for clan management",
    author="Iago GR",
    author_email="igonro@gmail.com",
    packages=find_namespace_packages(
        include="{}.*".format(MODULE_NAME), exclude=["tests", "logs"]
    ),
    include_package_data=True,
    platforms="any",
    python_requires=">=3.7",
    install_requires=install_requires,
)
