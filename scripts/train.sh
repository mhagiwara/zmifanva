# Create bilingual corpus

rm -rf corpus
rm -rf train

mkdir corpus

python scripts/convert_solr_xml_to_bitext.py docs/aspect.xml > corpus/bitext
python scripts/convert_solr_xml_to_bitext.py docs/cll.xml >> corpus/bitext
python scripts/convert_solr_xml_to_bitext.py docs/conlang.xml >> corpus/bitext
python scripts/convert_solr_xml_to_bitext.py docs/jbowiki.xml >> corpus/bitext
python scripts/convert_solr_xml_to_bitext.py docs/phrasebook.xml >> corpus/bitext
python scripts/convert_solr_xml_to_bitext.py docs/tatoeba.xml >> corpus/bitext
python scripts/convert_solr_xml_to_bitext.py docs/teris.xml >> corpus/bitext

# Preprocess corpus

cat corpus/bitext | cut -f 1 | python scripts/tokenize_jbo.py > corpus/bitext.tok.jb
cat corpus/bitext | cut -f 2 | mosesdecoder/scripts/tokenizer/tokenizer.perl -l en > corpus/bitext.tok.en

mosesdecoder/scripts/training/clean-corpus-n.perl corpus/bitext.tok jb en corpus/bitext.clean 1 80

# Build Lojban LM

mosesdecoder/bin/lmplz -o 3 < corpus/bitext.clean.jb > corpus/bitext.arpa.jb
mosesdecoder/bin/build_binary corpus/bitext.arpa.jb corpus/bitext.blm.jb

# Build English LM

mosesdecoder/bin/lmplz -o 3 < corpus/bitext.clean.en > corpus/bitext.arpa.en
mosesdecoder/bin/build_binary corpus/bitext.arpa.en corpus/bitext.blm.en

# Build jbo -> eng model

mosesdecoder/scripts/training/train-model.perl \
    -root-dir train -corpus corpus/bitext.clean \
    -f jb -e en -alignment grow-diag-final-and -reordering msd-bidirectional-fe \
    -lm 0:3:$PWD/corpus/bitext.blm.en:8 \
    -external-bin-dir mosesdecoder/tools

# Build eng -> jbo model

# mosesdecoder/scripts/training/train-model.perl \
#     -root-dir train -corpus corpus/bitext.clean \
#     -f en -e jb -alignment grow-diag-final-and -reordering msd-bidirectional-fe \
#     -lm 0:3:$PWD/corpus/bitext.blm.jb:8 \
#     -external-bin-dir mosesdecoder/tools


# Run moses in interative mode
# mosesdecoder/bin/moses -f train/model/moses.ini

# Evaluate (jbo -> eng)

python scripts/convert_solr_xml_to_bitext.py docs/introduction.xml > corpus/testset

cat corpus/testset | cut -f 1 | python scripts/tokenize_jbo.py > corpus/testset.tok.jb
cat corpus/testset | cut -f 2 | mosesdecoder/scripts/tokenizer/tokenizer.perl -l en > corpus/testset.tok.en

mosesdecoder/bin/moses -f train/model/moses.ini < corpus/testset.tok.jb > train/testset.translated.en
mosesdecoder/scripts/generic/multi-bleu.perl -lc corpus/testset.tok.en < train/testset.translated.en
# BLEU = 25.00, 61.2/37.0/21.5/9.8 (BP=0.950, ratio=0.951, hyp_len=98, ref_len=103)

# Evaluate (eng -> jbo)

# mosesdecoder/bin/moses -f train/model/moses.ini < corpus/testset.tok.en > train/testset.translated.jb
# mosesdecoder/scripts/generic/multi-bleu.perl -lc corpus/testset.tok.jb < train/testset.translated.jb
# BLEU = 23.28, 57.1/32.1/20.0/8.0 (BP=1.000, ratio=1.101, hyp_len=98, ref_len=89)
