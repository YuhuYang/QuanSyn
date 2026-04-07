# QuanSyn 文档

## 概览

QuanSyn 是一个面向句法计量分析的 Python 库。

当前模块：

- `quansyn.depval`：依存指标、分布、概率配价模式（PVP）与树库格式转换。
- `quansyn.lingnet`：依存/共现网络边提取。
- `quansyn.lawfitter`：常见计量语言学律的拟合。

包导出：

- `__all__ = ["depval", "lawfitter", "lingnet"]`

---

## 安装

```bash
pip install quansyn
```

依赖包含 `conllu`、`numpy`、`pandas`、`scipy`、`scikit-learn`。

---

## API 参考

### 模块：`quansyn.depval`

#### 类：`DepValAnalyzer`

支持以下输入初始化：

- CONLLU 文本流（`io.TextIOWrapper`）
- 解析后的句子列表
- 原始 CONLLU 字符串

```python
DepValAnalyzer(treebank, cleaned=False, punct_deprels=None, root_deprels=None)
```

方法：

- `calculate_dep_metrics(metrics=None) -> Dict[str, List]`
- `calculate_sent_metrics(metrics=None) -> Dict[str, List]`
- `calculate_text_metrics(metrics=None) -> Dict[str, float]`
- `calculate_distributions(metrics=None, normalize=False) -> Dict[str, Tuple[List, List]]`
- `calculate_pvp(input=None, target='deprel', normalize=True) -> Dict[str, List[Tuple[str, float]]]`

#### 函数：`getDepValFeatures(treebank, normalize=True, punct_deprels=None, root_deprels=None)`

返回：

`(text_metrics, dep_df, sent_df, pvp_df, distribution_dict)`

说明：

- `dep_df` 含 `sent_id` 列。
- `sent_df` 含 `sent_id` 列。

#### 函数：`analyze(treebank_path, out_path, normalize=True, punct_deprels=None, root_deprels=None)`

批处理 `.conllu` 文件并输出：

- `text_metrics.csv`
- 每个树库的 `dep_metrics.csv`、`sent_metrics.csv`、`pvp.csv`
- 分布文件：`dd/hd/sl/v/tw/th/rd/deprel/pos_distribution.csv`

`analyze` 输出的 `pvp.csv` 为“全部 `upos` × `deprel`”的长表，主要列为：

- `upos`, `Items`, `act as a gov`, `act as a dep`

#### 类：`Converter`

```python
Converter(treebank)
```

方法：

- `to_conllu(style)`，`style in {'pmt','conll','mcdt'}`
- `to_others(style)`，`style in {'conll','pmt','mcdt'}`
- `style2style(style_from, style_to)`
- `save(treebank, style, file_path)`

#### 函数：`convert(treebank_path, out_path, style_from, style_to)`

批量转换目录中的树库文件并写入目标目录。

---

### 模块：`quansyn.lingnet`

#### 类：`Network`

```python
Network(treebank)
```

方法：

- `getDeprel(lowercase=True, ignore_punct=True, weighted=False, directed=False)`
- `getBiGram(lowercase=True, ignore_punct=True, weighted=False, directed=False)`
- `mapWordId(contents)`
- `getEdge(contents, mapping)`

#### 函数

- `conllu2edge(treebank, mode='dependency', lowercase=True, ignore_punct=True, weighted=False, directed=False)`
- `load_edges(treebanks_path, output_path, mode='dependency', lowercase=True, ignore_punct=True, weighted=False, directed=False)`
  - 支持单文件或目录输入。
- `fitPowerLaw(data) -> (a, b, r2)`

---

### 模块：`quansyn.lawfitter`

内置律工厂：

- `piotrovski_altmann_law(variant=None|'partial'|'reversiable')`
- `zipf_law(variant=None)`
- `menzerath_altmann_law(variant=None|'simplified form'|'complex form')`
- `heap_law(variant=None)`
- `brevity_law(variant=None)`

核心函数：

- `fit(data, law_name=None, variant=None, customized_law=None) -> Dict[str, Any]`
  - `data` 形式：`[x_values, y_values]`
  - 返回：`{'params': params, 'r^2': r2}`

---

## 最小示例

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

## 备注

- depval 预处理默认忽略标点依存关系。
- 已支持 root-distance 相关：`rd`、`mrd`、`ndd` 及 `rd` 分布。
- 目录型接口（`analyze`、`convert`、`load_edges`）要求输出路径是目录。
