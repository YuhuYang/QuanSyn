#!/usr/bin/env python
# coding: utf-8

from collections import Counter 
import numpy as np
import os

from scipy.optimize import curve_fit
from sklearn.metrics import r2_score

from conllu import parse_incr

rootdeps = ['root','ROOT','s','HED']
stopdeps = ['punct','punkt','_','PUN']

class Network():

    def __init__(self,treebank):
        self.treebank = list(parse_incr(treebank))
    
    def getDeprel(self):
        edges = []
        for sent in self.treebank:
            for word in sent:
                if word['deprel'] not in rootdeps+stopdeps:
                    gov = sent[word['head']-1]['form'].lower()
                    dep = word['form'].lower()
                    if (dep,gov) not in edges and (gov,dep) not in edges:
                        edges.append((dep,gov))
        return edges

    def getBiGram(self):
        bigrams = []
        for sent in self.treebank:
            sent_list = [word['form'].lower() for word in sent if word['deprel'] not in rootdeps+stopdeps]
            bigram = [(sent_list[i], sent_list[i + 1]) for i in range(len(sent_list) - 1)]
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
        edges = nw.getDeprel()
    elif mode == 'adjacency':
        edges = nw.getBiGram()
    # mapping = nw.mapWordId(edges)
    # edges = nw.getEdge(edges,mapping)
    return edges

def load_edges(treebanks_path,output_path,mode='dependency'):

    if not os.path.splitext(output_path)[1]:
        os.makedirs(output_path,exist_ok=True)
    else:
        raise ValueError(f" The output path {output_path} is not a valid directory. It should be a directory. ")

    if os.path.isdir(treebanks_path):
        treebanks = [os.path.join(treebanks_path, i) for i in os.listdir(treebanks_path) if i.endswith('.conllu')]
        file_names = [os.path.basename(t).split('.')[0] for t in treebanks]
        for i,t in enumerate(treebanks):      
            treebank = open(t, encoding='utf-8')
            nw = Network(treebank)
            if mode == 'dependency':
                edges = nw.getDeprel()
            elif mode == 'adjacency':
                edges = nw.getBiGram()
            with open(os.path.join(output_path,file_names[i]+'.txt'), 'w', encoding='utf-8') as f:
                for edge in edges:
                    f.write(f"{edge[0]}\t{edge[1]}\n")
    



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
