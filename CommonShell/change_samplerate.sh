#使用sox 将 wavs 目录下的所有 wav音频转成16k，并保存到 wavs_16k 目录下
find wavs/ -name "*.wav" |awk -F "/" '{print "sox", $0, "-r 16k -b 16 wavs_16k/"$NF}' | sh
