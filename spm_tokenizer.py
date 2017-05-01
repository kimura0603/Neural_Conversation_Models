# -*- coding: utf-8 -*-
import subprocess
import shlex

model = 'ja_model_spm/ja_spm.model'
cmd = 'spm_encode --model %s' % model
spm = subprocess.Popen(shlex.split(cmd), stdin=subprocess.PIPE, stdout=subprocess.PIPE)

def spm_tokenizer(sentence):
    spm.stdin.write(sentence + '\n')
    res = spm.stdout.readline()

    return res.rstrip('\n').split()


if __name__ == '__main__':
    while True:
        print ' '.join(spm_tokenizer(raw_input()))
        
