import random
import json
import argparse


# Use this for the linked list (used to recover a computed path).
class Node():
    """
    A node representing a child/parent relationship. This can be used for a
    linked list to recover a computed path.
    """
    def __init__(self, content, parent):
        self.content = content
        self.parent = parent


class Graph():
    def __init__(self):
        self.edges = {}

    def add_vertex(self, v):
        self.edges[v] = []

    def add_vertices(self, vs):
        for v in vs:
            self.add_vertex(v)

    def get_edges_for_vertex(self, v):
        return self.edges[v]

    def add_edge(self, v1, v2, bidirectional=False):
        # Check if these vertices exist in the graph. If not, add them.
        if v1 in self.edges:
            self.edges[v1].append(v2)
        else:
            self.edges[v1] = [v2]

        if bidirectional:
            if v2 in self.edges:
                self.edges[v2].append(v1)
            else:
                self.edges[v2] = [v1]

    def has_children(self, vertex, visited=None):
        if not visited:
            return len(self.edges[vertex]) > 0
        # For the purpose of traversing the graph correctly, we need to
        # consider nodes with children we've already visited as being empty.
        # This is important since, if the graph is bidirectional, there will
        # always be a child element for every edge that exists.
        else:
            children = set(self.edges[vertex])
            unvisited_children = children.difference(visited)
            return len(unvisited_children) > 0

    def get_random_destination_from_node(self, start, steps):
        path = []
        stack = []
        stack.append(start)

        visited_childless_vertices = set()
        visited = set()

        repeated = 0

        i = 0
        while i < steps:
            # print(stack)
            # time.sleep(1)
            # Kind of a hack. We need to prevent an infinite loop where there
            # is no solution (e.g., this segment of the grid is cyclic).
            if stack[0] == start:
                repeated += 1
            if repeated == 2:
                return []

            vertex = stack.pop()
            visited.add(vertex)

            path.append(vertex)

            # if vertex in visited_childless_vertices:
            #     stack.clear()
            #     path.clear()
            #     visited.clear()
            #     i = 0
            #
            #     stack.append(start)
            #
            # if self.has_children(vertex, visited):
            #     children = list(set(self.edges[vertex]).difference(visited))
            #
            #     random.shuffle(children)
            #
            #     stack += children
            #     i += 1
            # else:
            #     visited_childless_vertices.add(vertex)
            #     stack.clear()
            #     path.clear()
            #     visited.clear()
            #     i = 0
            #
            #     stack.append(start)

            if self.has_children(vertex, visited):
                children = list(set(self.edges[vertex]).difference(visited))

                random.shuffle(children)

                stack += children
                i += 1
            # We do the same thing if the node has no children or if we've
            # already visited this node and no it has no children (might be
            # redundant?): start over.
            else:
                visited_childless_vertices.add(vertex)
                stack.clear()
                path.clear()
                visited.clear()
                i = 0

                stack.append(start)

        return path

    def print_graph(self):
        print(self.edges)

    def save_graph(self, output_path):
        with open('{}/graph.json'.format(output_path), 'w') as output_file:
            json.dump(self.edges, output_file)

    def load_graph(self, path):
        with open(path, 'r') as input_file:
            self.edges = json.load(input_file)


def word_diff(w1, w2):
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


def is_valid_sequence(seq):
    valid = True
    for i in range(len(seq)-1):
        current_word = seq[i]
        next_word = seq[i+1]
        if word_diff(current_word, next_word) > 1:
            valid = False
            print('{} and {} are more than 1 apart.'.format(current_word, next_word))
    return valid


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('number_of_sequences', help='Number of word ladders to generate')
    parser.add_argument('number_of_steps', help='The number of steps to take from this word')
    return parser


def main():
    g = Graph()

    p = build_parser()
    args = p.parse_args()

    g.load_graph('/Users/nickrogers/Desktop/graph.json')

    sequences = []

    intermediary_steps = int(args.number_of_steps)
    steps = intermediary_steps + 2

    words = set(g.edges.keys())
    i = 0
    while i < int(args.number_of_sequences):
        word = random.choice(list(words))
        sequence = g.get_random_destination_from_node(word, steps)
        words.remove(word)
        if is_valid_sequence(sequence) and len(sequence) > 0:
            sequences.append(sequence)
            i += 1

    print(sequences)

    # ---------- Use this to run the program
    # start = args.start_word
    # result = g.get_random_destination_from_node(start, steps=steps)
    # print(result)
    # print('Is sequence valid: {}'.format(is_valid_sequence(result)))
    # ----------


if __name__=='__main__':
    main()
