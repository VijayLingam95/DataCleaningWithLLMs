# DataCleaningWithLLMs
CS 386D Project

#### Note

The `requirements.txt` file contains all the required libraries to run our scripts and can be installed using:

```
pip install -r requirements.txt
```

#### Generating Error Files

The main script for generating errors is present in `create_errors.py`. An example command is pasted below:

```
python create_errors.py --clean_file datasets/sales_product/clean.csv --save_file datasets/sales_product/dirty_5.csv --erridx_file datasets/sales_product/erridx_5.pkl --err_perc 5
```

The arguments are briefly explained below:
1. `--clean_file`: path to the gold standard (clean) data file. Expected in a .CSV format.
2. `--save_file`: save path to the output file containing the corrupted datafile. The extension .csv is required.
3. `--erridx_file`: save path to the file containing error indices for every error type. This will be helpful for verifying and computing different metrics for individual error types (e.g. missing values, outliers)
4. `--err_perc`: an integer specifying the percentage of errors (perturbations) to be induced for each error type. For instance, if there 3 error types, and the err_perc is 5, 15% (5% for each error type) of the total cells in the datafile will be corrupted.

Our current script supports 6 types of erros: i) 'mv': missing values, ii) 'outlier', iii) 'date format', iv) 'domain', v) 'typos', vi) 'fn': functional constraints. Data format and functional constraints are specific to a dataset, and should be defined by the user (if required). 

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




