import random
import json


class Graph():
    """
    A directed graph for asscoiating words together based on their distances.
    This is key to how the word ladder generation works: words that are a
    distance of 1 (have 1 letter off) are adjacent to each other in the graph.
    """
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
            if stack[0] == start:
                repeated += 1
            if repeated == 2:
                return []

            vertex = stack.pop()
            visited.add(vertex)

            path.append(vertex)

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


def is_valid_sequence(seq):
    valid = True
    for i in range(len(seq)-1):
        current_word = seq[i]
        next_word = seq[i+1]
        if word_diff(current_word, next_word) > 1:
            valid = False
            print('{} and {} are more than 1 apart.'.format(current_word, next_word))
    return valid