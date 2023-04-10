import json
import os
import re
import sys

import openai

openai.api_key = os.environ['OPENAI_API_KEY']


def is_meaningful(s):
    if len(s) < 10:
        return False
    else:
        return True


def test_isa(instruction):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a helpful assistant to tell me the instructions, say what you learn from the json file."},
            {"role": "user", "content": instruction}
        ],
        max_tokens=2500,
        temperature=0,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["END"]
    )
    resp = response['choices'][0]['message']['content']
    return resp


def get_classifications(instruction, relations):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a helpful assistant to summarize the procedure, classify set of relationships in the form of instructions. Out put in json form. Do not output other words. If there is no relationships, just output a single word \"None\"."},
            {"role": "user",
             "content": "Polymerase chain reaction. The PSTCD BAP sequence \\(387 bp) is first amplified by PCR from pXa-1 plasmad \\(Promega, Madison, WI) as follows: for each reaction, add 5 \u00b5l Pfu buffer \\ (10x buffer), 2.5 \u00b5l of each upstream and downstream primer \\(10 \u03bcM), 1.5 \u00b5l dNTPs mix \\(5 mM). Set the conditions for the PCR as follows: an initial denaturation step at 95 <sup>o</sup>C for 3 min followed by 35 cycles of 30 sec 95 <sup>o</sup>C denaturation, 30 sec 48 <sup>o</sup>C annealing, 1 min 72 <sup>o</sup>C extension and a final extension step of 10 min."},
            {"role": "assistant",
             "content": '[{"name": "add", "reagent1": "5µl Pfu buffer(10x buffer)", "reagent2": "PCR reaction reagent"}, {"name": "add", "reagent1": "2.5μl of upstream primer", "reagent2": "PCR reaction reagent"}, {"name": "add", "reagent1": "2.5μl of downstream primer", "reagent2": "PCR reaction reagent"}, {"name": "add", "reagent1": "1.5μl dNTPs mix(5 mM)", "reagent2": "PCR reaction reagent"}, {"name": "incubate", "reagent1": "PCR reaction reagent", "thermo_program": "initial denaturation step at 95°C for 3 min followed by 35 cycles of 30 sec 95°C denaturation, 30 sec 48°C annealing, 1 min 72°C extension and a final extension step of 10 min"}]'},
            {"role": "user", "content": relations}
        ],
        max_tokens=2000,
        temperature=0,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["END"]
    )
    resp = response['choices'][0]['message']['content']
    if re.match("None", resp) is not None:
        return None
    print("resp : " + resp)
    return json.loads(resp.replace("\n", ""))


def parse_file(path, filename):
    instruction_string = ""
    with open("../isa.jsonl", "r") as f:
        for line in f:
            instruction_string += line
    with open(path + filename, 'r') as f:
        data = json.load(f)
        procedure_text = ""
        for text in data["content"]:
            if text["header"] == "Procedure":
                procedure_text = text["content"]
        procedure_divided = procedure_text.split('\n')
        classifications = []
        for procedure in procedure_divided:
            if is_meaningful(procedure):
                print(procedure)
                classification = get_classifications(instruction_string, procedure)
                if classification is not None:
                    for x in classification:
                        x['origin'] = procedure
                        classifications.append(x)

        with open("../../output/baseline4/" + "output_" + filename, "w", encoding='utf8') as out:
            json.dump(classifications, out, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    f_name = sys.argv[1]
    print("../../protocols/" + f_name)
    parse_file('../../protocols/', f_name)
