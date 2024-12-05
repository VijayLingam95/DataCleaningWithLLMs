# DataCleaningWithLLMs
## CS 386D Project

#### Setup

The `requirements.txt` file contains all the required libraries to run our scripts and can be installed using:

```bash
pip install -r requirements.txt
```

In addition, you must also install the error-generator package. Follow the below instructions:
```bash
cd error-generator
python setup.py install
```



#### Generating Error Files

The main script for generating errors is present in `create_errors.py`. An example command is pasted below:

```bash
python create_errors.py --clean_file datasets/sales_product/clean.csv --save_file datasets/sales_product/dirty_5.csv --erridx_file datasets/sales_product/erridx_5.pkl --err_perc 5
```

The arguments are briefly explained below:
1. `--clean_file`: path to the gold standard (clean) data file. Expected in a .CSV format.
2. `--save_file`: save path to the output file containing the corrupted datafile. The extension .csv is required.
3. `--erridx_file`: save path to the file containing error indices for every error type. This will be helpful for verifying and computing different metrics for individual error types (e.g. missing values, outliers)
4. `--err_perc`: an integer specifying the percentage of errors (perturbations) to be induced for each error type. For instance, if there 3 error types, and the err_perc is 5, 15% (5% for each error type) of the total cells in the datafile will be corrupted.

Our current script supports 6 types of erros: i) 'mv': missing values, ii) 'outlier', iii) 'date format', iv) 'domain', v) 'typos', vi) 'fn': functional constraints. Date format and functional constraints are specific to a dataset, and should be defined by the user (if required). 

We provide an example code below for the 'Sales Product' dataset (can be found in `datasets` folder).


```python
    all_sales_product_errors = [('mv', create_missing_data, args.err_perc, [0, 1, 2, 3, 4, 5, 6]), \
                  ('outlier', create_outlier, args.err_perc, [0, 1, 3, 4, 5, 6, 7, 8]), \
                  ('fn', create_fn_sales, args.err_perc, [0, 1, 2, 3, 4, 5, 6, 8]), \
                  ('date format', create_fn_dateformat, args.err_perc, [0, 1, 2, 3, 5, 6, 7, 8]), \
                  ('domain', create_domain, args.err_perc, [0, 1, 2, 3, 4, 5, 6]), \
                  ('typos', create_typos, args.err_perc, [0, 2, 3])]
```
In this code block, we defined 6 error types that we outline above. Each error type is defined as 4-tuple containing ```(error-type string, name of the function that introduces the error, error percentage, mute columns)```.
Mute columns correspond to column IDS that should be ignored while introducing the error type. For e.g., outliers cannot be introduced to a column containing strings. 

Error types such as 'mv', 'outlier', 'domain', and 'typos' can be utilized directly, provided that the mute-columns are correctly specified.

We briefly explain how we defined the functions to introduce functional constraints and date format errors for the Sales Product dataset. A similar procedure can be followed for your own dataset.

```python3
class Switch_City(object):
    def __init__(self,name="Outlier_Integer"):
        self.name=name
    
        
    def run(self,row,col,selected_value,dataset):
        """
        Returns a corrupted value to be inserted in dataset(row, column).
        This specific function is designed for swapping city names in the Sales Product dataset.

        Args:
        row: (int) row number
        col: (int) column number
        selected value: (str) current (clean) value present in dataset(row, col)
        dataset: (List[List]]) input dataset (clean)
        
        Returns: (any) corrupted value
        """
        assert dataset[row][col] == selected_value
        cities = list(set([dataset[i][col] for i in range(len(dataset))])-set(selected_value))
        other_city = random.choice(cities) 
        while other_city.lower().strip() == selected_value.lower().strip():
            other_city = random.choice(cities)
        return other_city


def create_fn_sales(dataset, selector, generator, perc, mc):
    mymethod = Switch_City()
    new_dataset, indices = generator.error_generator(method_gen=mymethod,selector=selector,percentage=perc,dataset=dataset,mute_column=mc)

    return new_dataset, indices
```
In the Sales Product dataset, the City column must align with the city mentioned in the Address column. Violations are introduced by replacing the City value with a different city from the dataset. The annotated code block above serves as a guide, providing steps to define your own error type by simply defining a new `mymethod`. The same structure must be preserved (Class definition should contain a ```run(self,row,col,selected_value,dataset)``` method).



#### Running LLMs and Generating Metrics

The main script for running an LLM is present in `run_api.py`. An example command is pasted below:

We use OpenAI models for our experiments. Paste the API key in line::8.


```bash
# For error identification
python run_api.py --clean_file datasets/sales_product/clean.csv --dirty_file datasets/sales_product/dirty_2.csv --erridx_file datasets/sales_product/erridx_2.pkl --run identify --stage 3 --err_perc 2

# For error correction
python run_api.py --clean_file datasets/sales_product/clean.csv --dirty_file datasets/sales_product/dirty_2.csv --erridx_file datasets/sales_product/erridx_2.pkl --run correct --stage 3 --err_perc 2
```

The arguments are briefly explained below:
1. `--clean_file`: path to the gold standard (clean) data file. Expected in a .CSV format.
2. `--dirty_file`: path to corrupted data file (generated by running `create_errors.py`).
3. `--erridx_file`: path to the file containing error indices for every error type (generated by running `create_errors.py`).
4. `--run`: choose from [identify, correct]
5. `--stage`: choose a prompting strategy from {0,1,2,3}. We summarize these strategies below.
6. `--err_perc`: percentage of errors in the dirty file. This is only used for naming convention for the output files.

#### Prompting Strategies

- **Stage 0:** Instruction-Only Prompt
This prompt provides basic instructions for tasks like error identification or data cleaning. It specifies the task and outlines input-output formats but lacks details about the data structure. Below is an example for a sales product dataset. This prompt is dataset independent. Refer to the below section of code for exact prompts.
https://github.com/VijayLingam95/DataCleaningWithLLMs/blob/b2699911e2229ef478113f452a08c74e142f8bbf/run_api.py#L12-L34

- **Stage 1:** Column-Aware Prompt
Building on Prompt 1, this prompt includes column names to offer a basic understanding of the dataset's structure. The additional column information remains consistent for both error identification and correction. This is a dataset specific prompt. Find below the exact prompt we used for the Sales Product dataset.
https://github.com/VijayLingam95/DataCleaningWithLLMs/blob/b2699911e2229ef478113f452a08c74e142f8bbf/run_api.py#L35-L36

- **Stage 2:** Metadata-Aware Prompt
Extending Prompt 2, this prompt provides metadata for each column, such as descriptions, expected data types, and formatting rules. This added detail enhances the LLM's ability to interpret data and detect errors effectively. This is a dataset specific prompt. An example prompt is included below:
https://github.com/VijayLingam95/DataCleaningWithLLMs/blob/b2699911e2229ef478113f452a08c74e142f8bbf/run_api.py#L37-L48


- **Stage 3:** Few-Shot Prompting
Expanding on Prompt 3, this prompt incorporates input-output examples to demonstrate expected behavior for error identification and data cleaning. These examples utilize few-shot learning to guide the model and improve performance. This is a dataset specific prompt. Refer to the below code to see how we define the input-output few shot examples for the Sales Product dataset.
https://github.com/VijayLingam95/DataCleaningWithLLMs/blob/b2699911e2229ef478113f452a08c74e142f8bbf/run_api.py#L50-L62

#### Metrics 
1. Error identification: for this task, we log recall for all individual error types and overall accuracy, precision, recall and F1 scores.
2. Error correction: for each error type we log i) total-errors, ii) errors corrected, iii) unsuccessful corrections, and iv) unchanged errors. At a global level, we additionally compute i) total non erroneous cells, ii) non erroneous cells that were changed, and iii) non erroneous cells that were unchanged.

The metrics are saved to an output file (`results_*.pkl`) and also displayed in the console log. For the error correction task, the LLM's output is additionally saved to a CSV file.

### Note
The prompts in this work are designed to generate outputs in a specific format, supported by custom parsers we developed. Any changes to the prompts may necessitate adjustments or refinements to the parsers.






