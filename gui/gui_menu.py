import functools
import threading
import tkinter as tk
from tkinter import ttk
import tkinter.font as tk_font
import getpass

from project import *
from .popup import Mbox
from .int_entry import IntEntry


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self.master)
        self.canvas = canvas
        scrollbar = ttk.Scrollbar(self.master, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _on_mouse_wheel(self, event):
        self.canvas.yview_scroll(-1 * int((event.delta / 120)), "units")


class Menu:
    """A simple gui for the bot made in tkinter"""

    SLOW_PRESET = {
        "min_think_time": 100,
        "max_think_time": 400,
        "min_typing_speed": 20,
        "max_typing_speed": 60,
        "word_length": 7,
        "is_long": False,
        "mistake_percent": 12,
        "speedup": 0,
        "human": True,
    }
    FAST_PRESET = {
        "min_think_time": 100,
        "max_think_time": 250,
        "min_typing_speed": 40,
        "max_typing_speed": 80,
        "word_length": 7,
        "is_long": False,
        "mistake_percent": 5,
        "speedup": 3,
        "human": True,
    }

    BOT_PRESET = {
        "min_think_time": 0,
        "max_think_time": 0,
        "min_typing_speed": 999,
        "max_typing_speed": 999,
        "word_length": 0,
        "is_long": False,
        "mistake_percent": 0,
        "speedup": 0,
        "human": False,
    }

    def __init__(self):
        self.root = tk.Tk()
        self.frame = None
        height = self.root.winfo_screenheight()
        self.root.geometry(f"800x{height - 150}")
        self.root.resizable(False, True)
        self.root.title("hadar759's bomb party bot")
        self.instant_typing = False
        self.bot_settings = {}
        self.widgets = {}
        self.human = False
        self.join_button = None
        self.is_long = False
        self.check = None
        self.num_of_bots = 0

    def main(self):
        """Run the menu"""
        self.create_screen()
        self.run()

    def create_screen(self):
        """Creates the menu screen with all elements on it"""
        title_font = tk_font.Font(
            family="Geneva", size=40, weight="bold", underline=True
        )
        label_font = tk_font.Font(family="Geneva", size=25)
        entry_font = label_font

        title = tk.Label(text="hadar759's bomb party bot", font=title_font)
        title.pack(pady=10)

        self.frame = ScrollableFrame(self.root)

        # Create the label and input for the game link
        self.widgets["game_code"] = self.create_label_and_entry(
            "Game Code: ",
            label_font,
            entry_font,
            5,
            25,
            tk.LEFT,
            "The last 4 letters in the game link.",
        )

        # Create the label and input for the bot name
        self.widgets["bot_name"] = self.create_label_and_entry(
            "Bot name: ", label_font, entry_font, 5, 25, tk.LEFT, "The name of the bot."
        )

        frame = tk.Frame(self.frame.scrollable_frame)

        label = tk.Label(master=frame, text="Presets: ", font=label_font)
        label.pack(side=tk.LEFT, anchor=tk.NW)

        slow_human = functools.partial(self.change_preset, preset=self.SLOW_PRESET)
        fast_human = functools.partial(self.change_preset, preset=self.FAST_PRESET)
        bot_mode = functools.partial(self.change_preset, preset=self.BOT_PRESET)

        button = tk.Button(
            master=frame,
            text="Human (slow)",
            font=(entry_font.name, 18),
            command=slow_human,
        )
        button.pack(side=tk.LEFT, anchor=tk.NW)
        button = tk.Button(
            master=frame,
            text="Human (fast)",
            font=(entry_font.name, 18),
            command=fast_human,
        )
        button.pack(side=tk.LEFT, anchor=tk.NW)
        button = tk.Button(
            master=frame, text="Bot", font=(entry_font.name, 18), command=bot_mode
        )
        button.pack(side=tk.LEFT, anchor=tk.NW)

        info_button = tk.Button(
            master=frame,
            text="🛈",
            font=(label_font.name, 18),
            command=lambda: Mbox(
                "Bot settings presets.\n"
                "Human (slow) - Make it appear like a very slow human player.\n"
                "Human (fast) - Make it appear like a fast human player.\n"
                "Bot - Make it play like an obvious bot, answering immediately."
            ),
            width=2,
            height=1,
            fg="dodger blue",
        )
        info_button.pack(side=tk.LEFT, anchor=tk.NW, padx=10)

        frame.pack(side=tk.TOP, anchor=tk.NW, padx=5, pady=15)

        frame = tk.Frame(self.frame.scrollable_frame)

        label = tk.Label(master=frame, text="Bot Settings:", font=(title_font.name, 30))
        label.pack(side=tk.TOP, padx=200)

        frame.pack(side=tk.TOP, pady=10, anchor=tk.NW)

        self.create_range(
            "Typing Speed (in cpm): ",
            label_font,
            entry_font,
            "min_typing_speed",
            "max_typing_speed",
            5,
            25,
            "The minimum and maximum typing speed of the bot.\nMeasured in characters per minute.",
        )

        self.create_range(
            "Think time (in ms): ",
            label_font,
            entry_font,
            "min_think_time",
            "max_think_time",
            5,
            25,
            'The minimum and maximum time the bot will "think" before answering.\nMeasured in milliseconds',
        )

        entry = self.bot_settings["word_length"] = self.create_label_and_entry(
            "Only words below len: ",
            label_font,
            entry_font,
            5,
            25,
            tk.LEFT,
            "The longest length of words the bot will use.\n"
            'Check "only above len" to make it the shortest length it will use instead.',
            percent=True,
            words=True,
        )
        checkbutton = tk.Checkbutton(
            master=entry.master,
            font=entry_font,
            text="Only above len",
            command=lambda: self.change_long(),
        )
        checkbutton.pack(padx=10)

        self.bot_settings["mistake_percent"] = self.create_label_and_entry(
            "Mistake Likelihood (%)",
            label_font,
            entry_font,
            5,
            25,
            tk.LEFT,
            "The likelihood of making a mistake each keystroke the bot makes.",
            percent=True,
        )

        self.bot_settings["speedup"] = self.create_label_and_entry(
            "Speedup (% of current speed)",
            label_font,
            entry_font,
            5,
            10,
            tk.LEFT,
            "The speed increase as a percent of starting speed. Will speed up each successful guess the bot makes.\n"
            "Will look more natural at values below 5.",
            percent=True,
        )

        frame = tk.Frame(self.frame.scrollable_frame)

        button = tk.Button(
            master=frame,
            text="JOIN",
            bg="lime green",
            font=(entry_font.name, 30),
            command=self.join_game,
            width=self.frame.winfo_width() + 31,
        )
        button.pack(side=tk.TOP, fill="both")
        self.join_button = button

        frame.pack(fill="both", side=tk.TOP, padx=15, pady=20, anchor=tk.NW)

        self.frame.pack()

    def change_long(self):
        self.is_long = not self.is_long

    def join_game(self):
        """Try to instantiate a requested bot and start it"""
        bot_args = {}
        all_inputs = {}
        all_inputs.update(self.bot_settings)
        all_inputs.update(self.widgets)

        for widget_name in all_inputs:
            widget = all_inputs[widget_name]
            if widget["state"] == "disabled":
                bot_args[widget_name] = "0"
            elif widget.get() == "":
                Mbox("Fields cannot be empty")
                return
            else:
                bot_args[widget_name] = all_inputs[widget_name].get()

        for arg_name in bot_args:
            arg = bot_args[arg_name]
            if arg.isdigit():
                bot_args[arg_name] = int(arg) / (60 if "typing" in arg_name else 100)
                if arg_name == "word_length":
                    bot_args[arg_name] *= 100
                    if 0 < bot_args[arg_name] < 3:
                        bot_args[arg_name] = 3
            elif arg_name == "bot_name":
                bot_args[arg_name] = self.create_bot_name(arg)

        # Performance reasons
        if self.num_of_bots > 5:
            Mbox("Can't have more than 5 bots running")
            return

        # Start the bot
        bot = JKLMBot(
            game_link=f"https://jklm.fun/{bot_args['game_code']}",
            bot_name=bot_args["bot_name"],
            think_time=(bot_args["min_think_time"], bot_args["max_think_time"]),
            typing_speed=(bot_args["min_typing_speed"], bot_args["max_typing_speed"]),
            word_length=round(bot_args["word_length"]),
            is_long=self.is_long,
            mistake_chance=bot_args["mistake_percent"],
            speedup=bot_args["speedup"],
            humanlike=self.human,
            started_by_gui=True,
        )
        threading.Thread(target=bot.main).start()
        self.num_of_bots += 1

        self.join_button["state"] = "disabled"

        self.create_game_running_window(bot)

    def create_game_running_window(self, running_bot):
        """A simple window to terminate the bot"""
        window = tk.Toplevel(self.root)
        window.geometry("300x300")
        window.title(f"running {running_bot.bot_name}")

        title_font = tk_font.Font(
            family="Geneva", size=25, weight="bold", underline=True
        )
        label_font = tk_font.Font(family="Geneva", size=30)
        entry_font = label_font

        title = tk.Label(window, text="BOT IS RUNNING", font=title_font)
        title.pack(pady=10)

        kill_button = tk.Button(
            master=window,
            text=f"KILL {running_bot.bot_name.upper()}",
            bg="red",
            font=(entry_font.name, 20),
            command=lambda: self.kill_bot(window, running_bot),
            width=window.winfo_screenwidth(),
            height=30,
        )
        kill_button.pack(fill="x")

        window.protocol("WM_DELETE_WINDOW", lambda: self.kill_bot(window, running_bot))

        self.join_button["state"] = "normal"

    def kill_bot(self, window, running_bot):
        """Terminate the bot and close all associated windows"""
        window.destroy()
        running_bot.stop()
        self.num_of_bots -= 1
        self.join_button["state"] = "normal"

    @staticmethod
    def create_bot_name(name):
        """Add 'bot' to the end of every bot name, to prevent malicious use"""
        if "bot" in name or getpass.getuser() == "hadar":
            return name
        else:
            return f"{name} bot"

    def change_preset(self, preset: dict):
        """Switch to a given preset"""
        bot = not preset["human"]
        self.human = not bot

        for widget in self.bot_settings:
            # Enable the entry then enter values
            if not bot:
                self.bot_settings[widget]["state"] = "normal"
            self.bot_settings[widget].delete(0, tk.END)
            self.bot_settings[widget].insert(0, preset[widget])
            # Enter values then disable the entry
            if bot:
                if widget != "word_length":
                    self.bot_settings[widget]["state"] = "disabled"

    def create_range(
        self,
        text: str,
        label_font,
        entry_font,
        first_entry: str,
        second_entry: str,
        padx: int,
        pady: int,
        info_text: str = "",
    ):
        """Creates a label and 2 int entries with a '-' in between, representing a range of numbers"""
        frame = tk.Frame(self.frame.scrollable_frame)

        label = tk.Label(master=frame, text=text, font=label_font)
        label.pack(side=tk.LEFT, anchor=tk.NW)

        entry = IntEntry(master=frame, font=entry_font, width=3)
        entry.pack(side=tk.LEFT, anchor=tk.NW, padx=20)
        self.bot_settings[first_entry] = entry

        label = tk.Label(master=frame, text="-", font=label_font)
        label.pack(side=tk.LEFT, anchor=tk.NW)

        entry = IntEntry(master=frame, font=entry_font, width=3)
        entry.pack(side=tk.LEFT, anchor=tk.NW, padx=20)
        self.bot_settings[second_entry] = entry

        if info_text:
            info_button = tk.Button(
                master=frame,
                text="🛈",
                font=(label_font.name, 18),
                command=lambda: Mbox(info_text),
                width=2,
                height=1,
                fg="dodger blue",
            )
            info_button.pack(side=tk.LEFT, anchor=tk.NW)

        frame.pack(side=tk.TOP, anchor=tk.NW, padx=padx, pady=pady)

    def create_label_and_entry(
        self,
        text: str,
        label_font: tk_font.Font,
        entry_font: tk_font.Font,
        padx: int = 0,
        pady: int = 0,
        side=tk.LEFT,
        info_text="",
        percent: bool = False,
        words: bool = False,
    ):
        """Creates a label and an entry field next to it on the screen"""
        frame = tk.Frame(self.frame.scrollable_frame)

        label = tk.Label(master=frame, text=text, font=label_font)
        label.pack(side=side, anchor=tk.NW, padx=10)

        entry_type = IntEntry if percent else tk.Entry

        entry = entry_type(master=frame, font=entry_font)
        if percent:
            entry.configure(width=3)
            entry.max_num = 100
        if words:
            entry.configure(width=3)
            entry.max_num = 19
        entry.pack(side=side, anchor=tk.NW, padx=10)

        if info_text:
            info_button = tk.Button(
                master=frame,
                text="🛈",
                font=(label_font.name, 18),
                command=lambda: Mbox(info_text),
                width=2,
                height=1,
                fg="dodger blue",
            )
            info_button.pack(side=side, anchor=tk.NW)

        frame.pack(side=tk.TOP, pady=pady, anchor=tk.NW)

        return entry

    def run(self):
        """Commands used after creating the menu screen"""
        self.root.mainloop()


def main():
    """Create and run a new menu"""
    menu = Menu()
    menu.main()


if __name__ == "__main__":
    main()
