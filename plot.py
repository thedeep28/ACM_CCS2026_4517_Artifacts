import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

# ===============================
# LOAD DATA
# ===============================

keys = pd.read_csv("ech-datekeycount-output-mar-and-apr.txt")
providers = pd.read_csv("ech_provider_summary_mar-and-apr2026.csv")

# -------------------------------
# FIX DATES
# -------------------------------

keys["date"] = pd.to_datetime(keys["date"], errors="coerce")

providers["date"] = (
    providers["date"]
    .str.replace("/", "", regex=False)
    .str.replace("-", "", regex=False)
)
providers["date"] = pd.to_datetime(providers["date"], format="%Y%m%d", errors="coerce")

keys = keys.dropna(subset=["date"])
providers = providers.dropna(subset=["date"])

providers["provider"] = providers["provider"].str.lower()

# ===============================
# FIGURE 1: CLOUDFLARE KEY VARIATION ONLY
# ===============================

# # Get cloudflare domains per day

# number of keys used by cloudflare
cf_keys = providers[providers["provider"] == "cloudflare"][["date", "unique_keys"]]
cf_keys = cf_keys.sort_values("date")

plt.figure(figsize=(6,4))

# plt.fill_between(cf_keys["date"], 0, cf_keys["unique_keys"],
#                  color="tab:rrggbb")

plt.plot(cf_keys["date"], cf_keys["unique_keys"],
         color="tab:blue", linewidth=2)

# plt.plot(
#     cf_keys["date"],
#     cf_keys["unique_keys"],
#     color="tab:blue",
#     linewidth=2,
#     marker='o',
#     markersize=2,
#     markerfacecolor='white',
#     markeredgecolor='tab:blue',
#     markeredgewidth=1
# )

# FORCE exact limits
plt.xlim(cf_keys["date"].min(), cf_keys["date"].max())

# plt.text(pd.Timestamp("2026-03-15"), 1, "March 2026", ha='center', va='top')
# plt.text(pd.Timestamp("2026-04-15"), 1, "April 2026", ha='center', va='top')
# plt.axvline(pd.Timestamp("2026-04-01"), color='gray', linestyle='--', alpha=0.5)

# plt.xlabel("60 Day Measurement Window")
plt.ylabel("Unique ECH keys\n(Cloudflare)")
# plt.title("Cloudflare Key Pool Variation")

plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d"))

ax = plt.gca()

# # Keep only left + bottom
# ax.spines['top'].set_visible(False)
# ax.spines['right'].set_visible(False)

# # Optional: make bottom/left slightly thicker
# ax.spines['left'].set_linewidth(1.2)
# ax.spines['bottom'].set_linewidth(1.2)

ax = plt.gca()
plt.ylim(bottom=0)
ax.margins(y=0)

# Get y-position slightly below axis
y_pos = -0.1  # adjust if needed

# Add labels in axis-relative coordinates
ax.text(0.28, y_pos, "| - - - - - - - - - - March 2026 - - - - - - - - - - ",
        transform=ax.transAxes,
        ha='center', va='top')

ax.text(0.524, y_pos, "|",
        transform=ax.transAxes,
        ha='center', va='top')

ax.text(0.76, y_pos, " - - - - - - - - - - Apr 2026 - - - - - - - - |",
        transform=ax.transAxes,
        ha='center', va='top')

# Keep only left + bottom
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Optional: make bottom/left slightly thicker
ax.spines['left'].set_linewidth(1.2)
ax.spines['bottom'].set_linewidth(1.2)


# Move ticks outward slightly
ax.tick_params(axis='both', direction='out')

plt.grid(True, linestyle="--", alpha=0.4)
plt.tight_layout()
plt.show()


# ===============================
# FIGURE 2: ECH ADOPTION (COLORED, MATCH YOUR STYLE)
# ===============================

cf = providers[providers["provider"] == "cloudflare"][["date", "domains_count"]]
cf = cf.rename(columns={"domains_count": "cf"})

others = providers[providers["provider"] != "cloudflare"]
others = others.groupby("date")["domains_count"].sum().reset_index()
others = others.rename(columns={"domains_count": "others"})

df_plot = pd.merge(cf, others, on="date", how="outer").fillna(0).sort_values("date")

plt.figure(figsize=(6,4))

# stacked fill
plt.fill_between(df_plot["date"], 0, df_plot["cf"],
                 color="tab:blue", label="Cloudflare")

plt.fill_between(df_plot["date"],
                 df_plot["cf"],
                 df_plot["cf"] + df_plot["others"],
                 color="tab:orange", label="Other providers")

# optional outline
plt.plot(df_plot["date"], df_plot["cf"], color="black", linewidth=1)

# FORCE exact limits
plt.xlim(cf_keys["date"].min(), cf_keys["date"].max())

# plt.text(pd.Timestamp("2026-03-15"), 0.1, "March 2026", ha='center', va='top')
# plt.text(pd.Timestamp("2026-04-15"), 0.1, "April 2026", ha='center', va='top')
# plt.axvline(pd.Timestamp("2026-04-01"), color='gray', linestyle='--', alpha=0.5)

# plt.xlabel("60 Day Measurement Window")
plt.ylabel("ECH-enabled domains")
# plt.title("ECH Adoption Over Time")

plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d"))

ax = plt.gca()
plt.ylim(bottom=0)
ax.margins(y=0)

# Get y-position slightly below axis
y_pos = -0.1  # adjust if needed

# Add labels in axis-relative coordinates
ax.text(0.28, y_pos, "| - - - - - - - - - March 2026 - - - - - - - - - - ",
        transform=ax.transAxes,
        ha='center', va='top')

ax.text(0.524, y_pos, "|",
        transform=ax.transAxes,
        ha='center', va='top')

ax.text(0.78, y_pos, " - - - - - - - - - - Apr 2026 - - - - - - |",
        transform=ax.transAxes,
        ha='center', va='top')

ax.yaxis.set_major_formatter(
    mticker.FuncFormatter(lambda x, _: f"{int(x/1000)}K" if x >= 1000 else str(int(x)))
)

# Keep only left + bottom
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Optional: make bottom/left slightly thicker
ax.spines['left'].set_linewidth(1.2)
ax.spines['bottom'].set_linewidth(1.2)

# Move ticks outward slightly
ax.tick_params(axis='both', direction='out')

plt.legend(loc="lower right", bbox_to_anchor=(1,0.03))
plt.grid(True, linestyle="--", alpha=0.4)
plt.tight_layout()
plt.show()

# ===============================
# FIGURE 3: KEY CENTRALIZATION (YOUR EXACT CATEGORY SPLIT)
# ===============================

# pick representative day (max domains)
target_day = providers.groupby("date")["domains_count"].sum().idxmax()

day = providers[providers["date"] == target_day]

# print(target_day)

# map categories
mapping = {
    "cloudflare": "Cloudflare",
    "google.com": "Google",
    "pornhub.com": "pornhub.com",
    "ietf.org": "ietf.org"
}

labels = []
values = []

for p in mapping:
    val = day[day["provider"] == p]["domains_count"].sum()
    if val > 0:
        labels.append(mapping[p])
        values.append(val)

# everything else → Others
others_val = day[~day["provider"].isin(mapping.keys())]["domains_count"].sum()

labels.append("Others")
values.append(others_val)

plt.figure(figsize=(6,4))

plt.bar(labels, values,
        color=["tab:blue", "tab:orange", "tab:green", "tab:red", "lightgray"])

# plt.xlabel("ECH Key Centralization on April 17 2026")
plt.yscale("log")
plt.ylabel("Number of domains (log scale)")
# plt.title("ECH Key Centralization")

plt.text(0, values[0], f"{int(values[0]):,}",
         ha='center', va='bottom')
# plt.text(0, values[0]*0.5, "single dominant key",
#          ha='center', va='bottom', fontsize=9)

ax = plt.gca()

# ax.annotate(
#     "99.99%  ECH-enabled domains",
#     xy=(0.4, values[0]),                    # point to top of bar
#     xytext=(0.5, values[0]*1.2),          # text position (right + above)
#     arrowprops=dict(arrowstyle="->", lw=0.8),
#     ha='left',
#     va='bottom'
# )

# Keep only left + bottom
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Optional: make bottom/left slightly thicker
ax.spines['left'].set_linewidth(1.2)
ax.spines['bottom'].set_linewidth(1.2)

# Move ticks outward slightly
ax.tick_params(axis='both', direction='out')

plt.grid(True, which="both", linestyle="--", alpha=0.4)
plt.tight_layout()
plt.show()
