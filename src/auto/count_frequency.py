import os
import json


def count(path):
    g = os.walk(path)
    files = []
    for path, dir_list, file_list in g:
        for file_name in file_list:
            files.append(os.path.join(path, file_name))
    freq = {}
    for file in files:
        with open(file, 'r') as f:
            data = json.load(f)
            for d in data:
                op = d.lower()
                if op not in freq:
                    freq[op] = data[d]["Frequency"]
                else:
                    freq[op] += data[d]["Frequency"]
    output = []
    for i in sorted(freq.items(), key=lambda x: x[1], reverse=True):
        tmp = {"opcode": i[0], "frequency": i[1]}
        output.append(tmp)
    with open("../../output/auto/" + "opcode_freq.json", "w", encoding='utf8') as out:
        json.dump(output, out, indent=4)


count('../../output/auto/')
