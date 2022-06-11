# coding:utf-8
import os
import soundfile as sf

indir = 'aa'
outdir = 'aa_out'

max_length = 5*60  # 5分钟

for path, pathname, filenames in os.walk(indir):
    for filename in filenames:
        if filename.endswith('.wav'):
            index = 0
            data, sr = sf.read(os.path.join(path, filename))
            for k in range(0, len(data), int(max_length*sr)):
                tmp_data = data[k : k+int(max_length*sr)]
                fname = filename.replace('.wav','') + "_" + str(index) + ".wav"
                out_fname = os.path.join(outdir, fname)
                sf.write(out_fname, tmp_data, sr, 'PCM_16')
                index += 1
