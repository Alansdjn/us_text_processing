"""
------------------------------------------------------------
USE: python <PROGNAME> (options) file1...fileN
OPTIONS:
    -h : print this help message
    -d FILE : use data file FILE

    -s FILE : use stoplist file FILE
    -I PATT : identify input files using pattern PATT, 
              (otherwise uses files listed on command line)
    -p : print message
    -N : print only top N
------------------------------------------------------------
"""
import sys, re, getopt, math
import pylab as p

opts, args = getopt.getopt(sys.argv[1:], 'hd:')
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

if '-d' in opts:
	datafile = opts['-d']
else:
	print('-d data file name must input', file=sys.stderr)
	sys.exit()

def get_all_token(filename):
	token_dict={}
	with open(filename, 'r') as fs:
		for line in fs:
			tmp_token_list = extract_tokens(line)
			for token in  tmp_token_list:
				token_count = token_dict.setdefault(token, 0)
				token_dict[token] = token_count + 1
	return token_dict

# extract all words from the input line
def extract_tokens(line):
    return re.compile('[A-Za-z0-9]+').findall(line.lower())

all_token_dict = get_all_token(datafile)
sorted_all_token_dict = sorted(all_token_dict.items(), key=lambda item:item[1], reverse = True)

print('Total number of word occurrences: %d' %(sum(all_token_dict.values())))
print('The number of distinct words: %d' %(len(all_token_dict)))
top_N = 20
print('Top %d words frequencies:' %(top_N))
for key,value in sorted_all_token_dict[:top_N]:
	print('\t', key, '\t:\t', value)

########################################
# plots
Y = sorted(all_token_dict.values(), reverse = True)
X = list(range(len(Y)))
########################################
# frequencies vs rank topN
p.subplot(131)
p.plot(X[:100],Y[:100])
p.subplot(132)
p.plot(X[:1000],Y[:1000])
p.subplot(133)
p.plot(X,Y)
p.suptitle('Frequencies vs Rank')
p.show()

########################################
# cumulative count vs rank topN
Y_cu = [Y[0],]
for i in X[1:]:
	Y_cu.append(Y_cu[i - 1] + Y[i])

p.subplot(131)
p.plot(X[:100],Y_cu[:100])
p.subplot(132)
p.plot(X[:1000],Y_cu[:1000])
p.subplot(133)
p.plot(X,Y_cu)
p.suptitle('Cumulative Count vs Rank')
p.show()

########################################
# log-log
Y_log = [math.log(Y[0]),]
X_log = [0,]
for i in X[1:]:
	X_log.append(math.log(i))
	Y_log.append(math.log(Y[i]))

p.plot(X_log,Y_log)
p.title('Power Law relationship')
p.show()
