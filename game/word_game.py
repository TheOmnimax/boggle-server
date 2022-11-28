import logging
import json

from google.cloud import storage

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

def trieFromFile() -> WordTrie:
  gcs = storage.Client()
  bucket = gcs.get_bucket('boggle-words-data')
  trie_blob = bucket.blob('word_trie.json')
  trie_data = json.loads(trie_blob.download_as_string())
  return WordTrie(word_index=trie_data)

word_trie = trieFromFile()