"""Shared visualization utilities for the Map Encryption Library notebooks."""
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display, Markdown


def plot_demographic_bar(acs, title="Racial / ethnic composition and poverty (ACS 2022)",
                         annotation_x=82, figsize=(10, 5)):
    """Horizontal grouped seaborn bar of racial/ethnic composition with poverty annotations.

    Parameters
    ----------
    acs : DataFrame with columns zip_code, pct_hispanic, pct_black, pct_white,
          pct_poverty, med_income_k.  Sorted ascending by pct_poverty before plotting.
    title : Chart title string.
    annotation_x : x-position (% of ZIP population) for the poverty/income label.
    figsize : (width, height) in inches.
    """
    import pandas as pd
    acs_plot = acs.sort_values("pct_poverty", ascending=True).copy()
    acs_plot["zip_code"] = acs_plot["zip_code"].astype(str)

    race_cols = {
        "pct_hispanic": "Hispanic / Latino (any race)",
        "pct_black":    "Black / African American",
        "pct_white":    "White (alone)",
    }
    melted = acs_plot.melt(
        id_vars=["zip_code", "pct_poverty", "med_income_k"],
        value_vars=list(race_cols.keys()),
        var_name="race_col", value_name="pct",
    )
    melted["Race / ethnicity"] = melted["race_col"].map(race_cols)

    palette = {
        "Hispanic / Latino (any race)": "#d62728",
        "Black / African American":     "#1f77b4",
        "White (alone)":                "#aec7e8",
    }
    zips_ordered = acs_plot["zip_code"].tolist()

    fig, ax = plt.subplots(figsize=figsize)
    sns.barplot(
        data=melted, x="pct", y="zip_code",
        hue="Race / ethnicity", palette=palette,
        order=zips_ordered, orient="h", ax=ax,
    )
    for i, row in enumerate(acs_plot.itertuples()):
        ax.text(
            annotation_x, i,
            f"{int(row.pct_poverty)}% pov | ${int(row.med_income_k)}k",
            va="center", ha="left", fontsize=8, color="#444",
        )
    ax.set_xlim(0, annotation_x + 30)
    ax.set_xlabel("% of ZIP population")
    ax.set_ylabel("ZIP code")
    ax.set_title(title)
    ax.legend(loc="upper right", bbox_to_anchor=(1, 1.12), ncol=3, fontsize=9)
    sns.despine()
    plt.tight_layout()
    plt.show()


def show_md_table(df, title=None):
    """Render a pandas DataFrame as a markdown table in a Jupyter notebook.

    Parameters
    ----------
    df : DataFrame to display.
    title : Optional bold heading rendered above the table.
    """
    header = "| " + " | ".join(str(c) for c in df.columns) + " |"
    sep    = "| " + " | ".join("---" for _ in df.columns) + " |"
    rows = [header, sep]
    for _, row in df.iterrows():
        rows.append("| " + " | ".join(str(v) for v in row) + " |")
    md = (f"**{title}**\n\n" if title else "") + "\n".join(rows)
    display(Markdown(md))
