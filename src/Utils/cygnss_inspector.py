"""CYGNSS L1 v3.2 data structure inspector.

This utility scans a set of CYGNSS NetCDF files, extracts structural metadata,
computes simple coverage statistics for key variables, and writes a Markdown
summary that can be used to guide downstream parsing logic.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

import numpy as np
import xarray as xr


# --- Data containers -------------------------------------------------------


@dataclass
class DimensionStats:
    sizes: List[int]

    @property
    def min(self) -> int:
        return int(min(self.sizes))

    @property
    def max(self) -> int:
        return int(max(self.sizes))

    @property
    def examples(self) -> str:
        sample = ", ".join(str(v) for v in self.sizes[:4])
        return sample + ("…" if len(self.sizes) > 4 else "")


@dataclass
class VarCoverage:
    units: str | None
    count_valid: int = 0
    count_total: int = 0
    sum_values: float = 0.0
    sum_sq_values: float = 0.0

    def update(self, arr: np.ndarray) -> None:
        if arr.size == 0:
            return
        data = np.asarray(arr, dtype=np.float64)
        finite_mask = np.isfinite(data)
        if not finite_mask.any():
            self.count_total += data.size
            return
        valid = data[finite_mask]
        self.count_valid += int(valid.size)
        self.count_total += int(data.size)
        self.sum_values += float(valid.sum())
        self.sum_sq_values += float(np.square(valid).sum())

    @property
    def coverage_pct(self) -> float:
        if self.count_total == 0:
            return 0.0
        return 100.0 * self.count_valid / self.count_total

    @property
    def mean(self) -> float | None:
        if self.count_valid == 0:
            return None
        return self.sum_values / self.count_valid

    @property
    def std(self) -> float | None:
        if self.count_valid == 0:
            return None
        mean = self.mean
        assert mean is not None
        variance = max(self.sum_sq_values / self.count_valid - mean**2, 0.0)
        return float(np.sqrt(variance))


# --- Helper functions ------------------------------------------------------


def iter_sample_files(root: Path, limit_per_spacecraft: int = 1) -> List[Path]:
    files: List[Path] = []
    for sid in range(1, 9):
        pattern = f"cyg{sid:02d}.ddmi.*.nc"
        matches = sorted(root.glob(pattern))
        if not matches:
            continue
        files.extend(matches[:limit_per_spacecraft])
    return files


def format_table(headers: Sequence[str], rows: Iterable[Sequence[str]]) -> str:
    header_line = "| " + " | ".join(headers) + " |"
    separator = "|" + "|".join([" --- " for _ in headers]) + "|"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header_line, separator, *body])


def inspect_files(paths: Sequence[Path]) -> Dict[str, str]:
    dim_samples: Dict[str, DimensionStats] = {}
    coord_dims: Dict[str, Counter] = defaultdict(Counter)
    reflectivity_vars = {
        "reflectivity_peak": VarCoverage(units="linear"),
        "ddm_nbrcs": VarCoverage(units="1"),
        "ddm_nbrcs_center": VarCoverage(units="1"),
        "ddm_nbrcs_peak": VarCoverage(units="1"),
    }
    coord_candidates = ["ddm_timestamp_utc", "sp_lat", "sp_lon", "sp_inc_angle"]
    coord_attrs: Dict[str, Dict[str, str]] = {}
    ddm_ant_counts: Counter = Counter()
    quality_flag_samples: Counter = Counter()

    for path in paths:
        with xr.open_dataset(path) as ds:
            # Dimensions
            for dim, size in ds.sizes.items():
                dim_stats = dim_samples.setdefault(dim, DimensionStats(sizes=[]))
                dim_stats.sizes.append(int(size))

            # Coordinates of interest
            for name in coord_candidates:
                if name in ds:
                    coord_dims[name][ds[name].dims] += 1
                    if name not in coord_attrs:
                        attrs = ds[name].attrs
                        coord_attrs[name] = {
                            "long_name": attrs.get("long_name", ""),
                            "units": attrs.get("units", ""),
                        }

            # DDM antenna distribution
            if "ddm_ant" in ds:
                values = np.asarray(ds["ddm_ant"].values).astype(np.int16)
                valid = values[np.isfinite(values)]
                ddm_ant_counts.update(valid.tolist())

            # Quality flags (sample a few unique values)
            if "quality_flags_2" in ds:
                q_values = np.asarray(ds["quality_flags_2"].values)
                sample = np.unique(q_values[np.isfinite(q_values)])
                for val in sample[:15]:
                    quality_flag_samples[str(int(val))] += 1

            # Reflectivity coverage
            for var, coverage in reflectivity_vars.items():
                if var in ds:
                    coverage.update(ds[var].values)

    # Build markdown fragments
    md_sections: Dict[str, str] = {}

    # Dimensions table
    dim_rows = []
    for dim, stats in sorted(dim_samples.items()):
        dim_rows.append(
            (
                dim,
                str(stats.min),
                str(stats.max),
                stats.examples,
            )
        )
    md_sections["dimensions"] = format_table(
        ["Dimension", "Min Size", "Max Size", "Examples"], dim_rows
    )

    # Coordinate overview
    coord_rows = []
    for name in coord_candidates:
        dims_seen = ", ".join(
            "×".join(d) + f" ({count} files)" for d, count in coord_dims[name].items()
        )
        attrs = coord_attrs.get(name, {})
        coord_rows.append(
            (
                name,
                dims_seen or "–",
                attrs.get("long_name", ""),
                attrs.get("units", ""),
            )
        )
    md_sections["coordinates"] = format_table(
        ["Coordinate", "Dims (files)", "Long Name", "Units"], coord_rows
    )

    # Reflectivity coverage
    refl_rows = []
    for var, coverage in reflectivity_vars.items():
        mean = coverage.mean
        std = coverage.std
        refl_rows.append(
            (
                var,
                coverage.units or "",
                f"{coverage.coverage_pct:.1f}%",
                "{:.3f}".format(mean) if mean is not None else "–",
                "{:.3f}".format(std) if std is not None else "–",
            )
        )
    md_sections["reflectivity"] = format_table(
        ["Variable", "Units", "Valid %", "Mean", "Std"], refl_rows
    )

    # DDM antenna counts
    ant_rows = []
    for val, count in sorted(ddm_ant_counts.items()):
        ant_rows.append((str(val), str(count)))
    md_sections["antennas"] = format_table(
        ["ddm_ant value", "Observations"], ant_rows
    )

    # Quality flag sample
    if quality_flag_samples:
        q_rows = []
        for val, count in quality_flag_samples.most_common(10):
            q_rows.append((val, str(count)))
        md_sections["quality_flags"] = format_table(
            ["quality_flags_2 value", "Files containing"], q_rows
        )

    return md_sections


def write_markdown(output: Path, files: Sequence[Path], sections: Dict[str, str]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# CYGNSS L1 v3.2 Structure Scan", ""]
    lines.append("## Files Sampled")
    for path in files:
        lines.append(f"- {path}")

    lines.append("")
    lines.append("## NetCDF Dimensions")
    lines.append(sections["dimensions"])

    lines.append("")
    lines.append("## Key Coordinates")
    lines.append(sections["coordinates"])

    lines.append("")
    lines.append("## Reflectivity Candidates")
    lines.append(sections["reflectivity"])

    lines.append("")
    lines.append("## ddm_ant Distribution")
    lines.append(sections["antennas"])

    if "quality_flags" in sections:
        lines.append("")
        lines.append("## quality_flags_2 Sample")
        lines.append(sections["quality_flags"])

    with output.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root",
        type=Path,
        help="Directory containing CYGNSS L1 v3.2 NetCDF files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("knowledge/cygnss_data_summary.md"),
        help="Markdown file to write",
    )
    parser.add_argument(
        "--limit-per-spacecraft",
        type=int,
        default=1,
        help="Number of files to sample per spacecraft (default: 1)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    files = iter_sample_files(args.root, args.limit_per_spacecraft)
    if not files:
        raise SystemExit(f"No NetCDF files found under {args.root}")
    sections = inspect_files(files)
    write_markdown(args.output, files, sections)


if __name__ == "__main__":
    main()
