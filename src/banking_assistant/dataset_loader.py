"""Dataset utilities for local JSON and CSV sample files.

The banking assistant project keeps sample data inside a repository-local
``dataset/`` directory so exploratory notebooks and application code can load the
same inputs without hard-coding absolute paths.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List
import json

SUPPORTED_EXTENSIONS = {".csv", ".json", ".jsonl", ".ndjson"}


@dataclass(frozen=True)
class DatasetAsset:
    """Metadata describing a discovered dataset file."""

    name: str
    path: Path
    file_type: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "path": str(self.path),
            "file_type": self.file_type,
        }


@dataclass(frozen=True)
class DatasetSummary:
    """High-level summary for a loaded tabular dataset."""

    asset_name: str
    file_type: str
    row_count: int
    column_count: int
    columns: List[str]

    def to_dict(self) -> Dict[str, object]:
        return {
            "asset_name": self.asset_name,
            "file_type": self.file_type,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "columns": self.columns,
        }


def get_project_root() -> Path:
    """Return the repository root based on the installed package location."""

    return Path(__file__).resolve().parents[2]


def get_dataset_dir(create: bool = False) -> Path:
    """Return the expected dataset directory path.

    Args:
        create: Whether to create the directory if it does not already exist.
    """

    dataset_dir = get_project_root() / "dataset"
    if create:
        dataset_dir.mkdir(parents=True, exist_ok=True)
    return dataset_dir


def discover_dataset_assets(dataset_dir: Path | None = None) -> List[DatasetAsset]:
    """Discover supported JSON and CSV files under the dataset directory."""

    resolved_dir = dataset_dir or get_dataset_dir()
    if not resolved_dir.exists():
        return []

    assets = [
        DatasetAsset(
            name=path.stem,
            path=path,
            file_type=path.suffix.lower().lstrip("."),
        )
        for path in sorted(resolved_dir.iterdir())
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    return assets


def _require_pandas() -> Any:
    """Import pandas on demand and raise a helpful error if unavailable."""

    try:
        import pandas as pd
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "pandas is required to load local datasets. Install project dependencies from "
            "requirements.txt before calling dataset loader functions."
        ) from exc
    return pd


def load_dataset(asset_name: str, dataset_dir: Path | None = None):
    """Load a named dataset asset from the local dataset directory.

    Args:
        asset_name: File stem or full filename for a dataset.
        dataset_dir: Optional override for the dataset directory.

    Raises:
        FileNotFoundError: If the dataset directory or file is missing.
        ValueError: If the file extension is unsupported.
    """

    pd = _require_pandas()
    resolved_dir = dataset_dir or get_dataset_dir()
    if not resolved_dir.exists():
        raise FileNotFoundError(
            f"Dataset directory does not exist: {resolved_dir}. "
            "Create repo_root/dataset and place CSV or JSON files there."
        )

    candidate_paths = [resolved_dir / asset_name]
    if not Path(asset_name).suffix:
        candidate_paths.extend(resolved_dir / f"{asset_name}{suffix}" for suffix in sorted(SUPPORTED_EXTENSIONS))

    for path in candidate_paths:
        if path.exists() and path.is_file():
            suffix = path.suffix.lower()
            if suffix == ".csv":
                return pd.read_csv(path)
            if suffix in {".jsonl", ".ndjson"}:
                return pd.read_json(path, lines=True)
            if suffix == ".json":
                payload = json.loads(path.read_text())
                if isinstance(payload, list):
                    return pd.DataFrame(payload)
                if isinstance(payload, dict):
                    if len(payload) == 1 and isinstance(next(iter(payload.values())), list):
                        return pd.DataFrame(next(iter(payload.values())))
                    return pd.json_normalize(payload)
                raise ValueError(f"Unsupported JSON structure in {path}")
            raise ValueError(f"Unsupported dataset file type: {path.suffix}")

    available = ", ".join(asset.path.name for asset in discover_dataset_assets(resolved_dir)) or "none found"
    raise FileNotFoundError(
        f"Could not find dataset '{asset_name}' in {resolved_dir}. Available files: {available}."
    )


def summarize_dataset(asset_name: str, dataset_dir: Path | None = None) -> DatasetSummary:
    """Load a dataset and return a compact structural summary."""

    frame = load_dataset(asset_name, dataset_dir=dataset_dir)
    file_type = next(
        asset.file_type
        for asset in discover_dataset_assets(dataset_dir or get_dataset_dir())
        if asset.name == Path(asset_name).stem or asset.path.name == asset_name
    )
    return DatasetSummary(
        asset_name=Path(asset_name).stem,
        file_type=file_type,
        row_count=int(len(frame)),
        column_count=int(len(frame.columns)),
        columns=frame.columns.astype(str).tolist(),
    )


def summarize_available_datasets(dataset_dir: Path | None = None) -> List[Dict[str, object]]:
    """Return structural summaries for all discovered local datasets."""

    summaries: List[Dict[str, object]] = []
    for asset in discover_dataset_assets(dataset_dir):
        try:
            summaries.append(summarize_dataset(asset.path.name, dataset_dir=dataset_dir).to_dict())
        except ValueError as exc:
            summaries.append(
                {
                    "asset_name": asset.name,
                    "file_type": asset.file_type,
                    "error": str(exc),
                }
            )
    return summaries
