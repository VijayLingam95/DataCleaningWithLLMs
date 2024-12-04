from error_generator import Explicit_Missing_Value
from error_generator import Implicit_Missing_Value
from error_generator import Typo_Butterfingers
from error_generator import List_selected
from error_generator import Error_Generator
from error_generator import Read_Write
from error_generator.strategies.switch_value.outlier_integer.outlier_integer import Outlier_Integer
from error_generator.strategies.switch_value.switch_relationship.Switch_Relationship import Switch_Relationship, Switch_City, Switch_DateFormat
from error_generator.strategies.switch_value.random_domain.Random_Domain import Random_Domain
import pickle
import argparse

def process_indices(indices, error_type):
    indices_set = set()
    for i in indices:
        indices_set.add((i[0],i[1]))
    assert len(indices_set) == len(indices)
    return {error_type: indices_set}

def check_overlap(indices):
    all = set()
    for v in indices.values():
        si = set(v)
        assert len(all.intersection(si)) == 0, breakpoint()
        all = all.union(si)
    return len(all)

def create_typos(dataset, selector, generator, perc, mc):
    mymethod=Typo_Butterfingers(prob=0.1)
    new_dataset, indices=generator.error_generator(method_gen=mymethod,selector=selector,percentage=perc,dataset=dataset,mute_column=mc)
    
    return new_dataset, indices

def create_missing_data(dataset, selector, generator, perc, mc):
    mymethod=Implicit_Missing_Value(dic={
                "0":"",
                "1":"null",
                "2":"?",
                "3":"NULL",
                "4":"unknown",
                "5":'""',
                "6":'N/A',
    })

    new_dataset, indices=generator.error_generator(method_gen=mymethod,selector=selector,percentage=perc,dataset=dataset,mute_column=mc)

    return new_dataset, indices

def create_outlier(dataset, selector, generator, perc, mc):
    mymethod = Outlier_Integer()
    new_dataset, indices=generator.error_generator(method_gen=mymethod,selector=selector,percentage=perc,dataset=dataset,mute_column=mc)

    return new_dataset, indices

def create_fn(dataset, selector, generator, perc, mc):
    mymethod = Switch_Relationship()
    new_dataset, indices = generator.error_generator(method_gen=mymethod,selector=selector,percentage=perc,dataset=dataset,mute_column=mc)

    return new_dataset, indices

def create_fn_sales(dataset, selector, generator, perc, mc):
    mymethod = Switch_City()
    new_dataset, indices = generator.error_generator(method_gen=mymethod,selector=selector,percentage=perc,dataset=dataset,mute_column=mc)

    return new_dataset, indices

def create_fn_dateformat(dataset, selector, generator, perc, mc):
    mymethod = Switch_DateFormat()
    new_dataset, indices = generator.error_generator(method_gen=mymethod,selector=selector,percentage=perc,dataset=dataset,mute_column=mc)

    return new_dataset, indices

def create_domain(dataset, selector, generator, perc, mc):
    mymethod = Random_Domain()
    new_dataset, indices=generator.error_generator(method_gen=mymethod,selector=selector,percentage=perc,dataset=dataset,mute_column=mc)
    
    return new_dataset, indices


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--clean_file', type=str, required=True)
    parser.add_argument('--save_file', type=str, required=True)
    parser.add_argument('--erridx_file', type=str, required=True)
    parser.add_argument('--err_perc', type=int, required=True)

    args = parser.parse_args()

    dataset, dataframe = Read_Write.read_csv_dataset(args.clean_file)

    selector = List_selected()
    generator = Error_Generator()

    all_indices = {}
    # all_adults_errors = [('typos', create_typos, 6, [0, 1, 9]), \
    #               ('mv', create_missing_data, 6, [0]), \
    #               ('outlier', create_outlier, 6, [0, 2, 3, 4, 5, 6, 7, 8, 10, 11]), \
    #               ('fn', create_fn, 6, [0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11]), \
    #               ('domain', create_domain, 6, [0])]
    
    all_sales_product_errors = [('mv', create_missing_data, args.err_perc, [0, 1, 2, 3, 4, 5, 6]), \
                  ('outlier', create_outlier, args.err_perc, [0, 1, 3, 4, 5, 6, 7, 8]), \
                  ('fn', create_fn_sales, args.err_perc, [0, 1, 2, 3, 4, 5, 6, 8]), \
                  ('date format', create_fn_dateformat, args.err_perc, [0, 1, 2, 3, 5, 6, 7, 8]), \
                  ('domain', create_domain, args.err_perc, [0, 1, 2, 3, 4, 5, 6]), \
                  ('typos', create_typos, args.err_perc, [0, 2, 3])]
    
    for error_type, f, perc, mc in all_sales_product_errors:
        dataset, indices = f(dataset, selector, generator, perc, mc)
        all_indices.update(process_indices(indices, error_type))
    
    num_total_err = check_overlap(all_indices)
    print(f"% of corrupted cells: {num_total_err/(len(dataset[0]*(len(dataset)-1)))}")

    Read_Write.write_csv_dataset(args.save_file, dataset)
    print(f'Saved {len(dataset)} corrupted rows to {args.save_file}')
    f_out = open(args.erridx_file, 'wb')
    pickle.dump(all_indices, f_out)
    f_out.close()
    print(f'Saved error types and indices to {args.erridx_file}')
