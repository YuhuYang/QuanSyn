from collections import Counter 
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from conllu import parse_incr
from sklearn.metrics import r2_score
from nltk import ngrams

class HyperGraph():
    
    def __init__(self,treebank):
        self.treebank = parse_incr(treebank)
        
    def getContent(self):
        # hyperedge = []
        # for sent in self.treebank:
        #     for word in sent:
        #         depdents = [(w['form'],w['upos']) for w in sent if w['head']==word['id'] and w['upos']!='PUNCT']
        #         if word['deprel'] not in ['punct','root','ROOT'] and type(word['head'])==int:
        #             governor = [(sent[word['head']-1]['form'],sent[word['head']-1]['upos'])]
        #             cons = set(depdents + governor)
        #         else:
        #             cons = set(depdents)
        #         if len(cons) > 1 and cons not in hyperedge:
        #             hyperedge.append(cons)
        # return hyperedge
        wordlist = {}
        for sent in self.treebank:
            for word in sent:
                tw =  (word['form'],word['upos']) 
                if tw not in wordlist:
                    wordlist[tw]=set()
                depdents = [(w['form'],w['upos']) for w in sent if w['head']==word['id'] and w['upos']!='PUNCT']
                if len(depdents) > 0:
                    for d in depdents:
                        if d not in wordlist[tw]:
                            wordlist[tw].add(d)
                if word['deprel'] not in ['punct','root','ROOT'] and type(word['head'])==int:
                    governor = (sent[word['head']-1]['form'],sent[word['head']-1]['upos'])
                    if governor not in wordlist[tw]:
                        wordlist[tw].add(governor)
        wordlist = {key: value for key, value in wordlist.items() if len(value) > 1}
        contents = []
        for e in wordlist.values():
            if e not in contents:
                contents.append(e)
        return contents

    def getSubtree(self):
        subtrees = []
        for sent in self.treebank:
            subtree = []
            for word in sent:
                tw =  (word['form'],word['upos']) 
                depdents = [(w['form'],w['upos']) for w in sent if w['head']==word['id'] and w['upos']!='PUNCT']
                subtree.append(tw)
                subtree = subtree + depdents
                subtrees.append(subtree)
        new_subtrees = []
        for e in subtrees:
            if e not in new_subtrees:
                new_subtrees.append(e)
        return new_subtrees

    def getTriGram(self):
        # tri_grams = []
        # for sent in self.treebank:
        #     sent_list = [(word['form'],word['upos']) for word in sent if word['upos'] != 'PUNCT']
        #     tri_gram = list(ngrams(sent_list,3))
        #     tri_gram = [{t[0],t[2]} for t in tri_gram]
        #     tri_grams = tri_grams+tri_gram
        # new_tri = []
        # for t in tri_grams:
        #     if t not in tri_grams:
        #         new_tri.append(t)
        # return tri_grams
        wordlist = {}
        for sent in self.treebank:
            sent_list = [(word['form'],word['upos']) for word in sent if word['upos'] != 'PUNCT']
            tri_gram = list(ngrams(sent_list,3))
            for t in tri_gram:
                if t[1] not in wordlist:
                    wordlist[t[1]] = set()
                if t[0] not in wordlist[t[1]]:
                    wordlist[t[1]].add(t[0])
                if t[2] not in wordlist[t[1]]:
                    wordlist[t[1]].add(t[2])
        wordlist = {key: value for key, value in wordlist.items() if len(value) > 1}
        contents = []
        for e in wordlist.values():
            if e not in contents:
                contents.append(e)
        return contents

    
    def mapWordId(self,contents):
        mapping = {}
        current_id = 0
        for st in contents:
            for word in st:
                if word not in mapping:
                    mapping[current_id] = word
                    current_id += 1                
        return mapping

    def getHyperEdge(self,contents,mapping):
        mapping = {v: k for k, v in mapping.items()}
        weighted_hyperedges = [[mapping[w] for w in st] for st in contents]
        hyperedges = []
        for whe in weighted_hyperedges:
            if whe not in hyperedges:
                hyperedges.append(whe)
        return hyperedges

def conllu2hyperedge(treebank,mode='dependency'):
    hp = HyperGraph(treebank)
    if mode == 'dependency':
        subtrees = hp.getContent()
    elif mode == 'adjacent':
        subtrees = hp.getTriGram()
    elif mode == 'pattern':
        subtrees = hp.getSubtree()
    mapping = hp.mapWordId(subtrees)
    hyperedges = hp.getHyperEdge(subtrees,mapping)
    return hyperedges

class Network():

    def __init__(self,treebank):
        self.treebank = parse_incr(treebank)
    
    def getDeprel(self):
        edges = []
        for sent in self.treebank:
            for word in sent:
                if word['deprel'] not in ['punct','root','ROOT']:
                    gov = (sent[word['head']-1]['form'],sent[word['head']-1]['upos'])
                    dep = (word['form'],word['upos'])
                    if (dep,gov) not in edges and (gov,dep) not in edges:
                        edges.append((dep,gov))
        return edges

    def getBiGram(self):
        bigrams = []
        for sent in self.treebank:
            sent_list = [(word['form'],word['upos']) for word in sent if word['upos'] != 'PUNCT']
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

from itertools import combinations
def hyper2simple(hyperedges):
    edges = []
    for h in hyperedges:
        edges = edges + list(combinations(h, 2))
    return edges
