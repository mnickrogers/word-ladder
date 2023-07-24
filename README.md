# word-ladder
A game of connecting the dots, but with words.

Word ladders give you start and end words and have you generate a "ladder" from the start word to the end word. You can only use valid dictionary words that change one character at a time for each step in the sequence.

For example, starting with `cakes` and moving to `rates`, a valid sequence would be:
```
cakes
makes
mates
fates
rates
```

This program generates valid word ladders and has helper functions to assist in managing the word dictionary. To generate the ladders, the program uses a modified DFS algorithm that accounts for how many desired steps should exist between the start and the end word.
