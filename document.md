### Depval Module

#### Class: `DepValAnalyzer`

**Parameters:**

- `treebank` (str) - Opened conllu format treebank.

---

#### Method 1: `calculate_dep_metrics`

**Parameters:**

- `metrics` (List[str]) - The types of metrics to calculate, default is `['dd', 'hd', 'ddir', 'v']`.

**Return Value:**

Returns a dictionary containing the results of various metrics:

- `dd` (List) - Dependency distance.
- `hd` (List) - Hierarchical distance.
- `ddir` (List) - Dependency direction.
- `v` (List) - Dynamic value.

---

#### Method 2: `calculate_sent_metrics`

**Parameters:**

- `metrics` (List[str]) - The metrics to calculate, default is `['mdd', 'mhd', 'mhdd', 'tdl', 'sl', 'mv', 'vk', 'tw', 'th', 'hi', 'hf']`.

**Return Value:**

Returns a dictionary containing the metrics for each sentence.

---

#### Method 3: `calculate_text_metrics`

**Parameters:**

- `metrics` (List[str]) - The metrics to calculate, default is `['mdd', 'mhd', 'mhdd', 'mtdl', 'msl', 'mv', 'vk', 'mtw', 'mth', 'hi', 'hf']`.

**Return Value:**

Returns a dictionary containing the metrics for the entire text.

---

#### Method 4: `calculate_distributions`

**Parameters:**

- `metrics` (List[str]) - The distribution metrics to calculate, default is `['dd', 'hd', 'sl', 'v', 'tw', 'th', 'deprel', 'pos']`.
- `normalize` (bool) - Whether to normalize the data, default is `False`.

**Return Value:**

Returns a dictionary containing the distribution data for each metric.

---

Class: `Converter`

**Parameters:**

- `treebank` (str) - Opened treebank.

---

#### Method 1: `style2style`

**Parameters:**

- `from_style` (str) - Original format.
- `to_style` (str) - Target format.

**Return Value:**

Returns the converted treebank.

---

#### Method 2: `save`

**Parameters:**

- `treebank` (str) - Converted treebank.
- `style` (str) - Target format.
- `path` (str) - Save path.

**Return Value:**

None.

---

### Lingnet Module

#### Class: `Network`

**Parameters:**

- `treebank` (str) - Opened treebank.

---

#### Method 1: `get_Deprel`

**Return Value:**

Returns a list of dependency edges.

---

#### Method 2: `get_Bigram`

**Return Value:**

Returns a list of co-occurrence edges.

---

#### Function: `conllu2edges`

**Parameters:**

- `treebank` (str) - Opened treebank.
- `mode` (str) - Edge type, default is `dependency`.

**Return Value:**

Returns a list of edges.

---

#### Function: `fitPowerLaw`

**Parameters:**

- `data` (List) - Data, a degree sequence.

**Return Value:**

Returns the fitting results.

---

### Lawfitter Module

#### Class: `fit`

**Parameters:**

- `data`: (tuple[List, list]) - Data, a tuple containing two lists.
- `law_name`: str = None
- `variant`: str = None
- `customized_law`: function = None

**Return Value:**

Returns the fitting results.