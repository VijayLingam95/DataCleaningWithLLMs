import pandas as pd
import pickle
import argparse
from copy import deepcopy
from openai import OpenAI
from tqdm import tqdm

OPEN_AI_KEY = "<add-your-api-key>"
client = OpenAI(api_key=OPEN_AI_KEY)


BASE_PROMPT_IDENTIFY = """You are a data quality expert. Your task is to analyze the following tabular data and identify any errors in the rows and columns. The input data is formatted with column values separated by '\t' and rows separated by '\n'.
Analyze each cell and determine if there are any errors. {} 
{}
Input data:
{}

If you find errors, report each error by specifying its row number and column number (both indexed starting from 1) in the input data. Use the following format for each error, with multiple errors separated by '\n'
RowNumber,ColumnNumber \nRowNumber,ColumnNumber

If no errors are found, respond with "No errors detected."
DO NOT OUTPUT ANY OTHER INFORMATION OR WORDS. DOUBLE CHECK YOUR OUTPUT AND MAKE SURE TO IT ONLY CONTAINS VALID ROW AND COLUMN NUMBERS THAT CAN ACTUALLY BE INDEXED IN THE INPUT DATA. 
Output:"""

BASE_PROMPT_CORRECT = """You are a data cleaning expert. Your task is to fix errors in the following tabular data. The input data is formatted with column values separated by '\t' and rows separated by '\n'.
Analyze each cell and if there are any errors in the input, fix them and output the cleaned version of all the rows.  {} 
{} 
Input data:
{}

If you find errors, fix them and output the cleaned version (also containing the cells without errors copied over from input) of all rows in the same format as input data where each row is separated by '\n' and each column is separated by '\t'.
DO NOT OUTPUT ANY OTHER INFORMATION OR WORDS OR SPECIAL CHARACTERS OTHER THAN THE ROW AND COLUMN SEPARATOR. MAKE SURE THAT THE NUMBER OF ROWS AND COLUMNS IN OUTPUT MATCHES THAT OF THE INPUT.
Output:
"""
COLUMN_NAMES_PROMPT = """The input data contains the following columns in the same order: Order ID, Product, Quantity Ordered, Price, Order Date, Time, Purchase Address, City, and Product Type.
"""
COLUMN_METADATA_PROMPT = """The description of the input data columns and their format is given below:
Order ID: A large integer value denoting the order ID. For example, 211806.
Product: A detailed name of the electronic item. For example, 27in 4K Gaming Monitor.
Quantity Ordered: The quantity of the product ordered. Shouldn't be too large. For example, 2. 
Price: The price of the product. For example, 3.84, 700.0 etc.
Order Date: The date when the order was placed. Should be in the dd-mm-yyyy format. For example, 26-03-2019.
Time: The time when the order was placed. Should be in the AM/PM format. For example, 06:10 AM.
Purchase Address: The exact delivery address of the order. Should contain a state code and zip code at the end. For example, 35 Elm St, New York City, NY 10001.
City: The delivery address city. Should be the same city which appears in the Purchase Address column. For example, New York City.
Product Type: The type of product. For example, Laptop, TV, etc.
The columns in input data appear in the same order as given above.
"""

FEW_SHOT_PROMPT_CORRECT = """Here are two examples of dirty rows(Input Data) followed by their corresponding clean versions(Output):
Input Data:
164739\t27in 4K Gaming Monitor\t-96\t389.99\t03-25-2019\t7:15 PM\t416 Church St, San Francisco, CA 94016\tNULL\t300.0\n239280\tUSB-C Charging Cable\t1\t11.95\t08-08.2019\t7:10 PM\t677 Meadow St, Atlanta, GA 30301\tN/A\tCagle
Output:
164739\t27in 4K Gaming Monitor\t1\t389.99\t25-03-2019\t7:15 PM\t416 Church St, San Francisco, CA 94016\t San Francisco\tMonitor\n239280\tUSB-C Charging Cable\t1\t11.95\t08-08-2019\t7:10 PM\t677 Meadow St, Atlanta, GA 30301\t Atlanta\tCable
"""

FEW_SHOT_PROMPT_IDENTIFY = """Here are two examples of dirty rows(Input Data) followed by the row and column numbers of cells with errors:
Input Data:
164739\t27in 4K Gaming Monitor\t-96\t389.99\t03-25-2019\t7:15 PM\t416 Church St, San Francisco, CA 94016\tNULL\t300.0\n239280\tUSB-C Charging Cable\t1\t11.95\t08-08.2019\t7:10 PM\t677 Meadow St, Atlanta, GA 30301\tN/A\tCagle
Output:
1,3\n1,5\n1,8\n1,9\n2,5\n2,7\n2,8
"""

def get_prompt(input_data, type, stage):
    prompt = None
    if type == 'identify':
        prompt = BASE_PROMPT_IDENTIFY
        fs_prompt = FEW_SHOT_PROMPT_IDENTIFY
    else:
        prompt = BASE_PROMPT_CORRECT
        fs_prompt = FEW_SHOT_PROMPT_CORRECT

    if stage == 0:
        prompt = prompt.format('', '', input_data)
    elif stage == 1:
        prompt = prompt.format(COLUMN_NAMES_PROMPT, '', input_data)
    elif stage == 2:
        prompt = prompt.format(COLUMN_METADATA_PROMPT, '', input_data)
    elif stage == 3:
        prompt = prompt.format(COLUMN_METADATA_PROMPT, fs_prompt, input_data)
    else:
        raise ValueError("Incorrect stage provided")
    
    return prompt

def get_response(input):
    response = client.chat.completions.create(model="gpt-4o-mini",
                                         messages=[{"role": "system", "content": "You are a helpful assistant."},
                                                   {"role": "user", "content": input}],
                                         max_tokens=1000,
                                         temperature=0)
    response = response.choices[0].message.content.strip()
    response = response.replace("```", '')
    response = response.strip()
    return response

def parse_response_identify(response, offset):
    output = []
    if 'no errors' in response.lower():
        return output
    response = response.strip().split('\n')
    for row in response:
        if not row.strip():
            continue
        r = row.split(',')
        try:
            r = [int(i.strip()) for i in r]
            assert len(r) == 2
            r[0] = r[0]+offset
            r[1] = r[1]-1
            output.append((r[0], r[1]))
        except:
            continue
    return output

def parse_response_correct(response, BS, num_columns):
    bad_indices = []
    output = []
    response = response.split('\n')
    for i, row in enumerate(response):
        r = row.split('\t')
        r = [j.strip() for j in r]
        if len(r) < num_columns:
            bad_indices.append(i)
            r.extend(['null' for _ in range(num_columns-len(r))])
        elif len(r) > num_columns:
            while len(r) != num_columns:
                if '' in r:
                    r.remove('')
                else:
                    r = r[:-1]
        output.append(r)
    while len(output) > BS:
        if len(bad_indices) > 0:
            del output[bad_indices[0]]
            del bad_indices[0]
        else:
            del output[-1]

    return output
    
def compute_results_identify(pred, target, df):
    pred_set = set(pred)
    # assert len(pred) == len(pred_set), breakpoint()
    results = {}
    if type(target) == dict:
        all_err_idx = set()
        for err_type, err_idx in target.items():
            all_err_idx = all_err_idx.union(err_idx)
            tpe = len(err_idx.intersection(pred_set))
            results.update({err_type: {'Recall': 100*tpe/len(err_idx)}})
        tp = len(all_err_idx.intersection(pred_set))
        fp = len(pred_set - all_err_idx)
        fn = len(all_err_idx - pred_set)
        total_errs = len(all_err_idx)

    else:
        tp = len(target.intersection(pred_set))
        fp = len(pred_set - target)
        fn = len(target - pred_set)
        total_errs = len(target)
    
    precision = tp/(tp+fp)
    recall = tp/total_errs
    results.update(
        {
            'Accuracy': 100*(1-((fp+fn)/df.size)),
            'Precision': 100*precision,
            'Recall': 100*recall,
            'F1': 100*2*precision*recall/(precision+recall)
        }
    )
    return results

def is_equal(x, y):
    try:
        if int(float(x)) != int(float(y)):
            return False
    except ValueError:
        if str(x).strip() != str(y).strip():
            return False
    return True

def compute_results_correct(input, pred, target, erridx):
    err_type_stats = {}
    stats = {
        'total_errs': 0,
        'total_non_errs': 0,
        'errs_corrected': 0,
        'errs_changed_incorrectly': 0,
        'errs_not_corrected': 0,
        'non_errs_changed': 0,
        'non_errs_unchanged': 0,
    }
    err_type_stats['all'] = deepcopy(stats)
    err_type = None
    if type(erridx) == dict:
        err_type = {}
        for k, v in erridx.items():
            err_type_stats[k] = deepcopy(stats)
            for i in v:
                err_type[i] = k

    num_columns = len(input[0])
    total_errs = 0
    errs_corrected = 0
    errs_changed_incorrectly = 0
    errs_not_corrected = 0
    for i in tqdm(range(len(input))):
        for j in range(num_columns):
            is_err = not is_equal(input[i][j], target[i][j])
            if is_err:
                typ = 'all'
                if err_type is not None:
                    typ = err_type[(i+1,j)]
                
                err_type_stats[typ]['total_errs'] += 1
                total_errs += 1
                # err_type_stats['all']['total_errs'] += 1
                if is_equal(pred[i][j], target[i][j]):
                    err_type_stats[typ]['errs_corrected'] += 1
                    errs_corrected += 1
                    # err_type_stats['all']['errs_corrected'] += 1
                elif not is_equal(pred[i][j], target[i][j]) and not is_equal(pred[i][j], input[i][j]):
                    err_type_stats[typ]['errs_changed_incorrectly'] += 1
                    errs_changed_incorrectly += 1
                    # err_type_stats['all']['errs_changed_incorrectly'] += 1
                else:
                    err_type_stats[typ]['errs_not_corrected'] += 1
                    errs_not_corrected += 1 
                    # err_type_stats['all']['errs_not_corrected'] += 1
            else:
                err_type_stats['all']['total_non_errs'] += 1
                try:
                    if not is_equal(pred[i][j], input[i][j]):
                        err_type_stats['all']['non_errs_changed'] += 1
                    else:
                        err_type_stats['all']['non_errs_unchanged'] += 1
                except:
                    breakpoint()

    err_type_stats['all']['total_errs'] = total_errs
    err_type_stats['all']['errs_corrected'] = errs_corrected
    err_type_stats['all']['errs_changed_incorrectly'] = errs_changed_incorrectly
    err_type_stats['all']['errs_not_corrected'] = errs_not_corrected
    return err_type_stats

def compute_err_indices(df_clean, df_dirty):
    err_indices = set()
    for col in df_dirty.columns:
        col_j = df_dirty.columns.get_loc(col)
        for i, row in df_dirty.iterrows():
            if not is_equal(df_dirty.iat[i, col_j], df_clean.iat[i, col_j]):
                err_indices.add((i+1, col_j))
            # try:
            #     if int(float(df_dirty.iat[i, col_j])) != int(float(df_clean.iat[i, col_j])):
            #         err_indices.add((i+1, col_j))
            # except ValueError:
            #     if df_dirty.iat[i, col_j].strip() != df_clean.iat[i, col_j].strip():
            #         err_indices.add((i+1, col_j))
    return err_indices

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--clean_file', type=str, required=True)
    parser.add_argument('--dirty_file', type=str, required=True)
    parser.add_argument('--erridx_file', type=str, required=False)
    parser.add_argument('--run', type=str, required=True)
    parser.add_argument('--stage', type=int, required=True)
    parser.add_argument('--err_perc', type=int, required=True)

    args = parser.parse_args()

    assert args.run in ['identify', 'correct'], "Run should be one of 'identify', 'correct'!"

    clean_df = pd.read_csv(args.clean_file, keep_default_na=False)
    dirty_df = pd.read_csv(args.dirty_file, keep_default_na=False)
    err_indices = None
    if args.erridx_file:
        err_indices = pickle.load(open(args.erridx_file, 'rb'))
    else:
        err_indices = compute_err_indices(clean_df, dirty_df)
    
    if args.run == 'identify':
        BATCH_SIZE = 10
    else:
        BATCH_SIZE = 5

    STAGE = args.stage

    inputs = []
    preds = []

    if args.run == 'identify':
        target = err_indices
    else:
        target = []

    print("Running API Calls")
    for i in tqdm(range(0, len(dirty_df), BATCH_SIZE)):
        dirty_batch = dirty_df.iloc[i:i + BATCH_SIZE]
        clean_batch = clean_df.iloc[i:i + BATCH_SIZE].values.tolist()
        dirty_input = dirty_batch.to_csv(sep='\t', index=False, header=None)
        dirty_batch = dirty_batch.values.tolist()
        inputs.extend(dirty_batch)
        # print("Dirty: ", repr(dirty_batch))
        # print("Clean: ", clean_batch)
        prompt = get_prompt(dirty_input, args.run, STAGE)
        # print(f"Prompt: {prompt}")
        response = get_response(prompt)

        if args.run == 'identify':
            parsed_response = parse_response_identify(response, i)
            preds.extend(parsed_response)
        else:
            target.extend(clean_batch)
            parsed_response = parse_response_correct(response, len(dirty_batch), len(clean_df.columns))
            preds.extend(parsed_response)
    
    print("Saving outputs")
    output_file = f'outputs_err{args.err_perc}_{args.run}_stage{args.stage}.pkl'
    f_out = open(output_file, 'wb')
    pickle.dump(preds, f_out)
    f_out.close()
    
    print("Running evaluations")
    if args.run == 'identify':
        results = compute_results_identify(preds, target, clean_df)
    else:
        results = compute_results_correct(inputs, preds, target, err_indices)

    print(f'\nResults for {args.run}: \n')
    for k, v in results.items():
        print(f'{k}: {v}')

    result_file = f'results_err{args.err_perc}_{args.run}_stage{args.stage}.pkl'
    f_out = open(result_file, 'wb')
    pickle.dump(results, f_out)
    f_out.close()

    if args.run == 'correct':
        preds_file = f'preds_err{args.err_perc}_{args.run}_stage{args.stage}.csv'
        preds_df = pd.DataFrame(preds, columns=list(clean_df.columns))
        preds_df.to_csv(preds_file, index=False)
    # breakpoint()
