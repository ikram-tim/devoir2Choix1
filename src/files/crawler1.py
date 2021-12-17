from typing_extensions import final
from pip._vendor import requests
import json
import os
from pathlib import Path



# Cette fonction va récupérée les noms de chaques spells que peut lancer une créature
# On va pour se faire se servir "d'indicateurs" dans le code html
# "<h1 id=" nous indique quand nous arrivons sur les caractéristiques de la créature
# "../coreRlebook/spells/" nous signale le nom d'un spell
# on va de plus s'assurer que nous n'entrons pas deux fois le même spell
def get_spell_list(html_text, creature_name):
    # on touve la créature recherchée
    index = html_text.find('<h1 id="' + creature_name)
    html_text = html_text[index + 12:]
    # parfois, plusieurs créatures sont sur la même page, alors on s'assure de ne garder que celle qui nous interesse
    index = html_text.find('<h1 id="')
    if index >= 0:
        html_text = html_text[:index]
    list_all_spells = []
    index = 0
    while index >= 0:
        index = html_text.find('../coreRulebook/spells/')
        html_text = html_text[index + 15:]
        if index >= 0:
            spell = ""
            index2 = html_text.find('" >')
            if index2 < 0:
                index2 = html_text.find('">')
                spell = html_text[index2 + 2:html_text.find('</a>')]
                spell = spell.replace("'", "")
            else:
                spell = html_text[index2 + 3:html_text.find('</a>')]
                spell = spell.replace("'", "")
            encore_un_index = spell.find("<a/")
            if encore_un_index >= 0:
                spell = spell[:encore_un_index]
            encore_un_index = spell.find("<a")
            if encore_un_index >= 0:
                spell = spell[:encore_un_index]
            exist = False
            # on vérifie que le spell n'a pas déjà été ajouté
            for k in range(len(list_all_spells)):
                if list_all_spells[k] == spell:
                    exist = True
            if not exist:
                list_all_spells.append(spell)
    return list_all_spells



# C'est la méthode qui nous sort un json "joli", c'est à dire avec des retours à la ligne et des espaces
# Elle sert principalement à la verification du json
def Create_pretty_json(final_dict):
    final_json = "[{\n"

    for key, value in final_dict.items():
        final_json += '    "name": "' + key + '",\n    "spells": ' + str(value[0]) + ',\n    "url": ' + value[1] + '\n},\n{\n'

    final_json = final_json[:-4]
    final_json += ']'

    final_json = final_json.replace("'", '"')
    final_json = final_json.replace(",-", "-")

    filename = r"CreaturesAndSpells.json"
    file_path = Path.cwd().joinpath(filename)
    print(file_path)
    my_file = open(file_path, "w")

    my_file.write(final_json)

    my_file.close()



# C'est la méthode qui nous ressort un json en une ligne, sans espaces inutiles
# C'est ce json qui sera importé dans apache spark
def Create_Oneline_json(final_dict):
    final_json = "[{"

    for key, value in final_dict.items():
        final_json += '"name":"' + key + '","spells":' + str(value[0]) + ',"url":' + value[1] + '},{'

    final_json = final_json[:-2]
    final_json += ']'

    final_json = final_json.replace("'", '"')
    final_json = final_json.replace(",-", "-")

    filename = r"CreaturesAndSpellsOneLine.json"
    file_path = Path.cwd().joinpath(filename)
    print(file_path)
    my_file = open(file_path, "w")

    my_file.write(final_json)

    my_file.close()



# On va créer une première liste avec les noms des créatures du premier bestiaire

url = 'http://legacy.aonprd.com/bestiary/monsterIndex.html'
r = requests.get(url)
html_text = r.text

tab_creature1 = []

i = 1

while(i >= 0):
    i = html_text.find(".html#")
    if i >= 0:
        html_text = html_text[i + 6:]
        guillemets = html_text.find('">')
        new_name = html_text[: guillemets]
        tab_creature1.append(new_name)
        html_text = html_text[guillemets:]

# On crée une seconde liste avec les noms des créatures du second bestiaire

url = 'http://paizo.com/pathfinderRPG/prd/bestiary2/additionalMonsterIndex.html'
r = requests.get(url)
html_text = r.text

tab_creature2 = []

i = 1

while(i >= 0):
    i = html_text.find(".html#")
    if i >= 0:
        html_text = html_text[i + 6:]
        guillemets = html_text.find('">')
        new_name = html_text[: guillemets]
        tab_creature2.append(new_name)
        html_text = html_text[guillemets:]

# On fusionne ensuite les deux listes pour n'en avoir qu'une seule contenant les noms de toutes les créatures

tab_creature = []
i = 0
j = 0
while len(tab_creature) < len(tab_creature1) + len(tab_creature2) - 1:
    if tab_creature1[i] < tab_creature2[j]:
        tab_creature.append([1, tab_creature1[i]])
        i += 1
    else:
        tab_creature.append([2, tab_creature2[j]])
        j += 1

if i < len(tab_creature1) - 1:
    tab_creature.append(tab_creature1[i])
else:
    tab_creature.append(tab_creature2[j])

# On part ensuite sur les liens correspondants à chaque créature afin de récupérer les informations qui nous interessent

final_dict = {}

for j in range(len(tab_creature)):
# for j in range(5):
    url1 = "http://legacy.aonprd.com/bestiary/"
    url2 = "http://legacy.aonprd.com/bestiary2/"
    index = tab_creature[j][1].find("-")
    supplement = ""
    if index < 0:
        supplement = tab_creature[j][1] + ".html#" + tab_creature[j][1]
    else:
        index2 = tab_creature[j][1].find(",")
        if index2 < 0:
            supplement = tab_creature[j][1][:index] + ".html#" + tab_creature[j][1]
        else:
            supplement = tab_creature[j][1][:index2] + ".html#" + tab_creature[j][1]
    if tab_creature[j][0] == 1:
        print(url1 + supplement)
        r = requests.get(url1 + supplement)
        html_text = r.text
        list_all_spell = get_spell_list(html_text, tab_creature[j][1])
        final_dict[tab_creature[j][1]] = [list_all_spell, '"' + url1 + supplement + '"']
    else:
        print(url2 + supplement)
        r = requests.get(url2 + supplement)
        html_text = r.text
        list_all_spell = get_spell_list(html_text, tab_creature[j][1])
        final_dict[tab_creature[j][1]] = [list_all_spell, '"' + url2 + supplement + '"']
    

# Create_pretty_json(final_dict)
Create_Oneline_json(final_dict)