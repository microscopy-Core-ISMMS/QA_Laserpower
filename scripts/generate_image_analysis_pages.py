from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]

IMAGE_ANALYSIS_DIR = (
    PROJECT_DIR / "image_analysis"
)

IMAGE_ANALYSIS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


analysis_pages = [
    {
        "title": "Fiji / ImageJ",
        "filename": "fiji_imagej.qmd",
    },
]


# --------------------------------------------------
# Image Analysis landing page
# --------------------------------------------------

index_lines = [
    "---",
    'title: "Image Analysis"',
    "toc: true",
    "---",
    "",
    "## Image Analysis Resources",
    "",
    (
        "This section provides image analysis workflows, "
        "protocols, and resources developed by the "
        "Microscopy and Advanced BioImaging CoRE."
    ),
    "",
    "## Software and Analysis Platforms",
    "",
    (
        "Select an image analysis platform to view "
        "available workflows and resources."
    ),
    "",
]


for page in analysis_pages:

    index_lines.append(
        f"- [{page['title']}]"
        f"({page['filename']})"
    )


(
    IMAGE_ANALYSIS_DIR / "index.qmd"
).write_text(
    "\n".join(index_lines) + "\n",
    encoding="utf-8",
)