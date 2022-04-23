#!/usr/bin/env python3

import os
import sys
import json
import datetime
import time

# python ./query_bench <query> <params>
# eg python ./query_bench.py ic1 parameters/ic1

def to_json(query, params, time):
  target_dict = {}
  target_dict["input"] = params
  target_dict["query"] = query
  with open("results" + '/' + query + '.txt', 'r') as txt:
    lines = txt.readline()
    lines = lines.splitlines()
    target = []
    for line in lines:
      load_dict = eval(line)[2]
      if query == "ic1":
        target.append(convert_ic1(load_dict))
    target_dict["result"] = target

  target_dict["time_elapsed"] = time    
  return target_dict

def convert_ic1(dict):
  keys = [key for key in dict.keys()]
  for key in keys:
    # print(key)
    new_key = key[7:]
    new_key = key[6].lower() + new_key
    dict[new_key] = dict.pop(key)
  dict["distance"] = dict.pop("ceFromPerson")
  for c in dict["companies"]:
    c["name"] = c.pop("orgName")
    c["workFrom"] = c.pop("orgYear")
    c["countryName"] = c.pop("orgPlace")

  for u in dict["universities"]:
    u["name"] = u.pop("orgName")
    u["classYear"] = u.pop("orgYear")
    u["cityName"] = u.pop("orgPlace")

  dict["birthday"] = int(datetime.datetime.strptime(dict["birthday"], "%Y-%m-%d %H:%M:%S").timestamp() * 1000)
  dict["creationDate"] = int(datetime.datetime.strptime(dict["creationDate"], "%Y-%m-%d %H:%M:%S").timestamp() * 1000)

  return dict


if __name__ == '__main__':
  query = sys.argv[1]
  para_dir = sys.argv[2]

  for root, _, files in os.walk(para_dir):
    with open("results/" + query + '.json', 'w+') as js:
      results = []
      for file in files:
        para_file = os.path.join(root, file)
        time = -1
        # print(para_file, "./driver.py run -q " + sys.argv[1] + " -p " + para_file)
        para = {}
        with os.popen("./driver.py run -q " + query + " -p " + para_file) as stdo:
          result = stdo.read()
          print(result)
          time = result.splitlines()[3].split()[2]
          with open(para_file, 'r') as para_json:
            s = para_json.read()
            para = eval(s)['ic1']
        target = to_json(query, para, time)
        results.append(target)
      js.write(json.dumps(results, indent=4, separators=(',', ': ')))

        
        


    
