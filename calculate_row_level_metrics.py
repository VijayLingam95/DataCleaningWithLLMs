import argparse
import pickle
import pandas as pd

def is_equal(x, y):
    try:
        if int(float(x)) != int(float(y)):
            return False
    except ValueError:
        if str(x).strip() != str(y).strip():
            return False
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--preds_file', type=str, required=True)
    parser.add_argument('--clean_file', type=str, required=False)
    parser.add_argument('--erridx_file', type=str, required=False)

    args = parser.parse_args()

    run = 'identify' if 'identify' in args.preds_file else 'correct'

    preds = pickle.load(open(args.preds_file, 'rb'))
    err_idx = pickle.load(open(args.erridx_file, 'rb'))
    clean_df = pd.read_csv(args.clean_file)

    if run == 'identify':
        total_rows = len(clean_df)
        preds_row = set([i[0] for i in preds])
        target_row = set([i[0] for v in err_idx.values() for i in v])
        tp = len(preds_row.intersection(target_row))
        fp = len(preds_row-target_row)
        fn = len(target_row-preds_row)
        accuracy = round(100*(1-((fp+fn)/total_rows)), 2)
        precision = round(100*tp/(tp+fp), 2)
        recall = round(100*tp/len(target_row), 2)
        f1 = round(2*precision*recall/(precision+recall), 2)
        print(f"Row level metrics for error identification: \nAccuracy: {accuracy} \nPrecision: {precision} \nRecall: {recall} \nF1: {f1}")
        
    else:
        errors = set([i[0] for v in err_idx.values() for i in v])
        assert len(preds) == len(clean_df)
        clean_rows = []
        for i, row in clean_df.iterrows():
            clean_batch = clean_df.iloc[i].values.tolist()
            clean_rows.append(clean_batch)
        cleaned_correctly = 0
        clean_unchanged = 0
        errors_not_corrected = 0
        clean_changed = 0
        for i in range(len(clean_rows)):
            assert len(clean_rows[i]) == len(preds[i])
            clean = True
            for j in range(len(clean_rows[i])):
                if is_equal(clean_rows[i][j], preds[i][j]):
                    continue
                else:
                    clean = False
                    break
            if clean and i+1 in errors:
                cleaned_correctly += 1
            elif clean and i+1 not in errors:
                clean_unchanged += 1
            elif not clean and i+1 in errors:
                errors_not_corrected += 1
            else:
                clean_changed += 1
        accuracy = round(100*(cleaned_correctly+clean_unchanged)/(len(clean_rows)), 2)
        perc_errors_cleaned = round(100*cleaned_correctly/(len(errors)), 2)
        print(f"Row level metrics for error correction: \nAccuracy: {accuracy} \n% errors cleaned: {perc_errors_cleaned}")
