from datetime import date
from pathlib import Path
from typing import List, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
import yaml

from metrics import METRIC_REGISTRY


class DatabaseConfig(BaseModel):
    engine: Literal["duckdb"] = "duckdb"
    filepath: Path = Field(default=Path("./data/research.duckdb"))
    table_name: str = "weather_observations"

    @field_validator("filepath")
    def ensure_parent_directory_exists(cls, v: Path) -> Path:
        v.parent.mkdir(parents=True, exist_ok=True)
        return v


class ExecutionConfig(BaseModel):
    batch_size_days: int = Field(default=30, ge=1, le=365)
    export_csv_on_complete: bool = False
    csv_output_path: Path = Field(default=Path("./exports/output.csv"))

    @field_validator("csv_output_path")
    def ensure_export_directory_exists(cls, v: Path) -> Path:
        v.parent.mkdir(parents=True, exist_ok=True)
        return v


class TimeWindowConfig(BaseModel):
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_date_range(self) -> "TimeWindowConfig":
        if self.start_date > self.end_date:
            raise ValueError(
                f"start_date ({self.start_date}) cannot be after end_date ({self.end_date})."
            )
        return self


class LocationConfig(BaseModel):
    id: str
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)


class ResearchConfig(BaseModel):
    version: str
    database: DatabaseConfig
    execution: ExecutionConfig
    time_window: TimeWindowConfig
    locations: List[LocationConfig]
    requested_metrics: List[str]

    @field_validator("requested_metrics")
    def validate_metrics_exist(cls, metrics: List[str]) -> List[str]:
        if not metrics:
            raise ValueError("requested_metrics cannot be empty.")
        invalid = [m for m in metrics if m not in METRIC_REGISTRY]
        if invalid:
            valid_keys = ", ".join(METRIC_REGISTRY.keys())
            raise ValueError(
                f"Invalid metric(s) requested: {invalid}. Allowed metrics: [{valid_keys}]"
            )
        return metrics

    @classmethod
    def load_from_yaml(cls, yaml_path: Path) -> "ResearchConfig":
        if not yaml_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {yaml_path}")

        with open(yaml_path, "r", encoding="utf-8") as f:
            try:
                raw_data = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                raise ValueError(f"Malformed YAML content: {exc}") from exc

        if not isinstance(raw_data, dict):
            raise ValueError("YAML file must contain a key-value mapping at root level.")

        return cls(**raw_data)