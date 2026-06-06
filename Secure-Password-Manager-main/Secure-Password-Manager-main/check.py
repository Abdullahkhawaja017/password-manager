import tkinter as tk
from tkinter import font as tkfont

class GlassApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")
        
        # --- Full Screen Setup ---
        self.root.attributes('-fullscreen', True)
        
        # Get actual screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Calculate the center point of the screen
        self.cx = self.screen_width / 2
        self.cy = self.screen_height / 2

        self.root.configure(bg="#120024")
        
        # Bind Escape key to exit
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        # --- Colors ---
        self.colors = {
            "bg_main": "#120024",       # Deep Purple Background
            "card_bg": "#2A1B5E",       # Glass Card Color
            "card_border": "#64B5F6",   # Cyan Glow
            "text_white": "#FFFFFF",
            "text_gray": "#AAAAAA",
            "input_bg": "#150b2b",      # Dark input background
            "btn_cyan": "#00E5FF",      # Neon Cyan
            "btn_hover": "#00B2CC"      # Darker Cyan
        }

        # --- Main Canvas ---
        self.canvas = tk.Canvas(
            root, 
            bg=self.colors["bg_main"], 
            height=self.screen_height, 
            width=self.screen_width, 
            bd=0, 
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        # --- Draw The Interface ---
        self.draw_glass_card()
        self.draw_text_elements()
        self.create_inputs()
        self.create_login_button()

    def round_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        """Helper function to draw rounded rectangles on Canvas"""
        points = [x1+radius, y1,
                  x1+radius, y1,
                  x2-radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1+radius,
                  x1, y1]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def draw_glass_card(self):
        # Card dimensions
        w, h = 360, 420
        
        x1, y1 = self.cx - w/2, self.cy - h/2
        x2, y2 = self.cx + w/2, self.cy + h/2

        # Draw the main card with a neon border
        self.round_rectangle(x1, y1, x2, y2, radius=30, 
                             fill=self.colors["card_bg"], 
                             outline=self.colors["card_border"], 
                             width=2)

    def draw_text_elements(self):
        # Title (Offset -140 pixels from center Y)
        self.canvas.create_text(self.cx, self.cy - 140, 
                                text="Password Manager", 
                                fill=self.colors["text_white"], 
                                font=("Times New Roman", 26))
        
        # Underline (Line)
        self.canvas.create_line(self.cx - 110, self.cy - 115, 
                                self.cx + 110, self.cy - 115, 
                                fill="white", width=1)

        # Labels
        self.canvas.create_text(self.cx, self.cy - 85, text="Username", fill=self.colors["text_gray"], font=("Arial", 10))
        self.canvas.create_text(self.cx, self.cy + 5, text="Master Password", fill=self.colors["text_gray"], font=("Arial", 10))

    def create_inputs(self):
        # 1. Username Input Box Background (Offset relative to center)
        # Coordinates: cx-125, cy-70 to cx+125, cy-30
        self.round_rectangle(self.cx - 125, self.cy - 70, self.cx + 125, self.cy - 30, 
                             radius=10, fill=self.colors["input_bg"], outline="#555555")
        
        # 1. Username Entry Widget
        self.user_entry = tk.Entry(self.root, bg=self.colors["input_bg"], fg="white", 
                                   bd=0, font=("Arial", 11), insertbackground="white")
        # Place relative to center
        self.user_entry.place(x=self.cx - 115, y=self.cy - 60, width=230, height=20)

        # 2. Password Input Box Background
        self.round_rectangle(self.cx - 125, self.cy + 20, self.cx + 125, self.cy + 60, 
                             radius=10, fill=self.colors["input_bg"], outline="#555555")

        # 2. Password Entry Widget
        self.pass_entry = tk.Entry(self.root, bg=self.colors["input_bg"], fg="white", 
                                   bd=0, font=("Arial", 11), show="*", insertbackground="white")
        self.pass_entry.place(x=self.cx - 115, y=self.cy + 30, width=230, height=20)

    def create_login_button(self):
        # Draw a Rounded Button using Canvas
        # Coordinates relative to center
        x1 = self.cx - 90
        y1 = self.cy + 100
        x2 = self.cx + 90
        y2 = self.cy + 145
        
        # This is the shape
        self.btn_shape = self.round_rectangle(x1, y1, x2, y2, radius=20, 
                                              fill=self.colors["btn_cyan"], outline="")
        
        # This is the text on top
        self.btn_text = self.canvas.create_text(self.cx, (y1+y2)/2, 
                                                text="Login", fill="#000000", 
                                                font=("Arial", 12, "bold"))

        # Bind events
        self.canvas.tag_bind(self.btn_shape, "<Button-1>", self.on_login)
        self.canvas.tag_bind(self.btn_text, "<Button-1>", self.on_login)
        
        # Hover effects
        self.canvas.tag_bind(self.btn_shape, "<Enter>", lambda e: self.canvas.itemconfig(self.btn_shape, fill=self.colors["btn_hover"]))
        self.canvas.tag_bind(self.btn_shape, "<Leave>", lambda e: self.canvas.itemconfig(self.btn_shape, fill=self.colors["btn_cyan"]))

    def on_login(self, event):
        u = self.user_entry.get()
        p = self.pass_entry.get()
        print(f"Attempting Login -> User: {u}, Pass: {p}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GlassApp(root)
    root.mainloop()



    



