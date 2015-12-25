* TO DO

- [DONE] Normalize (delete) '.i' beginning of sentences.
- [DONE] Normalize (delete) preceding / following periods of words.
- Add Lojban<->English dictionary of https://mw.lojban.org/papri/The_Crash_Course_(a_draft)


* Results

- Moses Baseline

(eng -> jbo)
BLEU = 27.64, 60.7/35.6/21.7/13.2 (BP=0.986, ratio=0.986, hyp_len=435, ref_len=441)

Errors:
- It &apos;ll be sunny , I hope . lo solri sei mi pacna   ba sunny kei mi pacna
    - OOV 'sunny'
- Do you feel pain ?      xu do cortu     xu do cinmo lo ka pain ma
    - OOV 'cortu'
- My knee hurts . mi cortu lo cidni       lo mi knee se cortu
    - OOV 'knee' <-> 'cidni'
- 

(jbo -> eng)
BLEU = 21.26, 58.6/31.0/16.2/8.1 (BP=0.961, ratio=0.962, hyp_len=452, ref_len=470)

Errors:
- [SOLVED] do mo?  How are you ?   You mo?
    - needs Lojban normalization/tokenization (delete '?')
- i ua xutla      Oh , it is smooth .     Oh xutla .'
- i le plise cu se sefta lo xutla The apple has a smooth surface .        , the apple is sefta xutla .
    - OOV 'xutla'
- mi tirna lo cladu       I hear something loud . I hear cladu .
    - OOV 'cladu'
- lo flora cu panci       It smells of flowers .  of is smells .
- mi sumne lo panci be lo za'u flora      I smell the odor of flowers .   I smell the smells of of .
    - OOV 'flora'?
    - 'flora' is in the training set, but probably word alignment
- i mi sruma lo nu mi bilma fi la zukam   I assume that I have a cold .   , I assume ill with Tom zukam to me .
    - OOV 'zukam'
- mi co'a speni la .suzan.        I married Susan .       I got married .suzan. Tom .
    - OOV 'suzan'



- seq2seq Model

--en_vocab_size 20000 --fr_vocab_size 20000 --num_layers 1 --size 512

1400    BLEU = 6.10, 32.5/10.9/2.8/1.4 (BP=1.000, ratio=1.109, hyp_len=489, ref_len=441)
2000    BLEU = 9.30, 42.7/17.6/7.4/4.0 (BP=0.763, ratio=0.787, hyp_len=347, ref_len=441)
2200    BLEU = 7.03, 40.1/14.3/5.5/1.9 (BP=0.804, ratio=0.821, hyp_len=362, ref_len=441)
2400    BLEU = 8.67, 45.6/16.2/5.8/3.0 (BP=0.815, ratio=0.830, hyp_len=366, ref_len=441)
2600    BLEU = 9.03, 45.7/16.1/6.4/2.9 (BP=0.836, ratio=0.848, hyp_len=374, ref_len=441)
2800    BLEU = 9.47, 42.7/15.2/5.1/2.5 (BP=0.993, ratio=0.993, hyp_len=438, ref_len=441)
3000    BLEU = 12.14, 43.2/18.8/9.0/3.6 (BP=0.954, ratio=0.955, hyp_len=421, ref_len=441)
3200    BLEU = 11.57, 42.3/16.1/7.7/4.3 (BP=0.942, ratio=0.943, hyp_len=416, ref_len=441)
3800    BLEU = 9.80, 42.1/15.1/5.9/3.2 (BP=0.934, ratio=0.937, hyp_len=413, ref_len=441)
4000    BLEU = 10.60, 41.5/14.4/6.9/4.5 (BP=0.908, ratio=0.912, hyp_len=402, ref_len=441)
4200    BLEU = 10.36, 43.3/16.0/5.9/3.7 (BP=0.934, ratio=0.937, hyp_len=413, ref_len=441)
4400    BLEU = 12.40, 42.1/17.9/8.4/3.8 (BP=1.000, ratio=1.007, hyp_len=444, ref_len=441)
4600    BLEU = 13.99, 44.8/18.5/9.9/5.4 (BP=0.965, ratio=0.966, hyp_len=426, ref_len=441)
4800    BLEU = 12.94, 43.7/18.4/9.8/5.6 (BP=0.893, ratio=0.898, hyp_len=396, ref_len=441)
5000    BLEU = 13.12, 41.7/19.4/9.3/5.3 (BP=0.927, ratio=0.930, hyp_len=410, ref_len=441)
5200    BLEU = 12.35, 45.7/19.6/10.4/6.1 (BP=0.801, ratio=0.819, hyp_len=361, ref_len=441)
5400    BLEU = 11.52, 44.3/16.2/8.2/5.4 (BP=0.862, ratio=0.871, hyp_len=384, ref_len=441)
5600    BLEU = 15.06, 43.3/20.4/11.0/5.7 (BP=0.979, ratio=0.980, hyp_len=432, ref_len=441)
5800    BLEU = 12.80, 44.2/18.1/8.7/5.4 (BP=0.920, ratio=0.923, hyp_len=407, ref_len=441)
6000    BLEU = 11.28, 42.0/16.3/7.4/4.2 (BP=0.932, ratio=0.934, hyp_len=412, ref_len=441)
6200    BLEU = 15.21, 46.5/20.2/11.7/7.7 (BP=0.893, ratio=0.898, hyp_len=396, ref_len=441)
7000    BLEU = 16.24, 48.8/22.2/12.5/7.4 (BP=0.912, ratio=0.916, hyp_len=404, ref_len=441)
7200    BLEU = 12.39, 42.8/17.3/8.1/5.2 (BP=0.930, ratio=0.932, hyp_len=411, ref_len=441)
7400    BLEU = 11.16, 43.7/17.9/8.1/3.3 (BP=0.927, ratio=0.930, hyp_len=410, ref_len=441)
7600    BLEU = 10.66, 43.0/17.0/8.5/3.7 (BP=0.867, ratio=0.875, hyp_len=386, ref_len=441)

--batch_size 32 (--learning_rate default)

2400    BLEU = 8.10, 33.5/13.2/5.8/2.5 (BP=0.903, ratio=0.907, hyp_len=400, ref_len=441)
3400    BLEU = 5.55, 38.1/11.7/3.1/1.0 (BP=0.900, ratio=0.905, hyp_len=399, ref_len=441)
8200    BLEU = 6.99, 34.9/12.1/5.0/2.1 (BP=0.854, ratio=0.864, hyp_len=381, ref_len=441)

--batch_size 32 --learning_rate 0.25

4200    BLEU = 8.69, 44.3/16.3/5.2/2.6 (BP=0.872, ratio=0.880, hyp_len=388, ref_len=441)
5200    BLEU = 8.82, 41.3/12.8/4.8/2.6 (BP=0.982, ratio=0.982, hyp_len=433, ref_len=441)
5600    BLEU = 12.35, 43.2/16.0/7.6/5.5 (BP=0.949, ratio=0.950, hyp_len=419, ref_len=441)
6200    BLEU = 12.97, 45.5/19.3/9.2/5.8 (BP=0.880, ratio=0.887, hyp_len=391, ref_len=441)
7400    BLEU = 10.01, 45.4/17.3/5.8/2.8 (BP=0.942, ratio=0.943, hyp_len=416, ref_len=441)
7600    BLEU = 9.57, 44.1/16.5/5.9/3.1 (BP=0.895, ratio=0.900, hyp_len=397, ref_len=441)
8400    BLEU = 11.83, 47.4/21.5/8.0/3.4 (BP=0.915, ratio=0.918, hyp_len=405, ref_len=441)
9000    BLEU = 11.11, 48.1/20.8/8.5/3.1 (BP=0.870, ratio=0.878, hyp_len=387, ref_len=441)
9800    BLEU = 10.63, 45.3/17.4/6.4/3.5 (BP=0.922, ratio=0.925, hyp_len=408, ref_len=441)
10600   BLEU = 9.77, 47.6/16.4/5.9/3.0 (BP=0.900, ratio=0.905, hyp_len=399, ref_len=441)
11400   BLEU = 9.64, 43.3/15.2/5.9/2.8 (BP=0.942, ratio=0.943, hyp_len=416, ref_len=441)

No Adagrad (SGD) --en_vocab_size 20000 --fr_vocab_size 20000 --num_layers 1 --size 512

2200    BLEU = 8.11, 49.4/17.9/5.3/2.7 (BP=0.765, ratio=0.789, hyp_len=348, ref_len=441)
