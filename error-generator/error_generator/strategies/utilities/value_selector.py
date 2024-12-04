import random

class Value_Selector(object):
    def __init__(self):
        self.value_selector_history=set()

    def number(self, dataset, percentage):
        number = int((percentage / 100.0) * (len(dataset[0]*(len(dataset)-1))))
        return number
    
    def select_value(self, dataset, number, mute_column):
        picked_value=[]
        all_columns = set(range(len(dataset[0])))
        select_columns = all_columns - set(mute_column)
        
        for i in range(number):
            prev_random_col = set()
            random_col = random.choice(list(select_columns))
            random_row = random.randint(1, len(dataset) - 1)
            num_tries = 1
            while (random_row, random_col) in self.value_selector_history:
                random_row = random.randint(1, len(dataset) - 1)
                num_tries += 1
                if num_tries >= len(dataset):
                    num_tries = 0
                    prev_random_col.add(random_col)
                    select_columns = select_columns - prev_random_col
                    if len(select_columns) > 0:
                        random_col = random.choice(list(select_columns - prev_random_col))
                    else:
                        raise RuntimeError("No other cells left to induce errors in.")
            
            self.value_selector_history.add((random_row, random_col))
            input_value = dataset[random_row][random_col]
            picked_value.append([random_row, random_col, input_value])

        return picked_value

