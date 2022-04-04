#!/usr/bin/env python3
import csv
import json
import sys

# generate json parameters for tiger graph
# [python3] ./gen_para.py <src/para.txt> <outdir> <query>
# eg: python3 gen_para.py interactive_1_param.txt out ic1

def create_map(query, row):
  with open("param.json",'r') as load_f:
    s = load_f.read()
    load_dict = eval(s)
  
  if query == 'ic1':
    load_dict['ic1'] = {"personId":row[0], "firstName":row[1]}
    return load_dict
  else:
    print("unsupported query")
    exit(-1)

def create_json(row, json_index):
  dst = sys.argv[2]
  query = sys.argv[3]
  with open(dst + '/' + query + '_' + str(json_index) + '.json', 'w+') as js:
    js.write(json.dumps(create_map(query, row), indent=4, separators=(',', ': ')))
    js.close()

def main(process):
  src = sys.argv[1]
  with open(src, 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter='|')
    index = -1
    for row in reader:
      index += 1
      if index == 0:
        continue
      process(row, index)
    csvfile.close()

if __name__ == '__main__':
  main(create_json)
