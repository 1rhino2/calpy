import tkinter as tk
from tkinter import font
import re
import math

from config import BG_COLOR, DISPLAY_BG_COLOR, TEXT_COLOR, OPERATOR_BG_COLOR, OPERATOR_PRESS_COLOR, BTN_BG_COLOR, BTN_PRESS_COLOR, EQUALS_BG_COLOR, EQUALS_PRESS_COLOR, FONT_STYLE


class ScientificCalculator:
    """
    An advanced scientific calculator with an improved layout, standard and
    scientific functions, and a '2nd' key for alternate operations.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Scientific Calculator")
        self.root.geometry("400x600") # Adjusted for a 7x5 layout
        self.root.configure(bg=BG_COLOR)
        self.root.minsize(400, 600)

        # State variables
        self.expression = ""
        self.is_inv = False # Tracks if the '2nd' function is active
        self.buttons = {}   # To store button widgets for text toggling

        # Configure custom fonts
        self.display_font = font.Font(family=FONT_STYLE, size=40, weight="bold")
        self.button_font = font.Font(family=FONT_STYLE, size=16)

        # Create UI elements
        self.display_frame = self.create_display_frame()
        self.display_label = self.create_display_label()
        self.buttons_frame = self.create_buttons_frame()
        self.create_buttons()
        
        # Bind keyboard events
        self.root.bind("<Key>", self.key_press)

    def create_display_frame(self):
        """Creates the frame for the calculator display."""
        frame = tk.Frame(self.root, bg=DISPLAY_BG_COLOR, height=120)
        frame.pack(expand=True, fill="both")
        return frame

    def create_display_label(self):
        """Creates the label that shows the expression."""
        label = tk.Label(
            self.display_frame, text="0", anchor=tk.E, bg=DISPLAY_BG_COLOR,
            fg=TEXT_COLOR, padx=24, font=self.display_font
        )
        label.pack(expand=True, fill="both")
        return label

    def create_buttons_frame(self):
        """Creates the frame to hold all buttons."""
        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack(expand=True, fill="both", pady=1)
        return frame

    def create_buttons(self):
        """Creates and lays out all calculator buttons in a 7x5 grid."""
        for i in range(7):  # 7 rows
            self.buttons_frame.rowconfigure(i, weight=1)
        for i in range(5):  # 5 columns
            self.buttons_frame.columnconfigure(i, weight=1)

        # (text, row, col, type)
        button_layout = [
            ('2ⁿᵈ', 0, 0, 'sci'), ('π', 0, 1, 'sci'), ('e', 0, 2, 'sci'), ('C', 0, 3, 'op'), ('⌫', 0, 4, 'op'),
            ('x²', 1, 0, 'sci'), ('1/x', 1, 1, 'sci'), ('|x|', 1, 2, 'sci'), ('exp', 1, 3, 'sci'), ('mod', 1, 4, 'op'),
            ('√', 2, 0, 'sci'), ('(', 2, 1, 'op'), (')', 2, 2, 'op'), ('n!', 2, 3, 'sci'), ('/', 2, 4, 'op'),
            ('xʸ', 3, 0, 'sci'), ('7', 3, 1, 'num'), ('8', 3, 2, 'num'), ('9', 3, 3, 'num'), ('*', 3, 4, 'op'),
            ('10ˣ', 4, 0, 'sci'), ('4', 4, 1, 'num'), ('5', 4, 2, 'num'), ('6', 4, 3, 'num'), ('-', 4, 4, 'op'),
            ('log', 5, 0, 'sci'), ('1', 5, 1, 'num'), ('2', 5, 2, 'num'), ('3', 5, 3, 'num'), ('+', 5, 4, 'op'),
            ('ln', 6, 0, 'sci'), ('+/-', 6, 1, 'num'), ('0', 6, 2, 'num'), ('.', 6, 3, 'num'), ('=', 6, 4, 'equals')
        ]

        for item in button_layout:
            text, row, col, btn_type = item
            
            bg_color, press_color = self.get_colors(btn_type)
            command = self.get_command(text)

            button = tk.Button(
                self.buttons_frame, text=text, bg=bg_color, fg=TEXT_COLOR,
                font=self.button_font, relief=tk.FLAT, borderwidth=0,
            )
            button.grid(row=row, column=col, sticky=tk.NSEW, padx=1, pady=1)
            
            # Store button if it's a toggleable scientific function
            if text in ('x²', '√', 'xʸ', '10ˣ', 'log', 'ln'):
                self.buttons[text] = button

            button.bind("<Button-1>", lambda e, btn=button, pc=press_color: self.on_press(btn, pc))
            button.bind("<ButtonRelease-1>", lambda e, btn=button, bg=bg_color, cmd=command: self.on_release(btn, bg, cmd))

    def get_colors(self, btn_type):
        """Returns the appropriate colors for a button type."""
        if btn_type == 'equals': return EQUALS_BG_COLOR, EQUALS_PRESS_COLOR
        if btn_type == 'op' or btn_type == 'sci': return OPERATOR_BG_COLOR, OPERATOR_PRESS_COLOR
        return BTN_BG_COLOR, BTN_PRESS_COLOR

    def get_command(self, text):
        """Returns the appropriate command for a given button text."""
        if text == '2nd': return self.toggle_second_functions
        if text == '=': return self.evaluate_expression
        if text == 'C': return self.clear_expression
        if text == '⌫': return self.delete_last_char
        if text == '+/-': return self.toggle_sign
        
        # Scientific functions that are built to be valid python expressions
        if text == '|x|': return lambda: self.add_to_expression('abs(')
        if text == '1/x': return lambda: self.add_to_expression('1/')
        if text == 'exp': return lambda: self.add_to_expression('math.exp(')
        if text == 'n!': return lambda: self.add_to_expression('!')
        if text == 'xʸ': 
            return lambda: self.add_to_expression('**(1/' if self.is_inv else '**')
        if text == '√': 
            return lambda: self.add_to_expression('**(1/3)' if self.is_inv else 'math.sqrt(')
        if text == 'x²': 
            return lambda: self.add_to_expression('**3' if self.is_inv else '**2')
        if text == '10ˣ': 
            return lambda: self.add_to_expression('2**' if self.is_inv else '10**')
        if text == 'log': 
            return lambda: self.add_to_expression('math.log2(' if self.is_inv else 'math.log10(')
        if text == 'ln': 
            return lambda: self.add_to_expression('math.exp(' if self.is_inv else 'math.log(')

        # Constants
        if text == 'π': return lambda: self.add_to_expression('math.pi')
        if text == 'e': return lambda: self.add_to_expression('math.e')

        # Default action for numbers and simple operators
        return lambda t=text: self.add_to_expression(t)

    def toggle_second_functions(self):
        """Toggles the text and function of scientific buttons."""
        self.is_inv = not self.is_inv
        
        # Normal and inverse function labels
        labels = {
            'x²': ('x²', 'x³'), 
            '√': ('√', '³√'), 
            'xʸ': ('xʸ', 'ʸ√x'),
            '10ˣ': ('10ˣ', '2ˣ'), 
            'log': ('log', 'log₂'), 
            'ln': ('ln', 'eˣ')
        }
        
        for base_text, (normal, inverse) in labels.items():
            button = self.buttons.get(base_text)
            if button:
                button.config(text=inverse if self.is_inv else normal)

    def on_press(self, button, press_color):
        button.config(bg=press_color)

    def on_release(self, button, original_color, command):
        button.config(bg=original_color)
        if command: command()

    def key_press(self, event):
        """Handles keyboard input."""
        key = event.keysym
        if key in "0123456789.+-*/()": self.add_to_expression(key)
        elif key == "Return" or key == "equal": self.evaluate_expression()
        elif key == "BackSpace": self.delete_last_char()
        elif key == "Escape": self.clear_expression()

    def add_to_expression(self, value):
        """Adds a value or operator to the expression string."""
        if self.display_label["text"] == "Error": self.expression = ""
        self.expression += str(value)
        self.update_display()

    def clear_expression(self):
        """Clears the entire expression."""
        self.expression = ""
        self.update_display("0")

    def delete_last_char(self):
        """Removes the last character from the expression."""
        if self.expression and self.display_label["text"] != "Error":
            self.expression = self.expression[:-1]
        else: self.expression = ""
        self.update_display()

    def toggle_sign(self):
        """Toggles the sign of the last entered number."""
        if not self.expression or self.expression == "0": return
        # Regex to find the last number in the expression
        matches = list(re.finditer(r"(-?\d+\.?\d*)$", self.expression))
        if matches:
            last_match = matches[-1]
            start, _ = last_match.span()
            number = last_match.group(1)
            if number.startswith('-'): 
                self.expression = self.expression[:start] + number[1:]
            else: 
                self.expression = self.expression[:start] + '-' + number
            self.update_display()

    def evaluate_expression(self):
        """Evaluates the final expression."""
        processed_expr = self.expression.replace('mod', '%')
        
        try:
            # Handle factorial with regex
            processed_expr = re.sub(r'(\d+\.?\d*)!', lambda m: f"math.factorial(int({m.group(1)}))", processed_expr)
            
            if not processed_expr: return
            
            # Using eval with a restricted globals dictionary for safety
            result = str(eval(processed_expr, {"math": math, "abs": abs}))
            
            # Format long results into scientific notation
            if len(result) > 12: result = f"{float(result):.5e}"
            self.expression = result
        except Exception:
            self.expression = ""
            result = "Error"
        self.update_display(result)

    def update_display(self, value=None):
        """Updates the display label with the current expression or a value."""
        text_to_display = value if value is not None else self.expression
        self.display_label.config(text=text_to_display or "0")


