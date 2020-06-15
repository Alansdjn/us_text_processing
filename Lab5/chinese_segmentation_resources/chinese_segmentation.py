"""
USE: python <PROGNAME> (options)
OPTIONS:
    -h : print this help message and exit
    -d FILE : use dictionary file FILE
    -i FILE : process text from input file FILE
    -o FILE : write results to output file FILE
"""
#command: 
# python3 chinese_segmentation.py -d chinesetrad_wordlist.utf8 -i chinesetext.utf8 -o result.utf8
# python3 eval_chinese_segmentation.py chinesetext_goldstandard.utf8 result.utf8
################################################################

import sys, getopt

################################################################

MAXWORDLEN = 5

################################################################
# Command line options handling, and help

opts, args = getopt.getopt(sys.argv[1:], 'hd:i:o:')
opts = dict(opts)

def printHelp():
    progname = sys.argv[0]
    progname = progname.split('/')[-1] # strip out extended path
    help = __doc__.replace('<PROGNAME>', progname, 1)
    print('-' * 60, help, '-' * 60, file=sys.stderr)
    sys.exit()
    
if '-h' in opts:
    printHelp()

if len(args) > 0:
    print("\n** ERROR: no arg files - only options! **", file=sys.stderr)
    printHelp()

if '-d' not in opts:
    print("\n** ERROR: must specify dictionary (opt: -d)! **", file=sys.stderr)
    printHelp()

if '-i' not in opts:
    print("\n** ERROR: must specify input text file (opt: -i)! **", file=sys.stderr)
    printHelp()

if '-o' not in opts:
    print("\n** ERROR: must specify output text file (opt: -o)! **", file=sys.stderr)
    printHelp()

################################################################

def get_chinese_word_set(dict_filename):
    word_set = set()
    with open(dict_filename, 'r', encoding='UTF-8') as dict_fs:
        for word in dict_fs:
            word_set.add(word.rstrip())
    return word_set

def maximum_match(sentence, word_set, max_word_len):
    result = []
    sentence_len = len(sentence)
    i = 0
    while i < sentence_len:
        for j in range(min(i + max_word_len, sentence_len), i, -1):
            word = sentence[i:j]
            if (word in word_set) or (i + 1 == j):
                result.append(word)
                i = j
                break
            
    # print('sentence:%s\nresult:' % sentence, result)            
    return result

def chinese_word_segmentation(filename, word_set, max_word_len):
    result = []
    with open(filename, 'r', encoding='UTF-8') as data_fs:
        for sentence in data_fs:
            result.append(maximum_match(sentence.rstrip(), word_set, max_word_len))
    return result

def write_result(filename, result):
    with open(filename, 'w', encoding='UTF-8') as output_fs:
        for segmented_sentence in result:
            line = ' '.join(segmented_sentence) + '\n'
            output_fs.writelines(line)

chinese_word_set = get_chinese_word_set(opts['-d'])
# print(chinese_word_set)
result = chinese_word_segmentation(opts['-i'], chinese_word_set, MAXWORDLEN)
write_result(opts['-o'], result)



