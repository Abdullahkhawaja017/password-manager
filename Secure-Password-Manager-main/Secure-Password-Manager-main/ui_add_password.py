import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import random
import string
import math
import ctypes
from PIL import Image

# --- Import your existing modules ---
import database
from encryption_key import cipher 

# --- Configuration & Colors ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

COLOR_BG = "#0a001a"
COLOR_CARD_BG = "#130026"
COLOR_ACCENT_CYAN = "#00f7ff"
COLOR_ACCENT_MAGENTA = "#d900ff"
COLOR_TEXT_WHITE = "#ffffff"
COLOR_INPUT_BG = "#2a003b"
COLOR_PLACEHOLDER = "#a366bc"
NEON_ANIMATION_RGB = (217, 0, 255)

# --- FIX: FORCE HIGH DPI AWARENESS ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

class GlassAddPassword(ctk.CTkToplevel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.title("Add New Password")
        self.configure(fg_color=COLOR_BG)

        # --- FIX: AGGRESSIVE FULLSCREEN SETUP ---
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        self.after(50, lambda: self.attributes('-fullscreen', True))
        
        self.bind("<Escape>", lambda e: self.destroy())

        # --- Dimensions ---
        # Adjusted height slightly to ensure fit on 768p screens
        self.card_width = 500
        self.card_height = 700  
        
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
        # FIX: Anchored to 'n' (North) with padding to ensure top-down flow
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.place(relx=0.5, rely=0.05, anchor="n", relwidth=0.85, relheight=0.9)

        # Title
        self.label_title = ctk.CTkLabel(
            self.content_frame, 
            text="ADD PASSWORD", 
            font=("Montserrat", 28, "bold"), 
            text_color=COLOR_ACCENT_CYAN
        )
        self.label_title.pack(pady=(10, 20))

        # --- Form Elements ---
        self.create_form_elements()

        # --- Loading Elements ---
        self.loading_label = None
        self.progress_bar = None

        self.animate_flow()

    def generate_glowing_texture(self):
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

    def create_form_elements(self):
        # 1. Service Name
        self.entry_service = self.create_input_field("Service / App Name")
        
        # 2. Username
        self.entry_username = self.create_input_field("Username / Email")

        # 3. Password Row (Input + Generate Button)
        pw_label = ctk.CTkLabel(self.content_frame, text="Password", font=("Roboto", 12, "bold"), 
                                text_color=COLOR_ACCENT_CYAN, anchor="w")
        pw_label.pack(fill="x", pady=(0, 5))

        self.pw_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.pw_frame.pack(fill="x", pady=(0, 5))

        # --- FIX: PACK BUTTON FIRST (RIGHT), THEN ENTRY (LEFT) ---
        self.btn_generate = ctk.CTkButton(
            self.pw_frame,
            text="Generate",
            width=100,
            height=45,
            font=("Roboto", 12, "bold"),
            fg_color="#4a148c", 
            hover_color=COLOR_ACCENT_MAGENTA,
            border_width=1,
            border_color=COLOR_ACCENT_MAGENTA,
            command=self.generate_password
        )
        self.btn_generate.pack(side="right", padx=(5, 0))

        self.entry_password = ctk.CTkEntry(
            self.pw_frame, 
            placeholder_text="Type password...",
            height=45,
            font=("Roboto", 14), 
            text_color=COLOR_TEXT_WHITE,
            placeholder_text_color=COLOR_PLACEHOLDER, 
            fg_color=COLOR_INPUT_BG,       
            border_width=2,                
            border_color=COLOR_ACCENT_CYAN,
            corner_radius=12
        )
        self.entry_password.pack(side="left", fill="x", expand=True)
        self.entry_password.bind("<KeyRelease>", self.update_password_strength)

        # 4. Strength Meter
        self.strength_progress = ctk.CTkProgressBar(self.content_frame, height=8, corner_radius=4)
        self.strength_progress.pack(fill="x", pady=(5, 5))
        self.strength_progress.set(0)
        self.strength_progress.configure(progress_color="red")

        self.strength_label = ctk.CTkLabel(self.content_frame, text="Strength: Empty", font=("Arial", 10), text_color="gray")
        self.strength_label.pack(fill="x", pady=(0, 10))

        # 5. Notes
        self.entry_notes = self.create_input_field("Notes (Optional)")

        # 6. Action Buttons
        self.btn_save = ctk.CTkButton(
            self.content_frame, 
            text="Save Password", 
            font=("Montserrat", 16, "bold"),
            height=50, 
            corner_radius=25,
            fg_color=COLOR_ACCENT_MAGENTA, 
            hover_color=COLOR_ACCENT_CYAN, 
            text_color=COLOR_TEXT_WHITE,
            command=self.initiate_save
        )
        self.btn_save.pack(fill="x", pady=(20, 10))

        self.btn_cancel = ctk.CTkButton(
            self.content_frame,
            text="Cancel",
            font=("Arial", 12, "underline"),
            fg_color="transparent",
            text_color="gray",
            hover_color=COLOR_CARD_BG,
            command=self.destroy
        )
        self.btn_cancel.pack(pady=(0, 10))

    def create_input_field(self, label_text):
        label = ctk.CTkLabel(self.content_frame, text=label_text, font=("Roboto", 12, "bold"), 
                             text_color=COLOR_ACCENT_CYAN, anchor="w")
        label.pack(fill="x", pady=(0, 5))
        
        entry = ctk.CTkEntry(
            self.content_frame, 
            height=45,
            font=("Roboto", 14), 
            text_color=COLOR_TEXT_WHITE,
            placeholder_text_color=COLOR_PLACEHOLDER, 
            fg_color=COLOR_INPUT_BG,       
            border_width=2,                
            border_color=COLOR_ACCENT_CYAN,
            corner_radius=12
        )
        entry.pack(fill="x", pady=(0, 10))
        return entry

    # -----------------------------
    # Backend Logic
    # -----------------------------
    def generate_password(self):
        characters = string.ascii_letters + string.digits + string.punctuation
        new_password = ''.join(random.choice(characters) for _ in range(12))
        
        self.entry_password.delete(0, 'end')
        self.entry_password.insert(0, new_password)
        self.update_password_strength()

    def update_password_strength(self, event=None):
        pw = self.entry_password.get()
        score = 0
        if len(pw) >= 8: score += 1
        if any(c.islower() for c in pw): score += 1
        if any(c.isupper() for c in pw): score += 1
        if any(c.isdigit() for c in pw): score += 1
        if any(c in string.punctuation for c in pw): score += 1

        progress = score / 5.0
        
        colors = ["red", "red", "#FF7F00", "yellow", "#7FFF00", "#00FF00"]
        texts = ["Very Weak", "Very Weak", "Weak", "Medium", "Strong", "Very Strong"]
        
        color = colors[score]
        text_val = texts[score]

        if len(pw) == 0:
            progress = 0
            text_val = "Empty"
            color = "gray"

        self.strength_progress.set(progress)
        self.strength_progress.configure(progress_color=color)
        self.strength_label.configure(text=f"Strength: {text_val}", text_color=color)

    def initiate_save(self):
        self.service = self.entry_service.get()
        self.username = self.entry_username.get()
        self.password = self.entry_password.get()
        self.notes = self.entry_notes.get()

        if self.service == "" or self.username == "" or self.password == "":
            messagebox.showerror("Error", "Please fill all required fields!")
            return
        
        self.start_loading_animation()

    # -----------------------------
    # Loading & Success Animation
    # -----------------------------
    def start_loading_animation(self):
        self.content_frame.place_forget() 
        self.main_frame.place_forget()   
        self.glow_label.place_forget()   

        self.loading_label = ctk.CTkLabel(
            self, 
            text="Encrypting & Saving...", 
            font=("Montserrat", 24, "bold"), 
            text_color=COLOR_ACCENT_MAGENTA
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
        self.animate_loader()

    def animate_loader(self):
        if self.loading_step < 50:
            self.loading_step += 2
            val = self.loading_step / 50
            self.progress_bar.set(val)
            self.after(20, self.animate_loader)
        else:
            self.finalize_save()

    def finalize_save(self):
        try:
            encrypted_pw = cipher.encrypt(self.password.encode()).decode()
            database.add_password(self.service, self.username, encrypted_pw, self.notes)
            
            self.loading_label.configure(text="Password Saved!", text_color="#00FF00")
            self.after(1500, self.destroy)
            
        except Exception as e:
            self.loading_label.configure(text=f"Error: {str(e)}", text_color="red")
            self.after(3000, self.destroy)

def open_window(parent=None):
	# Create the Add Password window as a Toplevel of `parent` (if provided)
	# Do NOT call another mainloop() — just create the window and return it.
	app = GlassAddPassword(parent=parent)
	try:
		# Attempt to make it modal/focused when parent provided
		app.grab_set()
		app.focus_force()
	except Exception:
		# If grab/focus fail (different platforms), ignore
		pass
	return app

if __name__ == "__main__":
    app = GlassAddPassword()
    app.mainloop()