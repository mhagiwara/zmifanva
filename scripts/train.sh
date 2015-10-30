python scripts/convert_solr_xml_to_bitext.py docs/aspect.xml > corpus/bitext
python scripts/convert_solr_xml_to_bitext.py docs/cll.xml >> corpus/bitext
python scripts/convert_solr_xml_to_bitext.py docs/conlang.xml >> corpus/bitext
python scripts/convert_solr_xml_to_bitext.py docs/jbowiki.xml >> corpus/bitext
python scripts/convert_solr_xml_to_bitext.py docs/phrasebook.xml >> corpus/bitext
python scripts/convert_solr_xml_to_bitext.py docs/tatoeba.xml >> corpus/bitext
python scripts/convert_solr_xml_to_bitext.py docs/teris.xml >> corpus/bitext

cat corpus/bitext | cut -f 1 | python scripts/tokenize_jbo.py > corpus/bitext.tok.jb
cat corpus/bitext | cut -f 2 |  mosesdecoder/scripts/tokenizer/tokenizer.perl -l en > corpus/bitext.tok.en

mosesdecoder/scripts/training/clean-corpus-n.perl corpus/bitext.tok jb en corpus/bitext.clean 1 80

