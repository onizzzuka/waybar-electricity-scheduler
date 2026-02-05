import json
import os
from datetime import datetime

import customtkinter as ctk

# setting up the appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CONFIG_PATH = os.path.expanduser("~/.config/waybar/electricity_schedule.json")


class ModernApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PowerSchedule")
        self.geometry("400x240")
        self.resizable(False, False)

        # Making the window "floating" for Hyprland (optional)
        self.attributes("-topmost", True)

        self.today = datetime.now().strftime("%A")

        # main frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.label = ctk.CTkLabel(
            self.main_frame,
            text=f"Schedule for {self.today}",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.label.pack(pady=(15, 5))

        self.sub_label = ctk.CTkLabel(
            self.main_frame,
            text="Intervals (e.g. 8-10, 14:30-17)",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        self.sub_label.pack(pady=(0, 10))

        # Input field
        self.entry = ctk.CTkEntry(
            self.main_frame,
            width=300,
            placeholder_text="Enter hours...",
            height=35,
            corner_radius=10,
            justify="center",
        )
        self.entry.pack(pady=10)

        # Load data
        current_raw = self.load_raw_data()
        self.entry.insert(0, current_raw)
        self.entry.focus_set()

        # Button
        self.button = ctk.CTkButton(
            self.main_frame,
            text="UPDATE",
            command=self.save,
            corner_radius=10,
            font=ctk.CTkFont(weight="bold"),
        )
        self.button.pack(pady=(10, 15))

        # Bind Enter key
        self.bind("<Return>", lambda event: self.save())

    def load_raw_data(self):
        if os.path.exists(CONFIG_PATH + ".raw"):
            with open(CONFIG_PATH + ".raw", "r") as f:
                return json.load(f).get("text", "")
        return ""

    def parse_time(self, t_str):
        t_str = t_str.strip().replace(".", ":")
        if ":" in t_str:
            h, m = map(int, t_str.split(":"))
        else:
            h, m = int(t_str), 0
        return h * 60 + m

    def save(self):
        try:
            txt = self.entry.get()
            slots = [0] * 48
            if txt.strip():
                for interval in txt.split(","):
                    start_s, end_s = interval.split("-")
                    for m in range(
                        self.parse_time(start_s), self.parse_time(end_s), 30
                    ):
                        idx = m // 30
                        if 0 <= idx < 48:
                            slots[idx] = 1

            with open(CONFIG_PATH, "w") as f:
                json.dump({"current_day": self.today, "slots": slots}, f)
            with open(CONFIG_PATH + ".raw", "w") as f:
                json.dump({"text": txt}, f)

            # Force update Waybar (if configured)
            os.system("pkill -RTMIN+8 waybar")
            self.destroy()
        except:
            self.entry.configure(border_color="red")


if __name__ == "__main__":
    app = ModernApp()
    app.mainloop()
