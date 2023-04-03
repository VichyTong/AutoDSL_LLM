import json
import os
import openai

openai.api_key = os.environ['OPENAI_API_KEY']


def get_reagents(reagents_text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant to find out the Reagents, I will give you some example. If the ingredients list is given, just tell me the main reagent, not the ingredients,"},
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
    print(response['choices'][0]['message']['content'])
    return response['choices'][0]['message']['content'].split(", ")


def get_equipments(equipments_text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant to find out the relation between the entities, I will give you some example."},
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
    print(response['choices'][0]['message']['content'])
    return response['choices'][0]['message']['content'].split(", ")


def get_relations(reagents, equipments, procedure):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant to extrapolate as many relationships as possible from the Procedure in a form of (entity, relation, entity)."},
            {"role": "user", "content": "Reagents List: " + ", ".join(reagents)},
            {"role": "user", "content": "Equipments List: " + ", ".join(equipments)},
            {"role": "user", "content": "Procedure: " + "Polymerase chain reaction. The PSTCD BAP sequence \\(387 bp) is first amplified by PCR from pXa-1 plasmid \\(Promega, Madison, WI) as follows: for each reaction, add 5 \u00b5l  Pfu buffer \\(10x buffer), 2.5 \u00b5l of each upstream and downstream primer \\(10 \u03bcM), 1.5 \u00b5l dNTPs mix \\(5 mM), 1 \u00b5l  pXa-1 \\(20 mg/L), 5 \u00b5l DMSO \\(Critical, PCR of BAP is not successful without it), 1 \u00b5l Pfu DNA polymerase \\(2.5 units/\u00b5l) and increase the volume to 50 \u00b5l with autoclaved ddH<sub>2</sub>O. Set the conditions for the PCR as follows: an initial denaturation step at 95 <sup>o</sup>C for 3 min followed by 35 cycles of 30 sec 95 <sup>o</sup>C denaturation, 30 sec 48 <sup>o</sup>C annealing, 1 min 72 <sup>o</sup>C extension and a final extension step of 10 min"},
        ],
        max_tokens=3000,
        temperature=0,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["END"]
    )
    print(response['choices'][0]['message']['content'])


if __name__ == "__main__":
    with open('../../protocols/protocol_nprot-4.json', 'r') as f:
        data = json.load(f)
        reagents_text = data["content"][1]["content"]
        equipments_text = data["content"][2]["content"]
        procedure_text = data["content"][3]["content"]
        reagents = get_reagents(reagents_text)
        equipments = get_equipments(equipments_text)
        relations = get_relations(reagents, equipments, procedure_text)

