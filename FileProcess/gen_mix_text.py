#codinng=utf-8
from random import randint

zh_file = "./000001-010000.txt"
en_file = "./metadata.csv"

# zh_file = "./aa.txt"
# en_file = "./bb.txt"

txtfile = "./new.txt"
zh_sentences = []
en_sentences = []

def gen_mixed_sentence(zh_sentence, en_sentence, num_en_words: int=10):
    insert_pos = randint(0, len(zh_sentence) - 1)
    en_list = en_sentence.split(" ")
    en_start = randint(0, len(en_list) - 1)
    en_end = min(en_start + num_en_words, len(en_list))
    new_en_str = " ".join(en_list[en_start: en_end])
    new_sentence = zh_sentence[ :insert_pos] + new_en_str + zh_sentence[insert_pos: ]

    return new_sentence


with open(txtfile, "w") as fw, open(zh_file, "r") as f1, open(en_file, "r") as f2:
    for line1 in f1.readlines():
        if line1.startswith("0"):
            list1 = line1.strip().split("\t")
            new_id = list1[0].zfill(6)
            new_zh_sentence = list1[-1].replace('#1','').replace('#2','').replace('#3','').replace('#4','')
            fw.write("zh_" + new_id + "|" + new_zh_sentence + "\n")
            zh_sentences.append(new_zh_sentence)

    en_num = 20000
    for line2 in f2.readlines():
        en_num += 1
        new_id = str(en_num).zfill(6)
        sentence = line2.strip().split("|")[-1]
        fw.write("en_" + new_id + "|" + sentence + "\n")
        en_sentences.append(sentence)


    mix_num = 40000
    zh_en_count = min(len(zh_sentences), len(en_sentences))
    for i in range(zh_en_count):
        mix_sentence = gen_mixed_sentence(zh_sentences[i], en_sentences[i])
        mix_num += 1
        new_id = str(mix_num).zfill(6)
        fw.write("zh_en_" + new_id + "|" + mix_sentence + "\n")




