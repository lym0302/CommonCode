# coding=utf-8
""" computer yuyin segementation accuracy """
"""
merge_vad = True: python3 test_acc.py
merge_vad = False: python3 test_acc.py --merge
"""


from base64 import b64encode
import os
import requests
import json


IP = "127.0.0.1"
PORT = "8654"
TEST_DIR = "./data"
LABEL_FILE = "./data/label.txt"



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
    if response.status_code == 200 and res_dict['success'] and res_dict['code'] == 0:
        return res_dict
    else:
        print("Response: " + response.text)
        print(cmd_name + ": Failed")

    return res_dict


def count(ref: list, pre: list):
    
    assert(len(ref) == len(pre))
    right_count = 0

    for i in range(len(ref)):
        if ref[i] == pre[i]:
            right_count += 1

    return right_count


def get_result(wavfile, merge_vad: bool=True):
    url = "/api/vprPreHandler/v1/clean"
    audio_data = readwav2base64(wavfile)
    body = {"audio_data": audio_data, "merge_vad": merge_vad}
    response = post_cmd(url, body, "speech_segmentation")
    vad_result = response["result"]["merged_vad"]

    return vad_result


def get_label(label_file):
    label_dict = {}

    with open(label_file, "r") as f:
        for line in f.readlines():
            utt = line.strip().split(" ")[0]
            label_str = (line.strip().split("[")[1]).replace("]", "")
            label = label_str.split(",")
            label = [int(i) for i in label]
            label_dict[utt] = label

    return label_dict
            
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="test yuyin vad")
    parser.add_argument("--merge", default=True, action="store_false", help="the bool value of merge_vad")
    args = parser.parse_args()
    print("The bool value of merge_vad: ", args.merge)
    
    right_count_sum = 0.0
    all_count = 0.0

    # get label
    label_dict = get_label(LABEL_FILE)
    
    # test
    for path, pathname, filenames in os.walk(TEST_DIR):
        for filename in filenames:
            if filename.endswith('.wav'):
                wavfile = os.path.join(path, filename)
                
                vad_result = get_result(wavfile, args.merge)

                ref_label = label_dict[filename]
                right_count = count(ref_label, vad_result)

                
                right_count_sum += right_count
                all_count += len(ref_label)

                print(filename, right_count, len(ref_label), right_count/len(ref_label))

    acc = right_count_sum / all_count
    print(right_count_sum, all_count, acc)

    print(f"Accuracy: {acc}")
