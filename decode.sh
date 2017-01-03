# python neural_conversation_model.py --decode=True --train_dir=./tmp --vocab_path=./tmp/vocab.txt
# python neural_conversation_model.py --decode=True --train_dir=./ja_model_attn --vocab_path=./ja_model_attn/vocab.txt --beam_search=True --attention=True --tokenizer=mecab --en_vocab_size=200000
cut -f 1 ja_data/test.tsv | python neural_conversation_model.py --decode=True --train_dir=./ja_model_attn_adam --vocab_path=./ja_model_attn_adam/vocab.txt --beam_search=True --attention=True --tokenizer=mecab --en_vocab_size=200000 --formatted_output | tee out.tsv

