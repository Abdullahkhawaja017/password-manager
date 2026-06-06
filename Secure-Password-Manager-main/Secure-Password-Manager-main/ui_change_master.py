import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import math
import ctypes
import bcrypt
from PIL import Image

# --- Import your existing modules ---
import database

# --- Configuration & Colors (Vault Access Theme) ---
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

class GlassChangeMasterPassword(ctk.CTkToplevel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.title("Change Master Password")
        self.configure(fg_color=COLOR_BG)

        # --- FIX: AGGRESSIVE FULLSCREEN SETUP ---
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        self.after(50, lambda: self.attributes('-fullscreen', True))
        
        self.bind("<Escape>", lambda e: self.destroy())

        # --- Dimensions ---
        self.card_width = 500
        self.card_height = 600
        
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
        self.content_frame.place(relx=0.5, rely=0.05, anchor="n", relwidth=0.85, relheight=0.9)

        # Title
        self.label_title = ctk.CTkLabel(
            self.content_frame, 
            text="SECURITY SETTINGS", 
            font=("Montserrat", 28, "bold"), 
            text_color=COLOR_ACCENT_CYAN
        )
        self.label_title.pack(pady=(10, 25))

        # --- Inputs ---
        self.entry_current = self.create_input("Current Master Password")
        self.entry_new = self.create_input("New Master Password")
        self.entry_confirm = self.create_input("Confirm New Password")

        # --- Buttons ---
        self.btn_update = ctk.CTkButton(
            self.content_frame,
            text="Update Password",
            font=("Montserrat", 16, "bold"),
            height=50,
            corner_radius=25,
            fg_color=COLOR_ACCENT_MAGENTA,
            hover_color=COLOR_ACCENT_CYAN,
            text_color="#ffffff",
            command=self.change_master_password
        )
        self.btn_update.pack(fill="x", pady=(30, 10))

        self.btn_cancel = ctk.CTkButton(
            self.content_frame,
            text="Cancel",
            font=("Arial", 12, "underline"),
            fg_color="transparent",
            text_color="gray",
            hover_color=COLOR_CARD_BG,
            command=self.destroy
        )
        self.btn_cancel.pack()

        # Start Animation
        self.animate_flow()

    def create_input(self, label_text):
        label = ctk.CTkLabel(self.content_frame, text=label_text, font=("Roboto", 12, "bold"), 
                             text_color=COLOR_ACCENT_CYAN, anchor="w")
        label.pack(fill="x", pady=(0, 5))
        
        entry = ctk.CTkEntry(
            self.content_frame, 
            height=45,
            font=("Roboto", 14), 
            text_color=COLOR_TEXT_WHITE,
            placeholder_text="Type password...",
            placeholder_text_color=COLOR_PLACEHOLDER, 
            fg_color=COLOR_INPUT_BG,       
            border_width=2,                
            border_color=COLOR_ACCENT_CYAN,
            corner_radius=12,
            show="*" # Security mask
        )
        entry.pack(fill="x", pady=(0, 15))
        return entry

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

    # -----------------------------
    # Backend Logic (Preserved)
    # -----------------------------
    def change_master_password(self):
        current_pw = self.entry_current.get()
        new_pw = self.entry_new.get()
        confirm_pw = self.entry_confirm.get()

        if not current_pw or not new_pw or not confirm_pw:
            messagebox.showerror("Error", "Please fill all fields.", parent=self)
            return

        # Fetch user
        users = database.get_all_users() # Returns [(id, username, hashed_pw)]
        if not users:
            messagebox.showerror("Error", "No user found!", parent=self)
            return
        
        user_id = users[0][0]
        stored_hash = users[0][2]

        # Verify Current Password
        try:
            if not bcrypt.checkpw(current_pw.encode('utf-8'), stored_hash.encode('utf-8')):
                messagebox.showerror("Error", "Incorrect current password!", parent=self)
                return
        except ValueError:
            messagebox.showerror("Error", "Database error: Invalid hash format.", parent=self)
            return

        # Verify New Passwords Match
        if new_pw != confirm_pw:
            messagebox.showerror("Error", "New passwords do not match!", parent=self)
            return

        # Update Password
        hashed_bytes = bcrypt.hashpw(new_pw.encode('utf-8'), bcrypt.gensalt())
        hashed_new = hashed_bytes.decode('utf-8') 

        database.update_master_password(user_id, hashed_new)

        messagebox.showinfo("Success", "Master password changed successfully!", parent=self)
        self.destroy()

def open_window(parent=None):
    # Create the Change Master window as a Toplevel of `parent` (if provided)
    # Do NOT call another mainloop() — just create the window and return it.
    app = GlassChangeMasterPassword(parent)
    try:
        # Attempt to make it modal/focused when parent provided
        app.grab_set()
        app.focus_force()
    except Exception:
        pass
    return app

if __name__ == "__main__":
    app = GlassChangeMasterPassword()
    app.mainloop()