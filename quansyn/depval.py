#!/usr/bin/env python
# coding: utf-8

from conllu import parse_incr
from collections import Counter

class DepValAnalyzer():
    """
    An Analyzer for Dependency structures.
    
    Parameters
    ----------
    data : conllu
        A dependency treebank in CoNLLU format.
    
    Methods
    ----------
    dd_distribution(pos=None, dependency=None, direction=None)
        Returns the distribution of dependency distribution.              
    mdd(pos=None, dependency=None, direction=None)
        Returns the mean dependency distance.
    pdd(pos=None, dependency=None, direction=None)
        Returns the percent of dependency directions.
    mhd(pos=None, dependency=None, direction=None)
        Returns the mean hierarchy distance.
    hd_distribution(pos=None, dependency=None, direction=None)
        Returns the distribution of hierarchy distance.
    tree(pos=None, dependency=None, direction=None)
        Returns the tree depth and width.
    tree_distribution(pos=None, dependency=None, direction=None)
        Returns the distribution of tree depth and width.
    describe(pos=None, dependency=None, direction=None)
        Returns a description of the dependency structure.

        
    Examples
    ----------
    >>> from depval import DependencyAnalyzer    
    >>> data = open(r'your_treebank.conllu',encoding='utf-8')
    >>> dep = DependencyAnalyzer(data) 
    >>> dep.dd_distribution()
    """

    def __init__(self,data):
        """
        Parameters
        ----------
        data : conllu
            A dependency treebank in CoNLLU format.
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
        Returns the mean dependency distance.
        
        About MDD: 
            Liu, H. (2008). Dependency distance as a metric of language comprehension difficulty. Journal of Cognitive Science, 9(2), 159-191.

        Parameters
        ----------
        pos : str, optional
            The mdd of a special part-of-speech tag. The default is None.
        dependency : str, optional
            The mdd of a special dependency relation. The default is None.
        direction : str, optional
            The mdd of a special dependency direction. The default is None.
        """
        dds = self.dd_distribution(pos,dependency,direction)
        mdd = sum([i[0]*i[1] for i in dds])/sum([i[1] for i in dds])
        MDD = round(mdd,3)
        return MDD    
    
    def dd_distribution(self,pos=None,dependency=None,direction=None):
        """
        Returns the distribution of dependency distances.
        """
        dds = []
        for sentence in self.data:    
            for word in sentence:
                conditions = self.select_conditions(word, pos, dependency, direction)
                if all(conditions+[word['deprel'] not in ['root','punct','_']]):
                    dd = abs(word['head'] - word['id'])
                    dds.append(dd)
        dds = sorted(Counter(dds).items())
        return dds      
    
    def pdd(self,pos=None,dependency=None):
        """
        Returns the proportion of dependency distance.
        
        About PDD: 
            Liu H.(2010) Dependency direction as a means of word-order typology: a method based on dependency treebanks. Lingua, 120(6): 1567-1578.

        """
        head_initial = 0
        head_final = 0
        for sentence in self.data:    
            for word in sentence:
                conditions = self.select_conditions(word, pos, dependency)
                if all(conditions+[word['deprel'] not in ['root','punct','_']]):
                    if word['head'] < word['id']:
                        head_initial += 1
                    else:
                        head_final += 1
                        
        total = head_initial + head_final
        proportion_head_initial = round(head_initial / total,3)
        proportion_head_final = round(head_final / total,3)
        pdd = {'head final':proportion_head_final,'head initial':proportion_head_initial}
        return  pdd
    
    def mhd(self, pos=None,dependency=None):
        """
        Returns the mean hierarchical distance.
        
        About MHD: 
            [1]刘海涛,敬应奇.英语句子层级结构计量分析[J].外国语(上海外国语大学学报),2016,39(06):2-11.
            Liu H., Jing Y. (2016). A Quantitative Analysis of English Hierarchical Structure. Journal of Foreign Languages, 39(6), 2-11.(in Chinese)

        """
        hds = self.hd_distribution(pos,dependency)
        mhd = sum([i[0]*i[1] for i in hds])/sum([i[1] for i in hds])
        MHD = round(mhd,3)
        return MHD
    
    def hd_distribution(self, pos=None,dependency=None):
        """
        Returns the distribution of hierarchical distances.
        """
        hds = []
        for sentence in self.data:
            word_index_by_id = {word['id']: word for word in sentence}
            selected_words = [word for word in sentence if all(self.select_conditions(word, pos, dependency)+[word['deprel'] not in ['root','punct','_']])]
            for word in selected_words:            
                head_id = word['head']
                distance = 0
                while head_id != 0:
                    distance += 1
                    head_id = word_index_by_id[head_id]['head']
                hds.append(distance)
        hds = sorted(Counter(hds).items())
        return hds    

    def tree(self,pos=None,dependency=None):
        """
        Returns the average height and width of the tree.

        About tree height and tree width:
            Zhang, H. & Liu, H. (2018). Interrelations among Dependency Tree Widths, Heights and Sentence 
        Lengths. In J. Jiang & H. Liu (Ed.), Quantitative Analysis of Dependency Structures (pp. 31-52). 
        Berlin, Boston: De Gruyter Mouton.

        """
        tree_indicators = self.tree_distribution(pos,dependency)
        tree_height = tree_indicators['height']
        tree_width = tree_indicators['width']
        height = sum([i[0]*i[1] for i in tree_height])/sum([i[1] for i in tree_height])
        width = sum([i[0]*i[1] for i in tree_width])/sum([i[1] for i in tree_width])
        tree = {'height':round(height,3),'width':round(width,3)}
        return tree
    
    def tree_distribution(self,pos=None,dependency=None):
        """
        Returns the distribution of tree height and width.
        """
        height = []
        width = []
        for sentence in self.data:
            word_index_by_id = {word['id']: word for word in sentence}
            levels = []
            for word in sentence:
                conditions = self.select_conditions(word, pos, dependency)
                if all(conditions+[word['deprel'] not in  ['punct','_']]):
                    depth = 0        
                    head_id = word['head']
                    while head_id != 0:
                        depth += 1
                        head_id = word_index_by_id[head_id]['head']
                    levels.append(depth)
            height.append(max(levels))
            width.append(levels.count(max(levels, key=levels.count)))
        
        width_distribution = sorted(Counter(width).items())
        height_distribution = sorted(Counter(height).items())

        tree = {'height':height_distribution,'width':width_distribution}
        return tree
    
    def mean_valency(self,pos=None):
        """
        Returns the mean valency.
        
        About mean valency: 
            Jianwei Yan, & Haitao Liu*. (2022). Quantitative analysis of 
        Chinese and English verb valencies based on Probabilistic Valency 
        Pattern Theory. In Dong, M., Gu, Y., & Hong, J. (Eds.), Chinese Lexical 
        Semantics. CLSW 2021. Lecture Notes in Computer Science (Vol. 13250) 
        (pp. 152-162). Cham: Springer. EI
        """
        val_distribution = self.valency_distribution(pos)
        mean_valency = sum([i[0]*i[1] for i in val_distribution])/sum([i[1] for i in val_distribution])
        mean_valency = round(mean_valency,3)
        return mean_valency

    def valency_distribution(self,pos=None):
        """
        Returns the distribution of valencies.
        """
        val = []
        for sentence in self.data:    
            for word in sentence:
                if all(self.select_conditions(word, pos)+[word['deprel']  not in ['punct','_']]): 
                    depdents = [w for w in sentence if w['head'] == word['id']]
                    val.append(len(depdents)) 
        val = sorted(Counter(val).items())
        return val
    
    def pvp(self,pos=None,target='dependency'):
        """
        Returns the PVP.
        
        About pvp: 
            Jianwei Yan, & Haitao Liu*. (2022). Quantitative analysis of 
        Chinese and English verb valencies based on Probabilistic Valency 
        Pattern Theory. In Dong, M., Gu, Y., & Hong, J. (Eds.), Chinese Lexical 
        Semantics. CLSW 2021. Lecture Notes in Computer Science (Vol. 13250) 
        (pp. 152-162). Cham: Springer. EI
        """

        dependents = []
        governors = []
        for sentence in self.data:    
            for word in sentence:
                conditions = self.select_conditions(word, pos)
                if all(conditions+[target=='dependency']+ [word['deprel'] not in ['punct','_']]): 
                    dependent = [w['deprel'] for w in sentence if w['head'] == word['id']]
                    dependents += dependent
                    governor = word['deprel']
                    governors.append(governor)
                if all(conditions+[target=='wordclass']+ [word['deprel'] not in ['punct','_']]):
                    dependent = [w['upos'] for w in sentence if w['head'] == word['id']]
                    dependents += dependent
                    governor = [w['upos'] for w in sentence if w['id'] == word['head']]
                    governors += governor                   
                    
        deps = Counter(dependents)
        govs = Counter(governors)
        govs = sorted([(i[0],round(i[1]/sum(govs.values()),3)) for i in govs.items()],key=lambda x: x[1],reverse = True)
        deps = sorted([(i[0],round(i[1]/sum(deps.values()),3)) for i in deps.items()],key=lambda x: x[1],reverse = True)
        pvp = {'act as a gov':deps,'act as a dep':govs}
        return pvp

    def calculate_by_sents(self):
        """
        Return the indicators of sentences or texts.

        About vk:
            Lu, Q., Lin, Y. & Liu, H. (2018). Dynamic Valency and Dependency Distance. 
        In J. Jiang & H. Liu (Ed.), Quantitative Analysis of Dependency Structures (pp. 145-166). 
        Berlin, Boston: De Gruyter.

        About mhdd:
            Chen, R., Deng, S., & Liu, H. (2021). Syntactic Complexity of Different Text Types: 
            From the Perspective of Dependency Distance Both Linearly and Hierarchically. 
            Journal of Quantitative Linguistics, 29(4), 510–540. 
        
        About tdl:
            Futrell, R., Mahowald, K., & Gibson, E. (2015). Large-scale evidence of dependency 
            length minimization in 37 languages. Proceedings of the National Academy of Sciences, 
            112(33), 10336-10341.

        """
        sents_info = []
        for sentence in self.data:
            sent_data = {}
            dds = []
            levels = []
            valencies = []
            word_index_by_id = {word['id']: word for word in sentence}
            for word in sentence:
                if word['deprel'] not in['punct','root','_']:
                    dd = abs(word['head'] - word['id'])
                    dds.append(dd)
                    depth = 0        
                    head_id = word['head']
                    while head_id != 0:
                        depth += 1
                        head_id = word_index_by_id[head_id]['head']
                    levels.append(depth)
                    k = len([i for i in sentence if i['head'] == word['id'] and i['deprel'] not in ['punct','_']])+1
                    valencies.append(k)
                if word['deprel'] is 'root':
                    k = len([i for i in sentence if i['head'] == word['id'] and i['deprel'] not in ['punct','_']])
                    valencies.append(k)
            sent_length = len(levels)+1
            vk = (sum(i**2 for i in valencies)/sent_length) - (2 - 2/sent_length)**2
            sent_data['mdd'] = round(sum(dds)/len(dds),3)
            sent_data['tdl'] = sum(dds)
            sent_data['mhd'] = round(sum(levels)/len(levels),3)
            sent_data['mhdd'] = len(levels)/max(levels)
            sent_data['dd'] = dds
            sent_data['hd'] = levels
            sent_data['sent_length'] = sent_length
            sent_data['tree_height'] = max(levels)
            sent_data['tree_width'] = levels.count(max(levels, key=levels.count))
            sent_data['vk'] = round(vk,3)
            sents_info.append(sent_data)
        return sents_info
        
def getDepValFeatures(conllu):
    dv = DepValAnalyzer(conllu)
    featuredict = {}
    featuredict['mdd'] = dv.mdd()
    featuredict['mhd'] = dv.mhd()
    featuredict['dd distribution'] = dv.dd_distribution()
    featuredict['hd distribution'] = dv.hd_distribution()
    featuredict['pdd'] = dv.pdd()
    featuredict['tree'] = dv.tree()
    featuredict['tree distribution'] = dv.tree_distribution()
    featuredict['mean valency'] = dv.mean_valency()
    featuredict['valency distribution'] = dv.valency_distribution()
    featuredict['probablistic valency pattern'] = dv.pvp()
    return featuredict