
from py2neo import Graph
from question_processor import question_process, generate_answer

graph = Graph(
    host='127.0.0.1',
    http_port='7474',
    user='neo4j',
    password='dby'
)

while True:
    question = input('问题:')
    question_info = question_process(question)
    if type(question_info) == str:
        print(question_info)
    else:
        if len(question_info) == 0:
            print("无法在问句提取到支持的信息")
        else:
            answer = generate_answer(graph, question_info)
            print('回答:', answer)