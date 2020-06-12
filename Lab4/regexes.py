
# COM3110/4155/6155: Text Processing
# Regular Expressions Lab Class

import sys, re

#------------------------------

# testRE = re.compile('(logic|sicstus)', re.I)
html_open_tag_re = re.compile('(<[^/](.*?)>)', re.I)
html_close_tag_re = re.compile('(</(.*?)>)', re.I)
html_open_tag_param_re = re.compile(r'(\b[A-Za-z]+=.*?)*', re.I)
#------------------------------

with open('RGX_DATA.html') as infs: 
    linenum = 0
    for line in infs:
        linenum += 1
        if line.strip() == '':
            continue
        print('  ', '-' * 100, '[%d]' % linenum, '\n   TEXT:', line, end='')
    
        # m = testRE.search(line)
        # if m:
        #     print('** TEST-RE:', m.group(1))

        # mm = testRE.finditer(line)
        # for m in mm:
        #   print('** TEST-RE:', m.group(1))

        open_tags = html_open_tag_re.finditer(line)
        for tag in open_tags:
            tag.group(1)
            # if tag.group().startswith('</'):
            #   print('  ', 'CLOSETAG:', tag.group().replace('</','').replace('>',''))
            # else:
            #   tag_with_params = tag.group().replace('<','').replace('>','')
            #   tag_params_list = tag_with_params.split()
            #   print('  ', 'OPENTAG:', tag_params_list[0])
            #   if len(tag_params_list) > 1:
            #       for param in tag_params_list[1:]:
            #           print('  ', '  ', 'PARAM:', param)


            
