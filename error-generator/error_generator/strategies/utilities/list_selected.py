from error_generator.strategies.utilities.value_selector import Value_Selector

class List_selected:
    def __init__(self):
        # create instance from value selector
        self.instance_value_selector = Value_Selector()

    def list_selected(self,dataset, percentage,mute_column):
        # how many cell we should change
        number_change = self.instance_value_selector.number(dataset, percentage)

        # list of the value that picked [[row,col,value]]
        list_selected_value = self.instance_value_selector.select_value(dataset, number_change, mute_column)

        return list_selected_value, number_change
