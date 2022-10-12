import re
from os.path import dirname, join
from setuptools import find_packages, setup

with open(join(dirname(__file__), "src", "pra_todos_verem", "__init__.py")) as fp:
    for line in fp:
        m = re.search(r'^\s*__version__\s*=\s*([\'"])([^\'"]+)\1\s*$', line)
        if m:
            version = m.group(2)
            break
    else:
        raise RuntimeError("Unable to find own __version__ string")

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="pra_todos_verem",
    version=version,
    author="Fabio Beranizo Fontes Lopes",
    author_email="fabio.beranizo@gmail.com",
    description="Geração automatizada de legendas para imagens de redes sociais.",
    license="Apache",
    url="https://github.com/fberanizo/pra-todos-verem",
    package_dir={"": "src"},
    packages=find_packages("src"),
    install_requires=requirements,
    python_requires=">=3.8.0",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
