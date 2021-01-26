# -*- coding: utf-8 -*-
import json
import pandas as pd
from pprint import pprint

df = pd.read_excel('人物关系表.xlsx')
# relations = list(df['关系'].unique())
# relations.remove('unknown')
# relation_dict = {'unknown': 0}
# relation_dict.update(dict(zip(relations, range(1, len(relations)+1))))

# with open('rel_dict.json', 'w', encoding='utf-8') as h:
#     h.write(json.dumps(relation_dict, ensure_ascii=False, indent=2))

# print('总数: %s' % len(df))
# pprint(df['关系'].value_counts())
# df['rel'] = df['关系'].apply(lambda x: relation_dict[x])

texts = []
for per1, per2, relation, sentence in zip(df['人物1'].tolist(), df['人物2'].tolist(), df['关系'].tolist(), df['文本'].tolist()):
    text = ','.join(["\""+sentence+"\"", relation, per1, str(sentence.find(per1)), per2, str(sentence.find(per2))])
    texts.append(text)

df['text'] = texts

train_df = df.sample(frac=0.8, random_state=22021209)
other_df = df.drop(train_df.index)
valid_df = other_df.sample(frac=0.5, random_state=22021209)
test_df = other_df.drop(valid_df.index)

with open('train.csv', 'w', encoding='utf-8') as f:
    f.write('\ufeff')
    f.write('sentence,relation,head,head_offset,tail,tail_offset\n')
    for t in train_df['text'].to_list():
        f.write(t + '\n')

with open('valid.csv', 'w', encoding='utf-8') as f:
    f.write('\ufeff')
    f.write('sentence,relation,head,head_offset,tail,tail_offset\n')
    for t in valid_df['text'].to_list():
        f.write(t + '\n')

with open('test.csv', 'w', encoding='utf-8') as f:
    f.write('\ufeff')
    f.write('sentence,relation,head,head_offset,tail,tail_offset\n')
    for t in test_df['text'].to_list():
        f.write(t + '\n')