from conllu import parse_incr
from collections import Counter

class DependencyAnalyzer():
    def __init__(self,data):
        self.data = list(parse_incr(data))
        
    def _pos_condition(self,word, pos):
        return word['upos'] == pos
    def _dep_condition(self,word, dep):
        return word['deprel'] == dep
    def _dir_condition(self,word, direc):
        if direc == 'hi':
            return word['id'] - word['head'] < 0
        if direc == 'hf':
            return word['id'] - word['head'] > 0
    def select_conditions(self,word, pos=None, dependency=None, direc=None):
        conditions = []
        conditions.append(True)
        if pos:
            conditions.append(self._pos_condition(word, pos))
        if dependency:
            conditions.append(self._dep_condition(word, dependency))
        if direc:
            conditions.append(self._dep_condition(word, direc))
        return conditions
    
    def mdd(self,pos=None,dependency=None,direction=None):
        dds = self.dd_distribution(pos,dependency,direction)
        MDD = sum(dds) / len(dds)
        return MDD    
    
    def dd_distribution(self,pos=None,dependency=None,direction=None):
        dds = []
        for sentence in self.data:    
            for word in sentence:
                conditions = self.select_conditions(word, pos, dependency, direction)
                if all(conditions+[word['deprel'] not in ['root','punct']]):
                    dd = abs(word['head'] - word['id'])
                    dds.append(dd)
        return dds      
    
    def pdd(self,pos=None,dependency=None):
        head_initial = 0
        head_final = 0
        for sentence in self.data:    
            for word in sentence:
                conditions = self.select_conditions(word, pos, dependency)
                if all(conditions+[word['deprel'] not in ['root','punct']]):
                    if word['head'] < word['id']:
                        head_initial += 1
                    else:
                        head_final += 1
                        
        total = head_initial + head_final
        proportion_head_initial = head_initial / total
        proportion_head_final = head_final / total
        pdd = {'head final':proportion_head_final,'head initial':proportion_head_initial}
        return  pdd
    
    def mhd(self, pos=None,dependency=None):
        hds = self.hd_distribution(pos,dependency)
        MHD = sum(hds)/len(hds)
        return MHD
    
    def hd_distribution(self, pos=None,dependency=None):
        hds = []
        for sentence in self.data:
            word_index_by_id = {word['id']: word for word in sentence}
            selected_words = [word for word in sentence if all(self.select_conditions(word, pos, dependency)+[word['deprel'] not in ['root','punct']])]
            for word in selected_words:            
                head_id = word['head']
                distance = 0
                while head_id != 0:
                    distance += 1
                    head_id = word_index_by_id[head_id]['head']
                hds.append(distance)
        return hds    

    def tree(self,pos=None,dependency=None):        
        tree_indicators = self.tree_distribution(pos,dependency)
        tree_height = tree_indicators['height']
        tree_width = tree_indicators['width']
        tree = {'height':sum(tree_height)/len(tree_height),'width':sum(tree_width)/len(tree_width)}
        return tree
    
    def tree_distribution(self,pos=None,dependency=None):
        height = []
        width = []
        for sentence in self.data:
            word_index_by_id = {word['id']: word for word in sentence}
            levels = []
            for word in sentence:
                conditions = self.select_conditions(word, pos, dependency)
                if all(conditions+[word['deprel'] != 'punct']):
                    depth = 0        
                    head_id = word['head']
                    while head_id != 0:
                        depth += 1
                        head_id = word_index_by_id[head_id]['head']
                    levels.append(depth)
            height.append(max(levels))
            width.append(levels.count(max(levels, key=levels.count)))
        tree = {'height':height,'width':width}
        return tree
    
    def describe(self,target='text'):
        sents_info = []
        for sentence in self.data:
            sent_data = {}
            dds = []
            levels = []
            valencies = []
            word_index_by_id = {word['id']: word for word in sentence}
            for word in sentence:
                if word['deprel'] not in['punct','root']:
                    dd = abs(word['head'] - word['id'])
                    dds.append(dd)
                    depth = 0        
                    head_id = word['head']
                    while head_id != 0:
                        depth += 1
                        head_id = word_index_by_id[head_id]['head']
                    levels.append(depth)
                    k = len([i for i in sentence if i['head'] == word['id'] and i['deprel'] is not 'punct'])+1
                if word['deprel'] is 'root':
                    k = len([i for i in sentence if i['head'] == word['id'] and i['deprel'] is not 'punct'])
                valencies.append(k)
            sent_length = len(levels)+1
            vk = (sum(i**2 for i in valencies)/sent_length) - (2 - 2/sent_length)**2
            sent_data['dd'] = dds
            sent_data['hd'] = levels
            sent_data['sent_length'] = sent_length
            sent_data['tree_height'] = max(levels)
            sent_data['tree_width'] = levels.count(max(levels, key=levels.count))
            sent_data['vk'] = vk
            sents_info.append(sent_data)
        
        if target=='text':
            mdd = sum([sum(i['dd']) for i in sents_info])/sum([len(i['dd']) for i in sents_info])
            mhd = sum([sum(i['hd']) for i in sents_info])/sum([len(i['hd']) for i in sents_info])
            senlen = sum([i['sent_length'] for i in sents_info])/len(sents_info)
            tree_hei = sum([i['tree_height'] for i in sents_info])/len(sents_info)
            tree_wid = sum([i['tree_width'] for i in sents_info])/len(sents_info)
            vk = sum([i['vk'] for i in sents_info])/len(sents_info) 
            text_info = {'mdd':mdd,'mhd':mhd,'sent_length':senlen,'tree_height':tree_hei,
                        'tree_width':tree_wid,'vk':vk}
            return text_info 
        
        if target=='sentence':
            return sents_info
        
def getDepFeatures(conllu):
    dep = DependencyAnalyzer(conllu)
    featuredict = {}
    featuredict['mdd'] = dep.mdd()
    featuredict['mhd'] = dep.mhd()
    featuredict['dd distribution'] = dep.dd_distribution()
    featuredict['hd distribution'] = dep.hd_distribution()
    featuredict['pdd'] = dep.pdd()
    featuredict['tree'] = dep.tree()
    featuredict['tree distribution'] = dep.tree_distribution()
    return featuredict

class ValencyAnalyzer():

    def __init__(self, data):
        self.data = list(parse_incr(data))

    def _pos_condition(self,word, pos):
        return word['upos'] == pos
    def _dep_condition(self,word, dep):
        return word['deprel'] == dep
    def select_conditions(self,word, pos=None, dependency=None):
        conditions = []
        conditions.append(True)
        if pos:
            conditions.append(self._pos_condition(word, pos))
        if dependency:
            conditions.append(self._dep_condition(word, dependency))
        return conditions    
    
    def mean_valency(self,pos=None):
        val_distribution = self.distribution(pos)
        mean_valency = sum(val_distribution)/len(val_distribution)
        return mean_valency

    def distribution(self,pos=None):
        val = []
        for sentence in self.data:    
            for word in sentence:
                if all(self.select_conditions(word, pos)+[word['deprel'] != 'punct']): 
                    depdents = [w for w in sentence if w['head'] == word['id']]
                    val.append(len(depdents)) 
        return val
    
    def PVP(self,pos=None,target='dependency'):
        dependents = []
        governors = []
        for sentence in self.data:    
            for word in sentence:
                conditions = self.select_conditions(word, pos)
                if all(conditions+[target=='dependency']): 
                    dependent = [w['deprel'] for w in sentence if w['head'] == word['id']]
                    dependents += dependent
                    governor = word['deprel']
                    governors.append(governor)
                if all(conditions+[target=='wordclass']):
                    dependent = [w['upos'] for w in sentence if w['head'] == word['id']]
                    dependents += dependent
                    governor = [w['upos'] for w in sentence if w['id'] == word['head']]
                    governors += governor                   
                    
        deps = Counter(dependents)
        govs = Counter(governors)
        pvp = {'act as a gov':deps,'act as a dep':govs}
        return pvp

def getValFeatures(conllu):
    val = ValencyAnalyzer(conllu)
    featuredict = {}
    featuredict['mean valency'] = val.mean_valency()
    featuredict['valency distribution'] = val.distribution()
    featuredict['probablistic valency pattern'] = val.PVP()
    return featuredict
