from pathlib import Path
from datetime import datetime
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# --------------------------------------------------
# Project directories
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parents[1]

PSF_DATA_DIR = (
    PROJECT_DIR
    / "data"
    / "PSF_Measurements"
)

PSF_OUTPUT_DIR = (
    PROJECT_DIR
    / "outputs"
    / "PSF_Measurements"
)


# --------------------------------------------------
# Detect microscopes
# --------------------------------------------------

def detect_microscopes(folder: Path) -> list[Path]:

    if not folder.exists():
        return []

    return sorted(
        [
            path
            for path in folder.iterdir()
            if path.is_dir()
            and not path.name.startswith(".")
        ],
        key=lambda path: path.name.lower(),
    )


# --------------------------------------------------
# Detect objectives from filenames
# --------------------------------------------------

def detect_objectives(csv_files: list[Path]) -> list[str]:

    objectives = set()

    for file_path in csv_files:

        filename = file_path.name.lower()

        match = re.search(
            r"(\d+x[wo]?)",
            filename,
        )

        if match:
            objectives.add(
                match.group(1)
            )

    return sorted(objectives)


# --------------------------------------------------
# Parse one PSF CSV
# --------------------------------------------------

def parse_psf_csv(file_path: Path) -> pd.DataFrame:
    """
    Parse MaxX, MaxY and MaxZ measurements from
    one PSF CSV file.

    This preserves the logic from the original
    PSF notebook.
    """

    with file_path.open(
        "r",
        encoding="latin1",
    ) as file:

        lines = [
            line.strip()
            for line in file
        ]

    # ----------------------------------------------
    # Extract measurement date from filename
    # ----------------------------------------------

    date_match = re.search(
        r"(\d{1,2})-(\d{2})",
        file_path.name,
    )

    if date_match:

        month = int(
            date_match.group(1)
        )

        year = (
            2000
            + int(date_match.group(2))
        )

        date_obj = datetime(
            year=year,
            month=month,
            day=1,
        )

    else:

        date_obj = None


    # ----------------------------------------------
    # PSF sections
    # ----------------------------------------------

    sections = {
        "X": "maxx",
        "Y": "maxy",
        "Z": "maxz",
    }

    section_data = {}


    # ----------------------------------------------
    # Parse each section
    # ----------------------------------------------

    for axis, section_name in sections.items():

        header_index = next(
            (
                index
                for index, line
                in enumerate(lines)
                if line.lower().startswith(
                    f"ch,{section_name}"
                )
            ),
            None,
        )

        if header_index is None:

            section_data[axis] = {}
            continue


        values = {}

        for line in lines[
            header_index + 1:
        ]:

            # Stop when next channel section starts
            if line.lower().startswith("ch,"):
                break

            if not line:
                continue

            if line.startswith("FWHM"):
                continue

            parts = line.split(",")

            if len(parts) < 2:
                continue

            try:

                channel = int(
                    parts[0]
                )

                if channel in values:
                    continue

                raw_value = parts[1]

                if raw_value == "-----":

                    value = np.nan

                else:

                    value = float(
                        raw_value
                    )

                    if value == 0:
                        value = np.nan

                values[channel] = value

            except (
                ValueError,
                TypeError,
            ):

                continue

        section_data[axis] = values


    # ----------------------------------------------
    # Determine all channels
    # ----------------------------------------------

    all_channels = sorted(
        set(
            list(
                section_data["X"].keys()
            )
            + list(
                section_data["Y"].keys()
            )
            + list(
                section_data["Z"].keys()
            )
        )
    )


    # ----------------------------------------------
    # Build records
    # ----------------------------------------------

    records = []

    for channel in all_channels:

        x = section_data["X"].get(
            channel,
            np.nan,
        )

        y = section_data["Y"].get(
            channel,
            np.nan,
        )

        z = section_data["Z"].get(
            channel,
            np.nan,
        )

        if (
            np.isnan(x)
            and np.isnan(y)
        ):

            avg_xy = np.nan

        else:

            avg_xy = np.nanmean(
                [x, y]
            )


        records.append(
            {
                "Date": date_obj,

                # Same channel numbering behavior
                # as your original notebook.
                "Channel": (
                    f"CH{channel + 1}"
                ),

                "MaxX": x,
                "MaxY": y,
                "AvgXY": avg_xy,
                "MaxZ": z,

                "SourceFile": (
                    file_path.name
                ),
            }
        )


    return pd.DataFrame(
        records
    )


# --------------------------------------------------
# Create XY plot
# --------------------------------------------------

def plot_psf_xy(
    dataframe: pd.DataFrame,
    objective: str,
    output_folder: Path,
) -> Path | None:

    if dataframe.empty:
        return None

    figure, axis = plt.subplots(
        figsize=(8, 5)
    )

    plotted = False

    for channel in (
        dataframe["Channel"].unique()
    ):

        channel_data = dataframe[
            dataframe["Channel"]
            == channel
        ].copy()

        channel_data = channel_data[
            ~channel_data[
                "AvgXY"
            ].isna()
        ]

        if channel_data.empty:
            continue

        axis.plot(
            channel_data["Date_str"],
            channel_data["AvgXY"],
            marker="o",
            label=channel,
        )

        plotted = True


    if not plotted:

        plt.close(figure)
        return None


    axis.set_title(
        f"PSF XY - Objective {objective}"
    )

    axis.set_ylabel(
        "XY (µm)"
    )

    axis.legend(
        title="Channel"
    )

    axis.tick_params(
        axis="x",
        rotation=45,
    )

    axis.grid(
        True,
        linestyle="--",
        alpha=0.5,
    )

    figure.tight_layout()


    output_path = (
        output_folder
        / f"PSF_XY_{objective}.png"
    )

    figure.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)

    return output_path


# --------------------------------------------------
# Create Z plot
# --------------------------------------------------

def plot_psf_z(
    dataframe: pd.DataFrame,
    objective: str,
    output_folder: Path,
) -> Path | None:

    if dataframe.empty:
        return None

    figure, axis = plt.subplots(
        figsize=(8, 5)
    )

    plotted = False


    for channel in (
        dataframe["Channel"].unique()
    ):

        channel_data = dataframe[
            dataframe["Channel"]
            == channel
        ].copy()

        channel_data = channel_data[
            ~channel_data[
                "MaxZ"
            ].isna()
        ]

        if channel_data.empty:
            continue


        axis.plot(
            channel_data["Date_str"],
            channel_data["MaxZ"],
            marker="o",
            label=channel,
        )

        plotted = True


    if not plotted:

        plt.close(figure)
        return None


    axis.set_title(
        f"PSF Z - Objective {objective}"
    )

    axis.set_ylabel(
        "Z (µm)"
    )

    axis.legend(
        title="Channel"
    )

    axis.tick_params(
        axis="x",
        rotation=45,
    )

    axis.grid(
        True,
        linestyle="--",
        alpha=0.5,
    )

    figure.tight_layout()


    output_path = (
        output_folder
        / f"PSF_Z_{objective}.png"
    )

    figure.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)

    return output_path


# --------------------------------------------------
# Run PSF analysis for one microscope
# --------------------------------------------------

def run_psf_analysis(
    microscope_dir: Path,
    output_dir: Path,
):

    microscope = microscope_dir.name

    print("")
    print(
        f"Processing PSF: {microscope}"
    )


    csv_files = sorted(
        microscope_dir.glob(
            "*.csv"
        )
    )


    if not csv_files:

        print(
            f"No PSF CSV files found "
            f"for {microscope}."
        )

        return


    objectives = detect_objectives(
        csv_files
    )


    print(
        "Objectives:",
        ", ".join(objectives)
        or "None",
    )


    plot_folder = (
        output_dir / "plots"
    )

    plot_folder.mkdir(
        parents=True,
        exist_ok=True,
    )


    # Remove old plots so stale plots
    # cannot remain on the website.
    for old_plot in (
        plot_folder.glob("*.png")
    ):

        old_plot.unlink()


    all_records = []


    # ----------------------------------------------
    # Process files by objective
    # ----------------------------------------------

    for objective in objectives:

        objective_files = [
            file_path
            for file_path
            in csv_files
            if objective
            in file_path.name.lower()
        ]


        for file_path in objective_files:

            try:

                dataframe = (
                    parse_psf_csv(
                        file_path
                    )
                )

                if dataframe.empty:
                    continue

                dataframe[
                    "Objective"
                ] = objective

                all_records.append(
                    dataframe
                )


            except Exception as exc:

                print(
                    "Skipping unreadable file: "
                    f"{file_path.name}"
                )

                print(
                    f"  {exc}"
                )


    # ----------------------------------------------
    # Combine data
    # ----------------------------------------------

    if not all_records:

        print(
            "No readable PSF data found."
        )

        return


    combined_df = pd.concat(
        all_records,
        ignore_index=True,
    )


    combined_df = (
        combined_df
        .sort_values(
            [
                "Objective",
                "Date",
                "Channel",
            ]
        )
        .reset_index(drop=True)
    )


    # ----------------------------------------------
    # Save combined data
    # ----------------------------------------------

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )


    combined_csv_path = (
        output_dir
        / "combined_PSF_data.csv"
    )


    combined_df.to_csv(
        combined_csv_path,
        index=False,
    )


    print(
        "Saved combined PSF data:",
        combined_csv_path,
    )


    # ----------------------------------------------
    # Create plots
    # ----------------------------------------------

    generated_plots = []


    for objective in objectives:

        df_obj = combined_df[
            combined_df["Objective"]
            == objective
        ].copy()


        if df_obj.empty:
            continue


        df_obj = df_obj.sort_values(
            "Date"
        )


        df_obj["Date_str"] = (
            df_obj["Date"]
            .dt.strftime("%Y-%m")
        )


        xy_plot = plot_psf_xy(
            df_obj,
            objective,
            plot_folder,
        )


        if xy_plot is not None:

            generated_plots.append(
                xy_plot
            )

            print(
                f"Saved: {xy_plot.name}"
            )


        z_plot = plot_psf_z(
            df_obj,
            objective,
            plot_folder,
        )


        if z_plot is not None:

            generated_plots.append(
                z_plot
            )

            print(
                f"Saved: {z_plot.name}"
            )


    return {
        "microscope": microscope,
        "data": combined_df,
        "plots": generated_plots,
        "combined_csv": (
            combined_csv_path
        ),
    }


# --------------------------------------------------
# Run all PSF microscopes
# --------------------------------------------------

psf_microscopes = (
    detect_microscopes(
        PSF_DATA_DIR
    )
)


print(
    "Detected PSF microscopes:",
    ", ".join(
        path.name
        for path
        in psf_microscopes
    )
    or "None",
)


for microscope_dir in psf_microscopes:

    microscope_output = (
        PSF_OUTPUT_DIR
        / microscope_dir.name
    )


    run_psf_analysis(
        microscope_dir,
        microscope_output,
    )


print("")
print(
    "PSF plotting complete."
)