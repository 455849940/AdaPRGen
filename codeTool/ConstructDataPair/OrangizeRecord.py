import pandas as pd
from collections import defaultdict

import json
from tqdm import tqdm
import re
from ..utlis.utils import load_list_from_json, calculate_md5
from .bleu import code_compute_bleu
# import load_list_from_json, calculate_md5
def remove_comments(code):
    """
    Remove comments from the code, including single-line and multi-line comments
    :param code: Code string containing comments
    :return: Code string with comments removed
    """
    # Define regular expressions for matching single-line and multi-line comments
    single_line_comment_pattern = r'//.*?$|#.*?$'
    multi_line_comment_pattern = r'/\*.*?\*/|\'\'\'.*?\'\'\'|""".*?"""'
    
    # Combine regular expressions
    pattern = re.compile(
        single_line_comment_pattern + '|' + multi_line_comment_pattern,
        re.DOTALL | re.MULTILINE
    )

    # Use regular expressions to remove comments
    cleaned_code = re.sub(pattern, '', code)
    
    return cleaned_code

# Define a user data structure
class UserData:
    def __init__(self, user_id):
        self.user_id = user_id
        self.records = []

    def add_record(self, record):
        self.records.append(record)




#Process the data for a single question
class SingleDataProcess:
    def __init__(self, CSVId, Resotre_File_Path, Language = "Python", Filt_Language = "Python3", prefix_url = "/home/develop/xxx/CodeFixProject/CodeDatasets/Project_CodeNet/"):
        # Create a default dictionary to store user data
        self.user_data_dict = defaultdict(lambda: UserData(None))
        self.prefix_url = prefix_url + "metadata"
        if 'p' not in CSVId:
            CSVId = f"p{CSVId}"
        CSV_Name = f"{self.prefix_url}/{CSVId}.csv"
        self.CSVId = CSVId
        self.Language = Language
        self.File_path = prefix_url + f"data/{CSVId}/{self.Language}"
        self.Resotre_File_Path = Resotre_File_Path
        
        # Construct and store the training data for this question
        self.filtered_records = []
        
        df = pd.read_csv(CSV_Name)

        # Filter using pandas built-in methods
        status_values = ['Accepted', 'Wrong Answer', 'Time Limit Exceeded']
        self.filtered_df = df[(df['language'] == Language) & ("Python (2" not in df['original_language']) & ("Python" != df['original_language']) & (df['status'].isin(status_values))].copy()

        if len( self.filtered_df) != 0:
            self.filtered_df = self.filtered_df.sort_values(by=['date', 'user_id'], ascending=[True, True]).copy()
            self.filtered_df.loc[:, 'useful'] = False
        
        for _, row in self.filtered_df.iterrows():
            user_id = row['user_id']
            if self.user_data_dict[user_id].user_id is None:
                self.user_data_dict[user_id] = UserData(user_id)
            self.user_data_dict[user_id].add_record(row)
            
    def read_python_file(self, submission_id):
        """Read the Python file at the specified path and return its content"""
        if self.Language == "Python":
            file_path = self.File_path + f"/{submission_id}.py"
        
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    
    def save_filtered_df(self, path_str = "./test_filtered_file.csv"):
        # Save the filtered DataFrame to a new CSV file
        self.filtered_df.to_csv(path_str, index=False)    
    
    def find_Specific_UserData(self, specific_user_id):
        if specific_user_id in self.user_data_dict:
            user_data = self.user_data_dict[specific_user_id]
            print(f"user ID: {user_data.user_id}")
            for record in user_data.records:
                print(record)
        else:
            print(f"No data found for user ID {specific_user_id}")

    # For the filtered wa, tle, and ac records of a single user, compute the similarity between each pair. Finally, perform a secondary filter on filtered_df to obtain usable data
    def Construct_Single_user_data(self, specific_user_id):
        user_data = self.user_data_dict[specific_user_id]
        Len = len(user_data.records)
        #record[j] is AC , record[i] is WA or TLE, they are similar() 
        s = -1
        t = -1
        maxval = 0
        for j in range(Len):
            
            if user_data.records[j]['status'] != "Accepted": 
                continue 
            t = j
            for i in range(0, j):
                if user_data.records[i]['original_language'] != user_data.records[j]['original_language']:continue
                code1 = self.read_python_file(user_data.records[i]['submission_id'])
                code2 = self.read_python_file(user_data.records[j]['submission_id'])
                code1 = remove_comments(code1)
                code2 = remove_comments(code2)
                if code1 == code2: continue 
                if len(code1) == 0 or len(code2) == 0:
                    bleu_score = 0
                else:
                    bleu_score = code_compute_bleu(code1, code2)
                if bleu_score > 0.60 and bleu_score > maxval:
                    maxval = bleu_score
                    s = i
            break
        
        if maxval > 0.60:
            user_data.records[s]['useful'] = True
            user_data.records[t]['useful'] = True
            filtered_record = {
                "user_id":user_data.records[s]['user_id'],
                "problem_id":user_data.records[s]['problem_id'],
                "submission1_id":user_data.records[s]['submission_id'],
                "submission2_id":user_data.records[t]['submission_id'],
                "status1":user_data.records[s]['status'],
                "status2":user_data.records[t]['status'],
                "code1":code1,
                "code2":code2,
                "original_language1":user_data.records[s]['original_language'],
                "original_language2":user_data.records[t]['original_language'],
                "date1":user_data.records[s]['date'],
                "date2":user_data.records[t]['date'],
                "bleu_score":bleu_score,
                "code1_test_status":[],
                "code1_test_score":0
            }
            #print(filtered_record)
            self.filtered_records.append(filtered_record)
                
    def Construct_submissionIDPairRecord_Set(self, first_path):
        file_path = first_path + f"{self.CSVId}.json"
        
        tmp_set = set()
        data_list = load_list_from_json(file_path)
        for item in data_list:
            tmpstr = item["submission1_id"] + item["submission1_id"] 
            tmp_set.add(tmpstr)
        return tmp_set

    def Construct_Single_user_data_Pattern2(self, specific_user_id, HaveRecordSet):
   
        user_data = self.user_data_dict[specific_user_id]
        Len = len(user_data.records)
        
        #record[j] is AC , record[i] is WA, they are similar() 
        s = -1
        t = -1
        AvailableRecordMd5Set = set()
        for j in range(Len):
            
            if user_data.records[j]['status'] != "Accepted": 
                continue
            t = j
            for i in range(0, j):
                if user_data.records[i]['original_language'] != user_data.records[j]['original_language']:continue
                code1 = self.read_python_file(user_data.records[i]['submission_id'])
                code2 = self.read_python_file(user_data.records[j]['submission_id'])
                code1 = remove_comments(code1)
                code2 = remove_comments(code2)
                if code1 == code2: continue 
                if len(code1) == 0 or len(code2) == 0:
                    bleu_score = 0
                else:
                    bleu_score = code_compute_bleu(code1, code2)
                if bleu_score > 0.60 and bleu_score:
                    tmp_str =  user_data.records[i]['submission_id'] + user_data.records[j]['submission_id']
                    if tmp_str in HaveRecordSet: continue
                    md5val = calculate_md5(code1)
                    if md5val not in AvailableRecordMd5Set:
                        AvailableRecordMd5Set.add(md5val)
                        user_data.records[i]['useful'] = True
                        user_data.records[t]['useful'] = True
                        filtered_record = {
                            "user_id":user_data.records[i]['user_id'],
                            "problem_id":user_data.records[i]['problem_id'],
                            "submission1_id":user_data.records[i]['submission_id'],
                            "submission2_id":user_data.records[t]['submission_id'],
                            "status1":user_data.records[i]['status'],
                            "status2":user_data.records[t]['status'],
                            "code1":code1,
                            "code2":code2,
                            "original_language1":user_data.records[i]['original_language'],
                            "original_language2":user_data.records[t]['original_language'],
                            "date1":user_data.records[i]['date'],
                            "date2":user_data.records[t]['date'],
                            "bleu_score":bleu_score,
                            "code1_test_status":[],
                            "code1_test_score":0
                        }
                        #print(filtered_record)
                        self.filtered_records.append(filtered_record)
            break


    def Construct_All_user_data(self, pattern = "First", first_path = "/home/develop/xxx/CodeFixProject/CodeFixDatasets/CodeFixPairData/PythonResultData_First/"):
        if pattern == "First":
            for k, v in self.user_data_dict.items():
                self.Construct_Single_user_data(k)
        else:
            for k, v in self.user_data_dict.items():
                HaveRecordSet = self.Construct_submissionIDPairRecord_Set(first_path)
                self.Construct_Single_user_data_Pattern2(k, HaveRecordSet)
        Resotre_File_name = self.Resotre_File_Path + f"{self.CSVId}.json"

        with open(Resotre_File_name, 'w') as json_file:
            json.dump(self.filtered_records, json_file, indent=4)
        
        
    
    
class AllDataProcess: 
    def __init__(self, Available_PId_path = "/home/develop/xxx/CodeFixProject/CodeFixDatasets/Program_Question_Data/Available_Filt_PId.json",\
        Resotre_File_Path = "/home/develop/xxx/CodeFixProject/CodeFixDatasets/CodeFixPairData/PythonData/"):
        self.Available_PId_Set = self.load_list_from_json(Available_PId_path)
        self.Resotre_File_Path = Resotre_File_Path 
        
    def load_list_from_json(self, input_file_path):
        """Read a list from a JSON file"""
        with open(input_file_path, 'r') as json_file:
            data_list = json.load(json_file)
        return data_list
    
    def ProcessAllData(self, pattern = "First"):
        for Pid in tqdm(self.Available_PId_Set, desc="Processing elements"):
            Single_data_process = SingleDataProcess(Pid, self.Resotre_File_Path)
            Single_data_process.Construct_All_user_data(pattern)


if __name__ == "__main__":
    #data_process = SingleDataProcess("00025","/home/develop/xxx/CodeFixProject/CodeFixDatasets/CodeFixPairData/")
    #data_process.Construct_All_user_data()
    #data_process.Construct_Single_user_data("u766477342")
    #data_process.save_filtered_df()

    alldataprocess = AllDataProcess()
    alldataprocess.ProcessAllData(pattern = "Second")
    
    
    