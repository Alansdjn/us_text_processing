"""
USE: python <PROGNAME> (options) 
OPTIONS:
    -h : print this help message and exit
    -d FILE : use FILE as data to create a new lexicon file
    -l FILE : create OR read lexicon file FILE
    -t FILE : apply lexicon to test data in FILE
"""
################################################################

import sys, re, getopt
import numpy as np

################################################################
# Command line options handling, and help

opts, args = getopt.getopt(sys.argv[1:],'hd:l:t:')
opts = dict(opts)

def printHelp():
    help = __doc__.replace('<PROGNAME>',sys.argv[0],1)
    print('-' * 60, help, '-' * 60, file=sys.stderr)
    sys.exit()
    
if '-h' in opts:
    printHelp()

if len(args) > 0:
    print("\n** ERROR: no arg files - only options! **", file=sys.stderr)
    printHelp()

lexicon_file = ''
if '-l' not in opts:
    print("\n** ERROR: must specify lexicon file name (opt: -l) **", file=sys.stderr)
    printHelp()
else:
    lexicon_file = opts['-l']
################################################################
# use FILE as data to create a new lexicon file
# {term 􏱄-> {postag 􏱄-> count}} ==> {once -> {IN -> 1}}

def update_term_postag_count(term_postag_count, term, postag, addcount):
    postag_count_dict = term_postag_count.get(term,{postag:0})
    postag_count_dict[postag] = postag_count_dict.get(postag, 0) + 1;
    term_postag_count[term] = postag_count_dict

def get_term_postag_count_dict(filename):
    term_postag_count = {}
    with open(filename, 'r') as data_fs:
        for line in data_fs:
            if len(line) == 0:
                continue
            term_postag_list = line.replace('\n', '').split() #.replace(r'\/', '/')
            for term_postag_str in term_postag_list:
                # only split the last one, eg. editing\/electronic/JJ
                term_postag = term_postag_str.rsplit('/',1) 
                if term_postag[1].find('|') > 0: # process multi tags, eg. male/JJ|NN
                    postags = term_postag[1].split('|')
                    for postag in postags:
                        update_term_postag_count(term_postag_count, term_postag[0], postag, 1)
                else:
                    update_term_postag_count(term_postag_count, term_postag[0], term_postag[1], 1)
    return term_postag_count

def write_term_postag_count(term_postag_count, lexicon_file):
    np.save(lexicon_file, term_postag_count)

def read_term_postag_count(lexicon_file):
    return np.load(lexicon_file, allow_pickle=True).item()

term_postag_count = {}
if '-d' in opts:
    term_postag_count = get_term_postag_count_dict(opts['-d'])
    write_term_postag_count(term_postag_count, lexicon_file)
    # sys.exit()
else:
    term_postag_count = read_term_postag_count(lexicon_file)
    print('term_postag_count length: ',len(term_postag_count))
    # print(term_postag_count)

###############################################################
# ** Types are the distinct words in a corpus, 
# ** whereas tokens are the words, including repeats.
# full set of POS tags used in the data

token_count = 0
type_count = 0
all_postag_count_dict = {}
type_ambiguous_count = 0
token_unambiguous_count = 0
most_common_tag_count = 0
for term, postag_count in term_postag_count.items():
    token_count += sum(postag_count.values())
    most_common_tag_count += max(postag_count.values())

    postag_count_len = len(postag_count)
    type_count += postag_count_len
    if postag_count_len > 1:
        type_ambiguous_count += 1
    if postag_count_len == 1:
        token_unambiguous_count += sum(postag_count.values())

    for postag,count in postag_count.items():
        all_postag_count_dict[postag] = all_postag_count_dict.setdefault(postag, 0) + count
        
        

print('a.1) All %d sorted tags:' %(len(all_postag_count_dict)))
sorted_tags_with_count = sorted(all_postag_count_dict.items(), key=lambda item: item[1], reverse = True)
for postag, count in sorted_tags_with_count[:10]:
    print('\t%s\t%.3f%%\t(%d / %d)' % (postag, 100 * count / token_count, count, token_count))
print('\t...')

most_common_tag = sorted_tags_with_count[0]
print('a.2) The most single common tag: %s / %d' % (most_common_tag[0], most_common_tag[1]))

accuracy_score = 100 * most_common_tag[1] / token_count
print('a.3) The accuracy score (just assigned the most common tag "%s" to every word): %.3f%%' % ( sorted_tags_with_count[0], accuracy_score))

print('b.1) Proportion of types that are ambiguous: %.3f%% (%d / %d)' % (100 * type_ambiguous_count / type_count, type_ambiguous_count, type_count))

print('b.1) Proportion of tokens that are unambiguous: %.3f%% (%d / %d)' % (100 * token_unambiguous_count / token_count, token_unambiguous_count, token_count))


print('A naive approach: assign to each token its own most common POS tag:')
print('\tAccuracy score(training data): %.3f%% (%d / %d)' % (100 * most_common_tag_count / token_count, most_common_tag_count, token_count))

#############################################
# convert term_postag_count to term_max_postag_count
# if a term has multi maxmuim postag, choose the first tag
def convert_max_term_postag(term_postag_count):
    max_term_postag = {}
    for term, postag_count in term_postag_count.items():
        max_postag_count = max(postag_count.items(),key=lambda item:item[1])
        # print(postag_count, '>>>>>', max_postag_count)
        max_term_postag.setdefault(term, max_postag_count[0])
    return max_term_postag

max_term_postag = convert_max_term_postag(term_postag_count)
test_term_postag_count = get_term_postag_count_dict(opts['-t'])
test_term_postag_count_by_naive = {}
right_token = 0
total_token = 0
unk_token = 0
unk_token_set = set()
for term, postag_count in test_term_postag_count.items():
    total_postag_count = sum(postag_count.values());
    total_token += total_postag_count
    if term not in max_term_postag.keys():
        test_term_postag_count_by_naive[term] = {'UNK': total_postag_count}
        unk_token += total_postag_count
        unk_token_set.add(term)
    else:
        test_term_postag_count_by_naive[term] = {max_term_postag[term]:total_postag_count}
        if max_term_postag[term] in postag_count.keys():
            right_token += postag_count[max_term_postag[term]]

print('\tUnknown token count(testing data): %d' % (unk_token))
print('\tAccuracy score(testing data): %.3f%% (%d / %d)' % (100 * right_token / total_token, right_token, total_token))
# print('unk_token_set :', unk_token_set)

#############################################################
# just use the single most common tag to UNK
print('Handle the UNK words: assign each unknown word the most common tag:')
unk_token_right_by_single_most_common_tag = 0
for term in unk_token_set:
    if most_common_tag[0] in test_term_postag_count[term]:
        unk_token_right_by_single_most_common_tag += test_term_postag_count[term][most_common_tag[0]]

print('\tRight unknown token count: %d' % (unk_token_right_by_single_most_common_tag))
print('\tThe naive approach in testing data accuracy score: %.3f%% (%d / %d)' % (100 * (right_token + unk_token_right_by_single_most_common_tag) / total_token, right_token + unk_token_right_by_single_most_common_tag, total_token))

# 
print('Handle the UNK words: assign each unknown word tag by using subclass rules:')
unk_token_right_by_subclass_term = 0
discard_unk_token_set = set()
for term in unk_token_set:
    # numbers
    if term.replace(',','').replace('-','').replace('.','').replace(':','').isdigit():
        if 'CD' in test_term_postag_count[term]:
            unk_token_right_by_subclass_term += test_term_postag_count[term]['CD']
            discard_unk_token_set.add(term)
        else:
            print('CD==>fail==>', term, '<==', test_term_postag_count[term])
    #xxx-xxxx-xx-xxx
    elif len(term.split('-')) > 1:
        if 'JJ' in test_term_postag_count[term]:
            unk_token_right_by_subclass_term += test_term_postag_count[term]['JJ']
            discard_unk_token_set.add(term)
        else:
            print('JJ==>fail==>', term, '<==', test_term_postag_count[term])
    #-ed
    elif term.endswith('ed'):
        if 'VBD' in test_term_postag_count[term]:
            unk_token_right_by_subclass_term += test_term_postag_count[term]['VBD']
            discard_unk_token_set.add(term)
        else:
            print('VBD==>fail==>', term, '<==', test_term_postag_count[term])
    #-ing
    elif term.endswith('ing'):
        if 'VBG' in test_term_postag_count[term]:
            unk_token_right_by_subclass_term += test_term_postag_count[term]['VBG']
            discard_unk_token_set.add(term)
        else:
            print('VBG==>fail==>', term, '<==', test_term_postag_count[term])
    #-ly
    elif term.endswith('ly'):
        if  'RB' in test_term_postag_count[term]:
            unk_token_right_by_subclass_term += test_term_postag_count[term]['RB']
            discard_unk_token_set.add(term)
        else:
            print('RB==>fail==>', term, '<==', test_term_postag_count[term])
    #-ly
    elif term.endswith('able'):
        if 'JJ' in test_term_postag_count[term]:
            unk_token_right_by_subclass_term += test_term_postag_count[term]['JJ']
            discard_unk_token_set.add(term)
        else:
            print('JJ==>fail==>', term, '<==', test_term_postag_count[term])
    #IBM
    elif term.isupper() or term[0].isupper():
        if term.endswith('s') or term.endswith('es'):
            if 'NNPS' in test_term_postag_count[term]:
                unk_token_right_by_subclass_term += test_term_postag_count[term]['NNPS']
                discard_unk_token_set.add(term)
            else:
                print('NNPS==>fail==>', term, '<==', test_term_postag_count[term])
        else:
            if 'NNP' in test_term_postag_count[term]:
                unk_token_right_by_subclass_term += test_term_postag_count[term]['NNP']
                discard_unk_token_set.add(term)
            else:
                print('NNP==>fail==>', term, '<==', test_term_postag_count[term])
    #-s/-es
    elif term.endswith('s') or term.endswith('es'):
        if 'NNS' in test_term_postag_count[term]:
            unk_token_right_by_subclass_term += test_term_postag_count[term]['NNS']
            discard_unk_token_set.add(term)
        else:
            print('NNS==>fail==>', term, '<==', test_term_postag_count[term])

    # most_common_tag
    elif most_common_tag[0] in test_term_postag_count[term]:
        unk_token_right_by_subclass_term += test_term_postag_count[term][most_common_tag[0]]
        discard_unk_token_set.add(term)
        # print('%s: %s' %(most_common_tag[0], term))
    else:
        print(most_common_tag[0],'==>fail==>', term, '<==', test_term_postag_count[term])
print('\tDiscard unknown token count(testing data): %d' % (len(discard_unk_token_set)))
print('\tUnknown token count(testing data): %d' % (len(unk_token_set) - len(discard_unk_token_set)))
print('\tThe advanced approach in testing data accuracy score: %.3f%% (%d / %d)' % (100 * (right_token + unk_token_right_by_subclass_term) / total_token, right_token + unk_token_right_by_subclass_term, total_token))



        


