# -*- coding: utf-8 -*-

"""Most of the code comes from seq2seq tutorial. Binary for training conversation models and decoding from them.

Running this program without --decode will  tokenize it in a very basic way,
and then start training a model saving checkpoints to --train_dir.

Running with --decode starts an interactive loop so you can see how
the current checkpoint performs

See the following papers for more information on neural translation models.
 * http://arxiv.org/abs/1409.3215
 * http://arxiv.org/abs/1409.0473
 * http://arxiv.org/abs/1412.2007
"""


import math
import os
import random
import sys
import time
import re

import numpy as np
from six.moves import xrange  # pylint: disable=redefined-builtin
import tensorflow as tf

from  data_utils import *
from  seq2seq_model import *
import codecs

from mecab_tokenizer import mecab_tokenizer
from spm_tokenizer import spm_tokenizer

class NeuralChatBot:
    def __init__(self, vocab_path, train_dir, beam_size=10, beam_search=True, attention=False, tokenizer=mecab_tokenizer):
        self.beam_search = beam_search
        self.beam_size = beam_size
        self.tokenizer = tokenizer
        self.buckets = [(5, 10), (10, 15), (20, 25), (40, 50)]
        self.session = tf.Session()
        self.model = self.create_model(self.session, True, train_dir, beam_search=beam_search, beam_size=beam_size, attention=attention)
        self.model.batch_size = 1  # We decode one sentence at a time.

        # Load vocabularies.
        self.vocab, self.rev_vocab = initialize_vocabulary(vocab_path)

    def create_model(self, session, forward_only, train_dir,
                     beam_search = True, beam_size = 10, attention = True, size=512,
                     en_vocab_size=16000, num_layers=3, max_gradient_norm = 5.0, batch_size = 1,
                     learning_rate=0.001, learning_rate_decay_factor=0.99,
                     max_to_keep=2, optimizer='sgd'):
        """Create translation model and initialize or load parameters in session."""
        model = Seq2SeqModel(
            en_vocab_size, en_vocab_size, self.buckets,
            size, num_layers, max_gradient_norm, batch_size,
            learning_rate, learning_rate_decay_factor,
            forward_only=forward_only, beam_search=beam_search, beam_size=beam_size, attention=attention,
            max_to_keep=max_to_keep, optimizer=optimizer)
        ckpt = tf.train.get_checkpoint_state(train_dir)

        model.saver.restore(session, ckpt.model_checkpoint_path)
        return model

    def choose_reply(self, cands):
        scores = []
        for i, cand in enumerate(cands):
            scores.append(len(cands) - i + len(''.join(cand).decode('utf-8')) + len(cand))
        r = random.randint(1, sum(scores))
        acc_score = 0
        for i,cand in enumerate(cands):
            acc_score += scores[i]
            if r <= acc_score:
                return cand
        return cands[0]

    def reply(self, sentence, max_chars=80, list_all=False):
        cands = self.decode(sentence)
        cands_filtered = filter(lambda l: ('_UNK' not in l) and (':' not in ''.join(l)) and len(l) > 0 and sum([len(x.decode('utf-8')) for x in l]) <= max_chars, cands)
        if not cands_filtered:
            cands_filtered = cands
        if not cands_filtered:
            return ''
        out_ary = self.choose_reply(cands_filtered)
        out = ''
        for w in out_ary:
            if len(out + w) > max_chars:
                break
            out = out + w

        out = out.lstrip('▁').replace('▁', ' ')
        out = re.sub(u'[「」（）\(\)]', '', out.decode('utf-8')).encode('utf-8')
        if list_all:
            out = '/'.join([''.join(x) for x in cands_filtered]) + '->' + out
        print '/'.join([''.join(x) for x in cands_filtered]) + '->' + out
        return out

    def decode(self, sentence):
        # Get token-ids for the input sentence.
        token_ids = sentence_to_token_ids(tf.compat.as_bytes(sentence), self.vocab, tokenizer=self.tokenizer)
        if len(token_ids) >= self.buckets[-1][0]:
            token_ids = token_ids[:(self.buckets[-1][0] - 1)]
        # Which bucket does it belong to?
        bucket_id = min([b for b in xrange(len(self.buckets))
                         if self.buckets[b][0] > len(token_ids)])
        # Get a 1-element batch to feed the sentence to the model.
        encoder_inputs, decoder_inputs, target_weights = self.model.get_batch(
            {bucket_id: [(token_ids, [])]}, bucket_id)
        if self.beam_search:
            # Get output logits for the sentence.
            path, symbol, output_logits = self.model.step(self.session, encoder_inputs, decoder_inputs,
                                                          target_weights, bucket_id, True, self.beam_search )

            k = output_logits[0]
            paths = []
            for kk in range(self.beam_size):
                paths.append([])
            curr = range(self.beam_size)
            num_steps = len(path)
            for i in range(num_steps-1, -1, -1):
                for kk in range(self.beam_size):
                    paths[kk].append(symbol[i][curr[kk]])
                    curr[kk] = path[i][curr[kk]]
            recos = []
            for kk in range(self.beam_size):
                foutputs = [int(logit)  for logit in paths[kk][::-1]]

                # If there is an EOS symbol in outputs, cut them at that point.
                if EOS_ID in foutputs:
                    foutputs = foutputs[:foutputs.index(EOS_ID)]
                rec = [tf.compat.as_str(self.rev_vocab[output]) for output in foutputs]
                if rec not in recos:
                    recos.append(rec)
            return recos
        else:
            _, _, output_logits = model.step(self.session, encoder_inputs, decoder_inputs,
                                             target_weights, bucket_id, True, self.beam_search)
            # This is a greedy decoder - outputs are just argmaxes of output_logits.

            outputs = [int(np.argmax(logit, axis=1)) for logit in output_logits]
            # If there is an EOS symbol in outputs, cut them at that point.
            if EOS_ID in outputs:
                # print outputs
                outputs = outputs[:outputs.index(EOS_ID)]
            rec = [tf.compat.as_str(self.rev_vocab[output]) for output in outputs]
            return [rec]
            

if __name__ == "__main__":
    chatbot = NeuralChatBot('ja_model_spm/vocab.txt', 'ja_model_spm', tokenizer=spm_tokenizer, beam_size=100)
    sys.stdout.write('> ')
    while True:
        line = sys.stdin.readline().split('\t')[0]
        print line.rstrip() + '\t' + chatbot.reply(line, list_all=True)
    
