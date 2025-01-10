#!/usr/bin/env python
# coding: utf-8

#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from conllu import parse_incr
from collections import Counter
import os
import time

from collections import Counter,defaultdict
from typing import List, Dict, Optional, Tuple, Any

__all__ = ['DepValAnalyzer','analyze','Converter','convert']

punctdeps = ['punkt','punct','pu','PU','PUN']
rootdeps = ['root','ROOT','s','HED','']
stopdeps = ['punct','punkt','_','PUN','PU','pu']

class DepValAnalyzer:

    def __init__(self, treebank):
        self.raw = list(parse_incr(treebank))
        self.treebank = self.preprocessing()
        self.dep_metrics = ['dd','hd','ddir','v']
        self.sent_metrics = ['mdd','mhd','mhdd','tdl','sl','mv','vk','tw','th','hi','hf']
        self.text_metrics = ['mdd','mhd','mhdd','mtdl','msl','mv','vk','mtw','mth','hi','hf']
        self.distribution_metrics = ['dd','hd','sl','v','tw','th','deprel','pos']
        self.projection = {'mdd':'dd','mhd':'hd','mhdd':'hd','mtdl':'dd','msl':'id','mv':'v','vk':'v',
                           'mtw':'hd','mth':'hd','hi':'ddir','hf':'ddir','pos':'dpos','deprel':'deprel'}

    def preprocessing(self):
        cleaned_treebank = []
        for sentence in self.raw:
            cleaned_sentence = []
            punkt_id = [word['id'] for word in sentence if word['deprel'] in punctdeps]
            clean_id = {word['id']:word['id']-len([i for i in punkt_id if i < word['id']]) for word in sentence if word['deprel'] not in stopdeps}
            for word in sentence:
                if word['deprel'] not in stopdeps:
                    word['id'] = clean_id[word['id']]
                    word['head'] = clean_id.get(word['head'],0)
                    cleaned_sentence.append(word)
            cleaned_treebank.append(cleaned_sentence)
        return cleaned_treebank  

    def _dd(self,word: Dict[str, Any])->int:
        dd = abs(word['head'] - word['id'])
        return dd
     
    def _hd(self,word: Dict[str, Any],word_index_by_id: Dict[int, Dict[str, Any]])->int:
        head_id = word['head']
        hd = 0
        while head_id != 0:
            hd += 1
            if head_id not in word_index_by_id.keys():
                hd = 0
                break
            elif head_id in word_index_by_id.keys():
                head_id = word_index_by_id[head_id]['head']
            if hd > len(word_index_by_id):
                hd = 0
                break
        return hd
    
    def _ddir(self,word: Dict[str, Any])->int:
        if word['head'] < word['id']:
            return 1
        elif word['head'] > word['id']:
            return -1

    def _v(self, word: Dict[str, Any],sent: List[Dict[str, Any]]) -> int:
        v = sum(1 for w in sent if w['head'] == word['id'] and w['deprel'] not in stopdeps) + 1
        if word['head'] == 0:
            v -= 1
        return v

    def calculate_dep_metrics(self, metrics: List[str] = None) -> Dict[str, List]:
        if metrics is None:
            metrics = self.dep_metrics
        metrics = ['id','form','dpos','head','gform','gpos','deprel']+[m for m in metrics if m not in ['id','dpos','head','gpos','deprel']]
        results = {metric: [] for metric in metrics}

        for sent in self.treebank:
            word_index_by_id = {word['id']: word for word in sent if type(word['id']) != tuple } if 'hd' in metrics or 'dd' in metrics else None
            temp_results = {metric: [] for metric in metrics}
            
            for word in sent:
                if word['deprel'] not in rootdeps+stopdeps and word['head'] != 0 and word['upos'] != 'pu':
                    if 'dd' in metrics:
                        temp_results['dd'].append(self._dd(word))  
                    if 'hd' in metrics:
                        temp_results['hd'].append(self._hd(word, word_index_by_id))
                    if 'ddir' in metrics:
                        temp_results['ddir'].append(self._ddir(word)) 
                    if 'v' in metrics:
                        temp_results['v'].append(self._v(word, sent)) 
                    temp_results['id'].append(word['id'])
                    temp_results['form'].append(word['form'])
                    temp_results['dpos'].append(word['upos'])
                    temp_results['head'].append(word['head'])
                    try:
                        temp_results['gform'].append(sent[word['head']-1]['form'])
                    except:
                        temp_results['gform'].append('ERROR_ANNOTATION')
                    try:
                        temp_results['gpos'].append(sent[word['head']-1]['upos'])
                    except:
                        temp_results['gpos'].append('ERROR_ANNOTATION')
                    temp_results['deprel'].append(word['deprel'])
                elif word['head'] == 0 and word['upos'] not in stopdeps:
                    if 'dd' in metrics:
                        temp_results['dd'].append(0)  
                    if 'hd' in metrics:
                        temp_results['hd'].append(0)
                    if 'ddir' in metrics:
                        temp_results['ddir'].append(0) 
                    if 'v' in metrics:
                        temp_results['v'].append(self._v(word, sent)) 
                    temp_results['id'].append(word['id'])
                    temp_results['form'].append(word['form'])
                    temp_results['dpos'].append(word['upos'])
                    temp_results['head'].append(word['head'])
                    temp_results['gform'].append('ROOT')
                    temp_results['gpos'].append('ROOT')
                    temp_results['deprel'].append(word['deprel'])

            for metric in results:
                results[metric].append(temp_results[metric])

        return results
    
    def calculate_sent_metrics(self, metrics: List[str] = None) -> Dict[str, List]:
        if metrics is None:
            metrics = self.sent_metrics
        
        dep_metrics = list(set([self.projection[metric] for metric in metrics if metric in self.projection]))
        dep_data = self.calculate_dep_metrics(dep_metrics)
        sent_data = {metric: [] for metric in metrics}

        metric_functions = {
            'mdd': lambda: [sum(i for i in j if i > 0) / max(1, len(j) - 1) for j in dep_data['dd']],
            'mhd': lambda: [sum(i for i in j if i > 0) / max(1, len(j) - 1) for j in dep_data['hd']],
            'mhdd': lambda: [(len(j)-1) / (max(j)+1) for j in dep_data['hd']],
            'tdl': lambda: [sum(j) for j in dep_data['dd']],
            'sl': lambda: [len(j) for j in dep_data['id']],
            'mv': lambda: [sum(j) / len(j) for j in dep_data['v']],
            'vk': lambda: [sum(k ** 2 for k in j) / (len(j)) - (2 - 2 / len(j)) ** 2 for j in dep_data['v']],
            'tw': lambda: [j.count(max(j, key=j.count)) for j in dep_data['hd']],
            'th': lambda: [max(j)+1 for j in dep_data['hd']],
            'hi': lambda: [j.count(1) for j in dep_data['ddir']],
            'hf': lambda: [j.count(-1) for j in dep_data['ddir']],
        }

        for metric in metrics:
            if metric in metric_functions:
                sent_data[metric] = metric_functions[metric]()

        return sent_data

    
    def calculate_text_metrics(self, metrics: List[str] = None) -> Dict[str, List]:
        if metrics is None:
            metrics = self.text_metrics

        dep_metrics = list(set([self.projection[metric] for metric in metrics if metric in self.projection]))
        dep_data = self.calculate_dep_metrics(dep_metrics)
        
        text_data = {}
        
        metric_calculators = {
            'mdd': lambda: sum(sum(dep_data['dd'], [])) / max(1,(len(sum(dep_data['dd'], []))-len(dep_data['dd']))),
            'mhd': lambda: sum(sum(dep_data['hd'], [])) / max(1,(len(sum(dep_data['hd'], []))-len(dep_data['hd']))),
            'mhdd': lambda: sum((len(j)-1) / (max(j)+1) for j in dep_data['hd']) / len(dep_data['hd']),
            'mtdl': lambda: sum(sum(j) for j in dep_data['dd']) / len(dep_data['dd']),
            'msl': lambda: sum(len(j) for j in dep_data['dd']) / len(dep_data['dd']),
            'mv': lambda: sum(sum(dep_data['v'], [])) / len(sum(dep_data['v'], [])),
            'vk': lambda: sum(
                sum(k ** 2 for k in j) / (len(j)) - (2 - 2 / len(j)) ** 2 for j in dep_data['v']
            ) / len(dep_data['v']),
            'mtw': lambda: sum(j.count(max(j, key=j.count)) for j in dep_data['hd']) / len(dep_data['hd']),
            'mth': lambda: sum(max(j)+1 for j in dep_data['hd']) / len(dep_data['hd']),
            'hi': lambda: sum(j.count(1) for j in dep_data['ddir']) / max(1,(len(sum(dep_data['ddir'], []))-len(dep_data['ddir']))),
            'hf': lambda: sum(j.count(-1) for j in dep_data['ddir']) / max(1,(len(sum(dep_data['ddir'], []))-len(dep_data['ddir']))),
        }
    
        for metric in metrics:
            if metric in metric_calculators:
                text_data[metric] = metric_calculators[metric]()

        return text_data


    def calculate_distributions(self, metrics: List[str] = None, normalize: bool = False) -> Dict[str, Tuple[List, List]]:
        if metrics is None:
            metrics = self.distribution_metrics

        dep_metrics = list(set(self.projection.get(metric, metric) for metric in metrics))
        dep_data = self.calculate_dep_metrics(dep_metrics)

        distributions = {}
        metric_functions = {
            'sl': lambda: [len(j) for j in dep_data['id']],
            'tw': lambda: [j.count(max(j, key=j.count)) for j in dep_data['hd']],
            'th': lambda: [max(j)+1 for j in dep_data['hd']]
        }

        def normalize_data(data):
            return [i[1] / sum(j[1] for j in data) for i in data] if normalize else [i[1] for i in data]

        for metric in metrics:
            if metric not in ['deprel', 'pos']:
                data = sorted(Counter(sum(dep_data[metric], [])).items())
                data = [i for i in data if i[0] > 0]
                x = [i[0] for i in data]
                y = normalize_data(data)
                distributions[metric] = (x, y)

            elif metric in ['deprel', 'pos']:
                data = sorted(Counter(sum(dep_data[self.projection.get(metric, metric)], [])).items(),key=lambda x: x[1], reverse=True)
                y = normalize_data(data)
                distributions[metric] = (range(1, len(y) + 1), y)

            if metric in metric_functions:
                data = sorted(Counter(metric_functions[metric]()).items())
                x = [i[0] for i in data]
                y = normalize_data(data)
                distributions[metric] = (x, y)

        return distributions


    def calculate_pvp(self, input: Optional[str] = None, target:str='deprel',normalize:bool=True):

        dependents = defaultdict(int)
        governors = defaultdict(int)

        def process_word(word, sentence):
            if target == 'deprel':
                dependent = [w['deprel'] for w in sentence if w['head'] == word['id'] and w['deprel'] not in stopdeps]
                for dep in dependent:
                    dependents[dep] += 1
                governors[word['deprel']] += 1

            if target == 'pos':
                dependent = [w['upos'] for w in sentence if w['head'] == word['id'] and w['deprel'] not in stopdeps]
                for dep in dependent:
                    dependents[dep] += 1
                governor = [w['upos'] for w in sentence if w['id'] == word['head'] and w['deprel'] not in stopdeps]
                for gov in governor:
                    governors[gov] += 1

        for sentence in self.treebank:
            for word in sentence:
                if word['deprel'] not in stopdeps and (input is None or word['upos'] == input):
                    process_word(word, sentence)

        total_deps = sum(dependents.values())
        total_govs = sum(governors.values())
        if normalize:
            govs = sorted(((k, v / total_govs) for k, v in governors.items()), key=lambda x: x[1], reverse=True)
            deps = sorted(((k, v / total_deps) for k, v in dependents.items()), key=lambda x: x[1], reverse=True)
        else:
            govs = sorted(governors.items(), key=lambda x: x[1], reverse=True)
            deps = sorted(dependents.items(), key=lambda x: x[1], reverse=True)
        return {'act as a gov': deps, 'act as a dep': govs}
    
def _pvp2df(pvp):
    df = pd.DataFrame()
    gov = dict(pvp['act as a gov'])
    dep = dict(pvp['act as a dep'])
    df['Items'] = sorted(list(set(gov.keys()).union(set(dep.keys()))))  
    df['act as a gov'] = [gov.get(d,0) for d in df['Items']]
    df['act as a dep'] = [dep.get(d,0) for d in df['Items']]
    return df

def getDepValFeatures(treebank:list,normalize:bool=True):
    treebank = DepValAnalyzer(treebank)
    text_data = treebank.calculate_text_metrics()
            
    dep_data = treebank.calculate_dep_metrics()
    dep_data = {x:sum(y,[]) for x,y in dep_data.items()}
    dep_data = pd.DataFrame(dep_data)

    sent_data = treebank.calculate_sent_metrics()
    sent_data = pd.DataFrame(sent_data)  

    pvp_data = treebank.calculate_pvp()
    pvp_data = _pvp2df(pvp_data)  

    distribution_dict = {}
    distributions = treebank.calculate_distributions(normalize=normalize)
    for m in ['dd','hd','sl','v','tw','th','deprel','pos']:
        data = pd.DataFrame(distributions[m]).T
        distribution_dict[m] = data
    
    return text_data,dep_data,sent_data,pvp_data,distribution_dict

def analyze(treebank_path:str,out_path:str,normalize:bool=True):

    if not os.path.splitext(out_path)[1]:
        os.makedirs(out_path,exist_ok=True)
    else:
        raise ValueError(f" The output path {out_path} is not a valid directory. It should be a directory. ")

    if os.path.isdir(treebank_path):
        treebanks = [os.path.join(treebank_path, i) for i in os.listdir(treebank_path) if i.endswith('.conllu')]
        text_csv = pd.DataFrame(columns=['mdd','mhd','mhdd','mtdl','msl','mv','vk','mtw','mth','hi','hf'])
        file_names = [os.path.basename(t).split('.')[0] for t in treebanks]
        files = [os.path.join(out_path, f) for f in file_names]
        for i,t in enumerate(treebanks):      
            os.makedirs(files[i],exist_ok=True)     
            treebank = open(t, encoding='utf-8')
            text_metrics,dep_metrics,sent_metrics,pvp_metrics,distribution_dict = getDepValFeatures(treebank)
                    
            text_csv.loc[i,:] = text_metrics   
            dep_metrics.round(2).to_csv(os.path.join(files[i],f'dep_metrics.csv'),index=False)   
            sent_metrics.round(2).to_csv(os.path.join(files[i],f'sent_metrics.csv'),index=False)   
            pvp_metrics.round(4).to_csv(os.path.join(files[i],f'pvp.csv'),index=False)    

            for m in distribution_dict:
                distribution_dict[m].to_csv(os.path.join(files[i],f'{m}_distribution.csv'),index=False,header=False) 
        
        text_csv = text_csv.astype(float).round(2)
        text_csv['treebank'] = file_names
        text_csv.to_csv(os.path.join(out_path, f'text_metrics.csv'), index=False)

class Converter:
     
    def __init__(self, treebank):
        self.treebank = treebank

    def to_conllu(self,style:str):

        if style == 'pmt':
            treebank = self.treebank.read()
            sents = treebank.strip().split('\n\n')
            conllu_sents = []
            for sent in sents:
                columns = [[i for i in line.split('\t') if i!=''] for line in sent.split('\n') if line]

                structured_sent = [
                    {
                        'id': i + 1,
                        'form': columns[0][i],
                        'lemma': '_',
                        'upos': columns[1][i],
                        'xpos': '_',
                        'feats': '_',
                        'head': columns[3][i],
                        'deprel': columns[2][i],
                        'deps': '_',
                        'misc': '_'
                    }
                    for i in range(len(columns[0])) if columns[3][i] != '_'
                ]
                
                conllu_sents.append(structured_sent)
            return conllu_sents
        
        elif style == 'conll':
            sents = parse_incr(self.treebank)
            conllu_sents = [[{**w, 'deps': '_','misc': '_'} for w in s] for s in sents]
            return conllu_sents
        
        elif style == 'mcdt':
            treebank = pd.read_csv(self.treebank, delimiter='\t')
            treebank = treebank.dropna(subset=[treebank.columns[4]])

            def senter(df: pd.DataFrame):
                index_slices = []
                current_indices = []

                for i in range(len(df)):
                    
                    if not current_indices or df.iloc[i, 1] > df.iloc[current_indices[-1], 1]:
                        current_indices.append(i)
                    else:
                        index_slices.append(current_indices.copy())
                        current_indices = [i]

                if current_indices:
                    index_slices.append(current_indices)
                
                return index_slices
            
            sent_ids = senter(treebank)
            conllu_sents = [
                [
                    {
                        'id': int(treebank.iloc[i, 1]),
                        'form': treebank.iloc[i, 2],
                        'lemma': '_',
                        'upos': treebank.iloc[i, 3],
                        'xpos': '_',
                        'feats': '_',
                        'head':  0 if treebank.iloc[i, 7] == 's' else int(treebank.iloc[i, 4]),
                        'deprel': treebank.iloc[i, 7],
                        'deps': '_',
                        'misc': '_'
                    }
                    for i in s
                ]
                for s in sent_ids]

            return conllu_sents
    
    def to_others(self,style:str,cache=None):
        if cache is None:
            sents = parse_incr(self.treebank)
        else:
            sents = cache
        if style == 'conll':
            conll_sents = [[{k: v for k, v in w.items() if k not in ['deps','misc']} for w in s] for s in sents]
            return conll_sents
        
        elif style == 'pmt':
            pmt_sents = [[
                [w['form'] for w in s],
                [w['upos'] for w in s],
                [w['deprel'] for w in s],
                [w['head'] for w in s]
            ] for s in sents]
            return pmt_sents
        
        elif style == 'mcdt':
            mcdt_sents = pd.DataFrame(columns=['sent','id','form', 'pos', 'head', 'gform','gpos','deprel'])
            sent_id = 0
            for s in sents:
                sent_id += 1
                for w in s:
                    if w['head'] != '_' and w['head'] is not None:
                        mcdt_sents.loc[len(mcdt_sents)] = [sent_id, w['id'], w['form'], w['upos'], w['head'], s[int(w['head'])-1]['form'], s[int(w['head'])-1]['upos'], w['deprel']]
            return mcdt_sents.to_csv(sep='\t', index=False).replace('\r','')
        
    def style2style(self,style_from:str,style_to:str):
        if style_from == style_to:
            raise ValueError(f"The input and output styles should be different. Got {style_from} and {style_to}.")
        elif style_from == 'conllu' and style_to != 'conllu':
            treebank = self.to_others(style_to)
        elif style_from != 'conllu' and style_to == 'conllu':
            treebank = self.to_conllu(style_from)
        elif style_from != 'conllu' and style_to != 'conllu':
            cache = self.to_conllu(style_from)
            treebank = self.to_others(style_to,cache=cache)
        return treebank
    
    def save(self,treebank,style:str,file_path:str):
        def format_feats(feats):
            if feats and feats != '_':
                return '|'.join(f"{k}={v}" for k, v in feats.items())
            return '_'
        
        if style == 'conllu':
            with open(file_path, 'w', encoding='utf-8') as f:
                for s in treebank:
                    for w in s:
                        if isinstance(w['id'], int) or isinstance(w['id'], str): 
                            f.write(f"{w['id']}\t{w['form']}\t{w['lemma']}\t{w['upos']}\t{w['xpos']}\t{format_feats(w['feats'])}\t{w['head']}\t{w['deprel']}\t{w['deps']}\t{w['misc']}\n")
                        elif isinstance(w['id'], tuple) :
                            f.write(f"{w['id'][0]}{w['id'][1]}{w['id'][2]}\t{w['form']}\t_\t_\t_\t_\t_\t_\t_\t_\n")
                    f.write('\n')
        elif style == 'pmt':
            with open(file_path, 'w', encoding='utf-8') as f:
                for s in treebank:
                    f.write('\t'.join(s[0]) + '\n')
                    f.write('\t'.join(s[1]) + '\n')
                    f.write('\t'.join(s[2]) + '\n')
                    f.write('\t'.join(map(lambda x: str(x) if x is not None else '_', s[3])))
                    f.write('\n\n')
        elif style == 'conll':
            with open(file_path, 'w', encoding='utf-8') as f:
                for s in treebank:
                    for w in s:
                        if isinstance(w['id'], int) or isinstance(w['id'], str): 
                            f.write(f"{w['id']}\t{w['form']}\t{w['lemma']}\t{w['upos']}\t{w['xpos']}\t{format_feats(w['feats'])}\t{w['head']}\t{w['deprel']}\n")
                        elif isinstance(w['id'], tuple):
                            f.write(f"{w['id'][0]}{w['id'][1]}{w['id'][2]}\t{w['form']}\t_\t_\t_\t_\t_\t_\n")
                    f.write('\n')
        elif style == 'mcdt':
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(treebank)
        else:
            raise ValueError(f"Invalid style {style}.")

def convert(treebank_path:str,out_path:str,style_from:str,style_to:str):

    if not os.path.splitext(out_path)[1]:
        os.makedirs(out_path,exist_ok=True)
    else:    
        raise ValueError(f" The output path {out_path} is not a valid directory. It should be a directory. ")
    
    if os.path.isdir(treebank_path):
            treebanks = [os.path.join(treebank_path, i) for i in os.listdir(treebank_path)]
            file_names = [os.path.basename(t).split('.')[0] for t in treebanks]
            for i,t in enumerate(treebanks):
                treebank = open(t, encoding='utf-8')
                converter = Converter(treebank)
                converted_treebank = converter.style2style(style_from,style_to)
                converter.save(converted_treebank,style_to,os.path.join(out_path,f'{file_names[i]}.txt'))
    else:
        raise ValueError(f"The input path {treebank_path} is not a valid directory. It should be a directory containing treebank files.")