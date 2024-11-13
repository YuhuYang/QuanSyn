

---

# QuanSyn中文文档

`QuanSyn` 是一个面向于句法计量分析的 Python 包，目前包括`depval`、`lingnet`、`lawfitter`三个模块。
- `Depval`提供了多种方法来计算依存关系的各种指标，包括平均依存距离（Mean Dependency Distance，MDD）、平均层级距离（ Mean Hierarchical Distance，HDD）、依存方向（Dependency Direction）、依存距离分布等。还提供了`conllu`、`conll`、`pmt`、`mcdt`等树库格式的转换接口。
- `Lingnet`可以快速将树库转换为句法依存网络和同现网络，用于语言系统建模和语言网络分析。
- `Lawfitter`可以把文本数据与目标数学模型快速拟合，检测语言的潜在结构模式。

此包可以用于语言学研究，尤其是针对树库进行计量分析。

---

## 目录

- [术语和概念](#术语和概念)
- [安装](#安装)
- [快速开始](#快速开始)【编程小白看过来】
- [用法](#用法)【编程老手请看】
- [许可证](#license)
- [联系方式](#contact)
- [引用](#citing)

---

## 术语和概念

1. depval的指标层级体系

!['依存有向图'](/figure/example.jpg)
(本图片引自：Chen, R., Deng, S., & Liu, H. (2021). Syntactic Complexity of Different Text Types: From the Perspective of Dependency Distance Both Linearly and Hierarchically. Journal of Quantitative Linguistics, 29(4), 510–540. https://doi.org/10.1080/09296174.2021.2005960)

以依存距离(dd)为例，它可以出现在词、句、语篇三个层级上。
在`QuanSyn`中，词层级的dd指的是目标词作为从属词时与其支配词的线性距离。
句层级的mdd指的是句内所有依存距离之均值。语篇层级的mdd指文本中所有依存距离的均值。
所谓的层级，即统计指标时关注的主体。根据这个差异，每个层级的指标有所变化。具体如下：

- 词层级：dd, hd, ddir, v
    - dd: Dependency Distance，目标词与其支配词之间的线性距离。如，Bush 和 will 之间的dd = 1。 
    - hd: Hierarchical Distance，目标词与句子的根的欧几里得距离。如，Bush 的hd = 1。
    - ddir: Dependency Direction，目标词与其支配词之间依存关系的方向。如，Bush 和 will 之间的依存关系指向前方，也即支配词后置。支配词前置时，ddir = 1，后置时，ddir = -1。
    - v: valency，目标词的动态广义价，也即与目标词有依存关系的词数。如，Bush 仅与 will有依存关系，因此v = 1。

- 句层级：mdd, mhd, mhdd, tdl, sl, mv, vk, ttw, tth, hi, hf
    - mdd: Mean Dependency Distance，句内dd的均值。图中句子的mdd为(8+1+1+3+1+1+1+1+1+2+1+1+1+2)/14 = 1.79。
        - $mdd = \frac{1}{sl-1}\sum_{i=1}^{sl-1}dd_i$
        - Liu, H. (2008). Dependency distance as a metric of language comprehension difficulty. Journal of Cognitive Science, 9(2), 159-191.
    - mhd: Mean Hierarchical Distance，句内hd的均值。图中句子的mhd为(2+5+4+3+4+5+2+2+3+4+4+5+6+6)/14 = 3.93。
        - $mhd = \frac{1}{sl-1}\sum_{i=1}^{sl-1}hd_i$
        - Jing, Y., & Liu, H. (2015, August). Mean hierarchical distance augmenting mean dependency distance. In Proceedings of the third international conference on dependency linguistics (Depling 2015) (pp. 161-170).
    - mhdd: Mean Hierarchical Dependency Distance，依存关系数量除以句内层级数。图中句子的mhdd为14/6 = 2.33。
        - $mhdd = \frac{sl-1}{MAXHL}$, MAXHL为句子中最大层级数。
        - Chen, R., Deng, S., & Liu, H. (2021). Syntactic Complexity of Different Text Types: From the Perspective of Dependency Distance Both Linearly and Hierarchically. Journal of Quantitative Linguistics, 29(4), 510–540. 
    - tdl: Total Dependency Length，句内所有dd的总和。图中句子的tdl为8+1+1+3+1+1+1+1+1+2+1+1+1+2 = 25。
        - $tdl = \sum_{i=1}^{sl-1}dd_i$
        - Futrell, R., Mahowald, K., & Gibson, E. (2015). Large-scale evidence of dependency length minimization in 37 languages. Proceedings of the National Academy of Sciences, 112(33), 10336-10341.
    - sl: Sentence Length，句子的长度。图中为15。
    - mv: Mean Valency，句子内v的均值。图中句子的mv为(2+1+2+3+2+1+1+4+2+1+3+2+3+1+1)/15 = 2.07。这个指标很少用到。
        - $mv = \frac{1}{sl}\sum_{i=1}^{sl}v_i$
        - 广义配价或全配价的文献请参考：
        1. Yan, J., & Liu, H. (2021, May). Quantitative analysis of Chinese and English verb valencies based on probabilistic valency pattern theory. In Workshop on Chinese Lexical Semantics (pp. 152-162). Cham: Springer International Publishing. 
        2. Čech, R., Pajas, P., & Mačutek, J. (2010). Full valency. Verb valency without distinguishing complements and adjuncts. Journal of quantitative linguistics, 17(4), 291-302.
    - vk: Variance of Dynamic Valencies ，句子的动态广义价的方差。
        - $vk = \sum_{i=1}^{sl}v_i^2 - (2-\frac{2}{sl})^2$
        - Lu, Q., Lin, Y., & Liu, H. (2018). Dynamic valency and dependency distance. Quantitative analysis of dependency structures, 145-166.
    - tw：Tree Width，句法树的树宽。例句的tw = 4。
    - th：Tree Height，句法树的树高。例句的th = 6。
        - tw & th: Zhang, H., & Liu, H. (2018). Interrelations among dependency tree widths, heights and sentence lengths. Quantitative Analysis of Dependency Structures, 72, 31-52. 
    - hi：num of head-initial dependencies，支配词前置型依存关系数量。例句的hi = 5。
    - hf：num of head-final dependencies，句子的层级频率。例句的hf = 9。
        - ddir & hi & hf: Liu, H. (2010). Dependency direction as a means of word-order typology: A method based on dependency treebanks. Lingua, 120(6), 1567-1578.

- 语篇层级：mdd, mhd, mhdd, mtdl, msl, mv, vk, mtw, mth, hi, hf
    - mdd: Mean Dependency Distance，文本中**所有dd**的均值。
    - mhd: Mean Hierarchical Distance，文本中**所有hd**的均值。
    - mhdd: Mean Hierarchical Dependency Distance，文本中所有句子的mhdd的均值。
    - mtdl: Mean Total Dependency Length，文本中所有句子的tdl的均值。
    - msl: Mean Sentence Length，文本中所有句子的sl的均值。
    - mv: Mean Valency，文本中所有v的均值。常用于计算词类。
    - vk: Variance of Dynamic Valencies ，文本中所有句子的vk的均值。
    - mtw: Mean Tree Width，文本中所有句子的tw的均值。
    - mth: Mean Tree Height，文本中所有句子的th的均值。
    - hi: proportion of head-initial dependencies，文本中hi型依存关系的**比例**。
    - hf: proportion of head-final dependencies，文本中hf型依存关系的**比例**。

- 分布：dd, hd, v, sl, tw, th, pos, deprel
    - dd: Dependency Distance Distribution，依存距离分布。
    - hd: Hierarchical Distance Distribution，层级距离分布。
    - v: Valency Distribution，动态广义价分布。
    - sl: Sentence Length Distribution，句子长度分布。
    - tw: Tree Width Distribution，树宽分布。
    - th: Tree Height Distribution，树高分布。
    - pos: Part-of-Speech Distribution，词性分布。
    - deprel: Dependency Relation Distribution，依存关系分布。

- 概率配价模式：pos deprel
    - pvp： probabilistic valency pattern，概率配价模式。即词或词类与其依存关系的概率分布。
    -   文献参考：
        1. 刘海涛, & 冯志伟. (2007). 自然语言处理的概率配价模式理论. 语言科学, 6(3), 32-41.
        2. Yan, J., & Liu, H. (2021, May). Quantitative analysis of Chinese and English verb valencies based on probabilistic valency pattern theory. In Workshop on Chinese Lexical Semantics (pp. 152-162). Cham: Springer International Publishing. 
        3. Čech, R., Pajas, P., & Mačutek, J. (2010). Full valency. Verb valency without distinguishing complements and adjuncts. Journal of quantitative linguistics, 17(4), 291-302.

ps: 
- 所有指标的计算均不考虑标点符号。
- 在本工具包中，请严格按照以上编码缩略使用指标。

2. 树库格式

我们目前仅支持依存树库。依存树库的最通用格式为conllu，详情请见[conllu格式](https://universaldependencies.org/format.html)。但我们也注意到，其他树库格式也经常被使用。因此，有必要扩充支持的树库格式。目前支持的的树库格式，除了conllu以外，还包括conll，pmt、mcdt。如果你想要使用conllu以外的格式，请先通过`depval.convert()`或`depval.Converter()`将其转换为conllu格式。

- conll：即conllu去除deps和misc两列，其他列没有区别。不再详细介绍。

- pmt：即[PKUMultiViewTreebank/北京大学多视图树库](https://github.com/qiulikun/PKUMultiviewTreebank)所使用的树库格式。该格式中，每个句子占四行，分别为词形、词性、依存关系类型、支配词线性序号。

    |这|是|一|个|例子|。|
    |  ----  |  ----  | ----  |  ----  | ---- | ---- |
    |pron|verb|num|class|noun|punct|
    |subj|root|det|mod|obj|punct|	
    |2|0|4|5|2|2|

- mcdt：即[MCDT/现代汉语依存树库](https://www.researchgate.net/publication/33017655_A_Chinese_Dependency_Syntax_for_Treebanking?_sg%5B0%5D=lsuUD85kTI5AWaecdmMgXv57mfrfiqz9742jcIKrQmKBRhix_-fCLMz-IcPHbBZkIZYfTMEn-5iMaycvEr3l-pSDv-y2MhjgWuel4Wd7.oTJp5BOdI_dKovhiuwNKWZHNf71LozC_j0Az1REHfauR6UtG91S0DEQbiCe6MsKWaeDkp0RDS5A1KWQdioUIqA&_tp=eyJjb250ZXh0Ijp7ImZpcnN0UGFnZSI6InB1YmxpY2F0aW9uIiwicGFnZSI6InByb2ZpbGUiLCJwcmV2aW91c1BhZ2UiOiJwcm9maWxlIiwicG9zaXRpb24iOiJwYWdlQ29udGVudCJ9fQ)所使用的树库格式。该格式本质为记录依存关系对。
    |sn|id|form|pos|head|gform|gpos|deprel|
    |  ----  |  ----  | ----  |  ----  | ---- | ---- |  ----  | ---- |
    |1|1|这|pron|2|是|verb|subj|
    |1|2|是|verb|0|。|punct|root|
    |1|3|一|num|4|个|class|det|
    |1|4|个|class|5|例子|noun|mod|
    |1|5|例子|noun|2|是|verb|obj|
    |1|6|。|punct|
---
## 安装

你可以通过 `pip` 安装 `QuanSyn` 包：

```bash
pip install quansyn
```

本工具包依赖于[`conllu`](https://github.com/EmilStenstrom/conllu)。

---

## 快速开始

这个世界上并不是所有人都会编程语言，但关上门就必须打开一扇窗。我们提供了一些便捷的API，它能让你使用简短的几行代码，将所有分析结果保存到本地，而你只需要更改其中几个论元。

### 计算句法指标
```python
from quansyn.depval import analyze

# 引号内是需要你更改的内容，分别是树库文件存放的*文件夹*路径，和结果保存的*文件夹*路径。
# 注意：必须是文件夹！！！
treebanks_path = r'path/to/treebank'
output_path = r'path/to/output'

# 进行计算
analyze(treebanks_path, output_path)

# 请查看已经保存到本地的结果，然后你就可以使用Excel，SPSS，jamovi等软件作统计分析了。
```
### 转换树库格式
```python
from quansyn.depval import convert

# 引号内是需要你更改的内容，分别是源文件存放的*文件夹*路径，和输出文件保存的*文件夹*路径。
# 注意：必须是文件夹！！！
input_path = r'path/to/treebank'
output_path = r'path/to/output'

# input_format 和 output_format 分别是源文件格式和输出文件格式，根据需求更改。
# 目前支持的格式有：'conllu', 'conll', 'pmt', 'mcdt'，关于4种格式请参考前文的介绍。
input_format = 'conll'
output_format = 'conllu'

convert(input_path, output_path, input_format, output_format)
```

### 搭建语言网络
```python
from quansyn.lingnet import load_edges

# 引号内是需要你更改的内容，分别是源文件存放的*文件夹*路径，和输出文件保存的*文件夹*路径。
# 注意：必须是文件夹！！！
input_path = r'path/to/treebank'
output_path = r'path/to/output'
# mode 选择 'dependency' 或 'adjacency'，分别对应树库中的依存关系和同现关系。
mode = 'dependency'
# 加载树库，生成网络
load_edges(input_path, output_path, mode)

```

---

## 用法

在这里，我们将详细说明QuanSyn包的构成及其使用方法。

### 示例 1：计算依存关系层级/词层级的指标

你可以计算依存关系层级/词层级的指标：

```python
from quansyn.depval import DepValAnalyzer

# 加载依存树库
treebank_path = 'path/to/treebank.conllu'
analyzer = DepValAnalyzer(open(treebank_path, encoding='utf-8'))

# 设置指标集,请【严格】按照开头的层级和编码使用指标
# 如果不设置指标集，则默认计算全部指标
metrics = ['dd', 'hd', 'ddir', 'v']
dep_metrics = analyzer.calculate_dep_metrics(metrics=metrics)

# 打印结果
dep_metrics

>>> {'dd': [[1,2,3,...],[2,3,5,6,...]], 'hd': [[4,1,1,...],[2,2,5,4,...]], ...}
```
返回格式为字典`dict`,`key`为指标名称，`value`为列表，列表的每个元素对应一个句子，列表的元素为**对应依存关系或词的相应指标数值**。

### 示例 2：计算句子级别的指标

同理，你也可以计算句子级别的指标，代码类似：

```python
from quansyn.depval import DepValAnalyzer

treebank_path = 'path/to/treebank.conllu'
analyzer = DepValAnalyzer(open(treebank_path, encoding='utf-8'))

metrics = ['mdd','mhd','mhdd', 'tdl','sl','mv', 'vk', 'tw', 'th', 'hi', 'hf']
sent_metrics = analyzer.calculate_sent_metrics(metrics=metrics)

sent_metrics    
>>> {'mdd': [1,2,3,2,3,5,6,...], 'mhd': [4,1,1,2,2,5,4,...], ...}
```
返回格式为字典`dict`,`key`为指标名称，`value`为列表，列表的每个元素对应**一个句子的相应指标数值**。

### 示例 3：计算文本级别的指标

你还可以计算文本级别的指标，代码类似：

```python
from quansyn.depval import DepValAnalyzer

treebank_path = 'path/to/treebank.conllu'
analyzer = DepValAnalyzer(open(treebank_path, encoding='utf-8'))

metrics = ['mdd','mhd','mhdd','mtdl','msl','mv', 'vk','mtw','mth', 'hi', 'hf']
text_metrics = analyzer.calculate_text_metrics(metrics=metrics)

text_metrics
>>> {'mdd': 2.32, 'mhd': 2.21, ...}
```
返回格式为字典`dict`,`key`为指标名称，`value`为**整个文本的相应指标数值**。

### 示例 4：计算指标的分布

```python
from quansyn.depval import DepValAnalyzer

treebank_path = 'path/to/treebank.conllu'
analyzer = DepValAnalyzer(open(treebank_path, encoding='utf-8'))

metrics = ['dd', 'hd','sl', 'v', 'tw', 'th', 'deprel', 'pos']

# normalize=True 表示对频次进行归一化处理,默认为False
distributions = analyzer.calculate_distributions(metrics=metrics, normalize=True)

# 打印结果
distributions
>>> {'dd': ([1,2,3,4],[0.1,0.2,0.3,0.4]), 'hd', ...}
```
返回格式为字典`dict`，`key`为分布名称，`value`为元组，包括两个元素，第一个为x，第二个为y(频次或频率)。xy皆为列表。

### 示例 5：计算概率配价模式


```python
from quansyn.depval import DepValAnalyzer

# 加载依存树库      
treebank_path = 'path/to/treebank.conllu'
analyzer = DepValAnalyzer(open(treebank_path, encoding='utf-8'))

# 计算词类的pvp，以动词为例，树库使用的标注体系为sud
# input是词类，如果不输入，将不区分词类计算pvp
# target是计算依存关系概率，还是词类概率，默认为'deprel'，可选'pos'
pvp = analyzer.calculate_pvp(input='NOUN',target='deprel',normalize=True)

pvp
>>> {'act as dependents': {'nmod': 0.1, 'nmod:poss': 0.2, 'nmod:tmod': 0.3, ...},
'act as governors':{...}}
```
返回格式为字典`dict`，`key`为作支配词还是作从属词，`value`为字典，包含该词类依存关系及其概率。

### 示例 6：转换树库格式

```python
from quansyn.depval import Converter

# 加载树库
treebank_path = 'path/to/treebank.conllu'
converter = Converter(open(treebank_path, encoding='utf-8'))

# 转换格式
# 论元1为原格式，论元2为目标格式
converted_treebank = converter.style2style('conllu', 'pmt')

# 保存结果 save(树库，树库格式，保存路径)
converter.save(converted_treebank, 'pmt', 'output_path/to/treebank.txt')
```

### 示例 7：搭建语言网络

```python
from quansyn.lingnet import load_edges
import networkx as nx

# 加载树库
treebank_path = 'path/to/treebank.conllu'
treebank = open(treebank_path, encoding='utf-8')

# 抽取依存关系为边，如果想抽取同现关系，将mode设置为'adjacency'
# edges 为边列表，每个元素为 (head, dependent)
edges = conllu2edges(treebank, mode='dependency')

# 构建网络，网络指标可以通过networkx计算
G = nx.graph(edges)
```

### 示例 8：拟合参数

```python
from quansyn.lawfitter import fit

# 加载数据
data = ([1,2,3,4,5],[0.1,0.2,0.3,0.4,0.5])

# 拟合内置分布
fit(data,'zipf')

# 拟合自定义分布
def custom_dist(x,a):
    return a/(x**2)

fit(data,customized_law=custom_dist)

>>> {'paras': [0.123456789],'r^2':-16.229684950920042}
```
---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

- GitHub: [@YuhuYang](https://github.com/YuhuYang)
- Email: yangmufy@163.com

## Citing

If our project has been helpful to you, please give it a star and cite our articles. We would be very grateful.

```
@article{Yang_2022,
doi = {10.1209/0295-5075/ac8bf2},
url = {https://dx.doi.org/10.1209/0295-5075/ac8bf2},
year = {2022},
month = {sep},
publisher = {EDP Sciences, IOP Publishing and Società Italiana di Fisica},
volume = {139},
number = {6},
pages = {61002},
author = {Mu Yang and Haitao Liu},
title = {The role of syntax in the formation of scale-free language networks},
journal = {Europhysics Letters},
abstract = {The overall structure of a network is determined by its micro features, which are different in both syntactic and non-syntactic networks. However, the fact that most language networks are small-world and scale-free raises the question: does syntax play a role in forming the scale-free feature? To answer this question, we build syntactic networks and co-occurrence networks to compare the generation mechanisms of nodes, and to investigate whether syntactic and non-syntactic factors have distinct roles. The results show that frequency is the foundation of the scale-free feature, while syntax is beneficial to enhance this feature. This research introduces a microscopic approach, which may shed light on the scale-free feature of language networks.}
}
``` 