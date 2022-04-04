#!/usr/bin/env python3

import os
import sys

# python ./query_bench <query> <params>
# eg python ./query_bench.py ic1 out

para_dir = sys.argv[2]

for root, _, files in os.walk(para_dir):
  for file in files:
    para_file = os.path.join(root, file)
    # print(para_file, "./driver.py run -q " + sys.argv[1] + " -p " + para_file)
    os.system("./driver.py run -q " + sys.argv[1] + " -p " + para_file)
