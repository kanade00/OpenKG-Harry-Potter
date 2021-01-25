import json
import re

with open('harry_potter_property.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

house_set = set()
blood_set = set()

for character in data.keys():
    character_info = data[character]
    if "学院" in character_info:
        house = character_info["学院"]
        house = house.replace("学院", "")
        house = house.replace("萊", "莱")
        house_set.add(house)
        house = house + "学院"
        character_info["学院"] = house
    if "血统" in character_info:
        blood = character_info["血统"]
        blood = re.sub(u"\\(.*?\\)", "", blood)
        blood = re.sub(u"（.*?）", "", blood)
        blood = re.sub(" ", "", blood)
        if blood == "未知":
            blood = "未知血统"
        if blood == "纯血":
            blood = "纯血统"
        if "媚娃" in blood:
            blood = "混血媚娃"
        blood_set.add(blood)
        character_info["血统"] = blood


for character in data.keys():
    character_info = data[character]
    if "从属" in character_info:
        group_list = character_info["从属"]
        for i in range(len(group_list)):
            group = group_list[i]
            group = re.sub(u"\\(.*?\\)", "", group)
            group = re.sub(u"（.*?）", "", group)
            if group == "霍格沃茨":
                group = "霍格沃茨魔法学校"
            if group in house_set:
                group += "学院"
            if group == "预言家日报":
                group = "《预言家日报》"
            group = group.replace(" ", "")
            group = group.replace("\xa0", "")
            group_list[i] = group

with open('harry_potter_property.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=1)
