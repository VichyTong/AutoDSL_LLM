import json
import os
import re
import sys

import openai

openai.api_key = os.environ['OPENAI_API_KEY']


def get_reagents(reagents_text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant to find out the Reagents, I will give you some example. If the ingredients list is given, just tell me the main reagent, not the ingredients. "},
            {"role": "user", "content": "10x TBST: To prepare 1L, 80 g of NaCl, 30 g Tris, pH 8, add 5 mL of Tween-20 and increase the volume with ddH<sub>2</sub>O."},
            {"role": "assistant", "content": "10x TBST"},
            {"role": "user", "content": "Thermostable high fidelity Pfu DNA polymerase and its buffer can be obtained from Stratagene \\(La Jolla, CA)"},
            {"role": "assistant", "content": "Thermostable high fidelity Pfu DNA polymerase, Thermostable high fidelity Pfu DNA polymerase's buffer"},
            {"role": "user", "content": reagents_text}
        ],
        max_tokens=1000,
        temperature=0,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["END"]
    )
    resp = response['choices'][0]['message']['content']
    if re.match("None", resp) is not None:
        return None
    return resp.split(", ")


def get_equipments(equipments_text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant to find out the relation between the entities, I will give you some example. If there is no relation, just output a single word \"None.\""},
            {"role": "user", "content": "Polymerase chain reaction is carried out using the multi block system \\(MBS) satellite thermal cycler \\(Thermo Electron Corporation, Waltham, MA)"},
            {"role": "assistant", "content": "multi block system, satellite thermal cycler"},
            {"role": "user", "content": "FACS analysis is performed using FACS-Calibur cytometer \\(Becton Dickinson, San Jose, CA)."},
            {"role": "assistant", "content": "FACS-Calibur cytometer"},
            {"role": "user", "content": equipments_text}
        ],
        max_tokens=1000,
        temperature=0,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["END"]
    )
    resp = response['choices'][0]['message']['content']
    if re.match("None", resp) is not None:
        return None
    return resp.split(", ")


def parse_relation_response(relation_str):
    res = []
    tmp = relation_str.split('), (')
    for x in tmp:
        res.append(x.split(' | '))
    return res


def get_relations(reagents, equipments, procedure):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant to extrapolate as many relationships as possible from the Procedure in a form of (entity | relation | entity). If there is no realtionships, just output a single word \"None.\""},
            {"role": "user", "content": "Reagents List: " + "Pfu buffer, upstream and downstream primer, dNTPs mix, pXa-1, DMSO, Pfu DNA polymerase, autoclaved ddH<sub>2</sub>O"},
            {"role": "user", "content": "Equipments List: " + ""},
            {"role": "user", "content": "Procedure: " + "Polymerase chain reaction. The PSTCD BAP sequence \\(387 bp) is first amplified by PCR from pXa-1 plasmid \\(Promega, Madison, WI) as follows: for each reaction, add 5 \u00b5l  Pfu buffer \\(10x buffer). Set the conditions for the PCR as follows: an initial denaturation step at 95 <sup>o</sup>C for 3 min followed by 35 cycles of 30 sec 95 <sup>o</sup>C denaturation, 30 sec 48 <sup>o</sup>C annealing, 1 min 72 <sup>o</sup>C extension and a final extension step of 10 min"},
            {"role": "assistant", "content": "(PSTCD BAP sequence | amplified by | PCR), (pXa-1 plasmid | used for | PCR amplification), (Pfu buffer | added in | PCR reaction), (PCR reaction | set with conditions of | initial denaturation step), (PCR reaction | set with conditions of | 35 cycles of denaturation, annealing, and extension), (PCR reaction | set with conditions of | final extension step)"},
            {"role": "user", "content": "" if reagents is None else "Reagents List: " + ", ".join(reagents)},
            {"role": "user", "content": "" if equipments is None else "Equipments List: " + ", ".join(equipments)},
            {"role": "user", "content": "Procedure: " + procedure}
        ],
        max_tokens=2500,
        temperature=0,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["END"]
    )
    resp = response['choices'][0]['message']['content']
    if re.search("None", resp) is not None:
        return None
    return parse_relation_response(resp[1: -2])


def is_meaningful(s):
    print(s)
    if len(s) < 10:
        return False
    else:
        return True


def get_classifications(instruction, relations):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant to categorize among the provided relationships, classify set of relationships that have operations, reagents, equipments, and conditions. Out put in json form. If there is no relationships, just output a single word \"None\"."},
            {"role": "system", "content": "Here is a instruction for you to learn from:" + instruction},
            {"role": "user", "content": "['PSTCD BAP sequence', 'amplified by', 'PCR'], ['pXa-1 plasmid', 'used for', 'PCR amplification'], ['Pfu buffer', 'added in', 'PCR reaction'], ['upstream and downstream primer', 'added in', 'PCR reaction'], ['PCR reaction', 'set with conditions of', '35 cycles of denaturation, annealing, and extension'], ['PCR reaction', 'set with conditions of', 'final extension ste']"},
            {"role": "assistant", "content": '[{"operation": "add", "reagent": "Pfu buffer, PCR reaction", "equipment": "None", "condition": "5 cycles of denaturation, annealing, and extension"}, {"operation": "add", "reagent": "upstream and downstream primer, PCR reaction", "equipment": "None", "condition": "5 cycles of denaturation, annealing, and extension"}]'},
            {"role": "user", "content": relations}
        ],
        max_tokens=1000,
        temperature=0,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["END"]
    )
    resp = response['choices'][0]['message']['content']
    if re.match("None", resp) is not None:
        return None
    return json.loads(resp)


def parse_file(path, filename):
    instruction_string = ""
    with open("../isa.jsonl", "r") as f:
        for line in f:
            instruction_string += line
    with open(path + filename, 'r') as f:
        data = json.load(f)
        reagents_text = ""
        equipments_text = ""
        procedure_text = ""
        for text in data["content"]:
            if text["header"] == "Reagents":
                reagents_text = text["content"]
            if text["header"] == "Equipment":
                equipments_text = text["content"]
            if text["header"] == "Procedure":
                procedure_text = text["content"]

        if reagents_text != "":
            reagents = get_reagents(reagents_text)
            print(reagents)
        if equipments_text != "":
            equipments = get_equipments(equipments_text)
            print(equipments)

        procedure_divided = procedure_text.split('\n')
        relations = []
        all_relations = []
        classifications = []
        for procedure in procedure_divided:
            if is_meaningful(procedure):
                relations_divided = get_relations(reagents, equipments, procedure)
                if relations_divided is not None:
                    for relation_divided in relations_divided:
                        relations.append(relation_divided)
                        all_relations.append(relation_divided)
                    classification = get_classifications(instruction_string, str(relations))
                    if classification is not None:
                        for x in classification:
                            x["origin"] = procedure
                            classifications.append(x)
                    relations.clear()
        with open("../../output/baseline3/" + "KG_" + filename, "w", encoding='utf8') as out:
            json.dump(all_relations, out, indent=4, ensure_ascii=False)
        with open("../../output/baseline3/" + "output_" + filename, "w", encoding='utf8') as out:
            json.dump(classifications, out, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    f_name = sys.argv[1]
    print("../../protocols/" + f_name)
    parse_file('../../protocols/', f_name)

