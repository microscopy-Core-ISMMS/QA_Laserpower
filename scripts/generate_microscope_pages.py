from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_DIR / "data"
PAGE_DIR = PROJECT_DIR / "microscopes"

PAGE_DIR.mkdir(parents=True, exist_ok=True)


def display_name(folder_name):
    return folder_name.replace("_", " ")


microscopes = sorted(
    [
        folder
        for folder in DATA_DIR.iterdir()
        if folder.is_dir()
        and not folder.name.startswith(".")
    ],
    key=lambda folder: folder.name.lower(),
)


# Remove previously generated microscope pages
for old_page in PAGE_DIR.glob("*.qmd"):
    if old_page.name != "index.qmd":
        old_page.unlink()


for microscope_dir in microscopes:

    microscope = microscope_dir.name
    title = display_name(microscope)

    page = PAGE_DIR / f"{microscope}.qmd"

    page.write_text(
        f"""---
title: "{title}"
toc: true
---

## Laser Power Calibration

The laser-power quality assurance results for **{title}** are shown below.

{{{{< include ../outputs/{microscope}/report.md >}}}}

## Download Data {{.unnumbered .unlisted}}

[Download {title} Excel workbook](../outputs/{microscope}/combined_power_data.xlsx){{.btn .btn-primary}}
""",
        encoding="utf-8",
    )

print(
    f"Generated {len(microscopes)} microscope pages."
)