---

# QuanSyn 中文文档

`QuanSyn` 是一个用于句法计量分析的 Python 包。目前包含三个模块：`depval`、`lingnet` 和 `lawfitter`。

- `Depval` 提供多种依存句法指标的计算方法，包括平均依存距离（MDD）、平均层级距离（MHD）、依存方向、依存距离分布等。同时也提供 `conllu`、`conll`、`pmt`、`mcdt` 等树库格式的转换器。

- `Lingnet` 可以将树库快速转换为句法依存网络和共现网络，用于语言系统建模与语言网络分析。

- `Lawfitter` 可以将数据快速拟合到目标数学模型，并发现语言中的潜在结构模式。

---

## 目录

- [术语与概念](#术语与概念)
- [安装](#安装)
- [快速开始](#快速开始)
- [用法](#用法)
- [许可证](#许可证)
- [联系方式](#联系方式)
- [引用](#引用)

---

## 术语与概念

1. **Depval 的指标层级体系**

!['Dependency Directed Graph'](/figure/example.jpg)
（图片来源：Chen, R., Deng, S., & Liu, H. (2021). Syntactic Complexity of Different Text Types: From the Perspective of Dependency Distance Both Linearly and Hierarchically. *Journal of Quantitative Linguistics, 29*(4), 510-540. https://doi.org/10.1080/09296174.2021.2005960）

以依存距离（dd）为例，它可以在词、句子、语篇三个层级上定义和使用。  
在 `QuanSyn` 中，词层级的 dd 指目标词（作从属词）与其中心词之间的线性距离。  
句层级的 mdd 指一个句子内部的平均依存距离。  
语篇层级的 mdd 指整个树库中的平均依存距离。  
所谓“层级”，指的是指标统计对象的层次不同，因此每一层的计算方式会有所变化。具体如下：

- **词层级**：dd, hd, ddir, v  
    - dd：Dependency Distance，目标词与其中心词之间的线性距离。例如图中 *Bush* 与 *will* 之间的 dd 为 1。  
    - hd：Hierarchical Distance，目标词与其中心词在树中的层级距离。例如 *Bush* 的 hd 为 1。  
    - ddir：Dependency Direction，依存关系方向。  
    - v：Valency，目标词的动态广义配价，即与目标词建立依存关系的词数量。例如 *Bush* 只与 *will* 建立依存关系，因此 v = 1。  

- **句层级**：mdd, ndd, mhd, mhdd, tdl, sl, mv, vk, tw, th, hi, hf, rd  
    - mdd：Mean Dependency Distance，句内依存距离的平均值。图中句子的 mdd = (8+1+1+3+1+1+1+1+1+2+1+1+1+2)/14 = 1.79。  
        - $mdd = \frac{1}{sl-1}\sum_{i=1}^{sl-1}dd_i$
        - Liu, H. (2008). Dependency distance as a metric of language comprehension difficulty. Journal of Cognitive Science, 9(2), 159-191.
    - mhd：Mean Hierarchical Distance，句内层级距离的平均值。图中句子的 mhd = (2+5+4+3+4+5+2+2+3+4+4+5+6+6)/14 = 3.93。  
        - $mhd = \frac{1}{sl-1}\sum_{i=1}^{sl-1}hd_i$
        - Jing, Y., & Liu, H. (2015, August). Mean hierarchical distance augmenting mean dependency distance. In Proceedings of the third international conference on dependency linguistics (Depling 2015) (pp. 161-170).
    - mhdd：Mean Hierarchy Dependency Distance，依存关系数量与句子最大层级数之比。图中句子的 mhdd = 14/6 = 2.33。  
        - $mhdd = \frac{sl-1}{MAXHL}$
        - Chen, R., Deng, S., & Liu, H. (2021). Syntactic Complexity of Different Text Types: From the Perspective of Dependency Distance Both Linearly and Hierarchically. Journal of Quantitative Linguistics, 29(4), 510-540. 
    - tdl：Total Dependency Length，句内所有依存距离之和。图中句子的 tdl = 25。  
        - $tdl = \sum_{i=1}^{sl-1}dd_i$
        - Futrell, R., Mahowald, K., & Gibson, E. (2015). Large-scale evidence of dependency length minimization in 37 languages. Proceedings of the National Academy of Sciences, 112(33), 10336-10341.    
    - sl：Sentence Length，句子长度。该例中 sl = 15。  
    - mv：Mean Valency，句内所有词配价的平均值。  
        - $mv = \frac{1}{sl}\sum_{i=1}^{sl}v_i$
        - 参考：  
        1. Yan, J., & Liu, H. (2021, May). Quantitative analysis of Chinese and English verb valencies based on probabilistic valency pattern theory. In Workshop on Chinese Lexical Semantics (pp. 152-162). Cham: Springer International Publishing. 
        2. Cech, R., Pajas, P., & Macutek, J. (2010). Full valency. Verb valency without distinguishing complements and adjuncts. Journal of quantitative linguistics, 17(4), 291-302.
    - vk：Variance of Dynamic Valencies，句内动态广义配价的方差。  
        - $vk = \frac{1}{sl}\sum_{i=1}^{sl}(v_i-\bar{v})^2$
        - Lu, Q., Lin, Y., & Liu, H. (2018). Dynamic valency and dependency distance. Quantitative analysis of dependency structures, 145-166.
    - tw：Tree Width，树宽。  
    - th：Tree Height，树高。 
        - tw & th: Zhang, H., & Liu, H. (2018). Interrelations among dependency tree widths, heights and sentence lengths. Quantitative Analysis of Dependency Structures, 72, 31-52.  
    - hi：head-initial 依存关系数量。  
    - hf：head-final 依存关系数量。  
    - rd：Root Distance，根节点在句子线性序列中的位置（从 1 开始）。
      - Lei, L., & Jockers, M. L. (2020). Normalized Dependency Distance: Proposing a New Measure. Journal of Quantitative Linguistics, 27(1), 62–79. 
    - ndd：Normalized Dependency Distance，归一化依存距离。  
    - $ndd = |\log(\frac{mdd}{\sqrt{rd \cdot sl}})|$
        - Lei, L., & Jockers, M. L. (2020). Normalized Dependency Distance: Proposing a New Measure. Journal of Quantitative Linguistics, 27(1), 62–79. 
    - ddir & hi & hf: Liu, H. (2010). Dependency direction as a means of word-order typology: A method based on dependency treebanks. Lingua, 120(6), 1567-1578.

- **语篇层级**：mdd, ndd, mhd, mhdd, mtdl, msl, mv, vk, mtw, mth, hi, hf, mrd  
    - mdd：语篇中所有依存距离的平均值。  
    - mhd：语篇中所有层级距离的平均值。  
    - mhdd：语篇中所有句子 mhdd 的平均值。  
    - mtdl：语篇中所有句子 tdl 的平均值。  
    - msl：语篇中所有句子长度的平均值。  
    - mv：语篇中所有配价值的平均值。  
    - vk：语篇中所有句子 vk 的平均值。  
    - mtw：语篇中所有句子 tw 的平均值。  
    - mth：语篇中所有句子 th 的平均值。  
    - mrd：语篇中所有句子根位置 rd 的平均值。  
    - ndd：语篇中所有句子 ndd 的平均值。  
    - hi：语篇中 head-initial 依存关系比例。  
    - hf：语篇中 head-final 依存关系比例。  

- **分布**：dd, hd, v, sl, tw, th, rd, pos, deprel  
    - dd：依存距离分布。  
    - hd：层级距离分布。  
    - v：配价分布。  
    - sl：句长分布。  
    - tw：树宽分布。  
    - th：树高分布。  
    - rd：根位置分布。  
    - pos：词性分布。  
    - deprel：依存关系分布。  

- **概率配价模式**：pos, deprel  
    - pvp：Probabilistic Valency Pattern，给定词或词类的依存关系概率分布。  
    - 参考：  
        1. Liu, H., & Feng, Z. (2007). Probabilistic Valency Pattern Theory for Natural Language Processing. *Linguistic Science, 6*(3), 32-41.  
        2. Yan, J., & Liu, H. (2021, May). Quantitative Analysis of Chinese and English Verb Valencies Based on Probabilistic Valency Pattern Theory. In *Workshop on Chinese Lexical Semantics* (pp. 152-162). Cham: Springer International Publishing.  
        3. Cech, R., Pajas, P., & Macutek, J. (2010). Full Valency: Verb Valency Without Distinguishing Complements and Adjuncts. *Journal of Quantitative Linguistics, 17*(4), 291-302.

*注：所有指标默认忽略标点。*  
*请严格使用上述缩写作为指标编码。*

2. **树库格式**

目前仅支持依存树库。最常用格式是 `conllu`，详见 [conllu format](https://universaldependencies.org/format.html)。除 `conllu` 外，当前还支持 `conll`、`pmt`、`mcdt`。若你使用非 `conllu` 格式，请先通过 `depval.convert()` 或 `depval.Converter()` 转换。

- **conll**：即去掉 `deps` 和 `misc` 列的 `conllu`，其余一致。  

- **pmt**：指 [PKUMultiViewTreebank](https://github.com/qiulikun/PKUMultiviewTreebank) 使用的格式。每个句子占 4 行：词形、词性、依存关系、中心词线性索引。

    |this|is|an|example|.|
    |  ----  | ----  |  ----  | ---- | ---- |
    |pron|verb|num|noun|punct|
    |subj|root|det|obj|punct|    
    |2|0|4|2|2|

- **mcdt**：指 [MCDT / Modern Chinese Dependency Treebank](https://www.researchgate.net/publication/33017655_A_Chinese_Dependency_Syntax_for_Treebanking?_sg%5B0%5D=lsuUD85kTI5AWaecdmMgXv57mfrfiqz9742jcIKrQmKBRhix_-fCLMz-IcPHbBZkIZYfTMEn-5iMaycvEr3l-pSDv-y2MhjgWuel4Wd7.oTJp5BOdI_dKovhiuwNKWZHNf71LozC_j0Az1REHfauR6UtG91S0DEQbiCe6MsKWaeDkp0RDS5A1KWQdioUIqA&_tp=eyJjb250ZXh0Ijp7ImZpcnN0UGFnZSI6InB1YmxpY2F0aW9uIiwicGFnZSI6InByb2ZpbGUiLCJwcmV2aW91c1BhZ2UiOiJwcm9maWxlIiwicG9zaXRpb24iOiJwYWdlQ29udGVudCJ9fQ)。
    |sn|id|form|pos|head|gform|gpos|deprel|
    |  ----  |  ----  | ----  |  ----  | ---- | ---- |  ----  | ---- |
    |1|1|this|pron|2|is|verb|subj|
    |1|2|is|verb|0|.|punct|root|
    |1|3|an|num|4|example|noun|det|
    |1|4|example|noun|2|is|verb|obj|
    |1|6|.|punct|

---

## 安装

你可以通过 `pip` 安装 `QuanSyn`：

```bash
pip install quansyn
```

本包依赖 [`conllu`](https://github.com/EmilStenstrom/conllu)。

---

## 快速开始

### 计算句法指标

```python
from quansyn.depval import analyze

# 请修改为：树库文件所在文件夹路径、结果输出文件夹路径
# 注意：都必须是“文件夹”路径

treebanks_path = r'path/to/treebank'
output_path = r'path/to/output'

# Serial mode (default)
analyze(treebanks_path, output_path)
```

### 转换树库格式

```python
from quansyn.depval import convert

# 请修改为输入文件夹与输出文件夹路径
input_path = r'path/to/treebank'
output_path = r'path/to/output'

# 支持格式：'conllu', 'conll', 'pmt', 'mcdt'
input_format = 'conll'
output_format = 'conllu'

convert(input_path, output_path, input_format, output_format)
```

### 构建语言网络

```python
from quansyn.lingnet import load_edges

input_path = r'path/to/treebank'
output_path = r'path/to/output'
mode = 'dependency'  # 或 'adjacency'

load_edges(
    input_path,
    output_path,
    mode=mode,
    lowercase=True,
    ignore_punct=True,
    weighted=False,
    directed=False
)
```

---

## 用法

### 示例 1：计算词层级指标

```python
from quansyn.depval import DepValAnalyzer

# 加载树库
treebank_path = 'path/to/treebank.conllu'
analyzer = DepValAnalyzer(open(treebank_path, encoding='utf-8'))

# DepValAnalyzer 也支持：已解析句子列表 / conllu 字符串
# 若输入已完成预处理，可设置 cleaned=True

metrics = ['dd', 'hd', 'ddir', 'v']
dep_metrics = analyzer.calculate_dep_metrics(metrics=metrics)

dep_metrics
>>> {'dd': [[1,2,3,...],[2,3,5,6,...]], 'hd': [[4,1,1,...],[2,2,5,4,...]], ...}
```

返回格式是 `dict`：`key` 为指标名，`value` 为列表（每个元素对应一个句子的该指标结果）。

### 示例 2：计算句层级指标

```python
from quansyn.depval import DepValAnalyzer

treebank_path = 'path/to/treebank.conllu'
analyzer = DepValAnalyzer(open(treebank_path, encoding='utf-8'))

metrics = ['mdd', 'ndd', 'mhd', 'mhdd', 'tdl', 'sl', 'mv', 'vk', 'tw', 'th', 'hi', 'hf', 'rd']
sent_metrics = analyzer.calculate_sent_metrics(metrics=metrics)

sent_metrics
>>> {'mdd': [1,2,3,2,3,5,6,...], 'mhd': [4,1,1,2,2,5,4,...], ...}
```

返回格式是 `dict`：`key` 为指标名，`value` 为列表（每个元素对应一个句子的该指标值）。

### 示例 3：计算语篇层级指标

```python
from quansyn.depval import DepValAnalyzer

treebank_path = 'path/to/treebank.conllu'
analyzer = DepValAnalyzer(open(treebank_path, encoding='utf-8'))

metrics = ['mdd', 'ndd', 'mhd', 'mhdd', 'mtdl', 'msl', 'mv', 'vk', 'mtw', 'mth', 'hi', 'hf', 'mrd']
text_metrics = analyzer.calculate_text_metrics(metrics=metrics)

text_metrics
>>> {'mdd': 2.32, 'mhd': 2.21, ...}
```

返回格式是 `dict`：`key` 为指标名，`value` 为语篇级标量结果。

### 示例 4：计算分布

```python
from quansyn.depval import DepValAnalyzer

treebank_path = 'path/to/treebank.conllu'
analyzer = DepValAnalyzer(open(treebank_path, encoding='utf-8'))

metrics = ['dd', 'hd', 'sl', 'v', 'tw', 'th', 'rd', 'deprel', 'pos']

# normalize=True 表示归一化为频率；默认 False（频次）
distributions = analyzer.calculate_distributions(metrics=metrics, normalize=True)

distributions
>>> {'dd': ([1,2,3,4],[0.1,0.2,0.3,0.4]), 'hd', ...}
```

返回格式是 `dict`：`key` 为分布名，`value` 为 `(x, y)` 二元组。

### 示例 5：计算概率配价模式

```python
from quansyn.depval import DepValAnalyzer

treebank_path = 'path/to/treebank.conllu'
analyzer = DepValAnalyzer(open(treebank_path, encoding='utf-8'))

# input: 词类；target: 'deprel' 或 'pos'
pvp = analyzer.calculate_pvp(input='NOUN', target='deprel', normalize=True)

pvp
>>> {'act as a gov': [('subj', 0.32), ('mod', 0.21), ...],
'act as a dep': [('mod', 0.28), ('comp:obj', 0.11), ...]}
```

### 示例 6：转换树库格式

```python
from quansyn.depval import Converter

treebank_path = 'path/to/treebank.conllu'
converter = Converter(open(treebank_path, encoding='utf-8'))

converted_treebank = converter.style2style('conllu', 'pmt')
converter.save(converted_treebank, 'pmt', 'output_path/to/treebank.txt')
```

### 示例 7：构建语言网络

```python
from quansyn.lingnet import conllu2edge
import networkx as nx

treebank_path = 'path/to/treebank.conllu'
treebank = open(treebank_path, encoding='utf-8')

edges = conllu2edge(
    treebank,
    mode='dependency',
    lowercase=True,
    ignore_punct=True,
    weighted=False,
    directed=False
)
G = nx.Graph(edges)
```

### 示例 8：拟合参数

```python
from quansyn.lawfitter import fit

data = ([1,2,3,4,5],[0.1,0.2,0.3,0.4,0.5])

fit(data, 'zipf')

# 自定义分布
def custom_dist(x, a):
    return a / (x ** 2)

fit(data, customized_law=custom_dist)

>>> {'params': [0.123456789], 'r^2': -16.229684950920042}
```

---

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE)。

## 联系方式

- GitHub: [@YuhuYang](https://github.com/YuhuYang)
- Email: yangmufy@163.com

## 引用

如果本项目对你有帮助，欢迎 star 并引用：

```bibtex
@article{Yang25022025,
author = {Mu Yang and Haitao Liu},
title = {QuanSyn: A Package for Quantitative Syntax Analysis},
journal = {Journal of Quantitative Linguistics},
volume = {0},
number = {0},
pages = {1--18},
year = {2025},
publisher = {Routledge},
doi = {10.1080/09296174.2025.2471157},
URL = {https://doi.org/10.1080/09296174.2025.2471157},
eprint = {https://doi.org/10.1080/09296174.2025.2471157}
}
```
