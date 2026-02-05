#!/usr/bin/env python3
import json
import os
from datetime import datetime

CONFIG_PATH = os.path.expanduser("~/.config/waybar/electricity_schedule.json")


def get_status():
    # 1. check if config file exists
    if not os.path.exists(CONFIG_PATH):
        return json.dumps(
            {
                "text": "󱐋 Enter schedule",
                "class": "unknown",
                "tooltip": "Click to configure",
            }
        )

    try:
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        # 2. what if file is empty or corrupted
        return json.dumps({"text": "󱐋 JSON error", "class": "unknown"})

    now = datetime.now()
    today_name = now.strftime("%A")

    # 3. check if config file is up to date
    if data.get("current_day") != today_name:
        return json.dumps(
            {
                "text": "󱐋 Update schedule",
                "class": "warning",
                "tooltip": "Schedule is outdated",
            }
        )

    day_slots = data.get("slots", [0] * 48)
    current_minute_total = now.hour * 60 + now.minute
    current_slot = current_minute_total // 30

    is_off = day_slots[current_slot] == 1

    # calculate time to next change
    remaining_in_slot = 30 - (current_minute_total % 30)
    extra_minutes = 0
    check_slot = (current_slot + 1) % 48

    # loop until we find a different slot
    while day_slots[check_slot] == day_slots[current_slot]:
        extra_minutes += 30
        check_slot = (check_slot + 1) % 48
        if check_slot == current_slot:
            break

    total_rem = remaining_in_slot + extra_minutes
    h, m = divmod(total_rem, 60)

    # style
    status_class = "normal"
    if is_off:
        icon = "󱎔 OFF"
        status_class = "off"
    else:
        if total_rem <= 20:
            icon = " CRITICAL"
            status_class = "critical"
        elif total_rem <= 60:
            icon = " SOON"
            status_class = "warning"
        else:
            icon = "󰚥 ON"

    # tooltip
    tooltip = f"Today: {'NO ELECTRICITY' if any(day_slots) else 'THERE IS LIGHT'}\n"
    for hour in range(24):
        s1 = "█" if day_slots[hour * 2] == 1 else "░"
        s2 = "█" if day_slots[hour * 2 + 1] == 1 else "░"
        tooltip += f"{hour:02d}: {s1}{s2}  "
        if (hour + 1) % 4 == 0:
            tooltip += "\n"

    return json.dumps(
        {"text": f"{icon} {h}h {m:02d}m", "class": status_class, "tooltip": tooltip}
    )


if __name__ == "__main__":
    print(get_status())
