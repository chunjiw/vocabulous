import os
import json
import re
import zipfile
import requests
import time
import credentials
from datetime import datetime

# import socket
# import csv

app_id = credentials.app_id
app_key = credentials.app_key
gdata_directory = credentials.gdata_directory
language = 'en'


def get_definitions(item):

    # request
    word_id = item
    url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + '/' + word_id.lower() + '/regions=us'
    r = requests.get(url, headers={'app_id': app_id, 'app_key': app_key})
    if r.status_code != 200:
        return False, None, None

    word = ''
    meaning = ''
    j = r.json()

    for result in j.get('results', []):
        word = result.get('word', item)
        meaning += word
        # print(result.get('word', ''))
        for pronunciation in result.get('pronunciations', []):
            # print(pronunciation.get('phoneticSpelling', ''))
            meaning += '<br>/' + pronunciation.get('phoneticSpelling', '') + '/'
        for ilexicalEntry, lexicalEntry in enumerate(result.get('lexicalEntries', [])):
            # print(lexicalEntry.get('lexicalCategory', ''))
            meaning += '<br><i>' + lexicalEntry.get('lexicalCategory', '').lower() + '</i>'
            for pronunciation in lexicalEntry.get('pronunciations', []):
                # print(pronunciation.get('phoneticSpelling', ''))
                meaning += ' /' + pronunciation.get('phoneticSpelling', '') + '/'
            for ientry, entry in enumerate(lexicalEntry.get('entries', [])):
                for pronunciation in entry.get('pronunciations', []):
                    # print(pronunciation.get('phoneticSpelling', ''))
                    meaning += ' /' + pronunciation.get('phoneticSpelling', '') + '/'
                for isense, sense in enumerate(entry.get('senses', [])):
                    for pronunciation in sense.get('pronunciations', []):
                        # print(pronunciation.get('phoneticSpelling', ''))
                        meaning += ' /' + pronunciation.get('phoneticSpelling', '') + '/'
                    for definition in sense.get('definitions', []):
                        # print(definition)
                        meaning += '<br>' + str(isense + 1) + '. ' + definition + '.'
                    for example in sense.get('examples', []):
                        # print(example.get('text', ''))
                        meaning += '<br><font color="grey">"' + example.get('text', '') + '"</font>'
                    for subsense in sense.get('subsenses', []):
                        for definition in subsense.get('definitions', []):
                            # print(definition)
                            meaning += '<br>&middot ' + definition + '.'
                        for example in subsense.get('examples', []):
                            # print(example.get('text', ''))
                            meaning += '<br><font color="grey">"' + example.get('text', '') + '"</font>'
                for etymology in entry.get('etymologies', []):
                    meaning += ' <br>[Etymology]<br>' + etymology
    return True, word, meaning


def get_entries():
    # if socket.gethostname() == 'Cbuntu':
    home = '/home'
    # elif socket.gethostname() == 'PT-CNRL04':
    #    home = 'C:/Users'

    # # set working directory
    # os.chdir(home + '/chunjiw/Dropbox/DefDict/')

    # unzip data
    filelist = os.listdir(gdata_directory)
    filelist.sort()
    zf = zipfile.ZipFile(gdata_directory + filelist[-1])
    # get the latest json file
    jsonlist = zf.namelist()
    jsonlist.sort()
    recent_json = jsonlist[-2]  # -2 is the most recent json file
    zf.extract(recent_json)
    zf.close()

    # read data
    with open(recent_json, encoding='utf8') as f:
        searches = json.load(f)['event']
    # last update time
    textfile = open('usec.txt', 'r')
    usec_last = int(textfile.read())
    textfile.close()

    # collect words
    wordslist = list()
    wordsdict = dict()
    for search in searches:
        usec = int(search['query']['id'][0]['timestamp_usec'])
        if usec > usec_last:
            date = time.strftime('%m/%d/%Y', time.gmtime(usec / 1000000))
            text = search['query']['query_text'].lower()
            if re.match('define', text):
                text = re.sub('define ', '', text)
                # # print(text)
            elif re.match('definition', text):
                text = re.sub(' definition', '', text)
                # # print(text)
            else:
                continue
            if text not in wordslist:
                wordslist.append(text)
                wordsdict[text] = date
    print(str(len(wordslist)) + ' words collected')
    # update update time
    usec_this = searches[0]['query']['id'][0]['timestamp_usec']
    textfile = open('usec.txt', 'w')
    textfile.write(usec_this)
    textfile.close()

    return wordslist, wordsdict


def write_definitions(filename, wordslist, wordsdict):
    nw = 0  # count words written
    with open(filename, 'w', newline='') as fw:
        for word in wordslist:
            success, entry, meaning = get_definitions(word)
            time.sleep(1.6)
            if success:
                print('write ' + entry + ' ' + wordsdict[word] +  '...')
                fw.writelines(entry + '<br>' + wordsdict[word] + '\t' + meaning + '\n')
                nw += 1
    fw.close()
    print(str(nw) + ' words written')


if __name__ == '__main__':
    words_list, words_dict = get_entries()
    write_definitions(str(datetime.now()), words_list, words_dict)
