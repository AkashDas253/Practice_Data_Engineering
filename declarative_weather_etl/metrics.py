from dataclasses import dataclass


@dataclass(frozen=True)
class MetricDefinition:
    alias: str
    api_param: str
    duckdb_type: str


# System-wide metric registry mapping user aliases to API fields and DuckDB datatypes
METRIC_REGISTRY: dict[str, MetricDefinition] = {
    "air_temp": MetricDefinition("air_temp", "temperature_2m", "DOUBLE"),
    "humidity": MetricDefinition("humidity", "relative_humidity_2m", "INTEGER"),
    "precipitation": MetricDefinition("precipitation", "precipitation", "DOUBLE"),
    "soil_moisture": MetricDefinition("soil_moisture", "soil_moisture_0_to_7cm", "DOUBLE"),
    "wind_speed": MetricDefinition("wind_speed", "wind_speed_10m", "DOUBLE"),
}