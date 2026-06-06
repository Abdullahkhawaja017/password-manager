import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import math
from PIL import Image
import bcrypt
import time

# --- Import your existing modules ---
import database
import ui_main
import encryption_key

# --- Configuration & Colors (From Vault Access Theme) ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# Deep purple/black background
COLOR_BG = "#0a001a"
# Dark purple card background
COLOR_CARD_BG = "#130026"

# Accent Colors
COLOR_ACCENT_CYAN = "#00f7ff"   # For Title, Labels, Input Borders
COLOR_ACCENT_MAGENTA = "#d900ff" # For Button
COLOR_ERROR_RED = "#ff3333"      # Added for error messages

# The RGB tuple for the flowing neon border animation (Magenta glow)
NEON_ANIMATION_RGB = (217, 0, 255)

# Input field colors
COLOR_INPUT_BG = "#2a003b"       # Dark purple fill for inputs
COLOR_TEXT_WHITE = "#ffffff"
COLOR_PLACEHOLDER = "#a366bc"    # Dimmed purple/grey for placeholders

class GlassLoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Vault Access")
        self.configure(fg_color=COLOR_BG)

        # --- FIX: Force Full Screen After Initialization ---
        # We use a small delay (0ms) to ensure the window is mapped before setting attributes
        self.after(0, lambda: self.attributes('-fullscreen', True))
        
        # Optional: Bind F11 to toggle fullscreen if needed
        self.bind("<F11>", self.toggle_fullscreen)

        # Escape to close
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Return>", lambda e: self.attempt_login())

        # --- Dimensions ---
        self.card_width = 380
        self.card_height = 480 
        
        # --- Border Thickness ---
        self.border_thickness = 4
        
        self.glow_w = self.card_width + (self.border_thickness * 2)
        self.glow_h = self.card_height + (self.border_thickness * 2)

        # Optimization: Render tiny, scale up for blur
        self.render_w = self.glow_w // 10
        self.render_h = self.glow_h // 10

        self.flow_offset = 0.0

        # --- 1. The Glow Label (Background Animation) ---
        self.glow_label = ctk.CTkLabel(self, text="", fg_color=COLOR_BG)
        self.glow_label.place(relx=0.5, rely=0.5, anchor="center")

        # --- 2. The Login Card (Foreground) ---
        self.login_frame = ctk.CTkFrame(
            self, 
            width=self.card_width, 
            height=self.card_height, 
            corner_radius=20,
            fg_color=COLOR_CARD_BG,
            border_width=0
        )
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        # --- Content ---
        self.content_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        self.content_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85)

        # Title: V A U L T (Cyan)
        self.label_title = ctk.CTkLabel(
            self.content_frame, 
            text="V A U L T", 
            font=("Montserrat", 36, "bold"), 
            text_color=COLOR_ACCENT_CYAN
        )
        self.label_title.pack(pady=(0, 25))

        # Error Label (Hidden initially)
        self.label_error = ctk.CTkLabel(
            self.content_frame,
            text="",
            font=("Roboto", 12),
            text_color=COLOR_ERROR_RED
        )
        self.label_error.pack(pady=(0, 5))

        # Inputs
        self.user_entry = self.create_input_field(self.content_frame, "Username", "Type username...")
        self.pass_entry = self.create_input_field(self.content_frame, "Master Password", "Type password...", is_password=True)

        # Button: Access Vault (Magenta)
        self.button_login = ctk.CTkButton(
            self.content_frame, 
            text="Access Vault", 
            font=("Montserrat", 16, "bold"),
            width=280, height=50, corner_radius=25,
            fg_color=COLOR_ACCENT_MAGENTA, 
            hover_color=COLOR_ACCENT_CYAN, 
            text_color=COLOR_TEXT_WHITE,
            command=self.attempt_login
        )
        self.button_login.pack(pady=(20, 0))

        # --- Loading Elements (Hidden Initially) ---
        self.loading_label = None
        self.progress_bar = None

        # Start animation
        self.animate_flow()

        # Check Logic
        self.check_initial_registration()

    def toggle_fullscreen(self, event=None):
        """Allows toggling fullscreen with F11"""
        self.attributes('-fullscreen', not self.attributes('-fullscreen'))

    # ---------------------------------------------------------
    #  UI ANIMATION LOGIC
    # ---------------------------------------------------------
    def generate_glowing_texture(self):
        """Generates the flowing neon texture using the new magenta RGB."""
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
        ctk_img = ctk.CTkImage(
            light_image=raw_img,
            dark_image=raw_img,
            size=(self.glow_w, self.glow_h)
        )
        self.glow_label.configure(image=ctk_img)
        self.flow_offset -= 1.0 
        self.after(30, self.animate_flow)

    def create_input_field(self, parent, label_text, placeholder, is_password=False):
        label = ctk.CTkLabel(parent, text=label_text, font=("Roboto", 12, "bold"), 
                             text_color=COLOR_ACCENT_CYAN, anchor="w")
        label.pack(fill="x", pady=(0, 5))
        
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder,
                             height=45,
                             font=("Roboto", 14), 
                             text_color=COLOR_TEXT_WHITE,
                             placeholder_text_color=COLOR_PLACEHOLDER, 
                             fg_color=COLOR_INPUT_BG,       
                             border_width=2,                
                             border_color=COLOR_ACCENT_CYAN,
                             corner_radius=12,              
                             show="*" if is_password else "")
        entry.pack(fill="x", pady=(0, 15))
        return entry

    # ---------------------------------------------------------
    #  BACKEND LOGIC
    # ---------------------------------------------------------
    def user_exists(self):
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        user = cursor.fetchone()
        conn.close()
        return user

    def register_user(self, username, password):
        hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_pw = hashed_bytes.decode('utf-8')
        
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, master_password) VALUES (?, ?)",
            (username, hashed_pw)
        )
        conn.commit()
        conn.close()

    def check_initial_registration(self):
        if not self.user_exists():
            messagebox.showinfo("Register", "No user found. Please register a master password.")

    def attempt_login(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()

        user = self.user_exists() 

        if username == "" or password == "":
            self.label_error.configure(text="Please enter both fields.")
            return

        if not user:
            self.register_user(username, password)
            messagebox.showinfo("Success", "User registered securely!")
            self.destroy()
            return

        stored_hash = user[2].encode('utf-8') 
        
        if username == user[1] and bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            try:
                encryption_key.cipher.initialize(password)
            except Exception as e:
                self.label_error.configure(text=f"Key Error: {e}")
                return

            self.label_error.configure(text="")
            self.start_loading_sequence()
        else:
            self.label_error.configure(text="Incorrect Username or Password")
            self.pass_entry.delete(0, 'end')

    # ---------------------------------------------------------
    #  LOADING SCREEN LOGIC
    # ---------------------------------------------------------
    def start_loading_sequence(self):
        self.login_frame.place_forget()
        self.glow_label.place_forget() 
        
        self.loading_label = ctk.CTkLabel(
            self, 
            text="Accessing Vault...", 
            font=("Montserrat", 24, "bold"), 
            text_color=COLOR_ACCENT_CYAN
        )
        self.loading_label.place(relx=0.5, rely=0.45, anchor="center")

        self.progress_bar = ctk.CTkProgressBar(
            self, 
            width=400, 
            height=15, 
            corner_radius=10,
            progress_color=COLOR_ACCENT_CYAN,
            fg_color=COLOR_INPUT_BG
        )
        self.progress_bar.place(relx=0.5, rely=0.5, anchor="center")
        self.progress_bar.set(0)

        self.loading_step = 0
        self.animate_loading()

    def animate_loading(self):
        if self.loading_step < 100:
            self.loading_step += 2
            val = self.loading_step / 100
            self.progress_bar.set(val)
            self.after(20, self.animate_loading)
        else:
            self.loading_label.configure(text="Access Granted", text_color="#00FF00")
            self.after(1000, self.finish_login)

    def finish_login(self):
        self.destroy()
        ui_main.open_main_window()

if __name__ == "__main__":
    app = GlassLoginApp()
    app.mainloop()