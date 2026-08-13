from pathlib import Path
import re

PROJECT_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "outputs"
PAGE_DIR = PROJECT_DIR / "microscopes"

PAGE_DIR.mkdir(parents=True, exist_ok=True)


def display_name(name: str) -> str:
    return name.replace("_", " ")


def wavelength_from_name(path: Path) -> int:
    match = re.search(r"(\d+)nm$", path.stem)
    if match:
        return int(match.group(1))
    return 99999


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
# Create the microscope landing page
# --------------------------------------------------

index_lines = [
    "---",
    'title: "Microscopes"',
    "toc: false",
    "---",
    "",
    "Select a microscope to view its laser-power "
    "quality assurance results.",
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
# Create one page per microscope
# --------------------------------------------------

for microscope_dir in microscopes:

    microscope = microscope_dir.name
    title = display_name(microscope)

    microscope_output = OUTPUT_DIR / microscope
    plot_dir = microscope_output / "plots"
    excel_path = (
        microscope_output / "combined_power_data.xlsx"
    )

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

    maximum_plots = []

    if plot_dir.exists():
        maximum_plots = sorted(
            plot_dir.glob(
                "laser_power_max_*nm.png"
            ),
            key=wavelength_from_name,
        )

    lines = [
        "---",
        f'title: "{title}"',
        "toc: true",
        "---",
        "",
    ]

    # ----------------------------------------------
    # Calibration plots
    # ----------------------------------------------

    if calibration_plots:

        lines.extend([
            "## Laser Power Calibration",
            "",
        ])

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
            "## Laser Power Calibration",
            "",
            "No calibration plots are available.",
            "",
        ])

    # ----------------------------------------------
    # Maximum-power plots
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

    page_path = PAGE_DIR / f"{microscope}.qmd"

    page_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


print(
    f"Generated {len(microscopes)} microscope pages."
)