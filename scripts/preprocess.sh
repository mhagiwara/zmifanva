# Create bilingual corpus

rm -rf corpus

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

# Preprocess corpus

cat corpus/train | cut -f 1 | python scripts/tokenize_jbo.py > corpus/train.tok.jb
cat corpus/train | cut -f 2 > corpus/train.tok.en

mosesdecoder/scripts/training/clean-corpus-n.perl corpus/train.tok jb en corpus/train.clean 1 80

# Create dev set

python scripts/convert_solr_xml_to_bitext.py docs/crashcourse4.xml | python scripts/mod.py --mod 2 -n 1 > corpus/dev

cat corpus/dev | cut -f 1 | python scripts/tokenize_jbo.py > corpus/dev.tok.jb
cat corpus/dev | cut -f 2 > corpus/dev.tok.en

# Create test set

python scripts/convert_solr_xml_to_bitext.py docs/crashcourse4.xml | python scripts/mod.py --mod 2 -n 0 > corpus/test

cat corpus/test | cut -f 1 | python scripts/tokenize_jbo.py > corpus/test.tok.jb
cat corpus/test | cut -f 2 > corpus/test.tok.en

# Moses results:
# Evaluate (jbo -> eng)

# (no tuning)
# BLEU = 21.80, 59.0/32.1/16.7/7.7 (BP=0.981, ratio=0.981, hyp_len=461, ref_len=470)
# (2015/11/05 ran MERT tuning)
# BLEU = 24.17, 60.6/32.3/17.4/10.4 (BP=0.989, ratio=0.989, hyp_len=465, ref_len=470)
# (2015/11/06 added crashcourse1, no tuning)
# BLEU = 21.26, 58.6/31.0/16.2/8.1 (BP=0.961, ratio=0.962, hyp_len=452, ref_len=470)

# Evaluate (eng -> jbo)

# (no tuning)
# BLEU = 27.69, 59.2/34.5/21.6/13.3 (BP=1.000, ratio=1.011, hyp_len=446, ref_len=441)
# (2015/11/05 ran MERT tuning
# BLEU = 28.06, 61.2/35.9/22.9/15.0 (BP=0.951, ratio=0.952, hyp_len=420, ref_len=441)
# (2015/11/06 added crashcourse1, no tuning)
# BLEU = 27.64, 60.7/35.6/21.7/13.2 (BP=0.986, ratio=0.986, hyp_len=435, ref_len=441)

