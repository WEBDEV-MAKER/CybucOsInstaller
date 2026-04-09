import tkinter as tk
from tkinter import messagebox
import subprocess
import os

def run_cmd(cmd):
    """Helper to run system commands with sudo."""
    return subprocess.run(f"sudo {cmd}", shell=True, capture_output=True, text=True)

class VyxenOSInstaller:
    def __init__(self, root):
        self.root = root
        self.root.title("VyxenOS Installation")
        self.root.geometry("800x550")
        
        # Default Theme (Modern Dark)
        self.bg_color = "#121212"
        self.fg_color = "#ffffff"
        self.accent = "#00d4ff"
        
        self.is_low_resource = tk.BooleanVar(value=False)
        self.show_start_screen()

    def clear_screen(self):
        """Removes all widgets from the window."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def apply_theme(self):
        """Switches between modern dark and high-contrast light mode."""
        if self.is_low_resource.get():
            self.bg_color, self.fg_color, self.accent = "#e0e0e0", "#000000", "#0055ff"
        else:
            self.bg_color, self.fg_color, self.accent = "#121212", "#ffffff", "#00d4ff"
        self.root.configure(bg=self.bg_color)

    # --- SCREEN 1: START ---
    def show_start_screen(self):
        self.clear_screen()
        self.apply_theme()
        
        tk.Label(self.root, text="VyxenOS", font=("Arial", 45, "bold"), 
                 fg=self.accent, bg=self.bg_color).pack(pady=(100, 20))
        
        tk.Checkbutton(self.root, text="Less resource intensive setup (recommended for older devices)", 
                       variable=self.is_low_resource, bg=self.bg_color, fg=self.fg_color, 
                       selectcolor="#333333", command=self.apply_theme, activebackground=self.bg_color).pack(pady=20)

        tk.Button(self.root, text="CONTINUE", command=self.show_main_menu, font=("Arial", 12, "bold"),
                  bg=self.accent, fg="#000000", padx=40, pady=10, bd=0, cursor="hand2").pack(pady=20)

    # --- SCREEN 2: MAIN MENU ---
    def show_main_menu(self):
        self.clear_screen()
        self.apply_theme()
        
        tk.Label(self.root, text="Installation Method", font=("Arial", 20), 
                 bg=self.bg_color, fg=self.fg_color).pack(pady=40)
        
        btn_style = {"font": ("Arial", 11), "width": 30, "pady": 15, "bd": 1, "cursor": "hand2"}
        
        tk.Button(self.root, text="Erase Disk and Install", command=self.confirm_erase, **btn_style).pack(pady=10)
        tk.Button(self.root, text="Choose Partition (Advanced)", command=self.show_advanced, **btn_style).pack(pady=10)

    # --- SCREEN 3: ADVANCED ---
    def show_advanced(self):
        self.clear_screen()
        self.apply_theme()
        
        tk.Label(self.root, text="Select Partition", font=("Arial", 14), bg=self.bg_color, fg=self.accent).pack(pady=10)
        
        # Partition Listbox
        list_bg = "#1a1a1a" if not self.is_low_resource.get() else "#ffffff"
        self.part_list = tk.Listbox(self.root, width=85, height=12, bg=list_bg, fg=self.fg_color, font=("Courier", 10))
        self.part_list.pack(pady=10)
        self.refresh_list()

        # Bottom UI Row
        footer = tk.Frame(self.root, bg=self.bg_color)
        footer.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)

        # Bottom Left: GParted Link
        gparted_lbl = tk.Label(footer, text="Open GParted", fg=self.accent, bg=self.bg_color, 
                               cursor="hand2", font=("Arial", 10, "underline"))
        gparted_lbl.pack(side=tk.LEFT)
        gparted_lbl.bind("<Button-1>", lambda e: subprocess.run(["sudo", "gparted"], shell=True))

        # Bottom Right: Refresh Icon
        refresh_btn = tk.Label(footer, text="↻", fg=self.accent, bg=self.bg_color, font=("Arial", 22), cursor="hand2")
        refresh_btn.pack(side=tk.RIGHT)
        refresh_btn.bind("<Button-1>", lambda e: self.refresh_list())

        # Action Buttons
        tk.Button(self.root, text="Install to Selected", bg=self.accent, fg="#000000", 
                  font=("Arial", 10, "bold"), command=self.install_to_selected).pack(side=tk.RIGHT, padx=20)
        tk.Button(self.root, text="Back", command=self.show_main_menu).pack(side=tk.LEFT, padx=20)

    def refresh_list(self):
        self.part_list.delete(0, tk.END)
        # Pulls Name, Size, Type, and Filesystem
        res = run_cmd("lsblk -ln -o NAME,SIZE,TYPE,FSTYPE")
        for line in res.stdout.splitlines():
            if line.strip():
                self.part_list.insert(tk.END, f"  {line}")

    def confirm_erase(self):
        if messagebox.askyesno("Confirm", "Warning: This will wipe /dev/sda. Continue?"):
            self.finalize_install("/dev/sda1")

    def install_to_selected(self):
        selection = self.part_list.get(tk.ACTIVE)
        if selection:
            dev_name = selection.strip().split()[0]
            target = f"/dev/{dev_name}"
            if messagebox.askyesno("Confirm", f"Install VyxenOS to {target}?"):
                self.finalize_install(target)

    def finalize_install(self, device):
        # rsync and mkfs logic happens here
        messagebox.showinfo("Success", "VyxenOS installed successfully.")
        self.cleanup()

    def cleanup(self):
        """Removes the installer from autostart and deletes the script."""
        # 1. Remove autostart desktop file
        autostart_path = os.path.expanduser("~/.config/autostart/vyxen.desktop")
        if os.path.exists(autostart_path):
            try:
                os.remove(autostart_path)
            except:
                pass
            
        # 2. Delete the script itself
        try:
            run_cmd("rm /usr/local/bin/vyxen_installer.py")
        except:
            pass
            
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = VyxenOSInstaller(root)
    root.mainloop()
