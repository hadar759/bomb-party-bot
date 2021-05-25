import tkinter as tk
from math import log


class IntEntry(tk.Entry):
    def __init__(self, master=None, max_num: int = 999, **kwargs):
        self.var = tk.StringVar()
        tk.Entry.__init__(self, master, textvariable=self.var, **kwargs)
        self.old_value = ""
        self.max_num = max_num
        self.var.trace("w", self.check)
        self.get, self.set = self.var.get, self.var.set

    def check(self, *args):
        # Make it so we're able to delete and restrict only up to 999
        if not self.get() or self.get().isdigit() and int(self.get()) <= self.max_num:
            # the current value is only digits; allow this
            self.old_value = self.get()
        else:
            # there's non-digit characters in the input; reject this
            self.set(self.old_value)
