import ahocorasick
from py2neo import Graph

def question_process(question):
    res = []
    properties = ["出生", "逝世", "血统", "物种", "性别", "身高", "婚姻", "职业", "学院"]
    file = open('character_list.txt', 'r', encoding='utf-8')
    character_list = file.read().split(",")
    file = open('group_list.txt', 'r', encoding='utf-8')
    group_list = file.read().split(",")
    file = open('relation_list.txt', 'r', encoding='utf-8')
    relation_list = file.read().split(",")

    properties_words = search_words(properties, question)
    character_words = search_words(character_list, question)
    group_words = search_words(group_list, question)
    relation_words = search_words(relation_list, question)
    belong_words = search_words(["从属", "隶属", "属于", "组织", "成员"], question)

    if len(character_words) > 1:
        return "无法识别问句，包含过多角色名字"

    if len(group_words) > 1:
        return "无法识别问句，包含过多组织名字"

    if len(character_words) == 1 and len(properties_words) >= 1:
        res.append(("character_property", character_words[0], properties_words))

    if len(character_words) == 1 and len(relation_words) >= 1:
        if question.index(character_words[0]) < question.index(relation_words[0]):
            res.append(("character_relation", character_words[0], relation_words))
        else:
            res.append(("character_relation_rev", character_words[0], relation_words))

    if len(belong_words) >= 1 and len(character_words) >= 1:
        res.append(("character_group", character_words[0]))
    elif len(belong_words) >= 1 and len(group_words) >= 1:
        res.append(("group_character", group_words[0]))

    return res

def search_words(key_list, question):
    res = []
    A = ahocorasick.Automaton()
    for index, word in enumerate(key_list):
        A.add_word(word, (index, word))
    A.make_automaton()

    for item in A.iter(question):
        res.append(item[1][1])
    return res


def generate_answer(graph, question_info):
    answer = ""

    for item in question_info:
        if item[0] == "character_property":
            for property in item[2]:
                if property == '婚姻':
                    property = '婚姻状况'
                if property == '血统' or property == '学院':
                    query_res = graph.run(
                        "MATCH (n:ns0__Character)-[:ns0__{}]-(b) "
                        "WHERE n.ns0__name = $name "
                        "RETURN b.ns0__name".format(property),
                        {"name": item[1]}
                    )
                else:
                    query_res = graph.run(
                        "MATCH (n:ns0__Character)  "
                        "WHERE n.ns0__name = $name "
                        "RETURN n.ns0__{}".format(property),
                        {"name": item[1]}
                    )
                query_res = list(query_res)
                if len(query_res) > 0:
                    answer += "{}的{}是".format(item[1], property)
                    answer = add_list_info(query_res, answer)
                    answer += "\n"
                else:
                    answer += "数据库中不存在{}的{}信息\n".format(item[1], property)
        elif item[0] == "character_relation":
            for relation in item[2]:
                query_res = graph.run(
                    "MATCH (n:ns0__Character)-[:ns0__{}]->(m:ns0__Character) "
                    "WHERE n.ns0__name = $name "
                    "RETURN m.ns0__name".format(relation),
                    {"name": item[1]}
                )
                query_res = list(query_res)
                if len(query_res) > 0:
                    answer += "{}的{}是".format(item[1], relation)
                    answer = add_list_info(query_res, answer)
                    answer += "\n"
                else:
                    answer += "数据库中不存在{}的{}信息\n".format(item[1], relation)
        elif item[0] == "character_relation_rev":
            for relation in item[2]:
                query_res = graph.run(
                    "MATCH (n:ns0__Character)<-[:ns0__{}]-(m:ns0__Character) "
                    "WHERE n.ns0__name = $name "
                    "RETURN m.ns0__name".format(relation),
                    {"name": item[1]}
                )
                query_res = list(query_res)
                if len(query_res) > 0:
                    answer = add_list_info(query_res, answer)
                    answer += "的{}是{}\n".format(relation, item[1])
                else:
                    answer += "数据库中不存在谁{}是{}信息\n".format(relation, item[1])
        elif item[0] == "character_group":
            query_res = graph.run(
                "MATCH (n:ns0__Character)-[:ns0__从属]-(m:ns0__Group) "
                "WHERE n.ns0__name = $name "
                "RETURN m.ns0__name",
                {"name": item[1]}
            )
            query_res = list(query_res)
            if len(query_res) > 0:
                answer += "{}从属的组织有：".format(item[1])
                answer = add_list_info(query_res, answer)
                answer += "\n"
            else:
                answer += "数据库中不存在{}的组织信息\n".format(item[1])
        elif item[0] == "group_character":
            query_res = graph.run(
                "MATCH (n:ns0__Character)-[:ns0__从属]-(m:ns0__Group) "
                "WHERE m.ns0__name = $name "
                "RETURN n.ns0__name",
                {"name": item[1]}
            )
            query_res = list(query_res)
            if len(query_res) > 0:
                answer += "从属于{}的成员有：".format(item[1])
                answer = add_list_info(query_res, answer)
                answer += "\n"
            else:
                answer += "数据库中不存在{}的成员信息\n".format(item[1])

    return answer


def add_list_info(query_res, answer):
    count = 0
    for res in query_res:
        answer += "{} ".format(res[0])
        count += 1
        if count % 5 == 0:
            answer += "\n"
    return answer

graph = Graph(
    host='127.0.0.1',
    http_port='7474',
    user='neo4j',
    password='dby'
)

if __name__ == '__main__':
    question_info = question_process("哈利·波特属于哪些组织？")
    answer = generate_answer(graph, question_info)
    print(answer)