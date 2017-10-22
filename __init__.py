# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo
# import all of the Qt GUI library
from aqt.qt import *
# import text importer
from anki.importing import TextImporter

import os
import json
import re
import zipfile
import requests
import time
from datetime import datetime

app_id = 'be715241'
app_key = '22ed51bc4eee05dd14fbdd3308503159'
# gdata_directory = "/home/chunjiw/Dropbox/Apps/Google Download Your Data/"
gdata_directory = "type/directory/of/your/downloaded/Google/Data/here"
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
    try:
        textfile = open('usec.txt', 'r')
        usec_last = int(textfile.read())
        textfile.close()
    except:
        usec_last = 0

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
    with open(filename, 'w', newline='', encoding='utf-8') as fw:
        for word in wordslist:
            success, entry, meaning = get_definitions(word)
            time.sleep(1.6)
            if success:
                print('write ' + entry + ' ' + wordsdict[word] +  '...')
                fw.writelines(entry + '<br>' + wordsdict[word] + '\t' + meaning + '\n')
                nw += 1
    fw.close()
    print(str(nw) + ' words written')
    return nw

# We're going to add a menu item below. First we want to create a function to
# be called when the menu item is activated.

def vocabulous():

    words_list, words_dict = get_entries()
    wordswritten = write_definitions("vocabulous.csv", words_list, words_dict)

    file = "vocabulous.csv"
    # select deck
    did = mw.col.decks.id("Default")
    mw.col.decks.select(did)
    # set note type for deck
    m = mw.col.models.byName("Basic")
    deck = mw.col.decks.get(did)
    deck['mid'] = m['id']
    mw.col.decks.save(deck)
    # import into the collection
    ti = TextImporter(mw.col, file)
    ti.allowHTML = True
    ti.importMode = 1
    ti.initMapping()
    ti.run()

    # get the number of cards in the current collection, which is stored in
    # the main window
    cardCount = mw.col.cardCount()
    # show a message box
    showInfo("Added %d new words. Now %d words in total." % (wordswritten, cardCount))

# create a new menu item, "Vocabulous"
action = QAction("Vocabulous", mw)
# set it to call vocabulous when it's clicked
action.triggered.connect(vocabulous)
# and add it to the tools menu
mw.form.menuTools.addAction(action)


