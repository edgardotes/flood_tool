import os
import re
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------
# CONFIG
# -------------------------
excel_file = "/Users/edolores/Documents/UBERN/Collaborations/Gaby/Data/new/campground_paper_table.xlsx"
sheet_name = "Sheet3"
output_root = "/Users/edolores/Documents/UBERN/Collaborations/Gaby/Data/new/impact_plots"

value_columns = [
    "L1: mobil",
    "L2:mobil",
    "L1:non-mobile",
    "L2:non-mobile"
]

plot_labels = [
    "L1 mobile",
    "L2 mobile",
    "L1 non-mobile",
    "L2 non-mobile"
]

impact_names = ["yellow", "orange", "red"]

# -------------------------
# HELPERS
# -------------------------
def safe_folder_name(name):
    return re.sub(r"[^\w\-]", "_", str(name).strip())

def parse_cell(cell):
    """
    Parse cells like:
      0
      '0'
      '33(11.34%)'
      12
    Returns:
      count (int), pct (float)
    """
    if pd.isna(cell):
        return 0, 0.0

    s = str(cell).strip()

    # Plain zero / integer
    if re.fullmatch(r"\d+", s):
        return int(s), 0.0

    # Pattern like 33(11.34%)
    m = re.fullmatch(r"(\d+)\s*\(\s*([\d.]+)\s*%\s*\)", s)
    if m:
        count = int(m.group(1))
        pct = float(m.group(2))
        return count, pct

    # Fallback: try extracting first integer
    m2 = re.search(r"(\d+)", s)
    if m2:
        return int(m2.group(1)), 0.0

    return 0, 0.0

def plot_impact(row, location, impact_name, threshold, output_path):
    counts = []
    percentages = []

    for col in value_columns:
        count, pct = parse_cell(row[col])
        counts.append(count)
        percentages.append(pct)

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(plot_labels, counts)

    ymax = max(counts) if max(counts) > 0 else 1
    ax.set_ylim(0, ymax * 1.25)

    for bar, count, pct in zip(bars, counts, percentages):
        height = bar.get_height()
        label = f"{count}\n({pct:.2f}%)"

        y = height + ymax * 0.02 if height > 0 else ymax * 0.03
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            y,
            label,
            ha="center",
            va="bottom",
            fontsize=10
        )

    ax.set_title(f"{location} - {impact_name.capitalize()} impact ({threshold} mm/h)")
    ax.set_ylabel("Counts")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

# -------------------------
# LOAD DATA
# -------------------------
df = pd.read_excel(excel_file, sheet_name=sheet_name)
df.columns = df.columns.str.strip()
df["Location"] = df["Location"].ffill()

# Optional debug
print("Columns:", df.columns.tolist())

# -------------------------
# MAIN LOOP
# -------------------------
for location, group in df.groupby("Location", sort=False):
    group = group.reset_index(drop=True)

    if len(group) < 3:
        print(f"Skipping {location}: fewer than 3 threshold rows.")
        continue

    loc_folder = os.path.join(output_root, safe_folder_name(location))
    os.makedirs(loc_folder, exist_ok=True)

    for i, impact_name in enumerate(impact_names):
        row = group.iloc[i]
        threshold = row["Physical thresholds (mm/h)"]
        output_file = os.path.join(loc_folder, f"{impact_name}_impact.png")
        plot_impact(row, location, impact_name, threshold, output_file)

    print(f"Saved plots for {location} in {loc_folder}")
