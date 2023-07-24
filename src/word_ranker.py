import csv
import json
from glob import glob
import os


class WordRank:
    """
    A class for representing word rankings. WordRank stores a word along with
    its associated word rank and total frequency (count).
    """
    def __init__(self, word, rank=0.0, count=0):
        self.word = word
        self.rank = rank
        self.count = count

    def __eq__(self, other):
        return self.word == other.word

    def __lt__(self, other):
        return self.rank < other.rank

    def __hash__(self):
        return hash(self.word)

    def __ne__(self, other):
        return not (self == other)

    def __str__(self):
        return '{} - {}, {}'.format(self.word, self.rank, self.count)

    def __repr__(self):
        return '{} - {}, {}'.format(self.word, self.rank, self.count)


def clean_word(word):
    """
    Remove puncutation, whitespace, returns and other artifacts from a word.

    Args:
        word (string): The input word to clean.

    Returns:
        string: The result of cleaning the input word.
    """
    punctuation = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
    word = word.strip().lower()
    for element in word:
        if element in punctuation:
            word = word.replace(element, '')
    return word


def rank_words(words, total):
    """
    Rank words by their occurrence in a sample set of text. This helps ensure
    that we're not frequently utilizing rare or generally unused words.

    Args:
        words {string: WordRank}: A dictionary representing a word and its
            WordRank object.
        total (int): The total word count for use in ranking.

    Returns:
        [string]: A list of WordRank objects with words assigned their
            respective ranks.
    """
    word_list = list(words.values())
    rank_min = 100000
    rank_max = 0
    for word in word_list:
        # word.rank /= word_count_total
        word.rank = word.count / total
        if word.rank < rank_min:
            rank_min = word.rank
        if word.rank > rank_max:
            rank_max = word.rank
    # Normalize the rankings between 0 and 1.
    for word in word_list:
        word.rank = (word.rank - rank_min) / (rank_max - rank_min)
    word_list.sort()
    return word_list


def load_words_csv(file):
    """
    Load words from a CSV file into a WordRank representation.

    Args:
        file (string): The input file path.

    Returns:
        (dict): A dictionary of {word: WordRank}.
    """
    # str: WordRank
    words = {}
    # Just count five letter words.
    word_count_total = 0
    with open(file, 'r') as word_file:
        reader = csv.DictReader(word_file)
        for row in reader:
            description = row['Description']
            split_words = description.split(' ')
            for word in split_words:
                word_count_total += 1
                word = clean_word(word)
                if len(word) == 5:
                    if word in words:
                        words[word].count += 1
                    else:
                        w = WordRank(word, count=1)
                        words[word] = w

    word_list = rank_words(words, word_count_total)
    return word_list


def load_words_in_directory(dir_path, target_length=5):
    """
    Iterates through files in a directory and reads all text files, then loads
    the strings into a list. Note: the directory loading is not recursive, so
    all files need to be at the same hierarchical level.

    Args:
        dir_path (string): The path to search for text files in.
        target_length (int=5): The target length of words to compare. Word
        ladders generally just operate on words with the same length, so we
        cut out unnecessary compute by reducing our problem space assuming
        this invariant.
    """
    words = {}
    # Only count words for comparison of the same length rather than every
    # word.
    word_count_total = 0
    files = glob(dir_path + '/*.txt')
    for f in files:
        with open(f, 'r') as input_file:
            for line in input_file:
                for word in line.split(' '):
                    word = clean_word(word)
                    if len(word) == target_length:
                        word_count_total += 1
                        if word in words:
                            words[word].count += 1
                        else:
                            w = WordRank(word, count=1)
                            words[word] = w
    word_list = rank_words(words, word_count_total)
    return word_list


def main():
    """
    Generate word rankings based on word frequency from sampled text.
    The objective is to avoid using words that are rare or otherwise
    unknown.
    """
    file_path = os.path.dirname(os.path.abspath(__file__))
    words = os.path.join(file_path, '..', 'data', 'writing_samples', 'files')
    # words = load_words_in_directory('/Users/nickrogers/Developer/word_ladder/data/writing_samples/files')
    json_output = {}
    for word in words:
        json_output[word.word] = word.rank

    word_rank_path = os.path.join(
        file_path, '..', 'data', 'word_rankings', 'word_rank.json'
    )
    # with open('/Users/nickrogers/Developer/word_ladder/data/word_rankings/word_rank.json', 'w') as output_file:
    with open(word_rank_path, 'w') as output_file:
        json.dump(json_output, output_file)


if __name__ == '__main__':
    main()
