# Create bilingual corpus

rm -rf corpus
rm -rf train.jb-en
rm -rf train.en-jb
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
python scripts/convert_solr_xml_to_bitext.py docs/crashcourse1.xml >> corpus/train
python scripts/convert_solr_xml_to_bitext.py docs/crashcourse.jbo_eng_dict.xml >> corpus/train
python scripts/convert_solr_xml_to_bitext.py docs/zmifanva_reports.xml >> corpus/train

# Preprocess corpus

cat corpus/train | cut -f 1 | python scripts/tokenize_jbo.py > corpus/train.tok.jb
cat corpus/train | cut -f 2 | mosesdecoder/scripts/tokenizer/tokenizer.perl -l en > corpus/train.tok.en

mosesdecoder/scripts/training/clean-corpus-n.perl corpus/train.tok jb en corpus/train.clean 1 80

# Create dev set

python scripts/convert_solr_xml_to_bitext.py docs/crashcourse4.xml | python scripts/mod.py --mod 2 -n 1 > corpus/dev

cat corpus/dev | cut -f 1 | python scripts/tokenize_jbo.py > corpus/dev.tok.jb
cat corpus/dev | cut -f 2 | mosesdecoder/scripts/tokenizer/tokenizer.perl -l en > corpus/dev.tok.en

# Build Lojban LM

mosesdecoder/bin/lmplz -o 3 < corpus/train.clean.jb > lm/train.arpa.jb
mosesdecoder/bin/build_binary lm/train.arpa.jb lm/train.blm.jb

# Build English LM

mosesdecoder/bin/lmplz -o 3 < corpus/train.clean.en > lm/train.arpa.en
mosesdecoder/bin/build_binary lm/train.arpa.en lm/train.blm.en

# Build jbo -> eng model

mosesdecoder/scripts/training/train-model.perl \
    -root-dir train.jb-en -corpus corpus/train.clean \
    -f jb -e en -alignment grow-diag-final-and -reordering msd-bidirectional-fe \
    -lm 0:3:$PWD/lm/train.blm.en:8 \
    -external-bin-dir mosesdecoder/tools

# Tuning

# mosesdecoder/scripts/training/mert-moses.pl \
#     corpus/dev.tok.jb corpus/dev.tok.en \
#     mosesdecoder/bin/moses train.jb-en/model/moses.ini --mertdir $PWD/mosesdecoder/bin/ \
#     --decoder-flags="-threads 4"

# Build eng -> jbo model

mosesdecoder/scripts/training/train-model.perl \
    -root-dir train.en-jb -corpus corpus/train.clean \
    -f en -e jb -alignment grow-diag-final-and -reordering msd-bidirectional-fe \
    -lm 0:3:$PWD/lm/train.blm.jb:8 \
    -external-bin-dir mosesdecoder/tools

#
# mosesdecoder/scripts/training/mert-moses.pl \
#     corpus/dev.tok.en corpus/dev.tok.jb \
#     mosesdecoder/bin/moses train/model/moses.ini --mertdir $PWD/mosesdecoder/bin/ \
#     --decoder-flags="-threads 4"

# Run moses in interative mode
# mosesdecoder/bin/moses -f train/model/moses.ini

# Evaluate (jbo -> eng)

python scripts/convert_solr_xml_to_bitext.py docs/crashcourse4.xml | python scripts/mod.py --mod 2 -n 0 > corpus/test

cat corpus/test | cut -f 1 | python scripts/tokenize_jbo.py > corpus/test.tok.jb
cat corpus/test | cut -f 2 | mosesdecoder/scripts/tokenizer/tokenizer.perl -l en > corpus/test.tok.en

mosesdecoder/bin/moses -f train.jb-en/model/moses.ini < corpus/test.tok.jb > train.jb-en/test.translated.en
mosesdecoder/scripts/generic/multi-bleu.perl -lc corpus/test.tok.en < train.jb-en/test.translated.en
# Generate regression report.
paste corpus/test.tok.jb train.jb-en/test.translated.en corpus/test.tok.en > train.jb-en/results

# Results
# (no tuning)
# BLEU = 21.80, 59.0/32.1/16.7/7.7 (BP=0.981, ratio=0.981, hyp_len=461, ref_len=470)
# (2015/11/05 ran MERT tuning)
# BLEU = 24.17, 60.6/32.3/17.4/10.4 (BP=0.989, ratio=0.989, hyp_len=465, ref_len=470)
# (2015/11/06 added crashcourse1, no tuning)
# BLEU = 21.26, 58.6/31.0/16.2/8.1 (BP=0.961, ratio=0.962, hyp_len=452, ref_len=470)
# (2015/12/23 added normalization)
# BLEU = 23.26, 62.5/34.2/18.2/9.9 (BP=0.934, ratio=0.936, hyp_len=440, ref_len=470)
# (2015/12/24 added crashcourse jbo<->eng dictionary)
# BLEU = 31.65, 66.0/40.5/25.2/17.7 (BP=0.957, ratio=0.957, hyp_len=450, ref_len=470)
# (2016/01/23 added report sentences.)
# BLEU = 29.38, 65.7/38.8/22.6/16.0 (BP=0.948, ratio=0.949, hyp_len=446, ref_len=470)

# Evaluate (eng -> jbo)

mosesdecoder/bin/moses -f train.en-jb/model/moses.ini < corpus/test.tok.en > train.en-jb/test.translated.jb
mosesdecoder/scripts/generic/multi-bleu.perl -lc corpus/test.tok.jb < train.en-jb/test.translated.jb
# Generate regression report.
paste corpus/test.tok.en train.en-jb/test.translated.jb corpus/test.tok.jb > train.en-jb/results

# Results
# (no tuning)
# BLEU = 27.69, 59.2/34.5/21.6/13.3 (BP=1.000, ratio=1.011, hyp_len=446, ref_len=441)
# (2015/11/05 ran MERT tuning
# BLEU = 28.06, 61.2/35.9/22.9/15.0 (BP=0.951, ratio=0.952, hyp_len=420, ref_len=441)
# (2015/11/06 added crashcourse1, no tuning)
# BLEU = 27.64, 60.7/35.6/21.7/13.2 (BP=0.986, ratio=0.986, hyp_len=435, ref_len=441)
# (2015/12/23 added normalization)
# BLEU = 28.80, 61.4/35.7/21.6/14.5 (BP=1.000, ratio=1.044, hyp_len=428, ref_len=410)
# (2015/12/24 added crashcourse jbo<->eng dictionary)
# BLEU = 39.68, 69.0/44.2/32.2/25.2 (BP=1.000, ratio=1.000, hyp_len=410, ref_len=410)
# (2016/01/23 added report sentences.)
# BLEU = 38.50, 69.0/43.1/30.7/24.0 (BP=1.000, ratio=1.015, hyp_len=416, ref_len=410)