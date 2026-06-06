import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from tkinter import font as tkfont
import database
from encryption_key import cipher   # Use the SAME cipher everywhere

# --- Appearance & Colors (match other UI files) ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

COLOR_BG = "#0a001a"
COLOR_CARD_BG = "#130026"
COLOR_ACCENT_CYAN = "#00f7ff"
COLOR_ACCENT_MAGENTA = "#d900ff"
COLOR_TEXT_WHITE = "#ffffff"
COLOR_INPUT_BG = "#2a003b"
COLOR_PLACEHOLDER = "#a366bc"

# ---------------------------------------------------------
#  CLASS 1: The Main List Window (Select to Edit/Delete)
# ---------------------------------------------------------
class GlassEditPassword:
    def __init__(self, root):
        # Use CTkToplevel so theme matches other windows
        self.window = ctk.CTkToplevel(root)
        self.window.title("Edit/Delete Password")
        self.window.configure(fg_color=COLOR_BG)
        
        # --- Full Screen Setup ---
        self.window.attributes('-fullscreen', True)
        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()
        self.cx = self.screen_width / 2
        self.cy = self.screen_height / 2

        # Keep Escape binding as before
        self.window.bind("<Escape>", lambda e: self.window.destroy())

        # --- Colors ---
        self.colors = {
            "bg_main": COLOR_BG,
            "card_bg": COLOR_CARD_BG,
            "card_border": COLOR_ACCENT_CYAN,
            "text_white": COLOR_TEXT_WHITE,
            "text_gray": "#AAAAAA",
            "input_bg": COLOR_INPUT_BG,
            "btn_cyan": COLOR_ACCENT_CYAN,
            "btn_hover": "#00B2CC",
            "btn_danger": "#FF4444",
            "btn_danger_hover": "#CC0000",
            "listbox_bg": COLOR_INPUT_BG,
            "listbox_select": "#4a148c"
        }

        # --- Main Canvas ---
        self.canvas = tk.Canvas(
            self.window, 
            bg=self.colors["bg_main"], 
            height=self.screen_height, 
            width=self.screen_width, 
            bd=0, 
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        # --- Draw UI ---
        self.draw_glass_card()
        self.draw_title()
        self.create_listbox()
        self.create_buttons()

        # Load data
        self.show_all()

    def round_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def draw_glass_card(self):
        w, h = 600, 600
        x1, y1 = self.cx - w/2, self.cy - h/2
        x2, y2 = self.cx + w/2, self.cy + h/2

        self.round_rectangle(x1, y1, x2, y2, radius=30, 
                             fill=self.colors["card_bg"], 
                             outline=self.colors["card_border"], 
                             width=2)

    def draw_title(self):
        self.canvas.create_text(self.cx, self.cy - 250, 
                                text="Manage Passwords", 
                                fill=self.colors["text_white"], 
                                font=("Times New Roman", 28))
        self.canvas.create_line(self.cx - 110, self.cy - 230, 
                                self.cx + 110, self.cy - 230, 
                                fill="white", width=1)

    def create_listbox(self):
        # Background for listbox styling
        lb_w, lb_h = 500, 300
        x1 = self.cx - lb_w/2
        y1 = self.cy - 180
        
        self.round_rectangle(x1-5, y1-5, x1+lb_w+5, y1+lb_h+5, radius=10, fill=self.colors["card_border"], outline="")
        self.round_rectangle(x1, y1, x1+lb_w, y1+lb_h, radius=10, fill=self.colors["input_bg"], outline="")

        # Keep tk.Listbox (behavior unchanged) but use theme colors
        self.listbox = tk.Listbox(self.window, width=50, height=18, 
                                  bg=self.colors["listbox_bg"], 
                                  fg=self.colors["text_white"], 
                                  bd=0, 
                                  highlightthickness=0,
                                  selectbackground=self.colors["listbox_select"],
                                  font=("Courier New", 10))
        self.listbox.place(x=x1 + 10, y=y1 + 10, width=lb_w - 20, height=lb_h - 20)

    def create_buttons(self):
        # Edit Button
        self.create_button(self.cx - 130, self.cy + 180, "Edit Selected", self.edit_password, self.colors["btn_cyan"], self.colors["btn_hover"])
        
        # Delete Button
        self.create_button(self.cx + 130, self.cy + 180, "Delete Selected", self.delete_password, self.colors["btn_danger"], self.colors["btn_danger_hover"])

        # Close Text
        cancel_text = self.canvas.create_text(self.cx, self.cy + 250, text="Back to Menu", fill=self.colors["text_gray"], font=("Arial", 10, "underline"))
        self.canvas.tag_bind(cancel_text, "<Button-1>", lambda e: self.window.destroy())

    def create_button(self, cx, cy, text, command, col_bg, col_hover):
        w, h = 200, 45
        x1, y1 = cx - w/2, cy - h/2
        x2, y2 = cx + w/2, cy + h/2

        btn = self.round_rectangle(x1, y1, x2, y2, radius=20, fill=col_bg, outline="")
        lbl = self.canvas.create_text(cx, cy, text=text, fill="black", font=("Arial", 11, "bold"))

        def on_enter(e): self.canvas.itemconfig(btn, fill=col_hover)
        def on_leave(e): self.canvas.itemconfig(btn, fill=col_bg)
        def on_click(e): command()

        for tag in [btn, lbl]:
            self.canvas.tag_bind(tag, "<Enter>", on_enter)
            self.canvas.tag_bind(tag, "<Leave>", on_leave)
            self.canvas.tag_bind(tag, "<Button-1>", on_click)

    # --- Logic (unchanged) ---
    def show_all(self):
        self.listbox.delete(0, tk.END)
        rows = database.get_all_passwords()
        for row in rows:
            self.listbox.insert(tk.END, f"{row[0]} - {row[1]} - {row[2]}")

    def edit_password(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "Select a password first!")
            return

        index = selected[0]
        row_text = self.listbox.get(index)
        record_id = int(row_text.split(" - ")[0])

        # Fetch full record
        rows = database.get_all_passwords()
        row = next((r for r in rows if r[0] == record_id), None)

        if row:
            # Open the Glass Edit Form (defined below) and ensure it's focused/raised
            form = GlassEditForm(self.window, row, self.show_all)
            try:
                form.window.grab_set()
                form.window.focus_force()
                form.window.lift()
            except Exception:
                pass
        else:
            messagebox.showerror("Error", "Record not found!")

    def delete_password(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "Select a password first!")
            return

        index = selected[0]
        row_text = self.listbox.get(index)
        record_id = int(row_text.split(" - ")[0])

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this password?")
        if confirm:
            database.delete_password(record_id)
            messagebox.showinfo("Success", "Password deleted successfully!")
            self.show_all()


# ---------------------------------------------------------
#  CLASS 2: The Edit Form Window (Opens on top)
# ---------------------------------------------------------
class GlassEditForm:
    def __init__(self, parent, row_data, refresh_callback):
        # Use CTkToplevel to keep theme consistent
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Edit Password")
        self.row_data = row_data
        self.refresh_callback = refresh_callback
        
        # Unpack data
        self.record_id = row_data[0]
        self.service = row_data[1]
        self.username = row_data[2]
        self.encrypted_pw = row_data[3]
        self.notes = row_data[4]

        # Decrypt password (backend unchanged)
        try:
            self.decrypted_pw = cipher.decrypt(self.encrypted_pw.encode()).decode()
        except:
            self.decrypted_pw = ""

        # Full Screen
        self.window.attributes('-fullscreen', True)
        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()
        self.cx = self.screen_width / 2
        self.cy = self.screen_height / 2

        self.window.configure(fg_color=COLOR_BG)
        self.window.bind("<Escape>", lambda e: self.window.destroy())

        # Colors (Reusing same palette)
        self.colors = {
            "bg_main": COLOR_BG,
            "card_bg": COLOR_CARD_BG,
            "card_border": COLOR_ACCENT_CYAN,
            "text_white": COLOR_TEXT_WHITE,
            "text_gray": "#AAAAAA",
            "input_bg": COLOR_INPUT_BG,
            "btn_cyan": COLOR_ACCENT_CYAN,
            "btn_hover": "#00B2CC"
        }

        self.canvas = tk.Canvas(self.window, bg=self.colors["bg_main"], height=self.screen_height, width=self.screen_width, bd=0, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.draw_ui()

        # Ensure the form gets focus and is raised above the parent (defensive)
        try:
            self.window.grab_set()
            self.window.focus_force()
            self.window.lift()
        except Exception:
            pass

    def round_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def draw_ui(self):
        # Card
        w, h = 450, 550
        self.round_rectangle(self.cx - w/2, self.cy - h/2, self.cx + w/2, self.cy + h/2, radius=30, fill=self.colors["card_bg"], outline=self.colors["card_border"], width=2)
        
        # Title
        self.canvas.create_text(self.cx, self.cy - 220, text="Edit Details", fill=self.colors["text_white"], font=("Times New Roman", 26))
        self.canvas.create_line(self.cx - 80, self.cy - 200, self.cx + 80, self.cy - 200, fill="white", width=1)

        # Inputs
        self.service_entry = self.create_input(self.cy - 125, "Service/App Name", self.service)
        self.username_entry = self.create_input(self.cy - 45, "Username/Email", self.username)
        # Show masked placeholder and enable edit-on-click for password field
        self.password_entry = self.create_input(self.cy + 35, "Password", self.decrypted_pw, is_password=True)
        self.notes_entry = self.create_input(self.cy + 115, "Notes (Optional)", self.notes)

        # Buttons
        self.create_save_button()
        
        cancel_text = self.canvas.create_text(self.cx, self.cy + 245, text="Cancel", fill=self.colors["text_gray"], font=("Arial", 10, "underline"))
        self.canvas.tag_bind(cancel_text, "<Button-1>", lambda e: self.window.destroy())

    def create_input(self, y_pos, label, default_value, is_password=False):
        self.canvas.create_text(self.cx, y_pos - 15, text=label, fill=self.colors["text_gray"], font=("Arial", 10))
        self.round_rectangle(self.cx - 150, y_pos, self.cx + 150, y_pos + 40, radius=10, fill=self.colors["input_bg"], outline="#555555")
        # Password field: show 7 literal asterisks and allow editing on first focus
        if is_password:
            entry = tk.Entry(self.window, bg=self.colors["input_bg"], fg="white", bd=0, font=("Arial", 11), insertbackground="white")
            entry.place(x=self.cx - 140, y=y_pos + 10, width=280, height=20)
            placeholder = "*" * 7
            entry.insert(0, placeholder)
            # track whether user replaced placeholder
            entry.password_changed = False
            # keep original decrypted password to preserve if user does not edit
            entry.original_password = default_value
            def on_focus_in(event):
                if not getattr(entry, "password_changed", False):
                    entry.delete(0, tk.END)
                    entry.config(show="*")   # mask user input
                    entry.password_changed = True
            entry.bind("<FocusIn>", on_focus_in)
            return entry

        # Non-password inputs: behave as before
        entry = tk.Entry(self.window, bg=self.colors["input_bg"], fg="white", bd=0, font=("Arial", 11), insertbackground="white")
        entry.place(x=self.cx - 140, y=y_pos + 10, width=280, height=20)
        entry.insert(0, default_value)
        return entry

    def create_save_button(self):
        y = self.cy + 200
        w, h = 200, 45
        btn = self.round_rectangle(self.cx - w/2, y - h/2, self.cx + w/2, y + h/2, radius=20, fill=self.colors["btn_cyan"], outline="")
        lbl = self.canvas.create_text(self.cx, y, text="Save Changes", fill="black", font=("Arial", 12, "bold"))

        def on_enter(e): self.canvas.itemconfig(btn, fill=self.colors["btn_hover"])
        def on_leave(e): self.canvas.itemconfig(btn, fill=self.colors["btn_cyan"])
        def on_click(e): self.save_changes()

        for tag in [btn, lbl]:
            self.canvas.tag_bind(tag, "<Enter>", on_enter)
            self.canvas.tag_bind(tag, "<Leave>", on_leave)
            self.canvas.tag_bind(tag, "<Button-1>", on_click)

    def save_changes(self):
        service = self.service_entry.get()
        username = self.username_entry.get()
        # If password field was never edited, keep original decrypted password
        if getattr(self.password_entry, "password_changed", False):
            password = self.password_entry.get()
        else:
            password = getattr(self.password_entry, "original_password", self.decrypted_pw)

        notes = self.notes_entry.get()

        if not service or not username or not password:
            messagebox.showerror("Error", "Please fill all required fields!")
            return

        # Re-encrypt and Save (backend unchanged)
        encrypted_pw = cipher.encrypt(password.encode()).decode()
        database.update_password(self.record_id, service, username, encrypted_pw, notes)
        
        messagebox.showinfo("Success", "Password updated successfully!")
        self.window.destroy()
        # Refresh the parent list
        if self.refresh_callback:
            self.refresh_callback()

# -----------------------------
# Function to open this window
# -----------------------------
def open_window(parent=None):
    # Create themed Edit window instance; do modal/focus on the underlying Toplevel
    app = GlassEditPassword(parent)
    try:
        # Use the actual Toplevel object held on the instance
        app.window.grab_set()
        app.window.focus_force()
    except Exception:
        pass
    return app

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    open_window()
    root.mainloop()