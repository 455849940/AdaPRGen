import json

class CustomJSONEncoder(json.JSONEncoder):
    def encode(self, obj):
        return self.encode_dict(obj)
        

    def encode_dict(self, obj):
        
        items = []

        for key, value in obj.items():

            item = f'        "{key}": {json.dumps(value, ensure_ascii=False)}'
            items.append(item)
        return '    {\n' + ',\n'.join(items) + '\n    }'

def save_data_to_json(data, filepath):
    """
    Save data to a JSON file at the specified path, ensuring that specific list fields do not have newlines,
    while other fields do.

    Args:
        data (list): The list of data to be saved.
        filepath (str): The path where the JSON file will be saved.
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as json_file:
            json_file.write('[\n')
            for i, element in enumerate(data):
                print(type(element))
                json_file.write(CustomJSONEncoder().encode(element))
                if i < len(data) - 1:
                    json_file.write(',\n')
            json_file.write('\n]')
        print(f"saved {filepath}")
    except Exception as e:
        print(f"save data error: {e}")

data = [{
    "submission1_id": "S324109094",
    "submission2_id": "S459822627",
    "status1": "Wrong Answer",
    "status2": "Accepted",
    "code1": "\n\n\n\nli = []\nfor x in range(3):\n    s = input()\n    s = int(s)\n    li.append(s)\n\n",
    "code2": "\n\n\n\nli = []\nfor x in range(10):\n    s = input()\n    s = int(s)\n    li.append(s)\n\n",
    "original_language1": "Python3",
    "original_language2": "Python3",
    "date1": 1410776608,
    "date2": 1410776776,
    "bleu_score": 0.974890996887752,
    "code1_test_status": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
},{
    "submission1_id": "S324109094",
    "submission2_id": "S459822627",
    "status1": "Wrong Answer",
    "status2": "Accepted",
    "code1": "\n\n\n\nli = []\nfor x in range(3):\n    s = input()\n    s = int(s)\n    li.append(s)\n\n",
    "code2": "\n\n\n\nli = []\nfor x in range(10):\n    s = input()\n    s = int(s)\n    li.append(s)\n\n",
    "original_language1": "Python3",
    "original_language2": "Python3",
    "date1": 1410776608,
    "date2": 1410776776,
    "bleu_score": 0.974890996887752,
    "code1_test_status": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
},{
    "submission1_id": "S324109094",
    "submission2_id": "S459822627",
    "status1": "Wrong Answer",
    "status2": "Accepted",
    "code1": "\n\n\n\nli = []\nfor x in range(3):\n    s = input()\n    s = int(s)\n    li.append(s)\n\n",
    "code2": "\n\n\n\nli = []\nfor x in range(10):\n    s = input()\n    s = int(s)\n    li.append(s)\n\n",
    "original_language1": "Python3",
    "original_language2": "Python3",
    "date1": 1410776608,
    "date2": 1410776776,
    "bleu_score": 0.974890996887752,
    "code1_test_status": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
}]

def load_list_from_json(input_file_path):
        with open(input_file_path, 'r') as json_file:
            data_list = json.load(json_file)
        return data_list

if __name__ == "__main__":
    save_data_to_json(data, './file.json')
    datalist = load_list_from_json('./file.json')
    for item in datalist:
        print(type(item))
        print(item["code1_test_status"])