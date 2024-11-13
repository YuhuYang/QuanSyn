
### Depval 模块

#### 类名：`DepValAnalyzer`

**参数：**

- `treebank` (str) - 已经打开的 conllu 格式树库。

---

#### 方法 1：`calculate_dep_metrics`

**参数：**

- `metrics` (List[str]) - 需要计算的指标类型，默认为 `['dd', 'hd', 'ddir', 'v']`。

**返回值：**

返回一个字典，包含各个指标计算结果：

- `dd` (List) - 依存距离。
- `hd` (List) - 层级距离。
- `ddir` (List) - 依存方向。
- `v` (List) - 动态价。

---

#### 方法 2：`calculate_sent_metrics`

**参数：**

- `metrics` (List[str]) - 需要计算的指标，默认为 `['mdd', 'mhd', 'mhdd', 'tdl', 'sl', 'mv', 'vk', 'tw', 'th', 'hi', 'hf']`。

**返回值：**

返回一个字典，包含每个句子的指标。

---

#### 方法 3：`calculate_text_metrics`

**参数：**

- `metrics` (List[str]) - 需要计算的指标，默认为 `['mdd', 'mhd', 'mhdd', 'mtdl', 'msl', 'mv', 'vk', 'mtw', 'mth', 'hi', 'hf']`。

**返回值：**

返回一个字典，包含整个文本的指标结果。

---

#### 方法 4：`calculate_distributions`

**参数：**

- `metrics` (List[str]) - 需要计算的分布度量，默认为 `['dd', 'hd', 'sl', 'v', 'tw', 'th', 'deprel', 'pos']`。
- `normalize` (bool) - 是否进行归一化处理，默认为 `False`。

**返回值：**

返回一个字典，包含每个指标的分布数据。

---

类名：`Converter`

**参数：**

- `treebank` (str) - 已经打开的树库。

---

#### 方法 1：`style2style`

**参数：**

- `from_style` (str) - 原格式。
- `to_style` (str) - 目标格式。

**返回值：**

返回转换后的树库。

---

#### 方法 2：`save`

**参数：**

- `treebank` (str) - 已经转换的树库。
- `style` (str) - 目标格式。
- `path` (str) - 保存路径。

**返回值：**

无。

---

### Lingnet 模块

#### 类名：`Network`

**参数：**

- `treebank` (str) - 已经打开的树库。

---

#### 方法 1：`get_Deprel`


**返回值：**

返回依存边列表。

---

#### 方法 2：`get_Bigram`

**返回值：**

返回同现边列表。

---

#### 函数：`conllu2edges`

**参数：**

- `treebank` (str) - 已经打开的树库。
- `mode` (str) - 边类型，默认为 `dependency`。

**返回值：**

返回边列表。

---

#### 函数：`fitPowerLaw`

**参数：**

- `data` (List) - 数据，度序列。

**返回值：**

返回拟合结果。

---

### Lawfitter 模块

#### 类名：`fit`

**参数：**

- `data`: (tuple[List,list]) - 数据，包括两个列表的元组。
- `law_name`：str = None
- `variant`：str = None
- `customized_law`：function = None

**返回值：**

返回拟合结果。