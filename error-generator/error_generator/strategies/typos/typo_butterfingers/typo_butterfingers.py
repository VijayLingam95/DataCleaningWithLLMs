
from error_generator.strategies.typos.typo_butterfingers.butterfingers import butterfinger


class Typo_Butterfingers(object):
    def __init__(self,name="Typo_Butterfingers",prob=0.6):
        self.name=name
        self.prob=prob


    def run(self,row,col,selected_value,dataset):
        temp = butterfinger(selected_value,prob=self.prob)
        return temp
