# QuanSyn Documentation

## Overview

QuanSyn is a Python library for quantitative syntax analysis.

Current modules:

- `quansyn.depval`: dependency metrics, distributions, pvp, and treebank format conversion.
- `quansyn.lingnet`: dependency/co-occurrence network edge extraction.
- `quansyn.lawfitter`: fitting common quantitative linguistics laws.

Package exports:

- `__all__ = ["depval", "lawfitter", "lingnet"]`

---

## Installation

```bash
pip install quansyn
```

Dependencies include `conllu`, `numpy`, `pandas`, `scipy`, `scikit-learn`.

---

## API Reference

### Module: `quansyn.depval`

#### Class: `DepValAnalyzer`

Initialize analyzer from one of:

- text stream (`io.TextIOWrapper`) of CONLLU
- parsed sentence list
- raw CONLLU string

```python
DepValAnalyzer(treebank, cleaned=False, punct_deprels=None, root_deprels=None)
```

Methods:

- `calculate_dep_metrics(metrics=None) -> Dict[str, List]`
- `calculate_sent_metrics(metrics=None) -> Dict[str, List]`
- `calculate_text_metrics(metrics=None) -> Dict[str, float]`
- `calculate_distributions(metrics=None, normalize=False) -> Dict[str, Tuple[List, List]]`
- `calculate_pvp(input=None, target='deprel', normalize=True) -> Dict[str, List[Tuple[str, float]]]`

#### Function: `getDepValFeatures(treebank, normalize=True, punct_deprels=None, root_deprels=None)`

Returns:

`(text_metrics, dep_df, sent_df, pvp_df, distribution_dict)`

Notes:

- `dep_df` includes `sent_id`.
- `sent_df` includes `sent_id`.

#### Function: `analyze(treebank_path, out_path, normalize=True, punct_deprels=None, root_deprels=None)`

Batch process `.conllu` file(s) and save:

- `text_metrics.csv`
- per-treebank `dep_metrics.csv`, `sent_metrics.csv`, `pvp.csv`
- distribution files: `dd/hd/sl/v/tw/th/rd/deprel/pos_distribution.csv`

`pvp.csv` output in `analyze` is grouped by all `upos` with `deprel` as labels:

- `upos`, `Items`, `act as a gov`, `act as a dep`

#### Class: `Converter`

```python
Converter(treebank)
```

Methods:

- `to_conllu(style)` where `style in {'pmt','conll','mcdt'}`
- `to_others(style)` where `style in {'conll','pmt','mcdt'}`
- `style2style(style_from, style_to)`
- `save(treebank, style, file_path)`

#### Function: `convert(treebank_path, out_path, style_from, style_to)`

Batch convert files in `treebank_path` and save into `out_path`.

---

### Module: `quansyn.lingnet`

#### Class: `Network`

```python
Network(treebank)
```

Methods:

- `getDeprel(lowercase=True, ignore_punct=True, weighted=False, directed=False)`
- `getBiGram(lowercase=True, ignore_punct=True, weighted=False, directed=False)`
- `mapWordId(contents)`
- `getEdge(contents, mapping)`

#### Functions

- `conllu2edge(treebank, mode='dependency', lowercase=True, ignore_punct=True, weighted=False, directed=False)`
- `load_edges(treebanks_path, output_path, mode='dependency', lowercase=True, ignore_punct=True, weighted=False, directed=False)`
  - supports both single file and directory input.
- `fitPowerLaw(data) -> (a, b, r2)`

---

### Module: `quansyn.lawfitter`

Built-in law factories:

- `piotrovski_altmann_law(variant=None|'partial'|'reversiable')`
- `zipf_law(variant=None)`
- `menzerath_altmann_law(variant=None|'simplified form'|'complex form')`
- `heap_law(variant=None)`
- `brevity_law(variant=None)`

Core function:

- `fit(data, law_name=None, variant=None, customized_law=None) -> Dict[str, Any]`
  - `data`: `[x_values, y_values]`
  - returns `{'params': params, 'r^2': r2}`

---

## Minimal Examples

```python
from quansyn.depval import DepValAnalyzer

analyzer = DepValAnalyzer(open('sample.conllu', encoding='utf-8'))
print(analyzer.calculate_text_metrics())
```

```python
from quansyn.lingnet import conllu2edge

edges = conllu2edge(
    open('sample.conllu', encoding='utf-8'),
    mode='dependency',
    lowercase=True,
    ignore_punct=True,
    weighted=False,
    directed=False
)
print(edges[:5])
```

```python
from quansyn.lawfitter import fit

result = fit(([1, 2, 3, 4], [10, 6, 4, 3]), law_name='zipf')
print(result)
```

---

## Notes

- Punctuation dependencies are excluded by default in depval preprocessing.
- Root-distance related metrics/distributions are supported: `rd`, `mrd`, `ndd`, and `rd` distribution.
- For directory APIs (`analyze`, `convert`, `load_edges`), output path must be a directory.
