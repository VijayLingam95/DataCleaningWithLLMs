
import random


class Random_Domain(object):
    def __init__(self,name="Outlier_Integer"):
        self.name=name
    
        
    def run(self,row,col,selected_value,dataset):

        rand_row = random.randint(0, len(dataset) - 1)
        
        rand_col = random.randint(0, len(dataset[rand_row]) - 1)

        while rand_col == col:
            rand_col = random.randint(0, len(dataset[rand_row]) - 1)

        return str(dataset[rand_row][rand_col])
        
        
