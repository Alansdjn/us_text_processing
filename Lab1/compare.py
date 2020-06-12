"""
------------------------------------------------------------
USE: python <PROGNAME> (options) file1...fileN
OPTIONS:
    -h : print this help message
    -b : use BINARY weights (default: count weighting)
    -s FILE : use stoplist file FILE
    -I PATT : identify input files using pattern PATT, 
              (otherwise uses files listed on command line)
    -p : print message
    -N : print only top N
------------------------------------------------------------
"""

import sys, re, getopt, glob

import numpy as np
from numpy import random
# import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

opts, args = getopt.getopt(sys.argv[1:], 'hs:bI:pN:')
opts = dict(opts)
filenames = args

##############################
# HELP option

if '-h' in opts:
    progname = sys.argv[0]
    progname = progname.split('/')[-1] # strip out extended path
    help = __doc__.replace('<PROGNAME>', progname, 1)
    print(help, file=sys.stderr)
    sys.exit()

##############################
# logging option
is_print_message = False
if '-p' in opts:
    is_print_message = True

def print_message(*objects):
    if is_print_message: print(*objects)

##############################
# Identify input files, when "-I" option used

if '-I' in opts:
    filenames = glob.glob(opts['-I'])
print_message('Input filenames: ', filenames)
filenames.sort()
print_message('Sorted filenames: ', filenames)

##############################
# STOPLIST option

stops = set()
if '-s' in opts:
    print_message('Stop file: ', opts['-s'])
    with open(opts['-s'], 'r') as stop_fs:
        for line in stop_fs :
            stops.add(line.strip())

##############################
# count-sensitive option

count_sensitive = 0
if '-b' in opts:
    count_sensitive = 1
print_message('count_sensitive: ', count_sensitive)

##############################
# top N option

N = 0
if '-N' in opts:
    if int(opts['-N']) <= int(len(filenames) * (len(filenames) - 1) / 2):
        N = int(opts['-N'])

print_message('N: ', N)

##############################
# param: filename, stops
# return: a dictionary of the words' counts

def count_words(filename, stops):
    words_counts = {}
    with open(filename, 'r') as news_fs:
        for line in news_fs: 
            words = extract_words(line)
            words_counts = update_words_counts(words_counts, words, stops)
    return words_counts

# extract all words from the input line
def extract_words(line):
    pattern = re.compile('[A-Za-z0-9]+')
    words = pattern.findall(line.lower())
    # print_message('line : ', line)
    # print_message('words: ', words)
    return words

# update the dictionary words_counts with a words list
def update_words_counts(words_counts, words, stops):
    for word in words:
        if word in stops:
            continue
        ## ??
        # elif word.isdigit():
        #     continue
        else: 
            words_counts[word] = words_counts.get(word, 0) + 1
    return words_counts

def jaccard_coefficient(A, B, count_sensitive):
    if count_sensitive:
        min_count, max_count = get_max_min_words_counts(A,B)
        return min_count / max_count
    else:
        A_keys_set = set(A.keys())
        B_keys_set = set(B.keys())
        joint_words = A_keys_set & B_keys_set

        # print_message('A_keys_set size: ', len(A_keys_set))
        # print_message('B_keys_set size: ', len(B_keys_set))
        # print_message('joint_words size: ', len(joint_words))
        # print_message('joint_words: ', joint_words)

        return len(joint_words) / (len(A_keys_set) + len(B_keys_set) - len(joint_words))

def get_max_min_words_counts(A, B):
    min_count = 0
    max_count = 0

    A_keys_set = set(A.keys())
    B_keys_set = set(B.keys())
    union_words = A_keys_set | B_keys_set

    # print_message('A_keys_set size: ', len(A_keys_set))
    # print_message('B_keys_set size: ', len(B_keys_set))
    # print_message('union_words size: ', len(union_words))
    #print_message('union_words: ', union_words)

    for word in union_words:
        w_A = 0
        w_B = 0
        if word in A_keys_set: w_A = A[word]
        if word in B_keys_set: w_B = B[word]
        #print_message(word + '_A: ', w_A)
        #print_message(word + '_B: ', w_B)
        
        min_count += min(w_A, w_B)
        max_count += max(w_A, w_B)

    # print_message('min_count: ', min_count, 'max_count: ', max_count)
    return min_count, max_count

def compare(filenames, count_sensitive):
    compare_file_jco_dict = {}
    filename_wordscount_dict = {}
    for file in filenames:
        result_file = count_words(file, stops)
        filename_wordscount_dict[file] = result_file

    for i in range(len(filenames) - 1):
        result_i = filename_wordscount_dict[filenames[i]]
        # print_message(filenames[i] + ': ', result_i)
        for j in range(i + 1, len(filenames)):
            result_j = filename_wordscount_dict[filenames[j]]
            # print_message(filenames[j] + ': ', result_j)
            jco = jaccard_coefficient(result_i, result_j, count_sensitive)
            compare_file_jco_dict[filenames[i] + ' <> ' +  filenames[j]] = jco
            #print('%s <> %s = %0.4f' %(filenames[i], filenames[j], jco))
    return compare_file_jco_dict


##############################
# compare files
compare_result = compare(filenames, count_sensitive)

# print(compare_result)
def print_result(compare_result, topN):
    if topN != 0:
        sorted_compare_list = sorted(compare_result.items(), key= lambda item: item[1], reverse=True)
        for i in range(topN):
            print('%s = %0.3f' %(sorted_compare_list[i][0], sorted_compare_list[i][1]))
    else:
        print(compare_result)
        for key, value in compare_result.items():
            print('%s = %0.3f' %(key, value))

print_result(compare_result, N)

###############################
## heat map
def heatmap(compare_result, filenames):
    size = len(filenames)
    R = np.zeros((size, size))
    for i in range(size):
        for j in range(size):
            if i == j:
                R[i][j] = 1
            elif i < j:
                R[i][j] = compare_result[filenames[i] + ' <> ' +  filenames[j]]
            else:
                R[i][j] = compare_result[filenames[j] + ' <> ' +  filenames[i]]

    # R = random.randn(20, 20)
    fig = plt.figure()
    # sns_plot = sns.heatmap(R, annot=True)
    sns_plot = sns.heatmap(R, cmap='YlGnBu', xticklabels=8, yticklabels=8)
    # fig.savefig("heatmap.pdf", bbox_inches='tight') # 减少边缘空白
    plt.show()

heatmap(compare_result, filenames)