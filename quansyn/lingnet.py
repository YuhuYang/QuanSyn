#!/usr/bin/env python
# coding: utf-8

from collections import Counter 
import numpy as np
from scipy.optimize import curve_fit
from conllu import parse_incr
from sklearn.metrics import r2_score
from nltk import ngrams

class Network():

    def __init__(self,treebank):
        self.treebank = parse_incr(treebank)
    
    def getDeprel(self):
        edges = []
        for sent in self.treebank:
            for word in sent:
                if word['deprel'] not in ['punct','root','ROOT','-','_']:
                    gov = sent[word['head']-1]['form']
                    dep = word['form']
                    if (dep,gov) not in edges and (gov,dep) not in edges:
                        edges.append((dep,gov))
        return edges

    def getBiGram(self):
        bigrams = []
        for sent in self.treebank:
            sent_list = [word['form'] for word in sent if word['upos'] != 'PUNCT']
            bigram = list(ngrams(sent_list,2))
            for t in bigram:
                if t not in bigrams and (t[1],t[0]) not in bigrams:
                    bigrams.append(t)
        return bigrams
    
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


def conllu2edge(treebank,mode='dependency'):
    nw = Network(treebank)
    if mode == 'dependency':
        subtrees = nw.getDeprel()
    elif mode == 'adjacent':
        subtrees = nw.getBiGram()
    mapping = nw.mapWordId(subtrees)
    edges = nw.getEdge(subtrees,mapping)
    return edges


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
        popt, pcov = curve_fit(self.func, x, y)
        a = popt[0]
        b = popt[1]
        y_pred = self.func(x, a, b) 
        r2 = r2_score(y_pred, y)
        return a, b, r2
    
def fitPowerLaw(data):
    a, b, r2 = Powerlaw(data).fit()
    return a, b, r2
