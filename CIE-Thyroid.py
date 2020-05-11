'''
Created on Oct 21, 2019

@author: milad moradi
'''

import csv
import sys, getopt

import xml.etree.ElementTree as ET
from xml.dom.minidom import parse, Node
import xml.dom.minidom       
from numpy import double


#--------------------------------
class Feature:
    
    def __init__(self, nam, typ):
        self.name = nam
        self.type = typ
#--------------------------------
class Item:
    
    def __init__(self, fea, val, typ):
        self.id = 0
        self.feature = fea #feature index
        self.value = val 
        self.type = typ
        self.frequency = 1
        self.overall_frequency = 0
        self.support = 0.0
        self.overall_support = 0.0
        self.confidence = 0.0
        self.appear = []
        
        self.is_range = False
        self.min_value = 'NA'
        self.max_value = 'NA'
        
    def update_appear(self, input_appear):
        for i in range(0, len(input_appear)):
            self.appear.append(input_appear[i])
            
    def return_item_text(self, features_list):
        item_text = ''
        if (self.is_range == False):
            item_text = features_list[self.feature].name + '=' + str(self.value)
        elif (self.is_range == True):
            if (self.min_value == 'NA' and self.max_value != 'NA'):
                item_text = features_list[self.feature].name + '<=' + str(self.max_value)
            elif (self.min_value != 'NA' and self.max_value != 'NA'):
                item_text = features_list[self.feature].name + ' in [' + str(self.min_value) + ', ' + str(self.max_value) + ']'
            elif (self.min_value != 'NA' and self.max_value == 'NA'):
                item_text = features_list[self.feature].name + '>=' + str(self.min_value)
        
        return item_text
    
    def is_same_item(self, input_item):
        is_same = True
        if (input_item.feature != self.feature):
            is_same = False
        elif (input_item.value != self.value):
            is_same = False
        elif (input_item.type != self.type):
            is_same = False
        elif (input_item.is_range != self.is_range):
            is_same = False
        elif (input_item.min_value != self.min_value):
            is_same = False
        elif (input_item.max_value != self.max_value):
            is_same = False
            
        return is_same
#--------------------------------

class Psudoitem:
    
    def __init__(self, input_id, input_feature):
        self.id = input_id
        self.feature = input_feature
        self.frequency = 1
        self.overall_frequency = 0
        self.support = 0
        self.overall_support = 0
        self.confidence = 0
        self.appear = []

#--------------------------------
class Itemlist:
    
    def __init__(self, cli, cln):
        self.class_index = cli
        self.class_name = cln
        self.items = []
        
        self.num_records = 0
        
    def add_item(self, input_item, record_num):
        
        is_already_existed = False
        existed_index = -1
        for i in range(0, len(self.items)):
            if (input_item.feature == self.items[i].feature) and (input_item.value == self.items[i].value):
                is_already_existed = True
                existed_index = i
                break
            
        if (is_already_existed == True):
            self.items[existed_index].frequency += 1
            self.items[existed_index].appear.append(record_num)
        else:
            input_item.appear.append(record_num)
            self.items.append(input_item)
            
    def add_psudoitem(self, input_item, record_num):
        
        is_already_existed = False
        existed_index = -1
        for i in range(0, len(self.items)):
            if (input_item.id == self.items[i].id):
                is_already_existed = True
                existed_index = i
                break
            
        if (is_already_existed == True):
            self.items[existed_index].frequency += 1
            self.items[existed_index].appear.append(record_num)
        else:
            input_item.appear.append(record_num)
            self.items.append(input_item)
            
    def return_frequent_items(self, min_sup, min_conf):
        frequent_items = []
        
        for i in range(0, len(self.items)):
            if (self.items[i].support >= min_sup and self.items[i].confidence >= min_conf):
                frequent_items.append(self.items[i])
                
        return frequent_items
    
    def add_to_range(self, input_item):
        for i in range(0, len(self.items)):
            if (input_item.feature == self.items[i].feature):
                
                if (self.items[i].min_value == 'NA' and self.items[i].max_value != 'NA'):
                    if (input_item.value <= self.items[i].max_value):
                        self.items[i].frequency += input_item.frequency
                        self.items[i].update_appear(input_item.appear)
                        
                elif (self.items[i].min_value != 'NA' and self.items[i].max_value != 'NA'):
                    if (input_item.value >= self.items[i].min_value and input_item.value <= self.items[i].max_value):
                        self.items[i].frequency += input_item.frequency
                        self.items[i].update_appear(input_item.appear)
                        
                elif (self.items[i].min_value != 'NA' and self.items[i].max_value == 'NA'):
                    if (input_item.value >= self.items[i].min_value):
                        self.items[i].frequency += input_item.frequency
                        self.items[i].update_appear(input_item.appear)
                        
    def return_item_by_id(self, input_id):
        does_appear = False
        for i in range(0, len(self.items)):
            if (self.items[i].id == input_id):
                does_appear = True
                return self.items[i]
        if (does_appear == False):
            return -1
            
#--------------------------------
class Itemset:
    
    def __init__(self):
        self.frequency = 0
        self.overall_frequency = 0
        self.support = 0.0
        self.overall_support = 0.0
        self.confidence = 0.0
        self.appear = []
        
        self.items = []
        
    def return_itemset_text(self, features_list):
        itemset_text = ''
        for i in range(0, len(self.items)):
            if (i > 0):
                itemset_text += ', '
            itemset_text += self.items[i].return_item_text(features_list)
        return itemset_text
    
    def combine_with_itemset(self, input_itemset1, input_itemset2):
        
        for i in range(0, len(input_itemset1.items)):
            self.items.append(input_itemset1.items[i])
        for i in range(0, len(input_itemset2.items)):
            does_appear = False
            for j in range(0, len(self.items)):
                if (self.items[j] == input_itemset2.items[i]):
                    does_appear = True
                    
            if (does_appear == False):
                self.items.append(input_itemset2.items[i])
                
        for i in range(0, len(input_itemset1.appear)):
            self.appear.append(input_itemset1.appear[i])
        new_appear = []
        for i in range(0, len(self.appear)):
            does_appear = False
            for j in range(0, len(input_itemset2.appear)):
                if (self.appear[i] == input_itemset2.appear[j]):
                    does_appear = True
            if (does_appear == True):
                new_appear.append(self.appear[i])
                
        self.appear = new_appear
        self.frequency = len(self.appear)
        
    def is_itemset_frequent(self, min_sup, min_conf):
        if (self.support >= min_sup and self.confidence >= min_conf):
            return True
        else:
            return False
        
    def can_be_combined(self, input_itemset, input_k):
        can_combine = False
        
        if (input_k == 2):
            if (input_itemset.items[0].feature != self.items[0].feature):
                can_combine = True
                
        elif (input_k > 2):
            if (len(self.items) == input_k-1 and len(input_itemset.items) == input_k-1):
                if (self.how_many_common_items(input_itemset) == input_k-2):
                    can_combine = True       
                
        return can_combine
    
    def how_many_common_items(self, input_itemset):
        common_items = 0
        for i in range(0, len(self.items)):
            if (self.items[i] in input_itemset.items):
                common_items += 1
                
        return common_items
    
#--------------------------------
class Itemsetlist:
    
    def __init__(self, cli, cln):
        self.class_index = cli
        self.class_name = cln
        self.itemsets = []
        
        self.num_records = 0
#--------------------------------
class Record:
    
    def __init__(self, input_record_num):
        self.record_num = input_record_num
        self.value_list = []
        self.class_name = ''
        self.tr_rep = [] #----- Transactional representation
        
        self.possible_predictions = []
        self.predicted_class = ''
        
    def does_item_appear(self, input_item):
        does_appear = False
        if (input_item.is_range == False): #----- categorical feature
            if (self.value_list[input_item.feature] == input_item.value):
                does_appear = True
        elif (input_item.is_range == True): #----- numerical feature
            if (input_item.min_value == 'NA' and input_item.max_value != 'NA'):
                if (self.value_list[input_item.feature] <= input_item.max_value):
                    does_appear = True
            elif (input_item.min_value != 'NA' and input_item.max_value != 'NA'):
                if (self.value_list[input_item.feature] >= input_item.min_value and self.value_list[input_item.feature] <= input_item.max_value):
                    does_appear = True
            elif (input_item.min_value != 'NA' and input_item.max_value == 'NA'):
                if (self.value_list[input_item.feature] >= input_item.min_value):
                    does_appear = True
            
        if (does_appear == True):
            return 1
        else:
            return 0
        
    def does_psudoitem_appear(self, input_item):
        if (input_item.id in self.tr_rep):
            return 1
        else:
            return 0
            
        
    def does_itemset_appear(self, input_itemset):
        how_many_items_appear = 0
        
        for i in range(0, len(input_itemset.items)):
            if (self.does_item_appear(input_itemset.items[i]) == True):
                how_many_items_appear += 1
                
        if (how_many_items_appear == len(input_itemset.items)):
            return 1
        else:
            return 0
        
    def does_psudoitemset_appear(self, input_itemset):
        how_many_items_appear = 0
        for i in range(0, len(input_itemset.items)):
            if (input_itemset.items[i] in self.tr_rep):
                how_many_items_appear += 1
        
        if (how_many_items_appear == len(input_itemset.items)):
            return 1
        else:
            return 0
        
#--------------------------------

class Recordlist:
    
    def __init__(self, input_class_index, input_class_name):
        self.class_index = input_class_index
        self.class_name = input_class_name
        self.records = []
        
#--------------------------------
        
class Prediction:
    
    def __init__(self, input_class, input_num_records):
        self.class_name = input_class
        self.num_records = input_num_records
        self.class_score = 0
        self.itemsets = []
        
    def add_itemset(self, input_itemset):
        self.itemsets.append(input_itemset)
        self.class_score += input_itemset.confidence

#--------------------------------

class Stats:
    
    def __init__(self, input_class):
        self.class_name = input_class
        self.num_records = 0
        self.correctly_classified = 0
        self.uncorrectly_classified = 0
        self.class_accuracy = 0        

#--------------------------------
        
class Overallstats:
    
    def __init__(self):
        self.statslist = []
    
    def add_to_list(self, input_stats):
        already_exist = False
        for i in range(0, len(self.statslist)):
            if (input_stats.class_name == self.statslist[i].class_name):
                already_exist = True
        
        if (already_exist == False):
            self.statslist.append(input_stats)
            
    def update_stats(self, real_class, predicted_class):
        for i in range(0, len(self.statslist)):
            
            if (self.statslist[i].class_name == real_class):
                self.statslist[i].num_records += 1
                if (predicted_class == real_class):
                    self.statslist[i].correctly_classified += 1
                else:
                    self.statslist[i].uncorrectly_classified += 1
                self.statslist[i].class_accuracy = self.statslist[i].correctly_classified / self.statslist[i].num_records

#------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------


def which_class_index(record, class_list):
    
    index = -1
    class_index = len(record) - 1
    for i in range(0, len(class_list)):
        if (record[class_index] == class_list[i]):
            index = i
            
    return index

def itemset_already_in_candidates(candidate_itemsets, input_itemset):
    already_appear = False
    for i in range(0, len(candidate_itemsets)):
        if (input_itemset.how_many_common_items(candidate_itemsets[i]) == len(input_itemset.items)):
            already_appear = True
            
    return already_appear

#------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------


def main(argv):
    
    support_threshold = 0
    confidence_threshold = 0.5
    
    
    Feature_list = []
    temp_feature = Feature('age', 1)
    Feature_list.append(temp_feature)
    temp_feature = Feature('sex', 2)
    Feature_list.append(temp_feature)
    temp_feature = Feature('on_thyroxine', 2)
    Feature_list.append(temp_feature)
    temp_feature = Feature('query_on_thyroxine', 2)
    Feature_list.append(temp_feature)
    temp_feature = Feature('on_antithyroid_medication', 2)
    Feature_list.append(temp_feature)
    temp_feature = Feature('sick', 2)
    Feature_list.append(temp_feature)
    temp_feature = Feature('pregnant', 2)
    Feature_list.append(temp_feature)
    temp_feature = Feature('thyroid_surgery', 2)
    Feature_list.append(temp_feature)
    temp_feature = Feature('I131_treatment', 2)
    Feature_list.append(temp_feature)
    temp_feature = Feature('query_hypothyroid', 2)
    Feature_list.append(temp_feature)
    temp_feature = Feature('query_hyperthyroid', 2)
    Feature_list.append(temp_feature)
    temp_feature = Feature('lithium', 2)
    Feature_list.append(temp_feature)
    temp_feature = Feature('goitre', 2)
    Feature_list.append(temp_feature)
    temp_feature = Feature('tumor', 2)
    Feature_list.append(temp_feature)
    temp_feature = Feature('hypopituitary', 2)
    Feature_list.append(temp_feature)
    temp_feature = Feature('psych', 2)
    Feature_list.append(temp_feature)
    temp_feature = Feature('TSH_measured', 2)
    Feature_list.append(temp_feature)
    temp_feature = Feature('TSH', 1)
    Feature_list.append(temp_feature)
    temp_feature = Feature('T3_measured', 2)
    Feature_list.append(temp_feature)
    temp_feature = Feature('T3', 1)
    Feature_list.append(temp_feature)
    temp_feature = Feature('TT4_measured', 2)
    Feature_list.append(temp_feature)
    temp_feature = Feature('TT4', 1)
    Feature_list.append(temp_feature)
    temp_feature = Feature('T4U_measured', 2)
    Feature_list.append(temp_feature)
    temp_feature = Feature('T4U', 1)
    Feature_list.append(temp_feature)
    temp_feature = Feature('FTI_measured', 2)
    Feature_list.append(temp_feature)
    temp_feature = Feature('FTI', 1)
    Feature_list.append(temp_feature)
    temp_feature = Feature('TBG_measured', 2)
    Feature_list.append(temp_feature)
    temp_feature = Feature('TBG', 1)
    Feature_list.append(temp_feature)
    temp_feature = Feature('referral_source', 2)
    Feature_list.append(temp_feature)
    
    
    Class_list = []
    Class_list.append('A')
    Class_list.append('B')
    Class_list.append('C')
    Class_list.append('D')
    Class_list.append('E')
    Class_list.append('F')
    Class_list.append('G')
    Class_list.append('H')
    Class_list.append('I')
    Class_list.append('J')
    Class_list.append('K')
    Class_list.append('L')
    Class_list.append('M')
    Class_list.append('N')
    Class_list.append('O')
    Class_list.append('P')
    Class_list.append('Q')
    Class_list.append('R')
    Class_list.append('S')
    Class_list.append('T')
    Class_list.append('-')
    
    
    #---------------------------------------- Training the model ----------------------------------------
    
    Record_list = []
    for i in range(0, len(Class_list)):
        temp_record_list = Recordlist(i, Class_list[i])
        Record_list.append(temp_record_list)
        
    with open('Train\\Thyroid-Train.csv') as input_file:
        
        row_num = 0
        
        input_data = csv.reader(input_file, delimiter=',')
        
        for row in input_data:
            
            row_num += 1
            temp_record = Record(row_num)
            
            for i in range(0, len(Feature_list)+1):
                if (i == 0):
                    temp_record.value_list.append(int(row[i]))
                elif (i in(17, 19, 21, 23, 25, 27)):
                    temp_record.value_list.append(double(row[i]))
                else:
                    temp_record.value_list.append(row[i])
            
            for i in range(0, len(Record_list)):
                if (temp_record.value_list[len(Feature_list)] == Record_list[i].class_name):
                    Record_list[i].records.append(temp_record)
            
    
    num_all_records = 0
    for i in range(0, len(Record_list)):
        for j in range(0, len(Record_list[i].records)):
            print(Record_list[i].records[j].value_list)
        
        num_all_records += len(Record_list[i].records)
            
    print(num_all_records, 'records were read.')
    
    #----- read all the records and create a listt for all items
        
    all_items_list = Itemlist(0, 'All')
    
    for i in range(0, len(Record_list)):
        for j in range(0, len(Record_list[i].records)):
            current_record = Record_list[i].records[j].value_list
            current_class_index = which_class_index(current_record, Class_list) # in order to know in which class_item_list must I add the items of the current record
        
            print('Current class index:', current_class_index)
        
            for m in range(0, len(current_record)-1): # the class feature must be excluded from items
                # items are added to the corresponding class_item_list
            
                temp_item = Item(m, current_record[m], Feature_list[m].type)
            
                # Add the item to the corresponding class_item_list
                all_items_list.add_item(temp_item, Record_list[i].records[j].record_num)
            
            all_items_list.num_records += 1
            
            
    print('-------------------- List of all items --------------------')
    
    for i in range(0, len(all_items_list.items)):
        current_item = all_items_list.items[i]
        print('Item:', Feature_list[current_item.feature].name, '=', current_item.value, ', Frequency:', current_item.frequency, ', Appears in:', current_item.appear)
    print('All items:', len(all_items_list.items))        
            
            
    #---------- For every numerical feature, manually create some ranges
    
    for i in range(0, len(Feature_list)):
        
        if (i == 0): #----- age
                
            temp_item1 = Item(i, 0, Feature_list[i].type)
            temp_item1.is_range = True
            temp_item1.max_value = int(15)
            
            temp_item2 = Item(i, 0, Feature_list[i].type)
            temp_item2.is_range = True
            temp_item2.min_value = int(16)
            temp_item2.max_value = int(30)
            
            temp_item3 = Item(i, 0, Feature_list[i].type)
            temp_item3.is_range = True
            temp_item3.min_value = int(31)
            temp_item3.max_value = int(45)
            
            temp_item4 = Item(i, 0, Feature_list[i].type)
            temp_item4.is_range = True
            temp_item4.min_value = int(46)
            temp_item4.max_value = int(60)
            
            temp_item5 = Item(i, 0, Feature_list[i].type)
            temp_item5.is_range = True
            temp_item5.min_value = int(61)
                
            temp_item1.frequency = temp_item2.frequency = temp_item3.frequency = temp_item4.frequency = temp_item5.frequency = 0
                
            copy_items = all_items_list.items
            all_items_list.items = []
                
            range_itemlist = Itemlist(all_items_list.class_index, all_items_list.class_name)
            range_itemlist.items.append(temp_item1)
            range_itemlist.items.append(temp_item2)
            range_itemlist.items.append(temp_item3)
            range_itemlist.items.append(temp_item4)
            range_itemlist.items.append(temp_item5)
                
            for m in range(0, len(copy_items)):
                if (copy_items[m].feature == i):
                    range_itemlist.add_to_range(copy_items[m])
                else:
                    all_items_list.items.append(copy_items[m])
                        
            for m in range(0, len(range_itemlist.items)):
                all_items_list.items.append(range_itemlist.items[m])
                
                
        if (i == 17): #----- TSH
                
            temp_item1 = Item(i, 0, Feature_list[i].type)
            temp_item1.is_range = True
            temp_item1.max_value = int(1)
            
            temp_item2 = Item(i, 0, Feature_list[i].type)
            temp_item2.is_range = True
            temp_item2.min_value = int(2)
            temp_item2.max_value = int(4)
            
            temp_item3 = Item(i, 0, Feature_list[i].type)
            temp_item3.is_range = True
            temp_item3.min_value = int(5)
            temp_item3.max_value = int(7)
            
            temp_item4 = Item(i, 0, Feature_list[i].type)
            temp_item4.is_range = True
            temp_item4.min_value = int(8)
            temp_item4.max_value = int(10)
            
            temp_item5 = Item(i, 0, Feature_list[i].type)
            temp_item5.is_range = True
            temp_item5.min_value = int(11)
                
            temp_item1.frequency = temp_item2.frequency = temp_item3.frequency = temp_item4.frequency = temp_item5.frequency = 0
                
            copy_items = all_items_list.items
            all_items_list.items = []
                
            range_itemlist = Itemlist(all_items_list.class_index, all_items_list.class_name)
            range_itemlist.items.append(temp_item1)
            range_itemlist.items.append(temp_item2)
            range_itemlist.items.append(temp_item3)
            range_itemlist.items.append(temp_item4)
            range_itemlist.items.append(temp_item5)
                
            for m in range(0, len(copy_items)):
                if (copy_items[m].feature == i):
                    range_itemlist.add_to_range(copy_items[m])
                else:
                    all_items_list.items.append(copy_items[m])
                        
            for m in range(0, len(range_itemlist.items)):
                all_items_list.items.append(range_itemlist.items[m])
                
                
                
        if (i == 19): #----- T3
                
            temp_item1 = Item(i, 0, Feature_list[i].type)
            temp_item1.is_range = True
            temp_item1.max_value = int(1)
            
            temp_item2 = Item(i, 0, Feature_list[i].type)
            temp_item2.is_range = True
            temp_item2.min_value = int(2)
            temp_item2.max_value = int(4)
            
            temp_item3 = Item(i, 0, Feature_list[i].type)
            temp_item3.is_range = True
            temp_item3.min_value = int(5)
            temp_item3.max_value = int(7)
            
            temp_item4 = Item(i, 0, Feature_list[i].type)
            temp_item4.is_range = True
            temp_item4.min_value = int(8)
            temp_item4.max_value = int(10)
            
            temp_item5 = Item(i, 0, Feature_list[i].type)
            temp_item5.is_range = True
            temp_item5.min_value = int(11)
                
            temp_item1.frequency = temp_item2.frequency = temp_item3.frequency = temp_item4.frequency = temp_item5.frequency = 0
                
            copy_items = all_items_list.items
            all_items_list.items = []
                
            range_itemlist = Itemlist(all_items_list.class_index, all_items_list.class_name)
            range_itemlist.items.append(temp_item1)
            range_itemlist.items.append(temp_item2)
            range_itemlist.items.append(temp_item3)
            range_itemlist.items.append(temp_item4)
            range_itemlist.items.append(temp_item5)
                
            for m in range(0, len(copy_items)):
                if (copy_items[m].feature == i):
                    range_itemlist.add_to_range(copy_items[m])
                else:
                    all_items_list.items.append(copy_items[m])
                        
            for m in range(0, len(range_itemlist.items)):
                all_items_list.items.append(range_itemlist.items[m])
                
                
                
        if (i == 21): #----- TT4
                
            temp_item1 = Item(i, 0, Feature_list[i].type)
            temp_item1.is_range = True
            temp_item1.max_value = int(100)
            
            temp_item2 = Item(i, 0, Feature_list[i].type)
            temp_item2.is_range = True
            temp_item2.min_value = int(101)
            temp_item2.max_value = int(200)
            
            temp_item3 = Item(i, 0, Feature_list[i].type)
            temp_item3.is_range = True
            temp_item3.min_value = int(201)
            temp_item3.max_value = int(300)
            
            temp_item4 = Item(i, 0, Feature_list[i].type)
            temp_item4.is_range = True
            temp_item4.min_value = int(301)
            temp_item4.max_value = int(400)
            
            temp_item5 = Item(i, 0, Feature_list[i].type)
            temp_item5.is_range = True
            temp_item5.min_value = int(401)
                
            temp_item1.frequency = temp_item2.frequency = temp_item3.frequency = temp_item4.frequency = temp_item5.frequency = 0
                
            copy_items = all_items_list.items
            all_items_list.items = []
                
            range_itemlist = Itemlist(all_items_list.class_index, all_items_list.class_name)
            range_itemlist.items.append(temp_item1)
            range_itemlist.items.append(temp_item2)
            range_itemlist.items.append(temp_item3)
            range_itemlist.items.append(temp_item4)
            range_itemlist.items.append(temp_item5)
                
            for m in range(0, len(copy_items)):
                if (copy_items[m].feature == i):
                    range_itemlist.add_to_range(copy_items[m])
                else:
                    all_items_list.items.append(copy_items[m])
                        
            for m in range(0, len(range_itemlist.items)):
                all_items_list.items.append(range_itemlist.items[m])
                
                
        if (i == 23): #----- T4U
                
            temp_item1 = Item(i, 0, Feature_list[i].type)
            temp_item1.is_range = True
            temp_item1.max_value = double(0.5)
            
            temp_item2 = Item(i, 0, Feature_list[i].type)
            temp_item2.is_range = True
            temp_item2.min_value = double(0.6)
            temp_item2.max_value = double(1)
            
            temp_item3 = Item(i, 0, Feature_list[i].type)
            temp_item3.is_range = True
            temp_item3.min_value = double(1.1)
            temp_item3.max_value = double(1.5)
            
            temp_item4 = Item(i, 0, Feature_list[i].type)
            temp_item4.is_range = True
            temp_item4.min_value = double(1.6)
            temp_item4.max_value = double(2)
            
            temp_item5 = Item(i, 0, Feature_list[i].type)
            temp_item5.is_range = True
            temp_item5.min_value = double(2.1)
                
            temp_item1.frequency = temp_item2.frequency = temp_item3.frequency = temp_item4.frequency = temp_item5.frequency = 0
                
            copy_items = all_items_list.items
            all_items_list.items = []
                
            range_itemlist = Itemlist(all_items_list.class_index, all_items_list.class_name)
            range_itemlist.items.append(temp_item1)
            range_itemlist.items.append(temp_item2)
            range_itemlist.items.append(temp_item3)
            range_itemlist.items.append(temp_item4)
            range_itemlist.items.append(temp_item5)
                
            for m in range(0, len(copy_items)):
                if (copy_items[m].feature == i):
                    range_itemlist.add_to_range(copy_items[m])
                else:
                    all_items_list.items.append(copy_items[m])
                        
            for m in range(0, len(range_itemlist.items)):
                all_items_list.items.append(range_itemlist.items[m])
                
                
                
        if (i == 25): #----- FTI
                
            temp_item1 = Item(i, 0, Feature_list[i].type)
            temp_item1.is_range = True
            temp_item1.max_value = int(100)
            
            temp_item2 = Item(i, 0, Feature_list[i].type)
            temp_item2.is_range = True
            temp_item2.min_value = int(101)
            temp_item2.max_value = int(200)
            
            temp_item3 = Item(i, 0, Feature_list[i].type)
            temp_item3.is_range = True
            temp_item3.min_value = int(201)
            temp_item3.max_value = int(300)
            
            temp_item4 = Item(i, 0, Feature_list[i].type)
            temp_item4.is_range = True
            temp_item4.min_value = int(301)
            temp_item4.max_value = int(400)
            
            temp_item5 = Item(i, 0, Feature_list[i].type)
            temp_item5.is_range = True
            temp_item5.min_value = int(401)
                
            temp_item1.frequency = temp_item2.frequency = temp_item3.frequency = temp_item4.frequency = temp_item5.frequency = 0
                
            copy_items = all_items_list.items
            all_items_list.items = []
                
            range_itemlist = Itemlist(all_items_list.class_index, all_items_list.class_name)
            range_itemlist.items.append(temp_item1)
            range_itemlist.items.append(temp_item2)
            range_itemlist.items.append(temp_item3)
            range_itemlist.items.append(temp_item4)
            range_itemlist.items.append(temp_item5)
                
            for m in range(0, len(copy_items)):
                if (copy_items[m].feature == i):
                    range_itemlist.add_to_range(copy_items[m])
                else:
                    all_items_list.items.append(copy_items[m])
                        
            for m in range(0, len(range_itemlist.items)):
                all_items_list.items.append(range_itemlist.items[m])
                
                
                
        if (i == 27): #----- TBG
                
            temp_item1 = Item(i, 0, Feature_list[i].type)
            temp_item1.is_range = True
            temp_item1.max_value = int(10)
            
            temp_item2 = Item(i, 0, Feature_list[i].type)
            temp_item2.is_range = True
            temp_item2.min_value = int(11)
            temp_item2.max_value = int(30)
            
            temp_item3 = Item(i, 0, Feature_list[i].type)
            temp_item3.is_range = True
            temp_item3.min_value = int(31)
            temp_item3.max_value = int(50)
            
            temp_item4 = Item(i, 0, Feature_list[i].type)
            temp_item4.is_range = True
            temp_item4.min_value = int(51)
            temp_item4.max_value = int(70)
            
            temp_item5 = Item(i, 0, Feature_list[i].type)
            temp_item5.is_range = True
            temp_item5.min_value = int(71)
                
            temp_item1.frequency = temp_item2.frequency = temp_item3.frequency = temp_item4.frequency = temp_item5.frequency = 0
                
            copy_items = all_items_list.items
            all_items_list.items = []
                
            range_itemlist = Itemlist(all_items_list.class_index, all_items_list.class_name)
            range_itemlist.items.append(temp_item1)
            range_itemlist.items.append(temp_item2)
            range_itemlist.items.append(temp_item3)
            range_itemlist.items.append(temp_item4)
            range_itemlist.items.append(temp_item5)
                
            for m in range(0, len(copy_items)):
                if (copy_items[m].feature == i):
                    range_itemlist.add_to_range(copy_items[m])
                else:
                    all_items_list.items.append(copy_items[m])
                        
            for m in range(0, len(range_itemlist.items)):
                all_items_list.items.append(range_itemlist.items[m])
                    
    #---------- End of ranging numerical features
    
    for i in range(0, len(all_items_list.items)):
        all_items_list.items[i].id = i
    
    print('-------------------- List of all items --------------------')
    for i in range(0, len(all_items_list.items)):
        current_item = all_items_list.items[i]
        print('Item:', current_item.id, ',', current_item.return_item_text(Feature_list), ', Frequency:', current_item.frequency, ', Appears in:', current_item.appear)
    print('All items:', len(all_items_list.items))
    
    #---------- Create a transactional representation for every record
    
    for i in range(0, len(Record_list)):
        for j in range(0, len(Record_list[i].records)):
            
            for m in range(0, len(all_items_list.items)):
                if (Record_list[i].records[j].does_item_appear(all_items_list.items[m]) == 1):
                    Record_list[i].records[j].tr_rep.append(all_items_list.items[m].id)
                    
    print('\n-------------------- Transactional representation of records --------------------')
    for i in range(0, len(Record_list)):
        for j in range(0, len(Record_list[i].records)):
            print('Record:', Record_list[i].records[j].record_num, 'Transactional representation:', Record_list[i].records[j].tr_rep)
            
    
    #---------- Read all records and create an Itemlist for every class        
    class_item_list = []
    for i in range(0, len(Class_list)):
        temp_item_list = Itemlist(i, Class_list[i])
        class_item_list.append(temp_item_list)
        
    for i in range(0, len(Record_list)):
        
        temp_item_list = Itemlist(Record_list[i].class_index, Record_list[i].class_name)
        
        for j in range(0, len(Record_list[i].records)):
            current_record = Record_list[i].records[j]
        
            print('Record_num:', current_record.record_num, 'Current class index:', Record_list[i].class_index)
        
            for m in range(0, len(current_record.tr_rep)):
                # items are added to the corresponding class_item_list
            
                temp_item = all_items_list.return_item_by_id(current_record.tr_rep[m])
                
                temp_psudoitem = Psudoitem(temp_item.id, temp_item.feature)
            
                # Add the item to the corresponding class_item_list
                temp_item_list.add_psudoitem(temp_psudoitem, current_record.record_num)
                
            temp_item_list.num_records += 1
                
        class_item_list.append(temp_item_list)
    
    print('-------------------- List of items per class --------------------')        
            
    for i in range(0, len(class_item_list)):
        
        print('\n********** Class:', class_item_list[i].class_name, 'Number of records:', class_item_list[i].num_records, 'Number of items:', len(class_item_list[i].items), '**********')
        
        for j in range(0, len(class_item_list[i].items)):
            
            current_item = class_item_list[i].items[j]
            print('Id:', current_item.id, ', Frequency:', current_item.frequency, ', Appears in:', current_item.appear)
    
    #---------- Identify frequent items and create a list of frequent 1-itemsets for every class
    
    #----- Compute support and frequency for every item
    for i in range(0, len(class_item_list)):
        for j in range(0, len(class_item_list[i].items)):
            
            #----- Check for every record
            for m in range(0, len(Record_list)):
                for n in range(0, len(Record_list[m].records)):
                    class_item_list[i].items[j].overall_frequency += Record_list[m].records[n].does_psudoitem_appear(class_item_list[i].items[j])
                
            #----- Compute support and confidence
            class_item_list[i].items[j].support = class_item_list[i].items[j].frequency / class_item_list[i].num_records
            class_item_list[i].items[j].overall_support = class_item_list[i].items[j].overall_frequency / num_all_records
            if (class_item_list[i].items[j].overall_frequency > 0):
                class_item_list[i].items[j].confidence = class_item_list[i].items[j].frequency / class_item_list[i].items[j].overall_frequency
            
    #----- Just to print
    for i in range(0, len(class_item_list)):
        
        print('\n********** Class:', class_item_list[i].class_name, 'Number of records:', class_item_list[i].num_records, 'Number of items:', len(class_item_list[i].items), '**********')
        
        for j in range(0, len(class_item_list[i].items)):
            
            current_item = class_item_list[i].items[j]
            print('Id:', current_item.id, ', Frequency:', current_item.frequency, ', Overall_frequency:', current_item.overall_frequency, ', Support:', current_item.support, ', Overall_support:', current_item.overall_support, ', Confidence:', current_item.confidence, ', Appears in:', current_item.appear)
    
    
    #----- Create a 1-itemset for every frequent item and add it to the corresponding class_itemset_list
    class_itemset_list = []
    
    for i in range(0, len(class_item_list)):
        
        temp_itemset_list = Itemsetlist(class_item_list[i].class_index, class_item_list[i].class_name)
        temp_itemset_list.num_records = class_item_list[i].num_records
        
        temp_frequent_items = class_item_list[i].return_frequent_items(support_threshold, confidence_threshold)
        for j in range(0, len(temp_frequent_items)):
            temp_itemset = Itemset()
            temp_itemset.frequency = temp_frequent_items[j].frequency
            temp_itemset.overall_frequency = temp_frequent_items[j].overall_frequency
            temp_itemset.support = temp_frequent_items[j].support
            temp_itemset.overall_support = temp_frequent_items[j].overall_support
            temp_itemset.confidence = temp_frequent_items[j].confidence
            temp_itemset.appear = temp_frequent_items[j].appear
            
            temp_itemset.items.append(temp_frequent_items[j].id)
            
            temp_itemset_list.itemsets.append(temp_itemset)
            
        class_itemset_list.append(temp_itemset_list)     
        
    #----- Just to print
    for i in range(0, len(class_itemset_list)):
        
        print('\n********** Class:', class_itemset_list[i].class_name, 'Number of records:', class_item_list[i].num_records, 'Number of itemsets:', len(class_itemset_list[i].itemsets), '**********')
        
        for j in range(0, len(class_itemset_list[i].itemsets)):
            
            current_itemset = class_itemset_list[i].itemsets[j]
            print('Itemset:', current_itemset.items, ', Frequency:', current_itemset.frequency, ', Overall_frequency:', current_itemset.overall_frequency, ', Support:', current_itemset.support, ', Overall_support:', current_itemset.overall_support, ', Confidence:', current_itemset.confidence, ', Appears in:', current_itemset.appear)             

    
    
    #---------- Frequent itemset mining algorithm
    
    k = 2
    algorithm_continue = True
    
    while (algorithm_continue == True):
        
        how_many_added = 0
        

        if (k == 2):
            
            for i in range(0, len(class_itemset_list)):
                
                print('\n---------- Class:', i)
                
                #----- Create candidate 2-itemsets
                candidate_itemsets = []
                
                num_candidates = 0
                
                for j in range(0, len(class_itemset_list[i].itemsets)):
                    for m in range(j+1, len(class_itemset_list[i].itemsets)):
                        
                        first_item = all_items_list.return_item_by_id(class_itemset_list[i].itemsets[j].items[0])
                        second_item = all_items_list.return_item_by_id(class_itemset_list[i].itemsets[m].items[0])
                        
                        if (first_item.feature != second_item.feature):
                        
                            temp_itemset = Itemset()
                            temp_itemset.combine_with_itemset(class_itemset_list[i].itemsets[j], class_itemset_list[i].itemsets[m])
                            print('Candidate:', temp_itemset.items, ', Frequency:', temp_itemset.frequency, ', Overall_frequency:', temp_itemset.overall_frequency, ', Support:', temp_itemset.support, ', Overall_support:', temp_itemset.overall_support, ', Confidence:', temp_itemset.confidence, ', Appears in:', temp_itemset.appear)
                        
                            #----- Compute the overall frequency
                            for n in range(0, len(Record_list)):
                                for p in range(0, len(Record_list[n].records)):
                                    temp_itemset.overall_frequency += Record_list[n].records[p].does_psudoitemset_appear(temp_itemset)
                            
                            #----- Compute support and confidence
                            temp_itemset.support = temp_itemset.frequency / class_itemset_list[i].num_records
                            temp_itemset.overall_support = temp_itemset.overall_frequency / num_all_records
                            if (temp_itemset.overall_frequency > 0):
                                temp_itemset.confidence = temp_itemset.frequency / temp_itemset.overall_frequency
                            else:
                                temp_itemset.confidence = 0
                            
                            candidate_itemsets.append(temp_itemset)
                            
                            num_candidates += 1
                            print('Candidate:', num_candidates)
                            #----- Candidate 2-itemsets were created
                        
                #----- Add frequent itemsets to the frequent itemsets list of the current class
                for j in range(0, len(candidate_itemsets)):
                    print('Itemset:', candidate_itemsets[j].items, ', Frequency:', candidate_itemsets[j].frequency, ', Overall_frequency:', candidate_itemsets[j].overall_frequency, ', Support:', candidate_itemsets[j].support, ', Overall_support:', candidate_itemsets[j].overall_support, ', Confidence:', candidate_itemsets[j].confidence, ', Appears in:', candidate_itemsets[j].appear)
                    if (candidate_itemsets[j].is_itemset_frequent(support_threshold, confidence_threshold) == True):
                        class_itemset_list[i].itemsets.append(candidate_itemsets[j])
                        how_many_added += 1
                        
        #----------
        
        if (k > 2):
            
            for i in range(0, len(class_itemset_list)):
                
                print('\n---------- Class:', i)
                
                #----- Create candidate k-itemsets
                candidate_itemsets = []
                
                num_candidates = 0
                
                for j in range(0, len(class_itemset_list[i].itemsets)):
                    for m in range(j+1, len(class_itemset_list[i].itemsets)):
                        
                        if (len(class_itemset_list[i].itemsets[j].items) == k-1 and len(class_itemset_list[i].itemsets[m].items) == k-1):
                            if (class_itemset_list[i].itemsets[j].how_many_common_items(class_itemset_list[i].itemsets[m]) == k-2):
                            
                                temp_itemset = Itemset()
                                temp_itemset.combine_with_itemset(class_itemset_list[i].itemsets[j], class_itemset_list[i].itemsets[m])
                                
                                #----- Check if the same feature appears more than once in temp_itemset
                                
                                does_same_feature_appear = False
                                appeared_features = []
                                for n in range(0, len(temp_itemset.items)):
                                    temp_item = all_items_list.return_item_by_id(temp_itemset.items[n])
                                    if (temp_item.feature in appeared_features):
                                        does_same_feature_appear = True
                                    else:
                                        appeared_features.append(temp_item.feature)
                                        
                                if (does_same_feature_appear == False):
                                
                                    print('Candidate:', temp_itemset.items, ', Frequency:', temp_itemset.frequency, ', Overall_frequency:', temp_itemset.overall_frequency, ', Support:', temp_itemset.support, ', Overall_support:', temp_itemset.overall_support, ', Confidence:', temp_itemset.confidence, ', Appears in:', temp_itemset.appear)
                                
                                    if (itemset_already_in_candidates(candidate_itemsets, temp_itemset) == False):
                                        #----- Compute the overall frequency
                                        for n in range(0, len(Record_list)):
                                            for p in range(0, len(Record_list[n].records)):
                                                temp_itemset.overall_frequency += Record_list[n].records[p].does_psudoitemset_appear(temp_itemset)
                                    
                                        #----- Compute support and confidence
                                        temp_itemset.support = temp_itemset.frequency / class_itemset_list[i].num_records
                                        temp_itemset.overall_support = temp_itemset.overall_frequency / num_all_records
                                        if (temp_itemset.overall_frequency > 0):
                                            temp_itemset.confidence = temp_itemset.frequency / temp_itemset.overall_frequency
                                        else:
                                            temp_itemset.confidence = 0
                            
                                        candidate_itemsets.append(temp_itemset)
                            
                                        num_candidates += 1
                                        print('Candidate:', num_candidates)
                                    
                                #----- Candidate k-itemsets were created
        
                #----- Add frequent itemsets to the frequent itemsets list of the current class
                for j in range(0, len(candidate_itemsets)):
                    print('Itemset:', candidate_itemsets[j].items, ', Frequency:', candidate_itemsets[j].frequency, ', Overall_frequency:', candidate_itemsets[j].overall_frequency, ', Support:', candidate_itemsets[j].support, ', Overall_support:', candidate_itemsets[j].overall_support, ', Confidence:', candidate_itemsets[j].confidence, ', Appears in:', candidate_itemsets[j].appear)
                    if (candidate_itemsets[j].is_itemset_frequent(support_threshold, confidence_threshold) == True):
                        class_itemset_list[i].itemsets.append(candidate_itemsets[j])
                        how_many_added += 1
        #---------------------------------------------------------------------
        print('\n', how_many_added, 'frequent', k, '-itemsets were added')
        
        k += 1
        
        if (how_many_added == 0 or k > 3):
            algorithm_continue = False
                    
                    
    #-------------------- End of itemset mininh algorithm
    
    for i in range(0, len(class_itemset_list)):
        
        print('\n********** Class:', class_itemset_list[i].class_name, 'Number of records:', class_item_list[i].num_records, 'Number of itemsets:', len(class_itemset_list[i].itemsets), '**********')
        
        for j in range(0, len(class_itemset_list[i].itemsets)):
            
            current_itemset = class_itemset_list[i].itemsets[j]
            print('Itemset: [', current_itemset.items, '] , Frequency:', current_itemset.frequency, ', Overall_frequency:', current_itemset.overall_frequency, ', Support:', current_itemset.support, ', Overall_support:', current_itemset.overall_support, ', Confidence:', current_itemset.confidence, ', Appears in:', current_itemset.appear)
    
    
    #---------- For every extracted k-itemset, extract the original items
    for i in range(0, len(class_itemset_list)):
        for j in range(0, len(class_itemset_list[i].itemsets)):
            temp_items = []
            for m in range(0, len(class_itemset_list[i].itemsets[j].items)):
                temp_item = all_items_list.return_item_by_id(class_itemset_list[i].itemsets[j].items[m])
                temp_items.append(temp_item)
            
            class_itemset_list[i].itemsets[j].items = []
            
            for m in range(0, len(temp_items)):
                class_itemset_list[i].itemsets[j].items.append(temp_items[m])
                
                
    for i in range(0, len(class_itemset_list)):
        
        print('\n********** Class:', class_itemset_list[i].class_name, 'Number of records:', class_item_list[i].num_records, 'Number of itemsets:', len(class_itemset_list[i].itemsets), '**********')
        
        for j in range(0, len(class_itemset_list[i].itemsets)):
            
            current_itemset = class_itemset_list[i].itemsets[j]
            print('Itemset: [', current_itemset.return_itemset_text(Feature_list), '] , Frequency:', current_itemset.frequency, ', Overall_frequency:', current_itemset.overall_frequency, ', Support:', current_itemset.support, ', Overall_support:', current_itemset.overall_support, ', Confidence:', current_itemset.confidence)
                
    print('\n-------------------- Original items were returned --------------------')
                
    
    
    Output = ''
    for i in range(0, len(class_itemset_list)):
        #print('---------- ItemsetList Class:', list_itemsetlist[i].label, '----------')
        Output += '\n---------- ItemsetList Class:' + str(class_itemset_list[i].class_name) + '----- Records:' + str(class_itemset_list[i].num_records) + '----------' + '\n'
        for j in range(0, len(class_itemset_list[i].itemsets)):
            #print('Itemset:', list_itemsetlist[i].itemsets[j].items, '----- Support:', list_itemsetlist[i].itemsets[j].support, '----- Confidence:', list_itemsetlist[i].itemsets[j].confidence)
            Output += 'Itemset: [' + class_itemset_list[i].itemsets[j].return_itemset_text(Feature_list) + '] ----- Freq:' + str(class_itemset_list[i].itemsets[j].frequency) + '----- OverallFreq:' + str(class_itemset_list[i].itemsets[j].overall_frequency) + '----- Support:' + str(class_itemset_list[i].itemsets[j].support) + '----- OverallSupport:' + str(class_itemset_list[i].itemsets[j].overall_support) + '----- Confidence:' + str(class_itemset_list[i].itemsets[j].confidence) + '\n'
    
    output_file_name = 'Train\\Model-Sup' + str(support_threshold) + '-Conf' + str(confidence_threshold) + '.txt'
    output_file = open(output_file_name, 'w')
    output_file.write(Output)
    output_file.close()
    
    print('\n-------------------- Text file was stored --------------------')
    
    #-------------------- Writing the model in a XML file
    
    
    model_xml = '<model>' + '\n'
    
    for i in range(0, len(class_itemset_list)): #---- Repeat for every class
        model_xml += '<class>' + '\n'
        model_xml += '<class_index>' + str(class_itemset_list[i].class_index) + '</class_index>' + '\n'
        #model_xml += '<class_name>' + class_itemset_list[i].class_name + '</class_name>' + '\n'
        model_xml += '<num_records>' + str(class_itemset_list[i].num_records) + '</num_records>' + '\n'
        model_xml += '<itemsets>' + '\n'
        
        for j in range(0, len(class_itemset_list[i].itemsets)): #---- Repeat for every itemset
            model_xml += '<itemset>' + '\n'
            model_xml += '<items>' + '\n'
            
            for m in range(0, len(class_itemset_list[i].itemsets[j].items)): #---- Repeat for every item
                model_xml += '<item>' + '\n'
                model_xml += '<feature>' + str(class_itemset_list[i].itemsets[j].items[m].feature) + '</feature>' + '\n'
                model_xml += '<value>' + str(class_itemset_list[i].itemsets[j].items[m].value) + '</value>' + '\n'
                model_xml += '<type>' + str(class_itemset_list[i].itemsets[j].items[m].type) + '</type>' + '\n'
                model_xml += '<is_range>' + str(class_itemset_list[i].itemsets[j].items[m].is_range) + '</is_range>' + '\n'
                model_xml += '<min_value>' + str(class_itemset_list[i].itemsets[j].items[m].min_value) + '</min_value>' + '\n'
                model_xml += '<max_value>' + str(class_itemset_list[i].itemsets[j].items[m].max_value) + '</max_value>' + '\n'
                model_xml += '</item>' + '\n'
                
            model_xml += '</items>' + '\n'
            model_xml += '<frequency>' + str(class_itemset_list[i].itemsets[j].frequency) + '</frequency>' + '\n'
            model_xml += '<overall_frequency>' + str(class_itemset_list[i].itemsets[j].overall_frequency) + '</overall_frequency>' + '\n'
            model_xml += '<support>' + str(class_itemset_list[i].itemsets[j].support) + '</support>' + '\n'
            model_xml += '<overall_support>' + str(class_itemset_list[i].itemsets[j].overall_support) + '</overall_support>' + '\n'
            model_xml += '<confidence>' + str(class_itemset_list[i].itemsets[j].confidence) + '</confidence>' + '\n'
            
            model_xml += '</itemset>' + '\n'
            
        model_xml += '</itemsets>' + '\n'
        model_xml += '</class>' + '\n'
        
    model_xml += '</model>' + '\n'
        
    output_file_name = 'Train\\Model-Sup' + str(support_threshold) + '-Conf' + str(confidence_threshold) + '.xml'
    output_file = open(output_file_name, 'w')
    output_file.write(model_xml)
    output_file.close()
    
    print('\n-------------------- XML model was stored --------------------')
    
    
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------
    
                
    #---------------------------------------- Testing the model ----------------------------------------
    
    #----- Read the test dataset
    
    Record_list = []
    with open('Test\\Thyroid-Test.csv') as input_file:
        
        input_data = csv.reader(input_file, delimiter=',')
        
        row_number = 0
        for row in input_data:
            
            row_number += 1
            temp_record = Record(row_number)
            
            for i in range(0, len(Feature_list)+1):
                if (i in(5, 6, 12)):
                    temp_record.value_list.append(int(row[i]))
                elif (i == 11):
                    temp_record.value_list.append(double(row[i]))
                else:
                    temp_record.value_list.append(row[i])
            
            temp_record.class_name = temp_record.value_list[len(temp_record.value_list) - 1]
            Record_list.append(temp_record)
            
    
    for i in range(0, len(Record_list)):
        print(Record_list[i].value_list)
            
    print(len(Record_list), 'records were read.')
    
    #----- Read the model
    
    model = xml.dom.minidom.parse('Train\\Model-Sup' + str(support_threshold) + '-Conf' + str(confidence_threshold) + '.xml')
    
    list_itemsetlist = []
    
    for cls in model.getElementsByTagName("class"):
        
        current_class_index = 0
        for cls_index in cls.getElementsByTagName("class_index"):
            for value in cls_index.childNodes:
                current_class_index = int(value.data)
        
        temp_itemsetlist = Itemsetlist(current_class_index, '')
        
        class_records = 0
        for cls_rec in cls.getElementsByTagName("num_records"):
            for value in cls_rec.childNodes:
                class_records = int(value.data)
                
        temp_itemsetlist.num_records = class_records
        print('\n')
        print('---------- Class:', temp_itemsetlist.class_index, '---------- Instances:', temp_itemsetlist.num_records)
        
        for itemset in cls.getElementsByTagName("itemset"):
            temp_itemset = Itemset()
            
            for item in itemset.getElementsByTagName("item"):
                temp_item = Item(0, 0, 0)
                
                for feat in item.getElementsByTagName("feature"):
                    for value in feat.childNodes:
                        temp_item.feature = int(value.data)
                        
                for typ in item.getElementsByTagName("type"):
                    for value in typ.childNodes:
                        temp_item.type = int(value.data)
                
                for val in item.getElementsByTagName("value"):
                    for value in val.childNodes:
                        if (temp_item.type == 1): #----- numerical feature
                            temp_item.value = int(value.data)
                        elif (temp_item.type == 2): #----- categorical feature
                            temp_item.value = value.data
                            
                for is_range in item.getElementsByTagName("is_range"):
                    for value in is_range.childNodes:
                        temp_item.is_range = value.data
                        if (temp_item.is_range == 'True'):
                            temp_item.is_range = True
                        elif (temp_item.is_range == 'False'):
                            temp_item.is_range = False
                        
                for min_val in item.getElementsByTagName("min_value"):
                    for value in min_val.childNodes:
                        temp_item.min_value = value.data
                        if (temp_item.min_value != 'NA'):
                            if (temp_item.feature == 11):
                                temp_item.min_value = double(temp_item.min_value)
                            else:
                                temp_item.min_value = int(temp_item.min_value)
                            
                for max_val in item.getElementsByTagName("max_value"):
                    for value in max_val.childNodes:
                        temp_item.max_value = value.data
                        if (temp_item.max_value != 'NA'):
                            if (temp_item.feature == 11):
                                temp_item.max_value = double(temp_item.max_value)
                            else:
                                temp_item.max_value = int(temp_item.max_value)
                            
                temp_itemset.items.append(temp_item)
            
            for freq in itemset.getElementsByTagName("frequency"):
                for value in freq.childNodes:
                    temp_itemset.frequency = double(value.data)
                    
            for overall_freq in itemset.getElementsByTagName("overall_frequency"):
                for value in overall_freq.childNodes:
                    temp_itemset.overall_frequency = double(value.data)
                    
            for supp in itemset.getElementsByTagName("support"):
                for value in supp.childNodes:
                    temp_itemset.support = double(value.data)
                    
            for overall_supp in itemset.getElementsByTagName("overall_support"):
                for value in overall_supp.childNodes:
                    temp_itemset.overall_support = double(value.data)
                    
            for conf in itemset.getElementsByTagName("confidence"):
                for value in conf.childNodes:
                    temp_itemset.confidence = double(value.data)
                    
                    
            print('Itemset:', temp_itemset.return_itemset_text(Feature_list), '----- Frequency:', temp_itemset.frequency, '----- Overal_frequency:', temp_itemset.overall_frequency, '----- Support:', temp_itemset.support, '----- Overall_support:', temp_itemset.overall_support, '----- Confidence:', temp_itemset.confidence)
            temp_itemsetlist.itemsets.append(temp_itemset)
            
        list_itemsetlist.append(temp_itemsetlist)
        
    for i in range(0, len(list_itemsetlist)):
        list_itemsetlist[i].class_name = Class_list[i]
        
    print('\n-------------------- Model has been loaded -------------------- All classes:', len(list_itemsetlist))
    
    
    overall_stats = Overallstats()
    
    for i in range(0, len(list_itemsetlist)):
        
        temp_stats = Stats(list_itemsetlist[i].class_name)
        overall_stats.add_to_list(temp_stats)
        
        print(i, '----- Class:', list_itemsetlist[i].class_name, '----- Instances:', list_itemsetlist[i].num_records)
        
        
        
    #----- Start classification
    
    correctly_predicted = 0
    
    for i in range(0, len(Record_list)):
        
        for j in range(0, len(list_itemsetlist)):
            
            current_class = list_itemsetlist[j].class_name
            num_records = list_itemsetlist[j].num_records
            temp_prediction = Prediction(current_class, num_records)
            
            for m in range(0, len(list_itemsetlist[j].itemsets)):
                if (Record_list[i].does_itemset_appear(list_itemsetlist[j].itemsets[m]) == 1):
                    temp_prediction.add_itemset(list_itemsetlist[j].itemsets[m])
                    
            if (len(temp_prediction.itemsets) > 0):
                Record_list[i].possible_predictions.append(temp_prediction)
                
        #----- Sort possible predictions based on the number of instances each one has
        for j in range(0, len(Record_list[i].possible_predictions)):
            for m in range(j+1, len(Record_list[i].possible_predictions)):
                if (Record_list[i].possible_predictions[j].num_records < Record_list[i].possible_predictions[m].num_records):
                    temp_prediction = Record_list[i].possible_predictions[j]
                    Record_list[i].possible_predictions[j] = Record_list[i].possible_predictions[m]
                    Record_list[i].possible_predictions[m] = temp_prediction
                    
        #----- Sort possible predictions based on their score
        for j in range(0, len(Record_list[i].possible_predictions)):
            for m in range(j+1, len(Record_list[i].possible_predictions)):
                if (Record_list[i].possible_predictions[j].class_score < Record_list[i].possible_predictions[m].class_score):
                    temp_prediction = Record_list[i].possible_predictions[j]
                    Record_list[i].possible_predictions[j] = Record_list[i].possible_predictions[m]
                    Record_list[i].possible_predictions[m] = temp_prediction
                    
        #----- Select the first possible prediction as the final prediction
        if (len(Record_list[i].possible_predictions) > 0):
            Record_list[i].predicted_class = Record_list[i].possible_predictions[0].class_name
        else:
            Record_list[i].predicted_class = list_itemsetlist[0].class_name
        
        if (Record_list[i].predicted_class == Record_list[i].class_name):
            correctly_predicted += 1
            
        overall_stats.update_stats(Record_list[i].class_name, Record_list[i].predicted_class)
            
        print('---------- Instance', i, 'was predicted ----------')
        
        
    #---------------------------------------------------------------------------------------------
    
                        
    print('\n-------------------- Sorting based on Confidence --------------------\n')
    for i in range(0, len(Record_list)):
        for j in range(0, len(Record_list[i].possible_predictions)):
            for m in range(0, len(Record_list[i].possible_predictions[j].itemsets)):
                for n in range(m+1, len(Record_list[i].possible_predictions[j].itemsets)):
                    if (Record_list[i].possible_predictions[j].itemsets[m].confidence < Record_list[i].possible_predictions[j].itemsets[n].confidence):
                        temp_itemset = Record_list[i].possible_predictions[j].itemsets[m]
                        Record_list[i].possible_predictions[j].itemsets[m] = Record_list[i].possible_predictions[j].itemsets[n]
                        Record_list[i].possible_predictions[j].itemsets[n] = temp_itemset
                        
    print('\n-------------------- Sorting based on Class_support --------------------\n')
    for i in range(0, len(Record_list)):
        for j in range(0, len(Record_list[i].possible_predictions)):
            for m in range(0, len(Record_list[i].possible_predictions[j].itemsets)):
                for n in range(m+1, len(Record_list[i].possible_predictions[j].itemsets)):
                    if (Record_list[i].possible_predictions[j].itemsets[m].support < Record_list[i].possible_predictions[j].itemsets[n].support):
                        temp_itemset = Record_list[i].possible_predictions[j].itemsets[m]
                        Record_list[i].possible_predictions[j].itemsets[m] = Record_list[i].possible_predictions[j].itemsets[n]
                        Record_list[i].possible_predictions[j].itemsets[n] = temp_itemset
                        
    print('\n-------------------- Sorting based on Support --------------------\n')
    for i in range(0, len(Record_list)):
        for j in range(0, len(Record_list[i].possible_predictions)):
            for m in range(0, len(Record_list[i].possible_predictions[j].itemsets)):
                for n in range(m+1, len(Record_list[i].possible_predictions[j].itemsets)):
                    if (Record_list[i].possible_predictions[j].itemsets[m].overall_support < Record_list[i].possible_predictions[j].itemsets[n].overall_support):
                        temp_itemset = Record_list[i].possible_predictions[j].itemsets[m]
                        Record_list[i].possible_predictions[j].itemsets[m] = Record_list[i].possible_predictions[j].itemsets[n]
                        Record_list[i].possible_predictions[j].itemsets[n] = temp_itemset
                        
                        
    #----- Results
    
    result = 'Total number of test instances: ' + str(len(Record_list)) + '\n'
    result += 'Correctly predicted instances: ' + str(correctly_predicted) + '\n'
    result += 'Uncorrectly predicted instances: ' + str(len(Record_list) - correctly_predicted) + '\n'
    result += '\n' + 'Accuracy: ' + str(correctly_predicted / len(Record_list))
    
    
    
    result += '\n\n------------------------------ Stitistics per class ------------------------------'
    for i in range(0, len(overall_stats.statslist)):
        result += '\n\n' + '---------- Class: ' + overall_stats.statslist[i].class_name + ' ----------'
        result += '\n' + '    Total instances: ' + str(overall_stats.statslist[i].num_records)
        result += '\n' + '    Correctly classified instances: ' + str(overall_stats.statslist[i].correctly_classified)
        result += '\n' + '    Uncorrectly classified instances: ' + str(overall_stats.statslist[i].uncorrectly_classified)
        result += '\n' + '    Classification accuracy: ' + str(overall_stats.statslist[i].class_accuracy)
    
    for i in range(0, len(Record_list)):
        print(i)
        result += '\n\n********************************************************************************'
        result += '\n' + str(i) + '----- Instance:' + str(Record_list[i].record_num) + '----- Real class:'+ Record_list[i].class_name + '----- Predicted class:' + Record_list[i].predicted_class
        #print('\n', i, '----- Instance:', Record_list[i].record_num, '----- Real class:',Record_list[i].class_name, '----- Predicted class:',Record_list[i].predicted_class)
        for j in range(0, len(Record_list[i].possible_predictions)):
            result += '\n\n' + '    Possible prediction class:' + Record_list[i].possible_predictions[j].class_name + '----- Score:' + str(Record_list[i].possible_predictions[j].class_score)
            #print('Possible prediction class:', Record_list[i].possible_predictions[j].class_name, '----- Score:', Record_list[i].possible_predictions[j].class_score)
            for m in range(0, len(Record_list[i].possible_predictions[j].itemsets)):
                if (len(Record_list[i].possible_predictions[j].itemsets[m].items) < 2):
                    result += '\n' + '        Itemset:[' + str(Record_list[i].possible_predictions[j].itemsets[m].return_itemset_text(Feature_list)) + '] ----- Confidence:' + str(Record_list[i].possible_predictions[j].itemsets[m].confidence) + '----- Class_support:' + str(Record_list[i].possible_predictions[j].itemsets[m].support) + '----- Overall_support:' + str(Record_list[i].possible_predictions[j].itemsets[m].overall_support)
                    #print('    Itemset:', Record_list[i].possible_predictions[j].itemsets[m].return_itemset_text(Feature_list), '----- Confidence:', Record_list[i].possible_predictions[j].itemsets[m].confidence, '----- Class_support:', Record_list[i].possible_predictions[j].itemsets[m].support, '----- Overall_support:', Record_list[i].possible_predictions[j].itemsets[m].overall_support)
                
    output_file = open('Test\\Result.txt', 'w')
    output_file.write(result)
    output_file.close()
    




if __name__ == '__main__':
    main(sys.argv[1:])