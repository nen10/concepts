"""Setup file"""
from pip._internal.req import parse_requirements
from setuptools import setup, find_packages

REQUIREMENTS = [str(req.requirement) for req in parse_requirements(
    'requirements.txt', session=None)]

if __name__ == "__main__":
    setup(
        name="concepts",
        package_data={"concepts": ["py.typed"]},
        packages=find_packages(exclude=['tests']),
        install_requires=REQUIREMENTS,
        url="https://github.com/nen10/concepts",
        python_requires=">= 3.8",
    )
