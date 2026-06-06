import customtkinter as ctk
import tkinter as tk
from tkinter import font as tkfont
import sys
import math
import ctypes
from PIL import Image

# -----------------------------
# Import your existing modules
# -----------------------------
import ui_add_password
import ui_view_passwords
import ui_backup
import ui_change_master
import ui_help
import ui_edit_password

# --- Configuration & Colors (Vault Access Theme) ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

COLOR_BG = "#0a001a"
COLOR_CARD_BG = "#130026"
COLOR_ACCENT_CYAN = "#00f7ff"
COLOR_ACCENT_MAGENTA = "#d900ff"
COLOR_TEXT_WHITE = "#ffffff"
NEON_ANIMATION_RGB = (217, 0, 255)

# --- FIX: FORCE HIGH DPI AWARENESS ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

class GlassMainMenu(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Vault Access - Main Menu")
        self.configure(fg_color=COLOR_BG)

        # --- FIX: AGGRESSIVE FULLSCREEN SETUP ---
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        self.after(50, lambda: self.attributes('-fullscreen', True))

        # Bind Escape to exit
        self.bind("<Escape>", lambda e: self.destroy())

        # --- Dimensions ---
        self.card_width = 450
        self.card_height = 650 
        
        self.border_thickness = 4
        self.glow_w = self.card_width + (self.border_thickness * 2)
        self.glow_h = self.card_height + (self.border_thickness * 2)

        self.render_w = self.glow_w // 10
        self.render_h = self.glow_h // 10
        self.flow_offset = 0.0

        # --- 1. Background Glow Animation ---
        self.glow_label = ctk.CTkLabel(self, text="", fg_color=COLOR_BG)
        self.glow_label.place(relx=0.5, rely=0.5, anchor="center")

        # --- 2. Main Card ---
        self.main_frame = ctk.CTkFrame(
            self, 
            width=self.card_width, 
            height=self.card_height, 
            corner_radius=20,
            fg_color=COLOR_CARD_BG,
            border_width=0
        )
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

        # --- Content Container ---
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85)

        # Title
        self.label_title = ctk.CTkLabel(
            self.content_frame, 
            text="MAIN MENU", 
            font=("Montserrat", 32, "bold"), 
            text_color=COLOR_ACCENT_CYAN
        )
        self.label_title.pack(pady=(0, 5))

        # Divider Line
        self.divider = ctk.CTkFrame(self.content_frame, height=2, fg_color=COLOR_ACCENT_MAGENTA, width=200)
        self.divider.pack(pady=(0, 30))

        # --- Create Menu Buttons ---
        self.create_menu_buttons()

        # --- Loading Elements (Hidden Initially) ---
        self.loading_label = None
        self.progress_bar = None

        # Start Animation
        self.animate_flow()

    def generate_glowing_texture(self):
        """Generates the flowing neon texture."""
        image = Image.new("RGB", (self.render_w, self.render_h))
        pixels = image.load()
        cr, cg, cb = NEON_ANIMATION_RGB
        for y in range(self.render_h):
            for x in range(self.render_w):
                pos_factor = (x + y) + self.flow_offset
                wave = math.sin(pos_factor / 15.0)
                intensity = (wave + 1.0) / 2.0
                min_brightness = 0.15
                final_intensity = min_brightness + (intensity * (1.0 - min_brightness))
                r = int(cr * final_intensity)
                g = int(cg * final_intensity)
                b = int(cb * final_intensity)
                pixels[x, y] = (r, g, b)
        return image

    def animate_flow(self):
        raw_img = self.generate_glowing_texture()
        ctk_img = ctk.CTkImage(light_image=raw_img, dark_image=raw_img, size=(self.glow_w, self.glow_h))
        self.glow_label.configure(image=ctk_img)
        self.flow_offset -= 1.0 
        self.after(30, self.animate_flow)

    def create_menu_buttons(self):
        # List of buttons and their commands
        buttons = [
            ("Add Password", lambda: ui_add_password.open_window(self)),
            ("View Passwords", lambda: ui_view_passwords.open_window(self)),
            ("Edit Password", lambda: ui_edit_password.open_window(self)),
            # Pass `self` as parent so the Backup window is properly parented.
            ("Backup/Export", lambda: ui_backup.open_window(self)),
            ("Change Master Password", lambda: ui_change_master.open_window(self)),
            ("Help/Instructions", lambda: ui_help.open_window(self)),
            ("Logout/Exit", self.start_logout)  
        ]

        for text, cmd in buttons:
            is_logout = "Logout" in text
            
            btn = ctk.CTkButton(
                self.content_frame,
                text=text,
                font=("Montserrat", 14, "bold"),
                height=45,
                corner_radius=22,
                fg_color="#2a003b" if not is_logout else COLOR_ACCENT_MAGENTA, # Different color for logout
                hover_color=COLOR_ACCENT_CYAN,
                border_width=1,
                border_color=COLOR_ACCENT_CYAN,
                text_color=COLOR_TEXT_WHITE,
                command=cmd
            )
            btn.pack(pady=8, fill="x")

    # -----------------------------
    # LOGOUT & ANIMATION LOGIC
    # -----------------------------
    def start_logout(self):
        # Hide the main card content
        self.main_frame.place_forget()
        self.glow_label.place_forget()

        # Show Logout Animation
        self.loading_label = ctk.CTkLabel(
            self, 
            text="Logging out...", 
            font=("Montserrat", 24, "bold"), 
            text_color=COLOR_ACCENT_MAGENTA
        )
        self.loading_label.place(relx=0.5, rely=0.45, anchor="center")

        self.progress_bar = ctk.CTkProgressBar(
            self, 
            width=400, 
            height=15, 
            corner_radius=10,
            progress_color=COLOR_ACCENT_MAGENTA,
            fg_color="#2a003b"
        )
        self.progress_bar.place(relx=0.5, rely=0.5, anchor="center")
        self.progress_bar.set(0)

        self.logout_step = 0
        self.animate_logout()

    def animate_logout(self):
        if self.logout_step < 50:
            self.logout_step += 2
            val = self.logout_step / 50
            self.progress_bar.set(val)
            self.after(20, self.animate_logout)
        else:
            self.perform_logout()

    def perform_logout(self):
        self.destroy()
        
        # Open Login Window
        # We try to import the new CTK login class
        try:
            import ui_login # Assuming the previous file is named login.py
            app = ui_login.GlassLoginApp()
            app.mainloop()
        except ImportError:
            # Fallback if file naming is different
            print("Could not launch login.py automatically.")

# -----------------------------
# Main menu window entry point
# -----------------------------
def open_main_window():
    # If a root already exists, we use Toplevel behavior logic or new instance
    # For CustomTkinter, usually best to create a new App instance if the previous one was destroyed.
    app = GlassMainMenu()
    app.mainloop()

if __name__ == "__main__":
    open_main_window()