

import random


class Switch_Relationship(object):
    def __init__(self,name="Outlier_Integer"):
        self.name=name
    
        
    def run(self,row,col,selected_value,dataset):
        
        if "Male" in list(dataset[row]):
            return "Wife"
        else:
            return "Husband"
        
class Switch_City(object):
    def __init__(self,name="Outlier_Integer"):
        self.name=name
    
        
    def run(self,row,col,selected_value,dataset):
        assert dataset[row][col] == selected_value
        cities = list(set([dataset[i][col] for i in range(len(dataset))])-set(selected_value))
        other_city = random.choice(cities) 
        while other_city.lower().strip() == selected_value.lower().strip():
            other_city = random.choice(cities)
        return other_city
        
class Switch_DateFormat(object):
    def __init__(self,name="Outlier_Integer"):
        self.name=name
    
        
    def run(self,row,col,selected_value,dataset):
        assert dataset[row][col] == selected_value
        org_format = selected_value.split('-')
        if int(org_format[0]) > 20:
            new_format = [1,0,2]
        else:
            new_format = [2,0,1]
        
        new_data = '-'.join([org_format[i] for i in new_format])
        return new_data