# Create bilingual corpus

python scripts/convert_solr_xml_to_bitext.py docs/aspect.xml > corpus/bitext
python scripts/convert_solr_xml_to_bitext.py docs/cll.xml >> corpus/bitext
python scripts/convert_solr_xml_to_bitext.py docs/conlang.xml >> corpus/bitext
python scripts/convert_solr_xml_to_bitext.py docs/jbowiki.xml >> corpus/bitext
python scripts/convert_solr_xml_to_bitext.py docs/phrasebook.xml >> corpus/bitext
python scripts/convert_solr_xml_to_bitext.py docs/tatoeba.xml >> corpus/bitext
python scripts/convert_solr_xml_to_bitext.py docs/teris.xml >> corpus/bitext

# Train jbo -> eng model

cat corpus/bitext | cut -f 1 | python scripts/tokenize_jbo.py > corpus/bitext.tok.jb
cat corpus/bitext | cut -f 2 | mosesdecoder/scripts/tokenizer/tokenizer.perl -l en > corpus/bitext.tok.en

mosesdecoder/scripts/training/clean-corpus-n.perl corpus/bitext.tok jb en corpus/bitext.clean 1 80

mosesdecoder/bin/lmplz -o 3 < corpus/bitext.clean.en > corpus/bitext.arpa.en
mosesdecoder/bin/build_binary corpus/bitext.arpa.en corpus/bitext.blm.en

mosesdecoder/scripts/training/train-model.perl \
    -root-dir train -corpus corpus/bitext.clean \
    -f jb -e en -alignment grow-diag-final-and -reordering msd-bidirectional-fe \
    -lm 0:3:$PWD/corpus/bitext.blm.en:8 \
    -external-bin-dir mosesdecoder/tools

# mosesdecoder/bin/moses -f train/model/moses.ini

# Evaluate

cat corpus/testset | cut -f 1 | python scripts/tokenize_jbo.py > corpus/testset.tok.jb
cat corpus/testset | cut -f 2 | mosesdecoder/scripts/tokenizer/tokenizer.perl -l en > corpus/testset.tok.en

mosesdecoder/bin/moses -f train/model/moses.ini < corpus/testset.tok.jb > train/testset.translated.en

mosesdecoder/scripts/generic/multi-bleu.perl -lc corpus/testset.tok.en < train/testset.translated.en

# BLEU = 20.44, 59.2/33.3/18.5/5.9 (BP=0.950, ratio=0.951, hyp_len=98, ref_len=103)
