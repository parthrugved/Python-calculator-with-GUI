import tkinter as tk
from tkinter import messagebox
import math


class CalculatorApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Simple Calculator")
        self.geometry("360x640")
        self.resizable(True ,True)

        # Theme colors
        self.color_background = "#0f172a"  # slate-900
        self.color_surface = "#111827"     # gray-900
        self.color_button = "#1f2937"      # gray-800
        self.color_button_text = "#e5e7eb" # gray-200
        self.color_accent = "#10b981"      # emerald-500
        self.color_warning = "#ef4444"     # red-500
        self.color_text = "#f9fafb"        # gray-50

        self.configure(bg=self.color_background)

        self.current_expression = tk.StringVar(value="")

        self._build_header()
        self._build_display()
        self._build_keypad()
        self._build_history()
        self._bind_keyboard()

    def _build_header(self):
        header = tk.Label(
            self,
            text="Calculator",
            font=("Segoe UI", 16, "bold"),
            bg=self.color_background,
            fg=self.color_text,
            pady=10,
        )
        header.pack(fill=tk.X)

    def _build_display(self):
        container = tk.Frame(self, bg=self.color_background)
        container.pack(fill=tk.X, padx=16, pady=(4, 10))

        entry = tk.Entry(
            container,
            textvariable=self.current_expression,
            font=("Consolas", 20),
            relief=tk.FLAT,
            bg=self.color_surface,
            fg=self.color_text,
            insertbackground=self.color_text,
            justify=tk.RIGHT,
        )
        entry.pack(fill=tk.X, ipady=14)

    def _build_keypad(self):
        keypad = tk.Frame(self, bg=self.color_background)
        keypad.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        def make_btn(parent, text, command=None, bg=None, fg=None):
            button = tk.Button(
                parent,
                text=text,
                command=command,
                font=("Segoe UI", 12, "bold"),
                bg=bg or self.color_button,
                fg=fg or self.color_button_text,
                activebackground=self.color_surface,
                activeforeground=self.color_text,
                relief=tk.FLAT,
                bd=0,
                padx=8,
                pady=8,
                cursor="hand2",
            )
            return button

        grid = tk.Frame(keypad, bg=self.color_background)
        grid.pack(expand=True)

        buttons_layout = [
            ["sum", "prod", "avg", ","],
            ["sin", "cos", "tan", "√"],
            ["log", "ln", "^", "DEL"],
            ["(", ")", "π", "C"],
            ["7", "8", "9", "÷"],
            ["4", "5", "6", "×"],
            ["1", "2", "3", "-"],
            ["0", ".", "=", "+"],
        ]

        for row_index, row in enumerate(buttons_layout):
            for col_index, label in enumerate(row):
                if label == "0" and row_index == 6:
                    btn = make_btn(
                        grid,
                        label,
                        command=lambda l=label: self._on_press(l),
                    )
                    btn.grid(row=row_index, column=0, columnspan=2, sticky="nsew", padx=6, pady=6)
                    # Add a placeholder so the next item starts at column 2
                    placeholder = tk.Frame(grid, width=0, height=0, bg=self.color_background)
                    placeholder.grid(row=row_index, column=1)
                    continue

                accent_labels = {"=", "+", "-", "×", "÷"}
                if label in accent_labels:
                    btn = make_btn(
                        grid,
                        label,
                        command=lambda l=label: self._on_press(l),
                        bg=self.color_accent,
                        fg="#062e22",
                    )
                elif label in {"C", "DEL"}:
                    btn = make_btn(
                        grid,
                        label,
                        command=lambda l=label: self._on_press(l),
                        bg=self.color_button,
                        fg=self.color_warning,
                    )
                else:
                    btn = make_btn(grid, label, command=lambda l=label: self._on_press(l))

                btn.grid(row=row_index, column=col_index, sticky="nsew", padx=6, pady=6)

        # Configure grid weights for responsive sizing
        for r in range(len(buttons_layout)):
            grid.rowconfigure(r, weight=1)
        for c in range(4):
            grid.columnconfigure(c, weight=1)

    def _on_press(self, label):
        if label == "C":
            self.current_expression.set("")
            return

        if label == "DEL":
            self.current_expression.set(self.current_expression.get()[:-1])
            return

        if label == "=":
            self._calculate_result()
            return

        # Map pretty symbols, functions, and constants
        if label == "√":
            insert = "sqrt("
        elif label == "ln":
            insert = "log("
        elif label == "^":
            insert = "^"
        elif label == "π":
            insert = "pi"
        elif label == "sum":
            insert = "sum("
        elif label == "prod":
            insert = "prod("
        elif label == "avg":
            insert = "avg("
        elif label in {"sin", "cos", "tan", "log"}:
            insert = f"{label}("
        elif label in {"(", ")", ","}:
            insert = label
        else:
            symbol_map = {"×": "*", "÷": "/"}
            insert = symbol_map.get(label, label)

        self.current_expression.set(self.current_expression.get() + insert)

    def _calculate_result(self):
        expression = self.current_expression.get().strip()
        if not expression:
            return
        try:
            # Replace caret with exponent operator for Python
            expression_eval = expression.replace("^", "**")

            # Allowed names for safe eval
            allowed_names = {
                "pi": math.pi,
                "e": math.e,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "sqrt": math.sqrt,
                "log": math.log,
                "abs": abs,
                "round": round,
                # Variadic helpers for multi-number ops
                "sum": lambda *args: sum(args),
                "prod": getattr(math, "prod", None) or (lambda *args: __import__("functools").reduce(lambda a,b: a*b, args, 1)),
                "avg": lambda *args: (sum(args) / len(args)) if args else 0,
            }

            # Enforce a maximum of 30 numeric literals in the expression
            import re
            numbers = re.findall(r"(?<![a-zA-Z_])\d+(?:\.\d+)?", expression_eval)
            if len(numbers) > 30:
                raise ValueError("Too many numbers (max 30)")

            result = eval(expression_eval, {"__builtins__": {}}, allowed_names)
            self.current_expression.set(str(result))
            self._push_history(expression, result)
        except ZeroDivisionError:
            messagebox.showerror("Error", "Division by zero is not allowed.")
        except Exception as ex:
            messagebox.showerror("Error", str(ex) if str(ex) else "Invalid expression.")

    def _bind_keyboard(self):
        # General key handler
        self.bind("<Key>", self._on_key)
        # Enter keys for equals
        self.bind("<Return>", lambda e: (self._on_press("="), "break"))
        self.bind("<KP_Enter>", lambda e: (self._on_press("="), "break"))
        # Backspace deletes last char
        self.bind("<BackSpace>", lambda e: (self._on_press("DEL"), "break"))
        # Escape clears all
        self.bind("<Escape>", lambda e: (self._on_press("C"), "break"))
        # Caret for power
        self.bind("^", lambda e: (self._on_press("^"), "break"))

    def _on_key(self, event):
        # Accept digits and common operators from keyboard
        char = event.char
        if char:
            if char in "0123456789.+-*/()^,":
                self._on_press(char)
                return "break"
            # Map x or X to multiply
            if char in {"x", "X"}:
                self._on_press("*")
                return "break"
            # Allow letters for typing function names
            if char.isalpha():
                self._on_press(char)
                return "break"
        # Some keyboards may send keysym for operators without char
        if event.keysym in {"plus", "minus", "slash", "asterisk", "parenleft", "parenright", "period"}:
            mapping = {
                "plus": "+",
                "minus": "-",
                "slash": "/",
                "asterisk": "*",
                "parenleft": "(",
                "parenright": ")",
                "period": ".",
            }
            self._on_press(mapping[event.keysym])
            return "break"

    def _build_history(self):
        # History panel
        container = tk.Frame(self, bg=self.color_background)
        container.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 12))

        header = tk.Label(
            container,
            text="History",
            font=("Segoe UI", 12, "bold"),
            bg=self.color_background,
            fg=self.color_text,
        )
        header.pack(anchor="w", pady=(0, 6))

        list_frame = tk.Frame(container, bg=self.color_background)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.history_list = tk.Listbox(
            list_frame,
            bg=self.color_surface,
            fg=self.color_text,
            selectbackground=self.color_accent,
            selectforeground="#062e22",
            highlightthickness=0,
            activestyle="none",
            font=("Consolas", 11),
        )
        self.history_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame, command=self.history_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_list.config(yscrollcommand=scrollbar.set)

        buttons = tk.Frame(container, bg=self.color_background)
        buttons.pack(fill=tk.X, pady=(8, 0))

        clear_btn = tk.Button(
            buttons,
            text="Clear History",
            command=self._clear_history,
            font=("Segoe UI", 10, "bold"),
            bg=self.color_button,
            fg=self.color_warning,
            relief=tk.FLAT,
            bd=0,
            padx=8,
            pady=6,
            cursor="hand2",
        )
        clear_btn.pack(side=tk.LEFT)

        reuse_btn = tk.Button(
            buttons,
            text="Use Item",
            command=self._reuse_selected,
            font=("Segoe UI", 10, "bold"),
            bg=self.color_accent,
            fg="#062e22",
            relief=tk.FLAT,
            bd=0,
            padx=8,
            pady=6,
            cursor="hand2",
        )
        reuse_btn.pack(side=tk.RIGHT)

        self.history_list.bind("<Double-Button-1>", lambda e: self._reuse_selected())

    def _push_history(self, expression, result):
        if hasattr(self, "history_list"):
            self.history_list.insert(tk.END, f"{expression} = {result}")
            self.history_list.see(tk.END)

    def _clear_history(self):
        if hasattr(self, "history_list"):
            self.history_list.delete(0, tk.END)

    def _reuse_selected(self):
        if not hasattr(self, "history_list"):
            return
        selection = self.history_list.curselection()
        if not selection:
            return
        item = self.history_list.get(selection[0])
        if " = " in item:
            expr = item.split(" = ", 1)[0]
            self.current_expression.set(expr)


def main():
    app = CalculatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()



