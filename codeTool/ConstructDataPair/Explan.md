#### Construct data pairs<wa or tle, ac>
1.Process and generate records for each question into the corresponding directory's JSON file using OrangizeRecord.py

#### Execute the code in the data pairs to populate "code1_test_status": [] and the values of "code1_test_score"
2. While executing, also validate the data for correctness, and discard or flag any invalid data
AddTestResultForRecord.py

project/
│
├── A/
│   ├── __init__.py
│   └── main.py
└── B/
    ├── __init__.py
    └── helpers.py


cd project
export PYTHONPATH=$(pwd)
python A/main.py
