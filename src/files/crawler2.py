import os
from typing import List
import requests
from pathlib import Path
from threading import Thread
import json


def dispay_components(components):
    all_components = []
    monstr = ""
    for i in components:
        if i == ",":
            all_components.append(monstr.strip().replace("\r", ""))
            monstr = ""
        if i != ",":
            monstr += i
    for j in range(len(all_components) - 1):
        index = all_components[j].find("(")
        if index >= 0:
            all_components[j] = all_components[j][0:index]
    return all_components


def display_levels(level):
    all_levels = dict()
    levels = level.strip().split(",")
    for level in levels:
        splat = level.strip().split(" ")
        all_levels[splat[0]] = splat[1]

    txt = '    "wizard": '
    wizard = all_levels.get("wizard", 0)
    txt += str(bool(wizard)).lower()

    txt += ',    "level": '
    txt += str(wizard)

    return txt


def make_json_spell(spell, list: List):
    spell = spell.strip()
    url = 'https://aonprd.com/SpellDisplay.aspx?ItemName=' + spell
    r = requests.get(url)
    truc = r.text

    spell_info = "{\n"

    spell_info += '    "name": "' + spell + '", \n'

    index = truc.find("Level</b>") + 9
    if index <= 9:
        spell_info += '    "level": "0",\n'
    else:
        truc = truc[index:]
        spell_info += display_levels(truc[0:truc.find("<h3")].strip()) + ', \n'

    index = truc.find("Components</b>") + 14
    if index <= 14:
        spell_info += '    "spell_resistance": "no"\n'
    else:
        truc = truc[index:]
        components = truc[0:truc.find("<h3")] + '", \n'
        all_components = dispay_components(components)
        spell_info += '    "components": ['
        for k in range(len(all_components) - 1):
            spell_info += '"' + all_components[k].strip() + '", '
        spell_info += '"' + \
            all_components[len(all_components) - 1].strip() + '],\n'

    index = truc.find("Spell Resistance</b>") + 20
    if index <= 20:
        spell_info += '    "spell_resistance": "no"\n'
    else:
        truc = truc[index:]
        spell_info += '    "spell_resistance": "' + \
            truc[0:truc.find("<h3")].strip() + '"\n'

    spell_info += "},\n"

    list.append(spell_info)


url = 'https://aonprd.com/Spells.aspx?Class=All'
r = requests.get(url)
truc = r.text

tab_spell = []

i = 1

while(i >= 0):
    i = truc.find("SpellDisplay.aspx?ItemName=")
    if i >= 0:
        truc = truc[i + 27:]
        guillemets = truc.find('"')
        tab_spell.append(truc[0: guillemets])

filename = r"onlinespells1.json"
file_path = Path.cwd().joinpath(filename)

all_spells = []
threads = []
n_threads = 512

count = 0
count_f_path = Path.cwd().joinpath("count")

if not Path.exists(count_f_path):
    with open(count_f_path, "x") as count_f:
        count_f.write("0")
else:
    with open(count_f_path) as count_f:
        count = int(count_f.read())

if not file_path.exists():
    with open(file_path, "x") as all_spells_f:
        all_spells_f.write("[\n")


for j in range(len(tab_spell)):

    if j < count:
        continue

    print(j)
    if tab_spell[j] != "Status, Greater":

        t = Thread(target=make_json_spell, args=[tab_spell[j], all_spells])
        t.start()
        threads.append(t)
    if len(threads) >= n_threads:
        for t in threads:
            t.join()
            count += 1

        with open(file_path, "a") as all_spells_f:
            all_spells_f.writelines(all_spells)

        with open(count_f_path, "wt") as count_f:
            count_f.write(str(count))

        all_spells = []
        threads = []

with open(file_path, "r") as all_spells_f:
    all_spells = all_spells_f.read()

all_spells = all_spells[:-2] + "\n]"

with open(file_path, "w") as all_spells_f:
    all_spells_f.write(json.dumps(json.loads(all_spells)))

os.remove(count_f_path)
