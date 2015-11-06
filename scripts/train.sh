# Create bilingual corpus

rm -rf corpus
rm -rf train
rm -rf mert-work

mkdir corpus

python scripts/convert_solr_xml_to_bitext.py docs/aspect.xml > corpus/train
python scripts/convert_solr_xml_to_bitext.py docs/cll.xml >> corpus/train
python scripts/convert_solr_xml_to_bitext.py docs/conlang.xml >> corpus/train
python scripts/convert_solr_xml_to_bitext.py docs/jbowiki.xml >> corpus/train
python scripts/convert_solr_xml_to_bitext.py docs/phrasebook.xml >> corpus/train
python scripts/convert_solr_xml_to_bitext.py docs/tatoeba.xml >> corpus/train
python scripts/convert_solr_xml_to_bitext.py docs/teris.xml >> corpus/train
python scripts/convert_solr_xml_to_bitext.py docs/introduction.xml >> corpus/train

# Preprocess corpus

cat corpus/train | cut -f 1 | python scripts/tokenize_jbo.py > corpus/train.tok.jb
cat corpus/train | cut -f 2 | mosesdecoder/scripts/tokenizer/tokenizer.perl -l en > corpus/train.tok.en

mosesdecoder/scripts/training/clean-corpus-n.perl corpus/train.tok jb en corpus/train.clean 1 80

# Create dev set

python scripts/convert_solr_xml_to_bitext.py docs/crashcourse4.xml | python scripts/mod.py --mod 2 -n 1 > corpus/dev

cat corpus/dev | cut -f 1 | python scripts/tokenize_jbo.py > corpus/dev.tok.jb
cat corpus/dev | cut -f 2 | mosesdecoder/scripts/tokenizer/tokenizer.perl -l en > corpus/dev.tok.en

# Build Lojban LM

mosesdecoder/bin/lmplz -o 3 < corpus/train.clean.jb > corpus/train.arpa.jb
mosesdecoder/bin/build_binary corpus/train.arpa.jb corpus/train.blm.jb

# Build English LM

mosesdecoder/bin/lmplz -o 3 < corpus/train.clean.en > corpus/train.arpa.en
mosesdecoder/bin/build_binary corpus/train.arpa.en corpus/train.blm.en

# Build jbo -> eng model

# mosesdecoder/scripts/training/train-model.perl \
#     -root-dir train -corpus corpus/train.clean \
#     -f jb -e en -alignment grow-diag-final-and -reordering msd-bidirectional-fe \
#     -lm 0:3:$PWD/corpus/train.blm.en:8 \
#     -external-bin-dir mosesdecoder/tools

# Tuning

# mosesdecoder/scripts/training/mert-moses.pl \
#     corpus/dev.tok.jb corpus/dev.tok.en \
#     mosesdecoder/bin/moses train/model/moses.ini --mertdir $PWD/mosesdecoder/bin/ \
#     --decoder-flags="-threads 4"

# Build eng -> jbo model

mosesdecoder/scripts/training/train-model.perl \
    -root-dir train -corpus corpus/train.clean \
    -f en -e jb -alignment grow-diag-final-and -reordering msd-bidirectional-fe \
    -lm 0:3:$PWD/corpus/train.blm.jb:8 \
    -external-bin-dir mosesdecoder/tools


mosesdecoder/scripts/training/mert-moses.pl \
    corpus/dev.tok.en corpus/dev.tok.jb \
    mosesdecoder/bin/moses train/model/moses.ini --mertdir $PWD/mosesdecoder/bin/ \
    --decoder-flags="-threads 4"

# Run moses in interative mode
# mosesdecoder/bin/moses -f train/model/moses.ini

# Evaluate (jbo -> eng)

python scripts/convert_solr_xml_to_bitext.py docs/crashcourse4.xml | python scripts/mod.py --mod 2 -n 0 > corpus/test

cat corpus/test | cut -f 1 | python scripts/tokenize_jbo.py > corpus/test.tok.jb
cat corpus/test | cut -f 2 | mosesdecoder/scripts/tokenizer/tokenizer.perl -l en > corpus/test.tok.en

# mosesdecoder/bin/moses -f mert-work/moses.ini < corpus/test.tok.jb > train/test.translated.en
# mosesdecoder/scripts/generic/multi-bleu.perl -lc corpus/test.tok.en < train/test.translated.en
# BLEU = 21.80, 59.0/32.1/16.7/7.7 (BP=0.981, ratio=0.981, hyp_len=461, ref_len=470)
# BLEU = 24.17, 60.6/32.3/17.4/10.4 (BP=0.989, ratio=0.989, hyp_len=465, ref_len=470) (after tuning)

# Evaluate (eng -> jbo)

mosesdecoder/bin/moses -f train/model/moses.ini < corpus/test.tok.en > train/test.translated.jb
mosesdecoder/scripts/generic/multi-bleu.perl -lc corpus/test.tok.jb < train/test.translated.jb
# BLEU = 27.69, 59.2/34.5/21.6/13.3 (BP=1.000, ratio=1.011, hyp_len=446, ref_len=441)
# BLEU = 27.69, 59.2/34.5/21.6/13.3 (BP=1.000, ratio=1.011, hyp_len=446, ref_len=441) (after tuning)