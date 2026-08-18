from pathlib import Path
import re


# --------------------------------------------------
# Project directories
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "outputs"

# Measurement data directories
LASER_DATA_DIR = (
    DATA_DIR / "Laser_Power_Measurements"
)

PSF_DATA_DIR = (
    DATA_DIR / "PSF_Measurements"
)

# Main microscope page directory
MICROSCOPE_PAGE_DIR = (
    PROJECT_DIR / "microscopes"
)

# Generated measurement page directories
LASER_PAGE_DIR = (
    MICROSCOPE_PAGE_DIR / "laser_power"
)

PSF_PAGE_DIR = (
    MICROSCOPE_PAGE_DIR / "psf"
)

# Create generated-page directories.
# This does NOT overwrite microscopes/index.qmd.
LASER_PAGE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

PSF_PAGE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def display_name(name: str) -> str:
    """
    Convert folder names into human-readable microscope names.

    Example:
        LSM_980 -> LSM 980
        Andor_Dragonfly_620 -> Andor Dragonfly 620
    """

    return name.replace("_", " ")


def wavelength_from_name(path: Path) -> int:
    """
    Extract wavelength from plot filename.

    Examples:
        laser_power_405nm.png -> 405
        laser_power_max_488nm.png -> 488
    """

    match = re.search(
        r"(\d+)nm$",
        path.stem,
    )

    if match:
        return int(match.group(1))

    return 99999


def detect_microscopes(data_folder: Path):
    """
    Return microscope directories inside a measurement folder.

    Hidden directories are ignored.
    """

    if not data_folder.exists():
        print(
            f"Warning: data directory does not exist: "
            f"{data_folder}"
        )
        return []

    return sorted(
        [
            folder
            for folder in data_folder.iterdir()
            if folder.is_dir()
            and not folder.name.startswith(".")
        ],
        key=lambda folder: folder.name.lower(),
    )


# --------------------------------------------------
# Detect microscopes automatically
# --------------------------------------------------

laser_microscopes = detect_microscopes(
    LASER_DATA_DIR
)

psf_microscopes = detect_microscopes(
    PSF_DATA_DIR
)


print(
    "Laser Power microscopes:",
    ", ".join(
        folder.name
        for folder in laser_microscopes
    )
    or "None",
)

print(
    "PSF microscopes:",
    ", ".join(
        folder.name
        for folder in psf_microscopes
    )
    or "None",
)


# --------------------------------------------------
# Generate automatic navbar
# --------------------------------------------------

NAVBAR_FILE = (
    PROJECT_DIR / "_navbar.yml"
)

navbar_lines = [
    "website:",
    "  navbar:",
    "    left:",
    "      - href: index.ipynb",
    '        text: "Home"',
    '      - text: "Confocal Microscopes"',
    "        menu:",
    '          - text: "Laser Power Measurements"',
    (
        "            href: "
        "microscopes/laser_power/index.qmd"
    ),
    '          - text: "PSF Measurements"',
    (
        "            href: "
        "microscopes/psf/index.qmd"
    ),
]

NAVBAR_FILE.write_text(
    "\n".join(navbar_lines) + "\n",
    encoding="utf-8",
)

print(
    "Generated navbar:"
)

print(
    f"  Laser Power Measurements: "
    f"{len(laser_microscopes)} microscopes"
)

print(
    f"  PSF Measurements: "
    f"{len(psf_microscopes)} microscopes"
)


# ==================================================
# LASER POWER MEASUREMENTS
# ==================================================


# --------------------------------------------------
# Create Laser Power landing page
# --------------------------------------------------

laser_index_lines = [
    "---",
    (
        'title: "Confocal Microscopes - '
        'Laser Power Measurements"'
    ),
    "toc: true",
    "---",
    "",
    "## Introduction",
    "",
    (
        "Quality assurance of illumination power stability "
        "is critical because fluorescence intensity "
        "measurements depend directly on the excitation "
        "power delivered to the sample. Under standard "
        "imaging conditions, the emitted fluorescence "
        "signal is proportional to the fluorophore "
        "concentration and the excitation light intensity. "
        "Any fluctuation in illumination power can therefore "
        "alter measured signal levels, potentially leading "
        "to incorrect conclusions about changes in "
        "fluorophore abundance, molecular interactions, "
        "or cellular dynamics. Ensuring stable and "
        "reproducible excitation conditions is essential "
        "for reliable quantitative fluorescence imaging."
    ),
    "",
    (
        "Over time, illumination sources such as lasers or "
        "LEDs can exhibit fluctuations due to component "
        "aging, temperature changes, electronic instability, "
        "or optical misalignment within the light path. "
        "These variations may occur over multiple time "
        "scales and can introduce unwanted variability "
        "between images acquired during a single experiment "
        "or across different experimental sessions. Routine "
        "monitoring of illumination power stability allows "
        "early detection of such fluctuations and helps "
        "ensure that excitation conditions remain "
        "consistent and reproducible."
    ),
    "",
    "## Laser Power Results",
    "",
    (
        "Select a confocal microscope to view its "
        "laser-power measurements."
    ),
    "",
]


for microscope_dir in laser_microscopes:

    microscope = microscope_dir.name
    title = display_name(microscope)

    laser_index_lines.append(
        f"- [{title}]({microscope}.qmd)"
    )


(LASER_PAGE_DIR / "index.qmd").write_text(
    "\n".join(laser_index_lines) + "\n",
    encoding="utf-8",
)

print(
    "Generated Laser Power landing page."
)


# --------------------------------------------------
# Create one Laser Power page per microscope
# --------------------------------------------------

for microscope_dir in laser_microscopes:

    microscope = microscope_dir.name
    title = display_name(microscope)

    # NOTE:
    # This keeps your existing output structure:
    #
    # outputs/
    #     LSM_880/
    #         plots/
    #         combined_power_data.xlsx
    #
    # If you later reorganize outputs too,
    # this section can be changed separately.

    microscope_output = (
        OUTPUT_DIR / microscope
    )

    plot_dir = (
        microscope_output / "plots"
    )

    excel_path = (
        microscope_output
        / "combined_power_data.xlsx"
    )


    # ----------------------------------------------
    # Find laser-power measurement plots
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
        (
            '  - text: '
            '"← Back to Laser Power Measurements"'
        ),
        "    href: index.html",
        "---",
        "",
    ]


    # ----------------------------------------------
    # Laser Power Measurements
    # ----------------------------------------------

    lines.extend([
        "## Laser Power Measurements",
        "",
    ])


    if calibration_plots:

        for plot in calibration_plots:

            wavelength = (
                wavelength_from_name(plot)
            )

            plot_title = (
                f"Laser Power - "
                f"{wavelength} nm"
            )

            # Page now lives at:
            #
            # microscopes/laser_power/LSM_880.qmd
            #
            # therefore ../../ returns to project root.

            image_path = (
                f"../../outputs/{microscope}/"
                f"plots/{plot.name}"
            )

            lines.extend([
                f"### {plot_title}",
                "",
                (
                    f"![{plot_title}]"
                    f"({image_path})"
                ),
                "",
            ])

    else:

        lines.extend([
            (
                "No laser-power measurement "
                "plots are available."
            ),
            "",
        ])


    # ----------------------------------------------
    # Maximum Laser Power
    # ----------------------------------------------

    if maximum_plots:

        lines.extend([
            "## Maximum Laser Power",
            "",
        ])

        for plot in maximum_plots:

            wavelength = (
                wavelength_from_name(plot)
            )

            plot_title = (
                "Maximum Laser Power - "
                f"{wavelength} nm"
            )

            image_path = (
                f"../../outputs/{microscope}/"
                f"plots/{plot.name}"
            )

            lines.extend([
                f"### {plot_title}",
                "",
                (
                    f"![{plot_title}]"
                    f"({image_path})"
                ),
                "",
            ])


    # ----------------------------------------------
    # Excel download
    # ----------------------------------------------

    lines.extend([
        (
            "## Download Data "
            "{.unnumbered .unlisted}"
        ),
        "",
    ])


    if excel_path.exists():

        excel_link = (
            f"../../outputs/{microscope}/"
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
    # Write Laser Power microscope page
    # ----------------------------------------------

    page_path = (
        LASER_PAGE_DIR
        / f"{microscope}.qmd"
    )

    page_path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    print(
        "Generated Laser Power page: "
        f"{page_path.name}"
    )


print(
    "Generated "
    f"{len(laser_microscopes)} "
    "Laser Power microscope pages."
)


# ==================================================
# PSF MEASUREMENTS
# ==================================================


# --------------------------------------------------
# Create PSF landing page
# --------------------------------------------------

psf_index_lines = [
    "---",
    (
        'title: "Confocal Microscopes - '
        'PSF Measurements"'
    ),
    "toc: true",
    "---",
    "",
    "## Introduction",
    "",
    (
        "Point spread function (PSF) measurements are used "
        "to evaluate the spatial resolution and optical "
        "performance of a microscope."
    ),
    "",
    (
        "Routine PSF measurements can help identify changes "
        "in microscope alignment, objective performance, "
        "optical aberrations, and other factors that may "
        "affect image quality and quantitative microscopy "
        "measurements."
    ),
    "",
    "## PSF Results",
    "",
    (
        "Select a confocal microscope to view its "
        "PSF measurements."
    ),
    "",
]


for microscope_dir in psf_microscopes:

    microscope = microscope_dir.name
    title = display_name(microscope)

    psf_index_lines.append(
        f"- [{title}]({microscope}.qmd)"
    )


(PSF_PAGE_DIR / "index.qmd").write_text(
    "\n".join(psf_index_lines) + "\n",
    encoding="utf-8",
)

print(
    "Generated PSF landing page."
)


# --------------------------------------------------
# Create one PSF page per microscope
# --------------------------------------------------
#
# These are currently placeholder pages.
#
# Once the format of your PSF data and plots is defined,
# we will replace this section with the actual PSF
# analysis/plot discovery code.
# --------------------------------------------------

for microscope_dir in psf_microscopes:

    microscope = microscope_dir.name
    title = display_name(microscope)

    psf_lines = [
        "---",
        f'title: "{title}"',
        "toc: true",
        "other-links:",
        (
            '  - text: '
            '"← Back to PSF Measurements"'
        ),
        "    href: index.html",
        "---",
        "",
        "## PSF Measurements",
        "",
        (
            "PSF measurement results will be "
            "displayed here."
        ),
        "",
    ]


    psf_page_path = (
        PSF_PAGE_DIR
        / f"{microscope}.qmd"
    )


    psf_page_path.write_text(
        "\n".join(psf_lines) + "\n",
        encoding="utf-8",
    )


    print(
        "Generated PSF page: "
        f"{psf_page_path.name}"
    )


print(
    "Generated "
    f"{len(psf_microscopes)} "
    "PSF microscope pages."
)


# --------------------------------------------------
# Finished
# --------------------------------------------------

print("")
print("----------------------------------------")
print("Page generation complete")
print("----------------------------------------")

print(
    "Laser Power pages:"
    f" {LASER_PAGE_DIR}"
)

print(
    "PSF pages:"
    f" {PSF_PAGE_DIR}"
)