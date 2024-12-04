
import random


class Outlier_Integer(object):
    def __init__(self,name="Outlier_Integer"):
        self.name=name
    
        
    def run(self,row,col,selected_value,dataset):
        rand = random.randint(0, 3)
        if rand == 0:
            return random.randint(-9999999, 0)
        elif rand == 1:
            return random.randint(-100, 0)
        elif rand == 2:
            return random.randint(200, 300)
        else:
            return random.randint(200, 9999999)