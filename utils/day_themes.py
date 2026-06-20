# Weekday (English, as returned by dt.day_name()) → theme name
DAY_THEMES = {
    "Monday":    "Sausage",
    "Tuesday":   "Vital",      # likely a "health/light meal" category, common in German canteens
    "Wednesday": "Chicken",
    "Thursday":  "Schnitzel",  # could also translate as "Breaded Cutlet"
    "Friday":    "Fish",
}

# Veg/non-veg split ratio per theme (veg_ratio, non_veg_ratio) — must sum to 1.0
# Source: confirmed portions Mon 30:30, Tue 30:40, Wed 30:40, Thu 30:50, Fri 30:30
THEME_VEG_RATIO = {
    "Sausage":   (0.50, 0.50),  # 30 veg : 30 non-veg
    "Vital":     (0.43, 0.57),  # 30 veg : 40 non-veg
    "Chicken":   (0.43, 0.57),  # 30 veg : 40 non-veg
    "Schnitzel": (0.37, 0.63),  # 30 veg : 50 non-veg
    "Fish":      (0.50, 0.50),  # 30 veg : 30 non-veg
}
