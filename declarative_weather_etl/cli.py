import argparse
import sys
from pathlib import Path
from pydantic import ValidationError

from config_parser import ResearchConfig
from pipeline import run_pipeline


def parse_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Declarative weather data ingestion pipeline targeting DuckDB.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=Path("exampl.yaml"),
        help="Path to configuration YAML file",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_cli_args()
    config_path: Path = args.config

    print(f" Reading configuration from: {config_path.resolve()}")

    try:
        config = ResearchConfig.load_from_yaml(config_path)
    except FileNotFoundError as e:
        print(f"❌ [Error] {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"❌ [YAML Error] {e}", file=sys.stderr)
        sys.exit(1)
    except ValidationError as e:
        print(f"❌ [Validation Error] Configuration failed validation:\n{e}", file=sys.stderr)
        sys.exit(1)

    print("\n Configuration Parsed Successfully!")
    print(f"• Database Engine : {config.database.engine.upper()}")
    print(f"• Database File   : {config.database.filepath}")
    print(f"• Target Table    : {config.database.table_name}")
    print(f"• Date Boundary   : {config.time_window.start_date} to {config.time_window.end_date}")
    print(f"• Locations Count : {len(config.locations)} location(s)")
    print(f"• Metrics ({len(config.requested_metrics)})     : {', '.join(config.requested_metrics)}")

    print("\n🚀 Executing Ingestion Pipeline...")
    try:
        # Pass the pre-parsed config object directly to avoid double YAML parsing
        records = run_pipeline(config)
        print(f" Pipeline complete! Successfully loaded {len(records)} records into DuckDB.")
    except Exception as e:
        print(f"❌ [Execution Error] Pipeline failed during execution: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()