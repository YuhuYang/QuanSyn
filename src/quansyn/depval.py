#!/usr/bin/env python
# coding: utf-8

import io
import os
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from conllu import parse, parse_incr

__all__ = ['DepValAnalyzer','analyze','Converter','convert']

punctdeps = ['punkt','punct','pu','PU','PUN','WP','wp']
rootdeps = ['root','ROOT','s','HED','']
stopdeps = ['punct','punkt','_','PUN','PU','pu','wp','WP']

def _flatten(values: List[List[Any]]) -> List[Any]:
    return [item for sub in values for item in sub]


def _safe_root_distance(dd_values: List[int]) -> int:
    try:
        return dd_values.index(0) + 1
    except ValueError:
        return 0


def _safe_twig(hd_values: List[int]) -> int:
    if not hd_values:
        return 0
    mode_value = Counter(hd_values).most_common(1)[0][0]
    return mode_value + 1


def _compute_hd(word_id: int, head_map: Dict[int, int], cache: Dict[int, int]) -> int:
    if word_id in cache:
        return cache[word_id]
    current = word_id
    depth = 0
    in_path = set()
    size = max(1, len(head_map))
    while True:
        if current in in_path:
            depth = 0
            break
        in_path.add(current)
        head = head_map.get(current)
        if head is None:
            depth = 0
            break
        if head == 0:
            break
        depth += 1
        if depth > size:
            depth = 0
            break
        if head in cache:
            depth += cache[head]
            break
        current = head
    cache[word_id] = depth
    return depth


def _compute_sentence_dep(payload: Tuple[List[Dict[str, Any]], Tuple[str, ...], Tuple[str, ...], Tuple[str, ...]]) -> Dict[str, List[Any]]:
    sentence, metrics, stop_deprels, root_deprels = payload
    metric_set = set(metrics)
    result: Dict[str, List[Any]] = {metric: [] for metric in metrics}

    valid_words = [
        word for word in sentence
        if isinstance(word.get('id'), int) and word.get('deprel') not in stop_deprels
    ]
    word_index_by_id = {word['id']: word for word in valid_words}
    head_map = {word['id']: int(word.get('head', 0) or 0) for word in valid_words}
    hd_cache: Dict[int, int] = {}
    child_counts = Counter(
        int(word.get('head', 0) or 0)
        for word in valid_words
        if isinstance(word.get('head'), int)
    )

    for word in valid_words:
        wid = word['id']
        head = int(word.get('head', 0) or 0)
        deprel = word.get('deprel')
        upos = word.get('upos')

        is_root = head == 0
        include_non_root = (
            not is_root
            and deprel not in root_deprels
            and upos != 'pu'
        )
        include_root = is_root
        if not (include_non_root or include_root):
            continue

        if 'id' in metric_set:
            result['id'].append(wid)
        if 'form' in metric_set:
            result['form'].append(word.get('form'))
        if 'dpos' in metric_set:
            result['dpos'].append(upos)
        if 'head' in metric_set:
            result['head'].append(head)
        if 'deprel' in metric_set:
            result['deprel'].append(deprel)

        if 'gform' in metric_set:
            if is_root:
                result['gform'].append('ROOT')
            else:
                head_word = word_index_by_id.get(head)
                result['gform'].append(head_word.get('form') if head_word else 'ERROR_ANNOTATION')
        if 'gpos' in metric_set:
            if is_root:
                result['gpos'].append('ROOT')
            else:
                head_word = word_index_by_id.get(head)
                result['gpos'].append(head_word.get('upos') if head_word else 'ERROR_ANNOTATION')

        if 'dd' in metric_set:
            result['dd'].append(0 if is_root else abs(head - wid))
        if 'hd' in metric_set:
            result['hd'].append(0 if is_root else _compute_hd(wid, head_map, hd_cache))
        if 'ddir' in metric_set:
            if is_root:
                result['ddir'].append(0)
            else:
                result['ddir'].append(1 if head < wid else -1)
        if 'v' in metric_set:
            result['v'].append(child_counts.get(wid, 0) if is_root else child_counts.get(wid, 0) + 1)

    return result


def _compute_sentence_pvp(
    payload: Tuple[List[Dict[str, Any]], Optional[str], str, Tuple[str, ...]]
) -> Tuple[Dict[str, int], Dict[str, int]]:
    sentence, input_upos, target, stop_deprels = payload

    valid_words = [
        word for word in sentence
        if isinstance(word.get('id'), int) and word.get('deprel') not in stop_deprels
    ]
    by_id = {word['id']: word for word in valid_words}
    children = defaultdict(list)
    for word in valid_words:
        head = word.get('head', 0)
        if isinstance(head, int):
            children[head].append(word)

    dependents = Counter()
    governors = Counter()
    for word in valid_words:
        if input_upos is not None and word.get('upos') != input_upos:
            continue
        wid = word['id']
        if target == 'deprel':
            for dep in children.get(wid, []):
                dependents[dep.get('deprel')] += 1
            governors[word.get('deprel')] += 1
        elif target == 'pos':
            for dep in children.get(wid, []):
                dependents[dep.get('upos')] += 1
            gov = by_id.get(word.get('head'))
            if gov is not None:
                governors[gov.get('upos')] += 1

    return dict(dependents), dict(governors)


def _calculate_pvp_from_dep_data(
    dep_data: Dict[str, List[List[Any]]],
    input_upos: Optional[str] = None,
    target: str = 'deprel',
    normalize: bool = True
) -> Dict[str, List[Tuple[Any, float]]]:
    dependents = Counter()
    governors = Counter()

    sent_count = len(dep_data.get('id', []))
    for sidx in range(sent_count):
        ids = dep_data['id'][sidx]
        heads = dep_data['head'][sidx]
        dpos = dep_data['dpos'][sidx]
        deprels = dep_data['deprel'][sidx]
        idx_by_id = {wid: i for i, wid in enumerate(ids)}
        children = defaultdict(list)
        for i, head in enumerate(heads):
            children[head].append(i)

        for i, wid in enumerate(ids):
            if input_upos is not None and dpos[i] != input_upos:
                continue

            if target == 'deprel':
                for child_i in children.get(wid, []):
                    dependents[deprels[child_i]] += 1
                governors[deprels[i]] += 1
            elif target == 'pos':
                for child_i in children.get(wid, []):
                    dependents[dpos[child_i]] += 1
                h = heads[i]
                hidx = idx_by_id.get(h)
                if hidx is not None:
                    governors[dpos[hidx]] += 1

    total_deps = sum(dependents.values())
    total_govs = sum(governors.values())
    if normalize:
        govs = sorted(
            ((k, (v / total_govs) if total_govs else 0) for k, v in governors.items()),
            key=lambda x: x[1],
            reverse=True
        )
        deps = sorted(
            ((k, (v / total_deps) if total_deps else 0) for k, v in dependents.items()),
            key=lambda x: x[1],
            reverse=True
        )
    else:
        govs = sorted(governors.items(), key=lambda x: x[1], reverse=True)
        deps = sorted(dependents.items(), key=lambda x: x[1], reverse=True)
    return {'act as a gov': govs, 'act as a dep': deps}


def _pvp_by_upos2df(analyzer: 'DepValAnalyzer', upos_values: List[str], normalize: bool = True) -> pd.DataFrame:
    frames = []
    for upos in upos_values:
        pvp = analyzer.calculate_pvp(input=upos, target='deprel', normalize=normalize)
        frame = _pvp2df(pvp)
        frame.insert(0, 'upos', upos)
        frames.append(frame)

    if not frames:
        return pd.DataFrame(columns=['upos', 'Items', 'act as a gov', 'act as a dep'])
    return pd.concat(frames, ignore_index=True)


def _analyze_single_file_worker(task: Dict[str, Any]) -> Tuple[int, str, Dict[str, float]]:
    with open(task['treebank_path'], encoding='utf-8') as treebank:
        analyzer = DepValAnalyzer(
            treebank,
            punct_deprels=task['punct_deprels'],
            root_deprels=task['root_deprels']
        )
        text_metrics, dep_metrics, sent_metrics, _, distribution_dict = analyzer._compute_feature_bundle(
            normalize=task['normalize'],
        )
        upos_values = sorted(
            x for x in dep_metrics.get('dpos', pd.Series(dtype=object)).dropna().unique().tolist()
            if isinstance(x, str) and x
        )
        pvp_metrics = _pvp_by_upos2df(analyzer, upos_values, normalize=task['normalize'])

    os.makedirs(task['out_dir'], exist_ok=True)
    dep_metrics.round(2).to_csv(os.path.join(task['out_dir'], 'dep_metrics.csv'), index=False)
    sent_metrics.round(2).to_csv(os.path.join(task['out_dir'], 'sent_metrics.csv'), index=False)
    pvp_metrics.round(4).to_csv(os.path.join(task['out_dir'], 'pvp.csv'), index=False)
    for metric_name, metric_df in distribution_dict.items():
        metric_df.to_csv(os.path.join(task['out_dir'], f'{metric_name}_distribution.csv'), index=False, header=False)

    return task['index'], task['file_name'], text_metrics

def _analyze_single_file_serial(
    treebank_path: str,
    out_dir: str,
    normalize: bool,
    punct_deprels: Optional[List[str]],
    root_deprels: Optional[List[str]]
) -> Dict[str, float]:
    task = {
        'index': 0,
        'treebank_path': treebank_path,
        'file_name': os.path.basename(treebank_path).split('.')[0],
        'out_dir': out_dir,
        'normalize': normalize,
        'punct_deprels': punct_deprels,
        'root_deprels': root_deprels,
    }
    _, _, text_metrics = _analyze_single_file_worker(task)
    return text_metrics


class DepValAnalyzer:

    def __init__(
        self,
        treebank,
        cleaned: bool = False,
        punct_deprels: Optional[List[str]] = None,
        root_deprels: Optional[List[str]] = None
    ):
        if type(treebank) is io.TextIOWrapper:
            self.raw = list(parse_incr(treebank))
        elif type(treebank) is list:
            self.raw = treebank
        elif type(treebank) is str:
            self.raw = parse(treebank)
        else:
            raise TypeError("treebank must be a text stream, list, or conllu string")
        self.punct_deprels = tuple(punct_deprels) if punct_deprels is not None else tuple(punctdeps)
        self.root_deprels = tuple(root_deprels) if root_deprels is not None else tuple(rootdeps)
        self.stop_deprels = tuple(set(self.punct_deprels).union({'_'}))
        if cleaned:
            self.treebank = treebank
        else:
            self.treebank = self.preprocessing()
        self.dep_metrics = ['dd','hd','ddir','v']
        self.sent_metrics = ['mdd','ndd','mhd','mhdd','tdl','sl','mv','vk','tw','th','hi','hf','rd']
        self.text_metrics = ['mdd','ndd','mhd','mhdd','mtdl','msl','mv','vk','mtw','mth','hi','hf','mrd']
        self.distribution_metrics = ['dd','hd','sl','v','tw','th','rd','deprel','pos']
        self.projection = {'mdd':'dd','mhd':'hd','mhdd':'hd','mtdl':'dd','msl':'id','mv':'v','vk':'v',
                           'mtw':'hd','mth':'hd','hi':'ddir','hf':'ddir','pos':'dpos','deprel':'deprel',
                           'rd':'dd','mrd':'dd','ndd':'dd','tw':'hd','th':'hd'}
        self._cache_dep: Dict[Tuple[Any, ...], Dict[str, List]] = {}
        self._cache_sent: Dict[Tuple[Any, ...], Dict[str, List]] = {}
        self._cache_text: Dict[Tuple[Any, ...], Dict[str, float]] = {}
        self._cache_dist: Dict[Tuple[Any, ...], Dict[str, Tuple[List, List]]] = {}
        self._cache_pvp: Dict[Tuple[Any, ...], Dict[str, List[Tuple[Any, float]]]] = {}

    def preprocessing(self):
        cleaned_treebank = []
        for sentence in self.raw:
            cleaned_sentence = []
            clean_id: Dict[int, int] = {}
            next_id = 1
            for word in sentence:
                wid = word.get('id')
                if isinstance(wid, int) and word.get('deprel') not in self.stop_deprels:
                    clean_id[wid] = next_id
                    next_id += 1
            for word in sentence:
                wid = word.get('id')
                if not isinstance(wid, int) or word.get('deprel') in self.stop_deprels:
                    continue
                new_word = dict(word)
                new_word['id'] = clean_id[wid]
                new_word['head'] = clean_id.get(word.get('head'), 0)
                cleaned_sentence.append(new_word)
            if len(cleaned_sentence) > 2:
                cleaned_treebank.append(cleaned_sentence)
        return cleaned_treebank  

    def _map_sentence_dep(self, metrics: List[str]) -> List[Dict[str, List[Any]]]:
        payloads = [(sent, tuple(metrics), self.stop_deprels, self.root_deprels) for sent in self.treebank]
        return [_compute_sentence_dep(payload) for payload in payloads]

    def _calculate_sent_metrics_from_dep(self, dep_data: Dict[str, List], metrics: List[str]) -> Dict[str, List]:
        sent_data = {metric: [] for metric in metrics}
        for metric in metrics:
            if metric == 'mdd':
                sent_data[metric] = [sum(i for i in j if i > 0) / max(1, len(j) - 1) for j in dep_data['dd']]
            elif metric == 'mhd':
                sent_data[metric] = [sum(i for i in j if i > 0) / max(1, len(j) - 1) for j in dep_data['hd']]
            elif metric == 'mhdd':
                sent_data[metric] = [(len(j) - 1) / (max(j) + 1) if j else 0 for j in dep_data['hd']]
            elif metric == 'tdl':
                sent_data[metric] = [sum(j) for j in dep_data['dd']]
            elif metric == 'sl':
                sent_data[metric] = [len(j) for j in dep_data['id']]
            elif metric == 'mv':
                sent_data[metric] = [sum(j) / max(1, len(j)) for j in dep_data['v']]
            elif metric == 'vk':
                sent_data[metric] = [float(np.var(j)) for j in dep_data['v']]
            elif metric == 'tw':
                sent_data[metric] = [_safe_twig(j) for j in dep_data['hd']]
            elif metric == 'th':
                sent_data[metric] = [max(j) + 1 if j else 0 for j in dep_data['hd']]
            elif metric == 'hi':
                sent_data[metric] = [j.count(1) for j in dep_data['ddir']]
            elif metric == 'hf':
                sent_data[metric] = [j.count(-1) for j in dep_data['ddir']]
            elif metric == 'rd':
                sent_data[metric] = [_safe_root_distance(j) for j in dep_data['dd']]
            elif metric == 'ndd':
                values = []
                for j in dep_data['dd']:
                    mdd = sum(i for i in j if i > 0) / max(1, len(j) - 1)
                    rd = _safe_root_distance(j)
                    denom = np.sqrt(max(1, rd) * max(1, len(j)))
                    values.append(abs(np.log(max(mdd, 1e-12) / max(denom, 1e-12))))
                sent_data[metric] = values
        return sent_data

    def _calculate_text_metrics_from_dep(self, dep_data: Dict[str, List], metrics: List[str]) -> Dict[str, float]:
        text_data: Dict[str, float] = {}
        flat_dd = _flatten(dep_data.get('dd', []))
        flat_hd = _flatten(dep_data.get('hd', []))
        flat_v = _flatten(dep_data.get('v', []))
        flat_ddir = _flatten(dep_data.get('ddir', []))
        n_sent = max(1, len(dep_data.get('dd', [])))

        for metric in metrics:
            if metric == 'mdd':
                text_data[metric] = sum(flat_dd) / max(1, len(flat_dd) - len(dep_data['dd']))
            elif metric == 'mhd':
                text_data[metric] = sum(flat_hd) / max(1, len(flat_hd) - len(dep_data['hd']))
            elif metric == 'mhdd':
                text_data[metric] = sum((len(j) - 1) / (max(j) + 1) if j else 0 for j in dep_data['hd']) / n_sent
            elif metric == 'mtdl':
                text_data[metric] = sum(sum(j) for j in dep_data['dd']) / n_sent
            elif metric == 'msl':
                text_data[metric] = sum(len(j) for j in dep_data['dd']) / n_sent
            elif metric == 'mv':
                text_data[metric] = sum(flat_v) / max(1, len(flat_v))
            elif metric == 'vk':
                text_data[metric] = sum(float(np.var(j)) for j in dep_data['v']) / max(1, len(dep_data['v']))
            elif metric == 'mtw':
                text_data[metric] = sum(_safe_twig(j) for j in dep_data['hd']) / max(1, len(dep_data['hd']))
            elif metric == 'mth':
                text_data[metric] = sum((max(j) + 1) if j else 0 for j in dep_data['hd']) / max(1, len(dep_data['hd']))
            elif metric == 'hi':
                text_data[metric] = sum(j.count(1) for j in dep_data['ddir']) / max(1, len(flat_ddir) - len(dep_data['ddir']))
            elif metric == 'hf':
                text_data[metric] = sum(j.count(-1) for j in dep_data['ddir']) / max(1, len(flat_ddir) - len(dep_data['ddir']))
            elif metric == 'mrd':
                text_data[metric] = sum(_safe_root_distance(j) for j in dep_data['dd']) / n_sent
            elif metric == 'ndd':
                sent_ndd = self._calculate_sent_metrics_from_dep(dep_data, ['ndd'])['ndd']
                text_data[metric] = sum(sent_ndd) / max(1, len(sent_ndd))
        return text_data

    def _calculate_distributions_from_dep(
        self,
        dep_data: Dict[str, List],
        metrics: List[str],
        normalize: bool
    ) -> Dict[str, Tuple[List, List]]:
        distributions: Dict[str, Tuple[List, List]] = {}

        def normalize_data(data_items):
            if not normalize:
                return [i[1] for i in data_items]
            total = sum(i[1] for i in data_items)
            if total == 0:
                return [0 for _ in data_items]
            return [i[1] / total for i in data_items]

        metric_functions = {
            'sl': lambda: [len(j) for j in dep_data['id']],
            'tw': lambda: [_safe_twig(j) for j in dep_data['hd']],
            'th': lambda: [(max(j) + 1) if j else 0 for j in dep_data['hd']],
            'rd': lambda: [_safe_root_distance(j) for j in dep_data['dd']],
        }

        for metric in metrics:
            if metric in metric_functions:
                data = sorted(Counter(metric_functions[metric]()).items())
                x = [i[0] for i in data]
                y = normalize_data(data)
                distributions[metric] = (x, y)
                continue

            if metric in ['deprel', 'pos']:
                source_metric = self.projection.get(metric, metric)
                data = sorted(
                    Counter(_flatten(dep_data.get(source_metric, []))).items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                x = [i[0] for i in data]
                y = normalize_data(data)
                distributions[metric] = (x, y)
                continue

            flattened = _flatten(dep_data.get(metric, []))
            data = sorted(Counter(flattened).items())
            data = [i for i in data if i[0] > 0]
            x = [i[0] for i in data]
            y = normalize_data(data)
            distributions[metric] = (x, y)

        return distributions

    def calculate_dep_metrics(
        self,
        metrics: List[str] = None
    ) -> Dict[str, List]:
        if metrics is None:
            metrics = self.dep_metrics
        base_metrics = ['id', 'form', 'dpos', 'head', 'gform', 'gpos', 'deprel']
        metrics = base_metrics + [m for m in metrics if m not in base_metrics]
        pkey = (False, 1)
        cache_key = (tuple(metrics), pkey)
        if cache_key in self._cache_dep:
            return self._cache_dep[cache_key]
        sentence_results = self._map_sentence_dep(metrics)
        dep_data = {metric: [sent[metric] for sent in sentence_results] for metric in metrics}
        self._cache_dep[cache_key] = dep_data
        return dep_data
    
    def calculate_sent_metrics(
        self,
        metrics: List[str] = None
    ) -> Dict[str, List]:
        if metrics is None:
            metrics = self.sent_metrics
        pkey = (False, 1)
        cache_key = (tuple(metrics), pkey)
        if cache_key in self._cache_sent:
            return self._cache_sent[cache_key]
        dep_metrics = list(set([self.projection[metric] for metric in metrics if metric in self.projection]))
        dep_data = self.calculate_dep_metrics(dep_metrics)
        sent_data = self._calculate_sent_metrics_from_dep(dep_data, metrics)
        self._cache_sent[cache_key] = sent_data
        return sent_data

    
    def calculate_text_metrics(
        self,
        metrics: List[str] = None
    ) -> Dict[str, float]:
        if metrics is None:
            metrics = self.text_metrics
        pkey = (False, 1)
        cache_key = (tuple(metrics), pkey)
        if cache_key in self._cache_text:
            return self._cache_text[cache_key]
        dep_metrics = list(set([self.projection[metric] for metric in metrics if metric in self.projection]))
        dep_data = self.calculate_dep_metrics(dep_metrics)
        text_data = self._calculate_text_metrics_from_dep(dep_data, metrics)
        self._cache_text[cache_key] = text_data
        return text_data

    def calculate_distributions(
        self,
        metrics: List[str] = None,
        normalize: bool = False
    ) -> Dict[str, Tuple[List, List]]:
        if metrics is None:
            metrics = self.distribution_metrics
        pkey = (False, 1)
        cache_key = (tuple(metrics), normalize, pkey)
        if cache_key in self._cache_dist:
            return self._cache_dist[cache_key]
        dep_metrics = list(set(self.projection.get(metric, metric) for metric in metrics))
        dep_data = self.calculate_dep_metrics(dep_metrics)
        dist_data = self._calculate_distributions_from_dep(dep_data, metrics, normalize)
        self._cache_dist[cache_key] = dist_data
        return dist_data

    def calculate_pvp(
        self,
        input: Optional[str] = None,
        target: str = 'deprel',
        normalize: bool = True
    ):
        payloads = [(sentence, input, target, self.stop_deprels) for sentence in self.treebank]
        pkey = (False, 1)
        cache_key = (input, target, normalize, pkey)
        if cache_key in self._cache_pvp:
            return self._cache_pvp[cache_key]

        # Fast path: reuse any cached dep vectors that contain required base fields.
        dep_metrics = ['id', 'head', 'dpos', 'deprel']
        dep_data_cached = None
        dep_cache_key = (tuple(dep_metrics), pkey)
        exact = self._cache_dep.get(dep_cache_key)
        if exact is not None:
            dep_data_cached = exact
        else:
            for cached_dep in self._cache_dep.values():
                if all(metric in cached_dep for metric in dep_metrics):
                    dep_data_cached = {metric: cached_dep[metric] for metric in dep_metrics}
                    break

        if dep_data_cached is not None:
            pvp_data = _calculate_pvp_from_dep_data(
                dep_data_cached,
                input_upos=input,
                target=target,
                normalize=normalize
            )
            self._cache_pvp[cache_key] = pvp_data
            return pvp_data

        sentence_counts = [_compute_sentence_pvp(payload) for payload in payloads]

        dependents = Counter()
        governors = Counter()
        for dep_part, gov_part in sentence_counts:
            dependents.update(dep_part)
            governors.update(gov_part)

        total_deps = sum(dependents.values())
        total_govs = sum(governors.values())
        if normalize:
            govs = sorted(
                ((k, (v / total_govs) if total_govs else 0) for k, v in governors.items()),
                key=lambda x: x[1],
                reverse=True
            )
            deps = sorted(
                ((k, (v / total_deps) if total_deps else 0) for k, v in dependents.items()),
                key=lambda x: x[1],
                reverse=True
            )
        else:
            govs = sorted(governors.items(), key=lambda x: x[1], reverse=True)
            deps = sorted(dependents.items(), key=lambda x: x[1], reverse=True)
        pvp_data = {'act as a gov': govs, 'act as a dep': deps}
        self._cache_pvp[cache_key] = pvp_data
        return pvp_data

    def _compute_feature_bundle(
        self,
        normalize: bool = True,
        compute_mode: str = 'full-output'
    ) -> Tuple[Dict[str, float], pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, pd.DataFrame]]:
        dep_metrics = ['id', 'dpos', 'head', 'deprel'] + list(self.dep_metrics)
        if compute_mode == 'full-output':
            dep_metrics = ['id', 'form', 'dpos', 'head', 'gform', 'gpos', 'deprel'] + list(self.dep_metrics)
        dep_metrics = list(dict.fromkeys(dep_metrics))
        dep_data = self.calculate_dep_metrics(metrics=dep_metrics)

        # Derive default pvp directly from dep vectors to avoid an extra full-treebank pass.
        pvp_data = _calculate_pvp_from_dep_data(dep_data, input_upos=None, target='deprel', normalize=True)

        sent_data = self._calculate_sent_metrics_from_dep(dep_data, self.sent_metrics)
        text_data = self._calculate_text_metrics_from_dep(dep_data, self.text_metrics)
        distributions = self._calculate_distributions_from_dep(dep_data, self.distribution_metrics, normalize=normalize)

        if compute_mode == 'full-output':
            dep_frame = pd.DataFrame({x: _flatten(y) for x, y in dep_data.items()})
            dep_sent_id = []
            for sidx, ids in enumerate(dep_data.get('id', []), start=1):
                dep_sent_id.extend([sidx] * len(ids))
            dep_frame.insert(0, 'sent_id', dep_sent_id)
        else:
            dep_frame = pd.DataFrame()

        sent_frame = pd.DataFrame(sent_data)
        sent_frame.insert(0, 'sent_id', list(range(1, len(sent_frame) + 1)))
        pvp_frame = _pvp2df(pvp_data)
        distribution_dict = {m: pd.DataFrame(distributions[m]).T for m in self.distribution_metrics}
        return text_data, dep_frame, sent_frame, pvp_frame, distribution_dict
    
def _pvp2df(pvp):
    df = pd.DataFrame()
    gov = dict(pvp['act as a gov'])
    dep = dict(pvp['act as a dep'])
    df['Items'] = sorted(list(set(gov.keys()).union(set(dep.keys()))))  
    df['act as a gov'] = [gov.get(d,0) for d in df['Items']]
    df['act as a dep'] = [dep.get(d,0) for d in df['Items']]
    return df

def getDepValFeatures(
    treebank: list,
    normalize: bool = True,
    punct_deprels: Optional[List[str]] = None,
    root_deprels: Optional[List[str]] = None
):
    analyzer = DepValAnalyzer(
        treebank,
        punct_deprels=punct_deprels,
        root_deprels=root_deprels
    )
    return analyzer._compute_feature_bundle(normalize=normalize)


def analyze(
    treebank_path: str,
    out_path: str,
    normalize: bool = True,
    punct_deprels: Optional[List[str]] = None,
    root_deprels: Optional[List[str]] = None
):

    if not os.path.splitext(out_path)[1]:
        os.makedirs(out_path,exist_ok=True)
    else:
        raise ValueError(f" The output path {out_path} is not a valid directory. It should be a directory. ")

    if os.path.isdir(treebank_path):
        treebanks = [os.path.join(treebank_path, i) for i in os.listdir(treebank_path) if i.endswith('.conllu')]
        treebanks.sort()
        text_csv = pd.DataFrame(columns=['mdd','ndd','mhd','mhdd','mtdl','msl','mv','vk','mtw','mth','hi','hf','mrd'])
        file_names = [os.path.basename(t).split('.')[0] for t in treebanks]
        files = [os.path.join(out_path, f) for f in file_names]
        for i,t in enumerate(treebanks):
            os.makedirs(files[i],exist_ok=True)
            text_metrics = _analyze_single_file_serial(
                treebank_path=t,
                out_dir=files[i],
                normalize=normalize,
                punct_deprels=punct_deprels,
                root_deprels=root_deprels
            )
            text_csv.loc[i,:] = text_metrics
        
        text_csv = text_csv.reindex(range(len(file_names)))
        text_csv = text_csv.astype(float).round(2)
        text_csv['treebank'] = [file_names[i] for i in range(len(file_names))]
        text_csv.to_csv(os.path.join(out_path, f'text_metrics.csv'), index=False)
    elif os.path.isfile(treebank_path):
        file_name = os.path.basename(treebank_path).split('.')[0]
        text_metrics = _analyze_single_file_serial(
            treebank_path=treebank_path,
            out_dir=out_path,
            normalize=normalize,
            punct_deprels=punct_deprels,
            root_deprels=root_deprels
        )
        text_csv = pd.DataFrame([text_metrics])
        text_csv = text_csv.astype(float).round(2)
        text_csv['treebank'] = [file_name]
        text_csv.to_csv(os.path.join(out_path, 'text_metrics.csv'), index=False)
    else:
        raise ValueError(f"treebank_path {treebank_path} is neither a directory nor a file.")

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
                with open(t, encoding='utf-8') as treebank:
                    converter = Converter(treebank)
                    converted_treebank = converter.style2style(style_from,style_to)
                    converter.save(converted_treebank,style_to,os.path.join(out_path,f'{file_names[i]}.conllu'))
    else:
        raise ValueError(f"The input path {treebank_path} is not a valid directory. It should be a directory containing treebank files.")




