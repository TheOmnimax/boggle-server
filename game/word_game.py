import logging
from os.path import dirname, join, realpath
import json

class WordTrie:
  def __init__(self, word_index):
    self.word_index = word_index
  
  def checkWordExists(self, word):
    working_dict = self.word_index
    for letter in word:
      if letter in working_dict:
        working_dict = working_dict[letter]
      else:
        return False
    if 'word' in working_dict:
      retrieved_word = working_dict['word']
      if retrieved_word == word:
        return True
      else:
        logging.error(f'Searched for word "{word}", and found part of it, but retrieved word is "{retrieved_word}".')
        return False

def trieFromFile(filepath) -> WordTrie:
  with open(filepath) as f:
    word_index = json.loads(f.read())
  return WordTrie(word_index=word_index)
  
word_trie = trieFromFile(join(dirname(dirname(realpath(__file__))), 'data', 'word_index.json'))