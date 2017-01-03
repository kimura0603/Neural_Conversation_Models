# python neural_conversation_model.py --data_path=ubuntu/train.tsv --dev_data=ubuntu/valid.tsv --vocab_path=tmp/vocab.txt
# python neural_conversation_model.py --data_path=ja_data/train.tsv --dev_data=ja_data/dev.tsv --vocab_path=ja_model/vocab.txt --train_dir=ja_model
# python neural_conversation_model.py --data_path=ja_data/train.tsv --dev_data=ja_data/dev.tsv --vocab_path=ja_model_attn/vocab.txt --train_dir=ja_model_attn --attention=True --tokenizer=mecab --en_vocab_size=200000 --max_to_keep=2
python neural_conversation_model.py --data_path=ja_data/train.tsv --dev_data=ja_data/dev.tsv --vocab_path=ja_model_attn_adam/vocab.txt --train_dir=ja_model_attn_adam --attention=True --tokenizer=mecab --en_vocab_size=200000 --max_to_keep=2 --optimizer=adam --learning_rate=0.001
