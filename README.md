# QuanSyn
QuanSyn：A python package for quantitative syntax analysis.


[![PyPI version](https://badge.fury.io/py/PackageName.svg)](https://badge.fury.io/py/PackageName)
[![Build Status](https://travis-ci.org/user/package.svg?branch=master)](https://travis-ci.org/user/package)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Description

`QuanSyn` is a Python package for Quantitative Linguistics. It provides functionality to quantify linguistic structures and explore language patterns.

This package is consisted of three main parts:
- `depval.py`: some indicators about dependency structures and valency structures.
- `lawfitter.py`: a small fitter for some laws in QL.
- `lingnet.py`: a module for complex network construction.


## Installation

You can install `QuanSyn` via pip:

```bash
pip install quansyn
```

`nltk` and `conllu` are required.

```bash
pip install nltk conllu
```

## Quick Start

Here's a simple example of how to use `QuanSyn`:

### 1. depval
```bash
from quansyn.depval import DepValAnalyzer   
data = open(r'your_treebank.conllu',encoding='utf-8')
dv = DependencyAnalyzer(data) 

# dependency distance distribution
dv.dd_distribution()
# mean dependency distance of specific wordclasses
dv.mdd(pos='NOUN')
# mean dependency distance of specific dependency relations
dv.mdd(dependency='nsubj')
# proportion of dependency distance
dv.pdd()
# tree width and tree depth
dv.tree()
# tree width distirbution and tree depth distribution
dv.tree_distribution()

# mean valency
dv.mean_valency()
# valency distribution
dv.valency_distribution()
# probalistic valency pattern 
dv.pvp()
```
or:
```bash
dv = getDepValFeatures(data)
print(dv)
```

### 2. lawfitter

```bash
from quansyn.lawfitter import fit   
#results = fit(data,model,variant)
results = fit([[1,2,3,4,5,6],[3,4,2,6,8,15]],'zipf')
print(resluts)
```

### 3. lingnet

```bash
from quansyn.lingnet import conllu2edge
import networkx as nx   
# use a conllu file to construction a network
data = open(r'your_treebank.conllu',encoding='utf-8')
edges = conllu2edge(data,mode='dependency')
# or to construct a co-occurance network 
#edges = conllu2edge(data,mode='adjacency')
G = nx.Graph()
G.add_edges_from(edges)

# to estimate the degree exponents
degree =[i[1] for i in G.degree()]
degree_exponents = fitPowerLaw(degree)
print(degree_exponents)
```

## Documentation

For more detailed information, please refer to the [video (in Chinese)](https://quansyn.readthedocs.io/).


## Features

- Dependency distance distribution
- Mean dependency distance of specific wordclasses
- Mean dependency distance of specific dependency relations
- Proportion of dependency distance
- Tree width and tree depth
- Tree width distribution and tree depth distribution
- Mean valency
- Valency distribution
- Probabilistic valency pattern
- Law fitter
- Complex network construction

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

- GitHub: [@YuhuYang](https://github.com/YuhuYang)
- Email: yangmufy@163.com

## Citing

If our project has been helpful to you, please give it a star and cite our articles. We would be very grateful.

```
@article{Yang_2022,
doi = {10.1209/0295-5075/ac8bf2},
url = {https://dx.doi.org/10.1209/0295-5075/ac8bf2},
year = {2022},
month = {sep},
publisher = {EDP Sciences, IOP Publishing and Società Italiana di Fisica},
volume = {139},
number = {6},
pages = {61002},
author = {Mu Yang and Haitao Liu},
title = {The role of syntax in the formation of scale-free language networks},
journal = {Europhysics Letters},
abstract = {The overall structure of a network is determined by its micro features, which are different in both syntactic and non-syntactic networks. However, the fact that most language networks are small-world and scale-free raises the question: does syntax play a role in forming the scale-free feature? To answer this question, we build syntactic networks and co-occurrence networks to compare the generation mechanisms of nodes, and to investigate whether syntactic and non-syntactic factors have distinct roles. The results show that frequency is the foundation of the scale-free feature, while syntax is beneficial to enhance this feature. This research introduces a microscopic approach, which may shed light on the scale-free feature of language networks.}
}
``` 