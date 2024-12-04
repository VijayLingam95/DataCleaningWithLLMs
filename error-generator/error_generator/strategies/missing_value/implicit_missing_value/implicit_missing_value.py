from difflib import SequenceMatcher
from operator import itemgetter
import random

class Implicit_Missing_Value(object):
    def __init__(self,name="Implicit_Missing_Value", dic=None):
        self.name=name
        self.dic={"phone number":"11111111","education":"Some college","Blood Pressurse":"0",
                  "workclass":"?","date":"20010101","Ref_ID":"-1","Regents Num":"s","Junction Control":"-1",
                  "age":"0","Birthday":"20010101","EVENT_DT":"20030101","state":"Alabama","country":"Afghanistan",
                  "email":"...@gmail.com","ssn":"111111111"}
        if dic is not None:
            self.dic=dic


    def run(self,row,col,selected_value,dataset):

        #insted putting the median and mode for implicit missing value
        #we do label matching and acording the dictionary we replace data

        # similar_first=Similar_First()
        # similar_first.similar_first(dataset)
        #
        # mod_value=similar_first.mod_value
        # median_value=similar_first.median_value
        #
        # col_list = [median_value[col], mod_value[col]]
        #
        #
        # rand = np.random.randint(0, 2)
        # selected = col_list[rand]
        #
        # while str(selected_value) == str(selected):
        #     col_list = col_list.remove(selected)
        #     if col_list is None:
        #         selected = median_value + median_value
        #
        # if (isinstance(selected, list)):
        #     if len(selected) > 1:
        #         selected = selected[0]

        choice = random.choice(list(self.dic.values()))


        return choice
