# Twitter chatbot based on Neural_Conversation_Models
=================================

Forked from https://github.com/pbhatia243/Neural_Conversation_Models, which implements seq2seq with beam serach and attention.

Added features:

- Choice of optimizer: SGD/AdaGrad/Adam
- Mecab as tokenizer
- Twitter chatbot

Prerequisites
-------------

- Python 2.7 or Python 3.3+
- [NLTK](http://www.nltk.org/)
- [TensorFlow](https://www.tensorflow.org/) r0.9 (Currently doesn't work on r0.12)
- tweepy (via pip)
- mecab, python-mecab, mecab-ipadic-utf8 (via apt-get)

Data
-----
Data accepted is in the tsv format where first component is the context and second is the reply

Usage
-----

To train a model with Ubuntu dataset:

    $ python neural_conversation_model.py --train_dir ubuntu/ --en_vocab_size 60000 --size 512 --data_path ubuntu/train.tsv --dev_data ubuntu/valid.tsv  --vocab_path ubuntu/60k_vocan.en --attention

To run a twitter bot:

    $ python twitter_bot.py

