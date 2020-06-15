
# COM3110/4155/6155: Text Processing
# Regular Expressions Lab Class

import sys, re

#------------------------------

# testRE = re.compile('(logic|sicstus)', re.I)
html_tags_re = re.compile(r'<([/]?)([A-Za-z0-9]+)[ ]*(.*?)>', re.I)
pair_tags_re = re.compile(r'<([A-Za-z0-9]+).*?>(.*?)</\1>', re.I)
url_re = re.compile(r'<a href=(["\']?)(.*?)\1*?>', re.I)
#------------------------------

with open('RGX_DATA.html') as infs: 
    linenum = 0
    for line in infs:
        linenum += 1
        if line.strip() == '':
            continue
        print('  ', '-' * 100, '[%d]' % linenum, '\n   TEXT:', line, end='')

        tags = html_tags_re.finditer(line)
        for tag in tags:
            if tag.group(1) != '/':
                print('  ', 'OPENTAG:', tag.group(2))
                if tag.group(3) != None and len(tag.group(3)) > 0:
                    params = re.split(' ', tag.group(3))
                    for param in params:
                          print('  ', '  ', 'PARAM:', param)
            else:
                print('  ', 'CLOSETAG:', tag.group(2))

        pair_tags = pair_tags_re.finditer(line)
        for pair_tag in pair_tags:
            print('  ', 'PAIR[%s]:' % pair_tag.group(1), pair_tag.group(2))

        urls = url_re.finditer(line)
        for url in urls:
            print('  ', 'URL:', url.group(2))


print('  ', '=' * 100)
with open('RGX_DATA.html') as infs: 
    linenum = 0
    for line in infs:
        linenum += 1
        if line.strip() == '':
            continue
        # print('  ', '-' * 100, '[%d]' % linenum, '\n   TEXT:', line, end='')

        replaced_line = re.sub(r'<([/]?)([A-Za-z0-9]+)[ ]*(.*?)>', '', line, flags=re.I).rstrip('\n')
        if len(replaced_line.rstrip()) > 0:
            print('  ', 'STRIPPED[%d]:' % len(replaced_line), replaced_line)

print('  ', '=' * 100)
with open('RGX_DATA.html') as infs: 
    text = ''
    for line in infs:
        if line.strip() == '':
            continue
        text += line

    replaced_text = re.sub(r'<([/]?)([A-Za-z0-9]+)[ ]*(.*?)>', '', text, flags=re.I|re.M|re.S)
    replaced_text = re.sub(r'[\n]+', '\n', replaced_text,flags=re.I|re.M|re.S)
    if len(replaced_text) > 0:
        print('  ', 'STRIPPED[%d]:' % len(replaced_text), replaced_text)



            
