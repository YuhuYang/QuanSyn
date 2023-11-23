###indicators form dependency grammar and valency grammar,such as dependency distance, dependency direction, 
###probabilistic valency pattern, valency and so on.###
from conllu import parse_incr
from collections import Counter

class DependencyAnalyzer():
    """
    An analyzer for dependency.
    
    :Items: mean dependency distance(mdd), dependency distance distribution(dd_distribution),
            proportion of dependency directions(pdd), 
            mean hierarchical distance(mhd), hierarchical distance distribution(hd_distribution),
            tree height and tree width(tree),
            describe(mdd,mhd,pdd,tree_hei,tree_wid,vk)
    """
    def __init__(self,data):
        """
        :data: must be conllu format or other byte-like formats, which means annotated
               such as, f = open(r'treebank.conllu',encoding='utf-8').read()
                        DenpendencyAnalyzer(f)
        """
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
        """
        These three paras can specialize the items you want.
        :pos: str
        :dependency: str
        :direction: str
                    'hi' - head final
                    'hf' - hean initial
        :return: mdd(float)
        :About mdd: 
               Liu H. Dependency distance as a metric of language comprehension difficulty[J]. 
                 Journal of Cognitive Science, 2008, 9(2): 159-191.  
        :example:
              dep = DenpendencyAnalyzer(conllu)
              dep.mdd()
              dep.mdd(pos='NOUN')
        """
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
        """
        :return: dict -> (proportion of head final, proportion of head initial)
        :About dependency direction:
              Liu-Directionalities
              Liu H. Dependency direction as a means of word-order typology: A method based on dependency treebanks[J].
                Lingua, 2010, 120(6): 1567-1578.
        :example:
              dep = DenpendencyAnalyzer(conllu)
              dep.pdd()
        
        """
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
        pdd = {'head final':proportion_head_final,'head_initial':proportion_head_initial}
        return  pdd
    
    def mhd(self, pos=None,dependency=None):
        """
        About mean hierarchical distance:
             Jing Y, Liu H. Mean hierarchical distance augmenting mean dependency distance[C]//
               Proceedings of the third international conference on dependency linguistics 
               (Depling 2015). 2015: 161-170.
        """
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
        """
        About tree height and tree width:
             Hongxin Zhang & Haitao Liu. (2018). Interrelations among dependency tree widths, 
               heights and sentence lengths. In: Haitao Liu & Jingyang Jiang (eds.). 
               Quantitative Analysis of Dependency Structure. Berlin/Boston: DE GRUYTER MOUTON.
        """
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
                if word['deprel'] != 'punct':
                    dd = abs(word['head'] - word['id'])
                    dds.append(dd)
                valencies.append(len([i for i in sentence if i['head'] == word['id']]))
                depth = 0        
                head_id = word['head']
                while head_id != 0:
                    depth += 1
                    head_id = word_index_by_id[head_id]['head']
                levels.append(depth)
            mdd = sum(dds) / len(dds)
            sent_length = len(levels)
            vk = (sum(i*2 for i in valencies)/sent_length) - (2 - 2/sent_length)**2
            sent_data['dd'] = dds
            sent_data['hd'] = levels
            sent_data['sent_length'] = sent_length
            sent_data['tree_height'] = max(levels)
            sent_data['tree_width'] = levels.count(max(levels, key=levels.count))
            sent_data['vk'] = vk
            sents_info.append(sent_data)
        
        if target=='text':
            #mdd = sum([i['mdd'] for i in sents_info])/len(sents_info)
            #mhd = sum([i['mhd'] for i in sents_info])/len(sents_info) 
            senlen = sum([i['sent_length'] for i in sents_info])/len(sents_info)
            tree_hei = sum([i['tree_height'] for i in sents_info])/len(sents_info)
            tree_wid = sum([i['tree_width'] for i in sents_info])/len(sents_info)
            vk = sum([i['vk'] for i in sents_info])/len(sents_info) 
            text_info = {'mdd':mdd,'mhd':mhd,'sent_length':senlen,'tree_height':tree_hei,
                        'tree_width':tree_wid,'vk':vk}
            return text_info 
        
        if target=='sentence':
            return sents_info

class ValencyAnalyzer():
    """
    A class for analyzing valency.
    
    :data: must be conllu format or other byte-like formats, which means annotated corpus(treebanks). 
    """
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