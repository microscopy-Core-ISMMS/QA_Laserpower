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

    Examples:
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


def objective_sort_key(name: str):
    """
    Sort objective names numerically.

    Examples:
        10x
        20xw
        40xo
        63xo
    """

    match = re.search(
        r"(\d+)",
        name,
    )

    if match:
        return (
            int(match.group(1)),
            name.lower(),
        )

    return (
        99999,
        name.lower(),
    )


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

NAVBAR_FILE = PROJECT_DIR / "_navbar.yml"

navbar_lines = [
    "website:",
    "  navbar:",
    "    left:",

    "      - href: index.html",
    '        text: "Home"',

    '      - text: "Quality Assessment - Confocal Microscopes"',
    "        menu:",
    '          - text: "Introduction"',
    "            href: microscopes/index.html",
    '          - text: "Laser Power Measurements"',
    "            href: microscopes/laser_power/index.html",
    '          - text: "PSF Measurements"',
    "            href: microscopes/psf/index.html",

    '      - text: "Image Analysis"',
    "        menu:",
    '          - text: "Introduction"',
    "            href: image_analysis/index.html",
    '          - text: "FIJI/ImageJ Workflows"',
    "            href: image_analysis/fiji_imagej/index.html",
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

    # Link to rendered HTML page
    laser_index_lines.append(
        f"- [{title}]({microscope}.html)"
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

    # ----------------------------------------------
    # Output locations
    # ----------------------------------------------

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
    # Find laser-power trend plots
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
    # Organize plots by wavelength
    # ----------------------------------------------

    calibration_by_wavelength = {
        wavelength_from_name(plot): plot
        for plot in calibration_plots
    }

    maximum_by_wavelength = {
        wavelength_from_name(plot): plot
        for plot in maximum_plots
    }


    wavelengths = sorted(
        set(
            calibration_by_wavelength.keys()
        )
        | set(
            maximum_by_wavelength.keys()
        )
    )


    # ----------------------------------------------
    # Start microscope page
    # ----------------------------------------------

    lines = [
        "---",
        f'title: "{title}"',
        "toc: true",
        "lightbox: true",
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
    # Laser Power Dashboard
    # ----------------------------------------------

    lines.extend([
        "## Laser Power Measurements",
        "",
    ])


    if wavelengths:

        for wavelength in wavelengths:

            lines.extend([
                f"### {wavelength} nm",
                "",
                "::: {.grid}",
                "",
            ])


            # ======================================
            # LEFT COLUMN
            # Laser Power Trend
            # ======================================

            lines.extend([
                (
                    "::: "
                    "{.g-col-12 .g-col-md-6 "
                    ".border .rounded .p-3}"
                ),
                "",
                "#### Laser Power Trend",
                "",
            ])


            calibration_plot = (
                calibration_by_wavelength.get(
                    wavelength
                )
            )


            if calibration_plot is not None:

                plot_title = (
                    f"Laser Power - "
                    f"{wavelength} nm"
                )

                image_path = (
                    f"../../outputs/"
                    f"{microscope}/"
                    f"plots/"
                    f"{calibration_plot.name}"
                )

                lines.extend([
                    (
                        f"![{plot_title}]"
                        f"({image_path})"
                    ),
                    "",
                ])

            else:

                lines.extend([
                    (
                        "No laser-power trend "
                        "plot is available."
                    ),
                    "",
                ])


            # Close left column
            lines.extend([
                ":::",
                "",
            ])


            # ======================================
            # RIGHT COLUMN
            # Maximum Laser Power
            # ======================================

            lines.extend([
                (
                    "::: "
                    "{.g-col-12 .g-col-md-6 "
                    ".border .rounded .p-3}"
                ),
                "",
                "#### Maximum Laser Power",
                "",
            ])


            maximum_plot = (
                maximum_by_wavelength.get(
                    wavelength
                )
            )


            if maximum_plot is not None:

                plot_title = (
                    "Maximum Laser Power - "
                    f"{wavelength} nm"
                )

                image_path = (
                    f"../../outputs/"
                    f"{microscope}/"
                    f"plots/"
                    f"{maximum_plot.name}"
                )

                lines.extend([
                    (
                        f"![{plot_title}]"
                        f"({image_path})"
                    ),
                    "",
                ])

            else:

                lines.extend([
                    (
                        "No maximum-power "
                        "plot is available."
                    ),
                    "",
                ])


            # Close right column
            lines.extend([
                ":::",
                "",
            ])


            # Close grid
            lines.extend([
                ":::",
                "",
            ])


    else:

        lines.extend([
            (
                "No laser-power plots "
                "are currently available."
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
            f"../../outputs/"
            f"{microscope}/"
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

    # Link to rendered HTML page
    psf_index_lines.append(
        f"- [{title}]({microscope}.html)"
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

for microscope_dir in psf_microscopes:

    microscope = microscope_dir.name
    title = display_name(microscope)


    # ----------------------------------------------
    # PSF output directories
    # ----------------------------------------------

    psf_output_dir = (
        OUTPUT_DIR
        / "PSF_Measurements"
        / microscope
    )

    psf_plot_dir = (
        psf_output_dir
        / "plots"
    )

    combined_psf_csv = (
        psf_output_dir
        / "combined_PSF_data.csv"
    )


    # ----------------------------------------------
    # Find XY PSF plots
    # ----------------------------------------------

    xy_plots = []

    if psf_plot_dir.exists():

        xy_plots = sorted(
            psf_plot_dir.glob(
                "PSF_XY_*.html"
            ),
            key=lambda path: path.name.lower(),
        )


    # ----------------------------------------------
    # Find Z PSF plots
    # ----------------------------------------------

    z_plots = []

    if psf_plot_dir.exists():

        z_plots = sorted(
            psf_plot_dir.glob(
                "PSF_Z_*.html"
            ),
            key=lambda path: path.name.lower(),
        )


    # ----------------------------------------------
    # Organize XY plots by objective
    # ----------------------------------------------

    xy_by_objective = {}

    for plot in xy_plots:

        objective = (
            plot.stem
            .replace(
                "PSF_XY_",
                ""
            )
        )

        xy_by_objective[
            objective
        ] = plot


    # ----------------------------------------------
    # Organize Z plots by objective
    # ----------------------------------------------

    z_by_objective = {}

    for plot in z_plots:

        objective = (
            plot.stem
            .replace(
                "PSF_Z_",
                ""
            )
        )

        z_by_objective[
            objective
        ] = plot


    # ----------------------------------------------
    # Determine all objectives
    # ----------------------------------------------

    objectives = sorted(
        set(
            xy_by_objective.keys()
        )
        | set(
            z_by_objective.keys()
        ),
        key=objective_sort_key,
    )


    # ----------------------------------------------
    # Start PSF microscope page
    # ----------------------------------------------

    psf_lines = [
        "---",
        f'title: "{title}"',
        "toc: true",
        "lightbox: true",
        "other-links:",
        (
            '  - text: '
            '"← Back to PSF Measurements"'
        ),
        "    href: index.html",
        "---",
        "",
    ]


    # ----------------------------------------------
    # PSF Dashboard
    # ----------------------------------------------

    psf_lines.extend([
        "## PSF Measurements",
        "",
    ])


    if objectives:

        for objective in objectives:

            display_objective = (
                objective.upper()
            )


            psf_lines.extend([
                (
                    f"### "
                    f"{display_objective} Objective"
                ),
                "",
                "::: {.grid}",
                "",
            ])


            # ======================================
            # LEFT COLUMN
            # Lateral PSF XY
            # ======================================

            psf_lines.extend([
                (
                    "::: "
                    "{.g-col-12 .g-col-md-6 "
                    ".border .rounded .p-3}"
                ),
                "",
                "#### Lateral PSF (XY)",
                "",
            ])


            xy_plot = (
                xy_by_objective.get(
                    objective
                )
            )


           if xy_plot is not None:

                plot_path = (
                    f"../../outputs/"
                    f"PSF_Measurements/"
                    f"{microscope}/"
                    f"plots/"
                    f"{xy_plot.name}"
                )

                psf_lines.extend(
                    [
                        '<div class="plotly-dashboard">',
                        (
                            f'<iframe '
                            f'src="{plot_path}" '
                            f'width="100%" '
                            f'height="520" '
                            f'style="border:none;" '
                            f'loading="lazy">'
                            f'</iframe>'
                        ),
                        "</div>",
                        "",
                    ]
                )


                psf_lines.extend([
                    (
                        f"![{plot_title}]"
                        f"({image_path})"
                    ),
                    "",
                ])

            else:

                psf_lines.extend([
                    (
                        "No lateral PSF "
                        "plot is available."
                    ),
                    "",
                ])


            # Close left column
            psf_lines.extend([
                ":::",
                "",
            ])


            # ======================================
            # RIGHT COLUMN
            # Axial PSF Z
            # ======================================

            psf_lines.extend([
                (
                    "::: "
                    "{.g-col-12 .g-col-md-6 "
                    ".border .rounded .p-3}"
                ),
                "",
                "#### Axial PSF (Z)",
                "",
            ])


            z_plot = (
                z_by_objective.get(
                    objective
                )
            )


            if z_plot is not None:

                plot_path = (
                    f"../../outputs/"
                    f"PSF_Measurements/"
                    f"{microscope}/"
                    f"plots/"
                    f"{z_plot.name}"
                )

                psf_lines.extend(
                    [
                        '<div class="plotly-dashboard">',
                        (
                            f'<iframe '
                            f'src="{plot_path}" '
                            f'width="100%" '
                            f'height="520" '
                            f'style="border:none;" '
                            f'loading="lazy">'
                            f'</iframe>'
                        ),
                        "</div>",
                        "",
                    ]
                )

                psf_lines.extend(
                    [
                        f"### {objective.upper()}",
                        "",
                        "::: {.grid}",
                        "",
                        "::: {.g-col-12 .g-col-md-6 .border .rounded .p-3}",
                        "",
                        "#### Lateral PSF (XY)",
                        "",
                    ]
                )

                psf_lines.extend(
                    [
                        "",
                        ":::",
                        "",
                        "::: {.g-col-12 .g-col-md-6 .border .rounded .p-3}",
                        "",
                        "#### Axial PSF (Z)",
                        "",
                    ]
                )

                psf_lines.extend(
                    [
                        "",
                        ":::",
                        "",
                        ":::",
                        "",
                    ]
                )
                
                psf_lines.extend([
                    (
                        f"![{plot_title}]"
                        f"({image_path})"
                    ),
                    "",
                ])

            else:

                psf_lines.extend([
                    (
                        "No axial PSF "
                        "plot is available."
                    ),
                    "",
                ])


            # Close right column
            psf_lines.extend([
                ":::",
                "",
            ])


            # Close grid
            psf_lines.extend([
                ":::",
                "",
            ])


    else:

        psf_lines.extend([
            (
                "No PSF plots are "
                "currently available."
            ),
            "",
        ])


    # ----------------------------------------------
    # PSF data download
    # ----------------------------------------------

    psf_lines.extend([
        (
            "## Download Data "
            "{.unnumbered .unlisted}"
        ),
        "",
    ])


    if combined_psf_csv.exists():

        csv_link = (
            f"../../outputs/"
            f"PSF_Measurements/"
            f"{microscope}/"
            "combined_PSF_data.csv"
        )

        psf_lines.append(
            f"[Download {title} PSF data]"
            f"({csv_link})"
            "{.btn .btn-primary}"
        )

    else:

        psf_lines.append(
            "The combined PSF data file "
            "is not available."
        )


    psf_lines.append("")


    # ----------------------------------------------
    # Write PSF microscope page
    # ----------------------------------------------

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