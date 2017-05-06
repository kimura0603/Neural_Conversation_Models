rm -rf ja_model_spm
mkdir ja_model_spm
### train spm
spm_train --input=ja_data/train.tsv --model_prefix=ja_model_spm/ja_spm --vocab_size=15000

### test spm
spm_encode ja_data/dev.tsv --model=ja_model_spm/ja_spm.model --output ja_data/dev.tsv.spm

### pretraining with identity sentence pairs
### python neural_conversation_model.py --data_path=ja_data/pretrain_corpus.tsv --dev_data=ja_data/dev.tsv --vocab_path=ja_model_spm/vocab.txt --train_dir=ja_model_spm --attention=True --tokenizer=spm --size 128 --en_vocab_size=16000 --max_to_keep=2 --optimizer=adam --learning_rate=0.001 --nsteps=2000

### train with spm
python neural_conversation_model.py --data_path=ja_data/train.tsv --dev_data=ja_data/dev.tsv --vocab_path=ja_model_spm/vocab.txt --train_dir=ja_model_spm --attention=True --tokenizer=spm --size 512 --en_vocab_size=16000 --max_to_keep=2 --optimizer=adam --learning_rate=0.001
