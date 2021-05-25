import concurrent
import concurrent.futures
import itertools
import json
from string import ascii_lowercase


def add_word_len():
    """Adds a list to the start of each combo with the value at i
     representing the index at which the last word of i + 3 length appeared.
     Used in order to limit the bot to words of x length."""
    with open("combo_dict_final.json", "r") as dict_file:
        words_dict = json.load(dict_file)

    for vowel in words_dict:
        lens = [1 for _ in range(3, 21)]
        current_len = 3
        index = 0
        words_dict[vowel] = sorted(words_dict[vowel], key=len)
        for word in words_dict[vowel]:
            while current_len < len(word) < 20:
                current_len += 1
            index += 1
            for i in range(current_len, 21):
                lens[i - 3] = index
        words_dict[vowel] = [lens, words_dict[vowel]]

    with open("combo_dict_final.json", "w") as dict_file:
        json.dump(words_dict, dict_file)


def get_words():
    """Returns a list of all words the bot will use"""
    # Open all words files
    with open("../best_words.txt", "r") as words_file:
        words_dict = words_file.read().split("\n")

    with open("../words-2.txt", "r") as words_file:
        words_2 = words_file.read().split("\n")

    with open("../words-3.txt", "r") as words_file:
        words_3 = words_file.read().split("\n")

    # Add to the original word list the words from the other lists, without duplicates
    for word in words_2 + words_3:
        if word not in words_dict:
            words_dict.append(word)

    return list(set([word.strip() for word in words_dict]))


def load_words():
    """Load the indexed words into a dictionary"""
    with open("combo_dict_final.json", "r") as words_dict_file:
        words_dict = json.load(words_dict_file)

    return words_dict


def words_to_dict():
    """Make a dictionary (json file) with 2 and 3 letter combinations as keys and a list of words they appear
    in as values (in order to make word selecting be O(1))"""
    # INDEX ALL 2 LETTER COMBINATIONS FIRST
    words_dict = {}
    # Load the words
    words = get_words()  # load_words()
    # Generate list of all 2 letter combos
    two_letters = ["".join(i) for i in itertools.product(ascii_lowercase, repeat=2)]
    future_dicts = []
    # Index the words inside the combos
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for combo in two_letters:
            future_dicts.append(executor.submit(index_combo, combo, words))
            print(combo)

    # Add indexed items to dict
    for future_dict in concurrent.futures.as_completed(future_dicts):
        words_dict.update(future_dict.result())

    # Save the dictionary in a file
    with open("combo_dict.json", "w") as combo_file:
        json.dump(words_dict, combo_file, indent=4)

    # THEN USE THOSE INDEXED COMBINATIONS TO INDEX THE 3 LETTERS
    # Generate list of all 3 letter combos
    three_letters = ["".join(i) for i in itertools.product(ascii_lowercase, repeat=3)]
    future_dicts = []
    # Index the words inside the combos
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for combo in three_letters:
            # In order to reduce run time. "abc" will only appear in words which "bc" and "ab" appears in
            matching_words = words_dict[combo[:2]] + words_dict[combo[1:]]
            future_dicts.append(executor.submit(index_combo, combo, matching_words))
            print(combo)

    # Add indexed items to dict
    for future_dict in concurrent.futures.as_completed(future_dicts):
        words_dict.update(future_dict.result())

    update_word_dict(words_dict)


def update_word_dict(words_dict):
    """Saves the combo dictionary in a file"""
    with open("combo_dict_final.json", "w") as combo_file:
        json.dump(words_dict, combo_file, indent=4)


def index_combo(combo, words):
    """Get a combo and list of all words and return a dictionary with the combo as key and list of all words
    the combo appears in as a value"""
    # Sort the words by length, in order to make further indexing by length easier.
    words = sorted(words, key=len)
    return {combo: list(set([word for word in words if combo in word]))}
