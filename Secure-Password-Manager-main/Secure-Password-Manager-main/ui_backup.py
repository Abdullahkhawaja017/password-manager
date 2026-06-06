import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import csv
import math
import ctypes
from PIL import Image

# --- Import your existing modules ---
import database
from encryption_key import cipher 

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

class GlassBackup(ctk.CTkToplevel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.title("Backup Passwords")
        self.configure(fg_color=COLOR_BG)

        # --- FIX: AGGRESSIVE FULLSCREEN SETUP ---
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        self.after(50, lambda: self.attributes('-fullscreen', True))
        
        self.bind("<Escape>", lambda e: self.destroy())

        # --- Dimensions ---
        self.card_width = 450
        self.card_height = 400
        
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
            text="DATA BACKUP", 
            font=("Montserrat", 28, "bold"), 
            text_color=COLOR_ACCENT_CYAN
        )
        self.label_title.pack(pady=(0, 20))

        # Description
        self.label_desc = ctk.CTkLabel(
            self.content_frame,
            text="Export all your passwords to a CSV file.\n\n⚠️ Keep this file safe!",
            font=("Roboto", 14),
            text_color=COLOR_TEXT_WHITE,
            justify="center"
        )
        self.label_desc.pack(pady=(0, 30))

        # --- Backup Button ---
        self.btn_backup = ctk.CTkButton(
            self.content_frame,
            text="Backup Now",
            font=("Montserrat", 16, "bold"),
            height=50,
            corner_radius=25,
            fg_color=COLOR_ACCENT_MAGENTA,
            hover_color=COLOR_ACCENT_CYAN,
            text_color="#ffffff",
            command=self.backup_database
        )
        self.btn_backup.pack(fill="x", pady=(0, 15))

        # --- Close Button ---
        self.btn_close = ctk.CTkButton(
            self.content_frame,
            text="Close",
            font=("Arial", 12, "underline"),
            fg_color="transparent",
            text_color="gray",
            hover_color=COLOR_CARD_BG,
            command=self.destroy
        )
        self.btn_close.pack()

        # Start Animation
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

    # -----------------------------
    # Logic (Preserved)
    # -----------------------------
    def backup_database(self):
        try:
            rows = database.get_all_passwords()
            filename = "backup_passwords.csv"
            
            with open(filename, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Service", "Username", "Password", "Notes"])
                
                for row in rows:
                    try:
                        # Decrypt using shared cipher
                        decrypted_pw = cipher.decrypt(row[3].encode()).decode()
                    except:
                        decrypted_pw = "[DECRYPTION FAILED]"
                    
                    writer.writerow([row[0], row[1], row[2], decrypted_pw, row[4]])

            messagebox.showinfo("Success", f"Backup completed successfully!\nSaved as '{filename}'")
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed: {str(e)}")

def open_window(parent=None):
    # Create the Backup window as a Toplevel of `parent` (if provided)
    # Do NOT call another mainloop() — just create the window and return it.
    app = GlassBackup(parent=parent)
    try:
        # Attempt to make it modal/focused when parent provided
        app.grab_set()
        app.focus_force()
    except Exception:
        pass
    return app

if __name__ == "__main__":
    app = GlassBackup()
    app.mainloop()