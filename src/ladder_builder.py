import random
import json
import csv
import os

import graph


class SequenceRank:
    """
    A class to rank the hardness of a given sequence. This enables us to
    easily compare sequences based on how hard they are to solve.
    """
    def __init__(self, sequence, rank=0.0):
        self.sequence = sequence
        self.rank = rank

    def __eq__(self, other):
        return self.sequence == other.sequence

    def __lt__(self, other):
        return self.rank < other.rank

    def __hash__(self):
        return hash(self.sequence)

    def __ne__(self, other):
        return not (self == other)

    def __str__(self):
        return '{} - {}'.format(self.sequence, self.rank)

    def __repr__(self):
        return '{} - {}'.format(self.sequence, self.rank)


def calculate_rank(sequence, word_rankings, rank_average):
    """
    Calculate the uniqueness of a given sequence based on how "rare" its words
    are.

    Args:
        sequence [string]: A list of strings that represent a word ladder
            sequence.
        word_rankings {string: double}: A dict of {word: ranking}.
        rank_average (double): The average ranking for our sequences.

    Returns:
        (double): The calculated rank for this sequence.
    """
    rank = 0.0
    for word in sequence:
        # If the word isn't in our rankings, just treat it as a rank of 0 or
        # punish it more.
        if word in word_rankings:
            rank += word_rankings[word]
        else:  # If the word isn't in our word rankings, punish it more.
            rank -= (rank_average * 2)
            # Let's see what happens if we just remove the sequence.
            # rank = -100
    return rank / len(sequence)


def distance(w1, w2):
    """
    Calculate the "distance" between two words based on how many letters in
    the words differ for each character position (similar to calculating
    Hamming distance). Used for determining the "distance" between the start
    word and the finished word. This is an analog for approximating the
    "hardness" of a given set of start/end pairs for a ladder. The farther the
    distance between the start and end words, generally the harder they'll be
    to solve.
    """
    length_discrepancy = 0
    outter = ''
    inner = ''

    if len(w1) > len(w2):
        outter = w2
        inner = w1
        length_discrepancy = len(w1) - len(w2)
    elif len(w2) > len(w1):
        outter = w1
        inner = w2
        length_discrepancy = len(w2) - len(w1)
    else:
        outter = w1
        inner = w2

    discrepancy = 0
    for i in range(len(outter)):
        if outter[i] != inner[i]:
            discrepancy += 1

    return discrepancy + length_discrepancy


def save_sequences(sequences):
    """
    Save the sequences to an output CSV file.

    Args:
        sequences (list): The sequences to save.

    Returns:
        none
    """
    file_path = os.path.dirname(os.path.abspath(__file__))
    save_path = os.path.join(
        file_path, '..', 'data', 'output', 'generated_ladders_2.csv'
    )
    # with open('/Users/nickrogers/Developer/word_ladder/data/output/generated_ladders_2.csv', 'w') as write_file:
    with open(save_path, 'w') as write_file:
        writer = csv.DictWriter(write_file, fieldnames=[
            'start', 'end', 'sequence', 'rank', 'hardness'
        ])

        writer.writeheader()
        for sequence in sequences:
            start = sequence.sequence[0]
            end = sequence.sequence[-1]
            hardness = distance(start, end)
            word_string = ' '.join(sequence.sequence)
            writer.writerow({
                'start': start,
                'end': end,
                'sequence': word_string,
                'rank': sequence.rank,
                'hardness': hardness
            })


def main():
    """
    Builds a sequence of ladders for use in our website. This involves running
    the ladder building operation many times over while randomizing the words
    each time and not reapeating any start/end sequences.
    """

    # The number of times to run the ladder generation sequence. Equivalent to
    # the number of ladder sequences we want to generate.
    iterations = 730*5
    # How many steps do we want from the start of each word to its end? Making
    # this number larger generally makes the ladders harder (though that's not
    # always the case) and reducese the solution space.
    intermediary_steps = 3
    # We add in two additional steps to account for the jumps after the start
    # word and before the end word.
    steps = intermediary_steps + 2

    # Use this file location to determine the relative paths of other files.
    file_path = os.path.dirname(os.path.abspath(__file__))
    graph_path = os.path.join(
        file_path, '..', 'data', 'graph_data', 'graph.json'
    )

    g = graph.Graph()
    # g.load_graph('/Users/nickrogers/Developer/word_ladder/data/graph_data/graph.json')
    g.load_graph(graph_path)

    five_letter_words_path = os.path.join(
        file_path,
        '..',
        'data',
        'word_lists',
        'even_more_five_letter_words.txt'
    )
    # Load in all available words into a set.
    words = set()
    # with open('/Users/nickrogers/Developer/word_ladder/data/word_lists/even_more_five_letter_words.txt', 'r') as words_file:
    with open(five_letter_words_path, 'r') as words_file:
        [words.add(x.strip()) for x in words_file.readlines()]

    # Get word rankings
    word_rank_path = os.path.join(
        file_path, '..', 'data', 'word_rankings', 'word_rank.json'
    )
    word_rankings = {}
    # with open('/Users/nickrogers/Developer/word_ladder/data/word_rankings/word_rank.json', 'r') as input_words:
    with open(word_rank_path, 'r') as input_words:
        word_rankings = json.load(input_words)

    # Only average words with a rating.
    rank_average = sum(i for i in word_rankings.values() if i > 0.0) / len(word_rankings)

    sequences = []

    i = 0
    while i < iterations:
        start_word = random.choice(list(words))
        words.remove(start_word)

        result = g.get_random_destination_from_node(start_word, steps)
        # For some reason the graph will sometimes return an empty list even for words that
        # can have valid sequences. This will involve more debugging. In the meantime,
        # just check for empty sequences and move on. CAUTION: this approach might lead to
        # an infinite loop if there is a word that actually has no solution.
        if result and graph.is_valid_sequence(result):
            # print(result)
            rank = calculate_rank(result, word_rankings, rank_average)
            sr = SequenceRank(result, rank)
            sequences.append(sr)
            i += 1

    sequences.sort(reverse=True)
    refined_sequences = []

    for seq in sequences:
        start = seq.sequence[0]
        end = seq.sequence[-1]
        rank = distance(start, end)
        if rank > 1:
            refined_sequences.append(seq)
    sequences = refined_sequences

    save_sequences(sequences)


if __name__ == '__main__':
    main()