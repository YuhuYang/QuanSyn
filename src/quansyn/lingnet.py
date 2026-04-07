#!/usr/bin/env python
# coding: utf-8

from collections import Counter
import os
from typing import Iterable, List, Tuple
import unicodedata

import numpy as np

from scipy.optimize import curve_fit
from sklearn.metrics import r2_score

from conllu import parse_incr

rootdeps = ['root','ROOT','s','HED']
stopdeps = ['punct','punkt','_','PUN']

_ROOTDEPS = set(rootdeps)
_STOPDEPS = set(stopdeps)


def _normalize_form(form, lowercase: bool) -> str:
    text = "" if form is None else str(form)
    return text.lower() if lowercase else text


def _is_punctuation_word(word: dict, ignore_punct: bool) -> bool:
    if not ignore_punct:
        return False
    deprel = word.get('deprel')
    if deprel in _STOPDEPS:
        return True
    upos = word.get('upos')
    if isinstance(upos, str) and upos.upper() == 'PUNCT':
        return True
    form = word.get('form')
    if form is None:
        return True
    text = str(form).strip()
    if not text:
        return True
    return all(unicodedata.category(ch).startswith('P') for ch in text)


def _normalize_edge(edge: Tuple[str, str], directed: bool) -> Tuple[str, str]:
    if directed:
        return edge
    a, b = edge
    return (a, b) if a <= b else (b, a)


def _iter_dependency_edges(
    treebank: Iterable,
    lowercase: bool,
    ignore_punct: bool
) -> Iterable[Tuple[str, str]]:
    for sent in treebank:
        by_id = {}
        for word in sent:
            wid = word.get('id')
            if isinstance(wid, int):
                by_id[wid] = word

        for word in sent:
            wid = word.get('id')
            if not isinstance(wid, int):
                continue
            if word.get('deprel') in _ROOTDEPS:
                continue
            if _is_punctuation_word(word, ignore_punct):
                continue

            head = word.get('head')
            if not isinstance(head, int) or head <= 0:
                continue
            gov_word = by_id.get(head)
            if gov_word is None:
                continue
            if _is_punctuation_word(gov_word, ignore_punct):
                continue

            dep = _normalize_form(word.get('form'), lowercase)
            gov = _normalize_form(gov_word.get('form'), lowercase)
            if not dep or not gov:
                continue
            # Keep historical orientation: dependent -> governor
            yield (dep, gov)


def _iter_adjacency_edges(
    treebank: Iterable,
    lowercase: bool,
    ignore_punct: bool
) -> Iterable[Tuple[str, str]]:
    for sent in treebank:
        sent_list = []
        for word in sent:
            wid = word.get('id')
            if not isinstance(wid, int):
                continue
            if word.get('deprel') in _ROOTDEPS:
                continue
            if _is_punctuation_word(word, ignore_punct):
                continue
            form = _normalize_form(word.get('form'), lowercase)
            if form:
                sent_list.append(form)
        for i in range(len(sent_list) - 1):
            yield (sent_list[i], sent_list[i + 1])


def _collect_edges(
    treebank: Iterable,
    mode: str = 'dependency',
    lowercase: bool = True,
    ignore_punct: bool = True,
    weighted: bool = False,
    directed: bool = False
) -> List[Tuple]:
    if mode == 'dependency':
        edge_iter = _iter_dependency_edges(treebank, lowercase=lowercase, ignore_punct=ignore_punct)
    elif mode == 'adjacency':
        edge_iter = _iter_adjacency_edges(treebank, lowercase=lowercase, ignore_punct=ignore_punct)
    else:
        raise ValueError(f"Unsupported mode: {mode}. Choose 'dependency' or 'adjacency'.")

    if weighted:
        counter = Counter(_normalize_edge(edge, directed=directed) for edge in edge_iter)
        return [(src, dst, w) for (src, dst), w in counter.items()]

    seen = set()
    result = []
    for edge in edge_iter:
        norm = _normalize_edge(edge, directed=directed)
        if norm in seen:
            continue
        seen.add(norm)
        result.append(norm)
    return result

class Network():

    def __init__(self,treebank):
        self.treebank = list(parse_incr(treebank))
    
    def getDeprel(self, lowercase: bool = True, ignore_punct: bool = True, weighted: bool = False, directed: bool = False):
        return _collect_edges(
            self.treebank,
            mode='dependency',
            lowercase=lowercase,
            ignore_punct=ignore_punct,
            weighted=weighted,
            directed=directed
        )

    def getBiGram(self, lowercase: bool = True, ignore_punct: bool = True, weighted: bool = False, directed: bool = False):
        return _collect_edges(
            self.treebank,
            mode='adjacency',
            lowercase=lowercase,
            ignore_punct=ignore_punct,
            weighted=weighted,
            directed=directed
        )
    
    def mapWordId(self,contents):
        mapping = {}
        current_id = 0
        for st in contents:
            for word in st:
                if word not in mapping:
                    mapping[word] = current_id
                    current_id += 1              
        return mapping

    def getEdge(self,contents,mapping):
        # mapping = {v: k for k, v in mapping.items()}
        edges = [[mapping[w] for w in st] for st in contents]
        return edges


def conllu2edge(
    treebank,
    mode='dependency',
    lowercase: bool = True,
    ignore_punct: bool = True,
    weighted: bool = False,
    directed: bool = False
):
    parsed = parse_incr(treebank)
    return _collect_edges(
        parsed,
        mode=mode,
        lowercase=lowercase,
        ignore_punct=ignore_punct,
        weighted=weighted,
        directed=directed
    )

def load_edges(
    treebanks_path,
    output_path,
    mode='dependency',
    lowercase: bool = True,
    ignore_punct: bool = True,
    weighted: bool = False,
    directed: bool = False
):

    if not os.path.splitext(output_path)[1]:
        os.makedirs(output_path,exist_ok=True)
    else:
        raise ValueError(f" The output path {output_path} is not a valid directory. It should be a directory. ")

    if os.path.isdir(treebanks_path):
        treebanks = [os.path.join(treebanks_path, i) for i in os.listdir(treebanks_path) if i.endswith('.conllu')]
        treebanks.sort()
        file_names = [os.path.basename(t).split('.')[0] for t in treebanks]
        for i,t in enumerate(treebanks):
            with open(t, encoding='utf-8') as treebank:
                edges = _collect_edges(
                    parse_incr(treebank),
                    mode=mode,
                    lowercase=lowercase,
                    ignore_punct=ignore_punct,
                    weighted=weighted,
                    directed=directed
                )
            with open(os.path.join(output_path,file_names[i]+'.txt'), 'w', encoding='utf-8') as f:
                for edge in edges:
                    if weighted:
                        f.write(f"{edge[0]}\t{edge[1]}\t{edge[2]}\n")
                    else:
                        f.write(f"{edge[0]}\t{edge[1]}\n")
    elif os.path.isfile(treebanks_path):
        file_name = os.path.basename(treebanks_path).split('.')[0]
        with open(treebanks_path, encoding='utf-8') as treebank:
            edges = _collect_edges(
                parse_incr(treebank),
                mode=mode,
                lowercase=lowercase,
                ignore_punct=ignore_punct,
                weighted=weighted,
                directed=directed
            )
        with open(os.path.join(output_path, file_name + '.txt'), 'w', encoding='utf-8') as f:
            for edge in edges:
                if weighted:
                    f.write(f"{edge[0]}\t{edge[1]}\t{edge[2]}\n")
                else:
                    f.write(f"{edge[0]}\t{edge[1]}\n")
    else:
        raise ValueError(f" The input path {treebanks_path} is not a valid file or directory. ")
    



class Powerlaw():
    
    def __init__(self, data):
        self.data = data
        
    def getCumDst(self):
        data_fredst = dict(sorted(dict(Counter(self.data)).items(), key=lambda x: x[0]))
        rank = np.log(np.array(list(data_fredst.keys())))
        prob = np.array(list(data_fredst.values())) / sum(data_fredst.values())
        sum_prob = np.array([])
        for p in prob:
            sum_prob = np.append(sum_prob, sum(prob[len(sum_prob):]))
        sum_prob = np.log(sum_prob)
        cdf = [rank,sum_prob]
        return cdf

    def func(self, x, a, b):
        return a * np.array(x) + b

    def fit(self):
        cdf = self.getCumDst()
        x = cdf[0]
        y = cdf[1]
        popt, _ = curve_fit(self.func, x, y)
        a = popt[0]
        b = popt[1]
        y_pred = self.func(x, a, b) 
        r2 = r2_score(y_pred, y)
        return a, b, r2
    
def fitPowerLaw(data):
    a, b, r2 = Powerlaw(data).fit()
    return a, b, r2
