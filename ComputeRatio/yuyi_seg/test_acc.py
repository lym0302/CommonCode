# coding=utf-8
""" computer yuyi segementation accuracy """

from base64 import b64encode
import requests
import json
import os 


IP = "127.0.0.1"
PORT = "8490"
TEST_DIR = "./data"
LABEL_FILE = "data/label.txt"


def readwav2base64(wav_file):
    """
    read wave file and covert to base64 string
    """
    with open(wav_file, 'rb') as f:
        base64_bytes = b64encode(f.read())
        base64_string = base64_bytes.decode('utf-8')
        
    return base64_string


def post_cmd(url, body, cmd_name):
    """
    Post cmd
    """
    url = 'http://' + IP + ':' + PORT + url
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(body), headers=headers)
    res_dict = json.loads(response.text)

    return res_dict


def compute_overlap(ref_start, ref_end, pre_start, pre_end):
    start = max(ref_start, pre_start)
    end = min(ref_end, pre_end)
    overlap = end - start

    return overlap


def get_result(wavfile):
    url = "/lym/search"
    audio_data = readwav2base64(wavfile)
    body = {"audio": audio_data, "audio_format": "wav", "sample_rate": 16000, "lang": "zh_cn"}
    response = post_cmd(url, body, "tw-segmentation")
    seg_result = response["result"]["acs"]

    return seg_result


def get_label(label_file):
    label_dict = {}

    with open(label_file, "r") as f:
        for line in f.readlines():
            line_dict = eval(line.strip())
            for key in line_dict.keys():
                label_dict[key] = line_dict[key]

    return label_dict

def get_overlap(ref: list, pre: list, check_word: bool=False):

    overlap_time = 0.0
    all_time = 0.0

    if len(ref) == 0:
        overlap_time = 0.0
        all_time = 0.0
        
    else:
        ref_words = [ref[i]['w'] for i in range(len(ref))]
        ref_bgs = [ref[i]['bg'] for i in range(len(ref))]
        ref_eds = [ref[i]['ed'] for i in range(len(ref))]
        ref_bgs, ref_eds, ref_words = (list(t) for t in zip(*sorted(zip(ref_bgs, ref_eds, ref_words))))
        assert(len(ref_words) == len(ref_bgs) and len(ref_bgs) == len(ref_eds))
        all_time = sum([(ref_eds[j] - ref_bgs[j]) for j in range(len(ref_bgs))])

        if len(pre) == 0:
            overlap_time = 0.0
        
        else:
            pre_words = [pre[i]['w'] for i in range(len(pre))]
            pre_bgs = [pre[i]['bg'] for i in range(len(pre))]
            pre_eds = [pre[i]['ed'] for i in range(len(pre))]
            pre_bgs, pre_eds, pre_words = (list(t) for t in zip(*sorted(zip(pre_bgs, pre_eds, pre_words))))

            assert(len(pre_words) == len(pre_bgs) and len(pre_bgs) == len(pre_eds))

            st_id = 0
            for i in range(len(pre_words)):
                for j in range(st_id, len(ref_words)):
                    if check_word:
                        from pypinyin import Style, pinyin
                        if pinyin(pre_words[i]) == pinyin(ref_words[j]):
                            flag = 1
                        else:
                            flag = 0
                    else:
                        flag = 1 

                    if pre_bgs[i] < ref_eds[j] and pre_eds[i] > ref_bgs[j] and flag:
                        overlap = min(pre_eds[i], ref_eds[j]) - max(pre_bgs[i], ref_bgs[j])
                        overlap_time += overlap
                        st_id = j + 1
                        break
                    elif pre_eds[i] < ref_bgs[j]:
                        st_id = j
                        break
                    else:
                        continue

    return overlap_time, all_time



            
if __name__ == "__main__":
    overlap_time_sum = 0.0
    all_time_sum = 0.0

    # get label
    label_dict = get_label(LABEL_FILE)
    
    # test
    for path, pathname, filenames in os.walk(TEST_DIR):
        for filename in filenames:
            if filename.endswith('.wav'):
                wavfile = os.path.join(path, filename)
                seg_result = get_result(wavfile)

                ref_label = label_dict[filename]
                overlap_time, all_time = get_overlap(ref_label, seg_result, True)

                acc = 1 if all_time == 0  else overlap_time / all_time
                print(f"file: {filename}; overlap time: {overlap_time} s; all time: {all_time} s; accuracy: {acc * 100}%")
                overlap_time_sum += overlap_time
                all_time_sum += all_time


    acc = 1 if all_time_sum == 0  else overlap_time_sum / all_time_sum

    print(f"overlap time: {overlap_time_sum} s; all time: {all_time_sum} s; accuracy: {acc * 100}%")
