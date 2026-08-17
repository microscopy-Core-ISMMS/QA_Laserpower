from pathlib import Path
import re


# --------------------------------------------------
# Project directories
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "outputs"
PAGE_DIR = PROJECT_DIR / "microscopes"

PAGE_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def display_name(name: str) -> str:
    """
    Convert folder names into human-readable microscope names.

    Example:
        LSM_980 -> LSM 980
    """
    return name.replace("_", " ")


def wavelength_from_name(path: Path) -> int:
    """
    Extract wavelength from plot filename.

    Examples:
        laser_power_405nm.png -> 405
        laser_power_max_488nm.png -> 488
    """

    match = re.search(r"(\d+)nm$", path.stem)

    if match:
        return int(match.group(1))

    return 99999


# --------------------------------------------------
# Detect microscopes automatically
# --------------------------------------------------

microscopes = sorted(
    [
        folder
        for folder in DATA_DIR.iterdir()
        if folder.is_dir()
        and not folder.name.startswith(".")
    ],
    key=lambda folder: folder.name.lower(),
)

# --------------------------------------------------
# Generate automatic navbar microscope menu
# --------------------------------------------------

NAVBAR_FILE = PROJECT_DIR / "_navbar.yml"

navbar_lines = [
    "website:",
    "  navbar:",
    "    left:",
    "      - href: index.ipynb",
    '        text: "Home"',
    '      - text: "Confocal Microscopes"',
    "        menu:",
    '          - text: "Laser Power Measurements"',
    "            href: microscopes/index.qmd",
]

NAVBAR_FILE.write_text(
    "\n".join(navbar_lines) + "\n",
    encoding="utf-8",
)

print(
    f"Generated navbar with "
    f"{len(microscopes)} microscopes."
)

# --------------------------------------------------
# Create microscope landing page
# --------------------------------------------------

index_lines = [
    "---",
    'title: "Laser Power Measurements"',
    "toc: true",
    "---",
    "",
    "## Introduction",
    "",
    "Quality assurance of illumination power stability is critical because "
    "fluorescence intensity measurements depend directly on the excitation "
    "power delivered to the sample. Under standard imaging conditions, the "
    "emitted fluorescence signal is proportional to the fluorophore "
    "concentration and the excitation light intensity. Any fluctuation in "
    "illumination power can therefore alter measured signal levels, potentially "
    "leading to incorrect conclusions about changes in fluorophore abundance, "
    "molecular interactions, or cellular dynamics. Ensuring stable and "
    "reproducible excitation conditions is essential for reliable quantitative "
    "fluorescence imaging.",
    "",
    "Over time, illumination sources such as lasers or LEDs can exhibit "
    "fluctuations due to component aging, temperature changes, electronic "
    "instability, or optical misalignment within the light path. These "
    "variations may occur over multiple time scales and can introduce unwanted "
    "variability between images acquired during a single experiment or across "
    "different experimental sessions. Routine monitoring of illumination power "
    "stability allows early detection of such fluctuations and helps ensure "
    "that excitation conditions remain consistent and reproducible.",
    "",
    "## Confocal Microscopes Laser-power Results",
    "",
    "Select a confocal microscope to view its laser-power quality assurance results.",
    "",
]


for microscope_dir in microscopes:

    microscope = microscope_dir.name
    title = display_name(microscope)

    index_lines.append(
        f"- [{title}]({microscope}.qmd)"
    )


(PAGE_DIR / "index.qmd").write_text(
    "\n".join(index_lines),
    encoding="utf-8",
)


# --------------------------------------------------
# Create one Quarto page per microscope
# --------------------------------------------------

for microscope_dir in microscopes:

    microscope = microscope_dir.name
    title = display_name(microscope)

    microscope_output = OUTPUT_DIR / microscope
    plot_dir = microscope_output / "plots"

    excel_path = (
        microscope_output /
        "combined_power_data.xlsx"
    )

    # ----------------------------------------------
    # Find calibration plots
    # ----------------------------------------------

    calibration_plots = []

    if plot_dir.exists():

        calibration_plots = sorted(
            [
                plot
                for plot in plot_dir.glob(
                    "laser_power_*nm.png"
                )
                if not plot.name.startswith(
                    "laser_power_max_"
                )
            ],
            key=wavelength_from_name,
        )

    # ----------------------------------------------
    # Find maximum-power plots
    # ----------------------------------------------

    maximum_plots = []

    if plot_dir.exists():

        maximum_plots = sorted(
            plot_dir.glob(
                "laser_power_max_*nm.png"
            ),
            key=wavelength_from_name,
        )

    # ----------------------------------------------
    # Start microscope page
    # ----------------------------------------------

    lines = [
        "---",
        f'title: "{title}"',
        "toc: true",
        "other-links:",
        '  - text: "← Back to Laser Power Measurements"',
        "    href: index.html",
        "---",
        "",
    ]

    # ----------------------------------------------
    # Calibration plots
    # ----------------------------------------------

    lines.extend([
        "## Laser Power Calibration",
        "",
    ])

    if calibration_plots:

        for plot in calibration_plots:

            wavelength = wavelength_from_name(plot)

            plot_title = (
                f"Laser Power - {wavelength} nm"
            )

            image_path = (
                f"../outputs/{microscope}/"
                f"plots/{plot.name}"
            )

            lines.extend([
                f"### {plot_title}",
                "",
                f"![{plot_title}]({image_path})",
                "",
            ])

    else:

        lines.extend([
            "No calibration plots are available.",
            "",
        ])

    # ----------------------------------------------
    # Maximum laser-power plots
    # ----------------------------------------------

    if maximum_plots:

        lines.extend([
            "## Maximum Laser Power",
            "",
        ])

        for plot in maximum_plots:

            wavelength = wavelength_from_name(plot)

            plot_title = (
                f"Maximum Laser Power - "
                f"{wavelength} nm"
            )

            image_path = (
                f"../outputs/{microscope}/"
                f"plots/{plot.name}"
            )

            lines.extend([
                f"### {plot_title}",
                "",
                f"![{plot_title}]({image_path})",
                "",
            ])

    # ----------------------------------------------
    # Excel download
    # ----------------------------------------------

    lines.extend([
        "## Download Data {.unnumbered .unlisted}",
        "",
    ])

    if excel_path.exists():

        excel_link = (
            f"../outputs/{microscope}/"
            "combined_power_data.xlsx"
        )

        lines.append(
            f"[Download {title} Excel workbook]"
            f"({excel_link})"
            "{.btn .btn-primary}"
        )

    else:

        lines.append(
            "The Excel workbook is not available."
        )

    lines.append("")

    # ----------------------------------------------
    # Write microscope page
    # ----------------------------------------------

    page_path = (
        PAGE_DIR /
        f"{microscope}.qmd"
    )

    page_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print(
        f"Generated microscope page: "
        f"{page_path.name}"
    )


print(
    f"Generated {len(microscopes)} microscope pages."
)