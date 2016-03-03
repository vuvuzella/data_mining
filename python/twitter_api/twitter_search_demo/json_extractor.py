"""
Extracts desired info from a json.load output
"""
import json

source = "./response_data.txt"
options = "r"
load_file = open(source, options).read()
# data_dict = json.loads(json.dumps(load_file))
data_dict = json.loads(load_file)
status_dict = data_dict['statuses']
# print json.dumps(data_dict['statuses'], indent=4, sort_keys=True)
print type(status_dict[0])

for tweet in status_dict:
    text = tweet['text']
    print json.dumps(text)
