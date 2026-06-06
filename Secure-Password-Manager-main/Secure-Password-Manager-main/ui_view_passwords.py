import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
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
COLOR_INPUT_BG = "#2a003b"
COLOR_PLACEHOLDER = "#a366bc"
NEON_ANIMATION_RGB = (217, 0, 255)

# --- FIX: FORCE HIGH DPI AWARENESS ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

class GlassViewPasswords(ctk.CTkToplevel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.title("View Passwords")
        self.configure(fg_color=COLOR_BG)

        # --- FIX: AGGRESSIVE FULLSCREEN SETUP ---
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        self.after(50, lambda: self.attributes('-fullscreen', True))
        
        self.bind("<Escape>", lambda e: self.destroy())

        # --- Dimensions ---
        self.card_width = 700
        self.card_height = 800  
        
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
        self.content_frame.place(relx=0.5, rely=0.05, anchor="n", relwidth=0.9, relheight=0.9)

        # Title
        self.label_title = ctk.CTkLabel(
            self.content_frame, 
            text="YOUR PASSWORDS", 
            font=("Montserrat", 28, "bold"), 
            text_color=COLOR_ACCENT_CYAN
        )
        self.label_title.pack(pady=(10, 15))

        # --- Search Bar Area ---
        self.search_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.search_frame.pack(fill="x", pady=(0, 15))

        self.entry_search = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Search Service...",
            height=40,
            font=("Roboto", 14),
            fg_color=COLOR_INPUT_BG,
            border_color=COLOR_ACCENT_CYAN,
            text_color=COLOR_TEXT_WHITE
        )
        self.entry_search.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.btn_search = ctk.CTkButton(
            self.search_frame, text="Search", width=80, height=40,
            fg_color="#4a148c", hover_color=COLOR_ACCENT_MAGENTA,
            command=self.search_passwords
        )
        self.btn_search.pack(side="left", padx=(0, 5))

        self.btn_show_all = ctk.CTkButton(
            self.search_frame, text="Show All", width=80, height=40,
            fg_color="#4a148c", hover_color=COLOR_ACCENT_MAGENTA,
            command=self.show_all
        )
        self.btn_show_all.pack(side="left")

        # --- Listbox Container ---
        # We use a standard Listbox because CTK doesn't have one, 
        # but we style it to match the theme.
        self.list_container = ctk.CTkFrame(
            self.content_frame, 
            fg_color=COLOR_INPUT_BG, 
            border_width=2, 
            border_color=COLOR_ACCENT_CYAN
        )
        self.list_container.pack(fill="both", expand=True, pady=(0, 20))

        self.listbox = tk.Listbox(
            self.list_container,
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT_WHITE,
            selectbackground=COLOR_ACCENT_MAGENTA,
            selectforeground=COLOR_TEXT_WHITE,
            bd=0,
            highlightthickness=0,
            font=("Courier New", 12),
            activestyle="none"
        )
        self.listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Scrollbar for Listbox
        self.scrollbar = ctk.CTkScrollbar(self.list_container, command=self.listbox.yview)
        self.scrollbar.pack(side="right", fill="y", padx=5, pady=5)
        self.listbox.config(yscrollcommand=self.scrollbar.set)

        # --- Action Buttons ---
        self.btn_decrypt = ctk.CTkButton(
            self.content_frame,
            text="Decrypt & Copy Password",
            font=("Montserrat", 16, "bold"),
            height=50,
            corner_radius=25,
            fg_color=COLOR_ACCENT_CYAN,
            hover_color=COLOR_ACCENT_MAGENTA,
            text_color="#000000",
            command=self.decrypt_password
        )
        self.btn_decrypt.pack(fill="x", pady=(0, 10))

        self.label_notification = ctk.CTkLabel(
            self.content_frame, text="", font=("Arial", 12, "bold"), text_color="#00FF00"
        )
        self.label_notification.pack(pady=(0, 5))

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

        # Start Animation & Load Data
        self.animate_flow()
        self.show_all()

    # -----------------------------
    # UI Animation Logic
    # -----------------------------
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
    def copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update() 
        self.show_notification("Password copied to clipboard!", "#00FF00")

    def show_notification(self, message, color):
        self.label_notification.configure(text=message, text_color=color)
        self.after(2000, lambda: self.label_notification.configure(text=""))

    def show_all(self):
        self.listbox.delete(0, tk.END)
        rows = database.get_all_passwords()  
        for row in rows:
            # Display format: ID - Service - Username
            self.listbox.insert(tk.END, f"{row[0]} - {row[1]} - {row[2]}")

    def search_passwords(self):
        query = self.entry_search.get()
        self.listbox.delete(0, tk.END)
        rows = database.search_passwords(query)
        for row in rows:
            self.listbox.insert(tk.END, f"{row[0]} - {row[1]} - {row[2]}")

    def decrypt_password(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "Select a password first!")
            return

        index = selected[0]
        row_text = self.listbox.get(index)

        try:
            record_id = int(row_text.split(" - ")[0])
        except ValueError:
            messagebox.showerror("Error", "Invalid selection format.")
            return

        rows = database.get_all_passwords()
        row = next((r for r in rows if r[0] == record_id), None)

        if row is None:
            messagebox.showerror("Error", "Record not found!")
            return

        encrypted_pw = row[3]

        try:
            decrypted_pw = cipher.decrypt(encrypted_pw.encode()).decode()
            self.copy_to_clipboard(decrypted_pw)
        except Exception:
            messagebox.showerror("Error", "Cannot decrypt password! Check encryption key.")

def open_window(parent=None):
    # Create the View Passwords window as a Toplevel of `parent` (if provided)
    # Do NOT call another mainloop() — just create the window and return it.
    app = GlassViewPasswords(parent=parent)
    try:
        # Attempt to make it modal/focused when parent provided
        app.grab_set()
        app.focus_force()
    except Exception:
        # If grab/focus fail (different platforms), ignore
        pass
    return app

if __name__ == "__main__":
    app = GlassViewPasswords()
    app.mainloop()