import os
import random
import sys
import time
from typing import Tuple

import json
from string import ascii_lowercase

import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class JKLMBot:
    HOUR = 60 * 60 * 60

    def __init__(
        self,
        game_link: str,
        bot_name: str,
        think_time: Tuple[int, int],
        typing_speed: Tuple[int, int],
        mistake_chance: int,
        speedup: int,
        word_length: int = 0,
        is_long: bool = False,
        humanlike: bool = True,
        started_by_gui: bool = False,
    ):
        # Indexed combos and words
        self.words_dict = load_words()
        self.game_link = game_link
        self.bot_name = bot_name
        # 2 values representing a range of possible time the bot will think before answering
        self.think_time = think_time
        # 2 values representing a range of possible time between each letter the bot will type
        self.typing_speed = typing_speed
        # The upper or lower bound of word length the bot will use
        self.word_length = word_length
        # Whether the bound is lower (long - only use words above that length) or upper
        self.is_long = is_long
        # Chance of the bot making a typo each keystroke
        self.mistake_chance = mistake_chance
        # Decimal representing a speed increase as a % of current speed each correct guess
        self.speedup = speedup
        # Whether the bot is humanlike or an obvious bot
        self.humanlike = humanlike
        # Correct guesses we've made
        self.guesses = 0
        # Create a new "invisible" (headless) chrome browser
        options = Options()
        if started_by_gui:
            options.add_argument("--headless")
        self.browser = webdriver.Chrome(
            executable_path=resource_path(r"project\chromedriver.exe"),
            chrome_options=options,
        )

    def main(self):
        self.enter_room()
        self.join_game(first=True)
        try:
            self.play()
        # The bot was kicked
        except (
            selenium.common.exceptions.StaleElementReferenceException,
            selenium.common.exceptions.InvalidSessionIdException,
        ):
            pass

    def play(self):
        """The bot's logic while playing a match"""
        # Wait until game start
        ongoing_round_element = WebDriverWait(self.browser, self.HOUR).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "round"))
        )
        while not ongoing_round_element.is_displayed():
            time.sleep(1)

        # The box to enter the guesses in
        enter_box = WebDriverWait(self.browser, self.HOUR).until(
            EC.visibility_of_element_located(
                (By.XPATH, "/html/body/div[2]/div[3]/div[2]/div[2]/form/input")
            )
        )

        # The letters the game wants
        combo_element = WebDriverWait(self.browser, self.HOUR).until(
            EC.visibility_of_element_located(
                (By.XPATH, "/html/body/div[2]/div[2]/div[2]/div[2]/div")
            )
        )

        # Variables to help the bot make less mistakes
        last_combo = ""
        last_guess_time = time.time()

        # While game is running
        while ongoing_round_element.is_displayed():
            # It is our turn
            if enter_box.is_displayed():
                # Make it so the bot appears to think
                if self.humanlike:
                    time.sleep(
                        max(
                            0.0,
                            random.randint(
                                self.think_time[0] * 100, self.think_time[1] * 100
                            )
                            / 100
                            - self.guesses * self.think_time[0] * self.speedup,
                        )
                    )

                # Get the wanted letters
                combo = combo_element.text.lower()

                # Make sure the bot isn't entering several values very fast, and also have it reguess if the guess was incorrect
                if enter_box.is_displayed() and (
                    combo != last_combo or time.time() - last_guess_time > 0.2
                ):
                    chosen_word = self.word_from_combo(combo)
                    last_combo = combo
                    valid_words = self.words_dict[combo][1]
                    # In order to not reuse words
                    try:
                        valid_words.remove(chosen_word)
                        self.words_dict[combo][1] = valid_words
                    except ValueError:
                        pass
                    # Send the answer to the game
                    self.enter_answer(chosen_word, enter_box)
                    last_guess_time = time.time()
                    self.guesses += 1

            # Not our turn
            else:
                last_combo = ""

        # Game ended, join the next one
        self.join_game()

        # Play again
        self.play()

    def word_from_combo(self, combo):
        """Gets a combo and returns a semi random word from it"""
        len_indices, valid_words = self.words_dict[combo]
        # In case there is a preference to a certain word length
        if self.word_length != 0:
            valid_words = (
                valid_words[len_indices[self.word_length - 3]:]
                if self.is_long
                else valid_words[: len_indices[self.word_length - 3]]
            )

        # No word available for this combo
        if not valid_words:
            return "No idea :("

        chosen_word = random.choice(valid_words)

        return chosen_word

    def enter_room(self):
        """Enters a room with a given link and inputs the nickname"""
        # Enter the room
        self.browser.get(self.game_link)

        # Get the element when it's clickable
        name_element = WebDriverWait(self.browser, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@placeholder]"))
        )

        # Delete the original text
        webdriver.ActionChains(self.browser).double_click(name_element).perform()
        # Enter the bot's name
        name_element.send_keys(self.bot_name)
        # Send the input
        name_element.submit()

    def stop(self):
        """Kill the bot"""
        self.browser.close()

    def join_game(self, first: bool = False):
        """Joins a game in the room the bot is in"""
        # Switch to button's frame
        if first:
            if "bot" in self.bot_name:
                # Open chat
                open_chat_path = "/html/body/div[1]/button"
                open_chat_element = WebDriverWait(self.browser, 5).until(
                    EC.element_to_be_clickable((By.XPATH, open_chat_path))
                )
                open_chat_element.click()

                # Send a msg shouting out this bot
                chat_path = "/html/body/div[2]/div[4]/div[2]/div[2]/div[2]/textarea"
                chat = WebDriverWait(self.browser, 3).until(
                    EC.element_to_be_clickable((By.XPATH, chat_path))
                )

                bot_link = "https://tinyurl.com/bomb-party-bot"
                enter_text = (
                    f"Hello! I am a bot made by hadar759\nYou can download me over at "
                    f"{bot_link} and run more bots like me :D\nHave fun and enjoy this bot!"
                )
                chat.send_keys(enter_text)
                chat.send_keys(Keys.ENTER)

            # Switch to the join button's frame if it's our first time joining
            wanted_path = "/html/body/div[2]/div[4]/div[1]/iframe"
            frame = WebDriverWait(self.browser, self.HOUR).until(
                EC.presence_of_element_located((By.XPATH, wanted_path))
            )
            # Wait until frame appears
            self.browser.switch_to.frame(frame)

        # Join the game
        wanted_path = "/html/body/div[2]/div[3]/div[1]/div[1]/button"
        join_button = WebDriverWait(self.browser, self.HOUR).until(
            EC.element_to_be_clickable((By.XPATH, wanted_path))
        )

        join_button.click()

    def enter_answer(self, answer: str, enter_field):
        """Enters the given answer into the answer bar"""
        # To give the illusion of typing
        if self.humanlike:
            for i in range(len(answer)):
                letter = answer[i]
                # Enter a single letter
                self.enter_keys(enter_field, letter)

                # Generate a random time between letters
                wait_time = max(
                    0.05,
                    random.randint(5, 35) / 100
                    - self.guesses * self.typing_speed[0] * self.speedup,
                )
                mistakes = 0
                mistake = random.random() < self.mistake_chance
                # Make an error a decent percent of the time
                if mistake:
                    mistake_offset = self.get_mistake_offset(answer, i)
                    # Make the error
                    self.enter_keys(enter_field, answer[mistake_offset])
                    mistakes += 1
                    time.sleep(wait_time)

                    mistake = random.random() < min(self.mistake_chance - 0.1, 0.01)
                    # Random chance of entering more characters
                    if mistake:
                        mistake_offset = self.get_mistake_offset(answer, mistake_offset)
                        self.enter_keys(enter_field, answer[mistake_offset])
                        mistakes += 1
                        time.sleep(wait_time)

                    # Wait a bit
                    time.sleep(wait_time * 2)

                    # Delete the mistakes
                    [
                        self.enter_keys(enter_field, Keys.BACKSPACE)
                        for _ in range(mistakes)
                    ]

                # Type letters in a speed of between 0.5 to 0.35 secs per letter
                time.sleep(wait_time)

        # If it's an obvious bot just instantly enter the answer
        else:
            self.enter_keys(enter_field, answer)

        # Press enter to send the answer
        self.enter_keys(enter_field, Keys.ENTER)

    def enter_keys(self, enter_field, keys):
        """Enter keys to an element if it's possible"""
        if enter_field.is_displayed():
            enter_field.send_keys(keys)

    @staticmethod
    def get_mistake_offset(word, index):
        """Returns an index of a letter in the given word which will be typed as a typo"""
        if index + 2 < len(word):
            return index + 2
        if index - 1 > 0:
            return index - 1
        else:
            return random.randint(0, len(word) - 1)


def load_words():
    """Load the indexed words into a dictionary"""
    with open(resource_path(r"project\combo_dict_final.json"), "r") as words_dict_file:
        words_dict = json.load(words_dict_file)

    return words_dict


def resource_path(relative_path):
    """Get the absolute path to the resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
