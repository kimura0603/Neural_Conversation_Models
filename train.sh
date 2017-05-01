# rm -rf ja_model_spm/*
### train spm
# spm_train --input=ja_data/train.tsv --model_prefix=ja_model_spm/ja_spm --vocab_size=16000
# test spm
# python spm_tokenizer.py < ja_data/train.tsv > ja_data/train.tsv.spm

### pretraining with identity sentence pairs
# python neural_conversation_model.py --data_path=ja_data/pretrain_corpus.tsv --dev_data=ja_data/dev.tsv --vocab_path=ja_model_spm/vocab.txt --train_dir=ja_model_spm --attention=True --tokenizer=spm --size 128 --en_vocab_size=16000 --max_to_keep=2 --optimizer=adam --learning_rate=0.001

### train with spm
python neural_conversation_model.py --data_path=ja_data/train.tsv --dev_data=ja_data/dev.tsv --vocab_path=ja_model_spm/vocab.txt --train_dir=ja_model_spm --attention=True --tokenizer=spm --size 128 --en_vocab_size=16000 --max_to_keep=2 --optimizer=adam --learning_rate=0.001
