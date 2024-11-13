
---

# QuanSyn Documentation (English)

`QuanSyn` is a Python package designed for quantitative syntax analysis. Currently, it includes three modules: `depval`, `lingnet`, and `lawfitter`.

- `Depval` provides various methods to calculate dependency-based metrics, including Mean Dependency Distance (MDD), Mean Hierarchy Distance (MHD), Dependency Direction, Dependency Distance Distribution, etc. It also offers a convertor for treebank formats such as `conllu`, `conll`, `pmt`, and `mcdt`.
  
- `Lingnet` can quickly convert a treebank into syntactic dependency networks and co-occurrence networks for language system modeling and language network analysis.
  
- `Lawfitter` can quickly fit data to a target mathematical model and detect potential structural patterns in languages.

---

## Table of Contents

- [Terms and Concepts](#terms-and-concepts)
- [Installation](#installation)
- [Quick Start](#quick-start)【For beginners】
- [Usage](#usage)【For experts】
- [License](#license)
- [Contact](#contact)
- [Citing](#citing)

---

## Terms and Concepts

1. **Metric Hierarchy in Depval**

!['Dependency Directed Graph'](/figure/example.jpg)
(This image is sourced from: Chen, R., Deng, S., & Liu, H. (2021). Syntactic Complexity of Different Text Types: From the Perspective of Dependency Distance Both Linearly and Hierarchically. *Journal of Quantitative Linguistics, 29*(4), 510–540. https://doi.org/10.1080/09296174.2021.2005960)

Take Dependency Distance (dd) as an example, which can be used at the word, sentence, and discourse levels.  
In `QuanSyn`, the word-level dd refers to the linear distance between a target word and its head word when the target word is a dependent.  
The sentence-level mdd refers to the mean dependency distance within a sentence.  
The text-level mdd refers to the mean dependency distance in a treebank.  
The "level" refers to the subject of the statistical metric, which changes the calculation at each level. The specifics are as follows:

- **Word-level**: dd, hd, ddir, v  
    - dd: Dependency Distance, the linear distance between a target word and its governor. For example, the dd between *Bush* and *will* is 1.  
    - hd: Hierarchical Distance, the Euclidean distance between a target word and its governor in a tree. For example, the hd of *Bush* is 1.  
    - ddir: Dependency Direction, the direction of the dependency relation. 
    - v: Valency, the dynamic generalized valency of a target word, referring to the number of words that link to the target word. For example, *Bush* only has a dependency with *will*, so v = 1.  

- **Sentence-level**: mdd, mhd, mhdd, tdl, sl, mv, vk, ttw, tth, hi, hf  
    - mdd: Mean Dependency Distance, the average of all dependency distances in a sentence. The MDD of the sentence in the figure is (8+1+1+3+1+1+1+1+1+2+1+1+1+2)/14 = 1.79.  
        - $mdd = \frac{1}{sl-1}\sum_{i=1}^{sl-1}dd_i$
        - Liu, H. (2008). Dependency distance as a metric of language comprehension difficulty. Journal of Cognitive Science, 9(2), 159-191.
    - mhd: Mean Hierarchical Distance, the average of all hierarchical distances in a sentence. The MHD of the sentence in the figure is (2+5+4+3+4+5+2+2+3+4+4+5+6+6)/14 = 3.93.  
        - $mhd = \frac{1}{sl-1}\sum_{i=1}^{sl-1}hd_i$
        - Jing, Y., & Liu, H. (2015, August). Mean hierarchical distance augmenting mean dependency distance. In Proceedings of the third international conference on dependency linguistics (Depling 2015) (pp. 161-170).
    - mhdd: Mean Hierarchy Dependency Distance, the number of dependency relationships divided by the number of hierarchical levels in the sentence. The mhdd for the sentence in the figure is 14/6 = 2.33.  
        - $mhdd = \frac{sl-1}{MAXHL}$, MAXHL为句子中最大层级数。
        - Chen, R., Deng, S., & Liu, H. (2021). Syntactic Complexity of Different Text Types: From the Perspective of Dependency Distance Both Linearly and Hierarchically. Journal of Quantitative Linguistics, 29(4), 510–540. 
    - tdl: Total Dependency Length, the sum of all dependency distances in a sentence. The TDL for the sentence in the figure is 25.  
        - $tdl = \sum_{i=1}^{sl-1}dd_i$
        - Futrell, R., Mahowald, K., & Gibson, E. (2015). Large-scale evidence of dependency length minimization in 37 languages. Proceedings of the National Academy of Sciences, 112(33), 10336-10341.    
    - sl: Sentence Length, the length of the sentence. In this example, the sentence length is 15.  
    - mv: Mean Valency, the average valency for all words in a sentence.  
        - $mv = \frac{1}{sl}\sum_{i=1}^{sl}v_i$
        - ：
        1. Yan, J., & Liu, H. (2021, May). Quantitative analysis of Chinese and English verb valencies based on probabilistic valency pattern theory. In Workshop on Chinese Lexical Semantics (pp. 152-162). Cham: Springer International Publishing. 
        2. Čech, R., Pajas, P., & Mačutek, J. (2010). Full valency. Verb valency without distinguishing complements and adjuncts. Journal of quantitative linguistics, 17(4), 291-302.
    - vk: Variance of Dynamic Valencies, the variance of dynamic generalized valencies for the sentence.  
        - $vk = \sum_{i=1}^{sl}v_i^2 - (2-\frac{2}{sl})^2$
        - Lu, Q., Lin, Y., & Liu, H. (2018). Dynamic valency and dependency distance. Quantitative analysis of dependency structures, 145-166.
    - tw: Tree Width, the width of a tree.  
    - th: Tree Height, the height of a tree. 
        - tw & th: Zhang, H., & Liu, H. (2018). Interrelations among dependency tree widths, heights and sentence lengths. Quantitative Analysis of Dependency Structures, 72, 31-52.  
    - hi: Number of head-initial dependencies.  
    - hf: Number of head-final dependencies.
        - ddir & hi & hf: Liu, H. (2010). Dependency direction as a means of word-order typology: A method based on dependency treebanks. Lingua, 120(6), 1567-1578.

- **Text-level**: mdd, mhd, mhdd, mtdl, msl, mv, vk, mtw, mth, hi, hf  
    - mdd: Mean Dependency Distance, the average of all dependency distances across all sentences in the text.  
    - mhd: Mean Hierarchical Distance, the average of all hierarchy distances across all sentences in the text.  
    - mhdd: Mean Hierarchical Dependency Distance, the average of all mhdd values across all sentences in the text.  
    - mtdl: Mean Total Dependency Length, the average of all tdl values across all sentences in the text.  
    - msl: Mean Sentence Length, the average of all sentence lengths across the text.  
    - mv: Mean Valency, the average of all valency values across all sentences in the text.  
    - vk: Variance of Dynamic Valencies, the average of all VK values across all sentences in the text.  
    - mtw: Mean Tree Width, the average of all tree widths across all sentences in the text.  
    - mth: Mean Tree Height, the average of all tree heights across all sentences in the text.  
    - hi: Proportion of head-initial dependencies in the text.  
    - hf: Proportion of head-final dependencies in the text.

- **Distributions**: dd, hd, v, sl, tw, th, pos, deprel  
    - dd: Dependency Distance Distribution.  
    - hd: Hierarchical Distance Distribution.  
    - v: Valency Distribution.  
    - sl: Sentence Length Distribution.  
    - tw: Tree Width Distribution.  
    - th: Tree Height Distribution.  
    - pos: Part-of-Speech Distribution.  
    - deprel: Dependency Relation Distribution.  

- **Probabilistic Valency Patterns**: pos, deprel  
    - pvp: Probabilistic Valency Pattern, the probability distribution of dependency relations of a given word or word class.  
    - References:  
        1. Liu, H., & Feng, Z. (2007). Probabilistic Valency Pattern Theory for Natural Language Processing. *Linguistic Science, 6*(3), 32-41.  
        2. Yan, J., & Liu, H. (2021, May). Quantitative Analysis of Chinese and English Verb Valencies Based on Probabilistic Valency Pattern Theory. In *Workshop on Chinese Lexical Semantics* (pp. 152-162). Cham: Springer International Publishing.  
        3. Čech, R., Pajas, P., & Mačutek, J. (2010). Full Valency: Verb Valency Without Distinguishing Complements and Adjuncts. *Journal of Quantitative Linguistics, 17*(4), 291-302.

*Note: All metric calculations ignore punctuation marks.*  
*Please strictly adhere to the abbreviations and coding specified above.*

2. **Treebank Formats**

Currently, only dependency treebanks are supported. The most common format for dependency treebanks is `conllu`. For further details on the `conllu` format, please refer to [conllu format](https://universaldependencies.org/format.html). However, other treebank formats are also commonly used, so it is necessary to support additional formats. The currently supported formats, in addition to `conllu`, include `conll`, `pmt`, and `mcdt`. If you want to use formats other than `conllu`, please first convert them to the `conllu` format using `depval.convert()` or `depval.Converter()`.

- **conll**: The `conllu` format with the `deps` and `misc` columns removed, with no other differences.  

- **pmt**: This refers to the treebank format used by [PKUMultiViewTreebank](https://github.com/qiulikun/PKUMultiviewTreebank) format. In this format, each sentence spans four lines: the word form, part-of-speech tag, dependency relation type, and the linear index of the governing word.

    |this|is|an|example|.|
    |  ----  | ----  |  ----  | ---- | ---- |
    |pron|verb|num|noun|punct|
    |subj|root|det|obj|punct|    
    |2|0|4|2|2|

- **mcdt**: This refers to the treebank format used by [MCDT / Modern Chinese Dependency Treebank](https://www.researchgate.net/publication/33017655_A_Chinese_Dependency_Syntax_for_Treebanking?_sg%5B0%5D=lsuUD85kTI5AWaecdmMgXv57mfrfiqz9742jcIKrQmKBRhix_-fCLMz-IcPHbBZkIZYfTMEn-5iMaycvEr3l-pSDv-y2MhjgWuel4Wd7.oTJp5BOdI_dKovhiuwNKWZHNf71LozC_j0Az1REHfauR6UtG91S0DEQbiCe6MsKWaeDkp0RDS5A1KWQdioUIqA&_tp=eyJjb250ZXh0Ijp7ImZpcnN0UGFnZSI6InB1YmxpY2F0aW9uIiwicGFnZSI6InByb2ZpbGUiLCJwcmV2aW91c1BhZ2UiOiJwcm9maWxlIiwicG9zaXRpb24iOiJwYWdlQ29udGVudCJ9fQ). 
    |sn|id|form|pos|head|gform|gpos|deprel|
    |  ----  |  ----  | ----  |  ----  | ---- | ---- |  ----  | ---- |
    |1|1|this|pron|2|is|verb|subj|
    |1|2|is|verb|0|.|punct|root|
    |1|3|an|num|4|example|noun|det|
    |1|4|example|noun|2|is|verb|obj|
    |1|6|.|punct|

---

## Installation

You can install the `QuanSyn` package via `pip`:

```bash
pip install quansyn
```

This package depends on [`conllu`](https://github.com/EmilStenstrom/conllu).

---

## Quick Start

Not everyone in the world knows how to program, but when the door is closed, a window must open. We provide some convenient APIs that allow you to save all analysis results locally with just a few lines of code, and you only need to change a few arguments.

### Calculating Syntactic Metrics
```python
from quansyn.depval import analyze

# The content in quotes needs to be changed: the *folder* path where the treebank files are stored and the *folder* path where the results should be saved.
# Note: These must be folders!!!
treebanks_path = r'path/to/treebank'
output_path = r'path/to/output'

# Perform the calculation
analyze(treebanks_path, output_path)

# Check the results saved locally, then you can use software like Excel, SPSS, jamovi for statistical analysis.
```

### Converting Treebank Formats
```python
from quansyn.depval import convert

# The content in quotes needs to be changed: the *folder* path where the source files are stored, and the *folder* path where the output files should be saved.
# Note: These must be folders!!!
input_path = r'path/to/treebank'
output_path = r'path/to/output'

# input_format and output_format refer to the source file format and output file format, change them as needed.
# The supported formats are: 'conllu', 'conll', 'pmt', 'mcdt'. Please refer to the previous introduction for details on these four formats.
input_format = 'conll'
output_format = 'conllu'

convert(input_path, output_path, input_format, output_format)
```

### Building a Linguistic Network
```python
from quansyn.lingnet import load_edges

# The content in quotes needs to be changed: the *folder* path where the source files are stored and the *folder* path where the output files should be saved.
# Note: These must be folders!!!
input_path = r'path/to/treebank'
output_path = r'path/to/output'
# Select 'dependency' or 'adjacency' mode, corresponding to the dependency relations or co-occurrence relations in the treebank.
mode = 'dependency'
# Load the treebank and generate the network
load_edges(input_path, output_path, mode)
```

---

## Usage

Here, we will explain in detail the structure and usage of the `QuanSyn` package.

### Example 1: Calculating Dependency-Level / Word-Level Metrics

You can calculate dependency-level or word-level metrics:

```python
from quansyn.depval import DepValAnalyzer

# Load the dependency treebank
treebank_path = 'path/to/treebank.conllu'
analyzer = DepValAnalyzer(open(treebank_path, encoding='utf-8'))

# Set the set of metrics (please follow the hierarchy and encoding strictly)
# If no metrics set is provided, all metrics are calculated by default.
metrics = ['dd', 'hd', 'ddir', 'v']
dep_metrics = analyzer.calculate_dep_metrics(metrics=metrics)

# Print the results
dep_metrics

>>> {'dd': [[1,2,3,...],[2,3,5,6,...]], 'hd': [[4,1,1,...],[2,2,5,4,...]], ...}
```
The return format is a dictionary `dict`, where the `key` is the metric name, and the `value` is a list, with each element corresponding to a sentence and containing **the respective metric value for the dependency or word**.

### Example 2: Calculating Sentence-Level Metrics

Similarly, you can calculate sentence-level metrics with a similar code structure:

```python
from quansyn.depval import DepValAnalyzer

treebank_path = 'path/to/treebank.conllu'
analyzer = DepValAnalyzer(open(treebank_path, encoding='utf-8'))

metrics = ['mdd', 'mhd', 'mhdd', 'tdl', 'sl', 'mv', 'vk', 'tw', 'th', 'hi', 'hf']
sent_metrics = analyzer.calculate_sent_metrics(metrics=metrics)

sent_metrics    
>>> {'mdd': [1,2,3,2,3,5,6,...], 'mhd': [4,1,1,2,2,5,4,...], ...}
```
The return format is a dictionary `dict`, where the `key` is the metric name, and the `value` is a list, with each element corresponding to **the respective metric value for each sentence**.

### Example 3: Calculating Text-Level Metrics

You can also calculate text-level metrics in a similar manner:

```python
from quansyn.depval import DepValAnalyzer

treebank_path = 'path/to/treebank.conllu'
analyzer = DepValAnalyzer(open(treebank_path, encoding='utf-8'))

metrics = ['mdd', 'mhd', 'mhdd', 'mtdl', 'msl', 'mv', 'vk', 'mtw', 'mth', 'hi', 'hf']
text_metrics = analyzer.calculate_text_metrics(metrics=metrics)

text_metrics
>>> {'mdd': 2.32, 'mhd': 2.21, ...}
```
The return format is a dictionary `dict`, where the `key` is the metric name, and the `value` is **the respective metric value for the entire text**.

### Example 4: Calculating Metric Distributions

```python
from quansyn.depval import DepValAnalyzer

treebank_path = 'path/to/treebank.conllu'
analyzer = DepValAnalyzer(open(treebank_path, encoding='utf-8'))

metrics = ['dd', 'hd', 'sl', 'v', 'tw', 'th', 'deprel', 'pos']

# normalize=True means to normalize the frequency, the default is False
distributions = analyzer.calculate_distributions(metrics=metrics, normalize=True)

# Print the results
distributions
>>> {'dd': ([1,2,3,4],[0.1,0.2,0.3,0.4]), 'hd', ...}
```
The return format is a dictionary `dict`, where the `key` is the distribution name, and the `value` is a tuple containing two elements: the first being `x` and the second being `y` (frequency or frequency ratio). Both `x` and `y` are lists.

### Example 5: Calculating Probabilistic Valency Patterns

```python
from quansyn.depval import DepValAnalyzer

# Load the dependency treebank      
treebank_path = 'path/to/treebank.conllu'
analyzer = DepValAnalyzer(open(treebank_path, encoding='utf-8'))

# Calculate the pvp (probabilistic valency patterns) for a specific word class, e.g., nouns.
# The treebank uses the 'sud' annotation system.
# 'input' is the word class; if not specified, pvp is calculated for all word classes.
# 'target' specifies whether to calculate dependency relation probabilities ('deprel') or part-of-speech probabilities ('pos'). Default is 'deprel'.
pvp = analyzer.calculate_pvp(input='NOUN', target='deprel', normalize=True)

pvp
>>> {'act as dependents': {'nmod': 0.1, 'nmod:poss': 0.2, 'nmod:tmod': 0.3, ...},
'act as governors': {...}}
```
The return format is a dictionary `dict`, where the `key` indicates whether the word is acting as a governor or a dependent, and the `value` is a dictionary containing the corresponding dependency relations and their probabilities.

### Example 6: Converting Treebank Formats

```python
from quansyn.depval import Converter

# Load the treebank
treebank_path = 'path/to/treebank.conllu'
converter = Converter(open(treebank_path, encoding='utf-8'))

# Convert the format
# The first argument is the source format, and the second argument is the target format
converted_treebank = converter.style2style('conllu', 'pmt')

# Save the result
# converter.save(treebank, treebank_format, output_path)
converter.save(converted_treebank, 'pmt', 'output_path/to/treebank.txt')
```

### Example 7: Building a Linguistic Network

```python
from quansyn.lingnet import load_edges
import networkx as nx

# Load the treebank
treebank_path = 'path/to/treebank.conllu'
treebank = open(treebank_path, encoding='utf-8')

# Extract dependency relations as edges, or co-occurrence relations by setting mode to 'adjacency'
# edges is a list of tuples, where each tuple is (head, dependent)
edges = conllu2edges(treebank, mode='dependency')

# Build the network using NetworkX
G = nx.Graph(edges)
```

### Example 8: Fitting Parameters

```python
from quansyn.lawfitter import fit

# Load the data
data = ([1,2,3,4,5],[0.1,0.2,0.3,0.4,0.5])

# Fit built-in distributions
fit(data, 'zipf')

# Fit a custom distribution
def custom_dist(x, a):
    return a / (x ** 2)

fit(data, customized_law=custom_dist)

>>> {'paras': [0.123456789], 'r^2': -16.229684950920042}
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