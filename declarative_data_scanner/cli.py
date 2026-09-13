import argparse

import yaml

from engine import Engine


def main():
    parser = argparse.ArgumentParser(
        description="Declarative Data Scanner"
    )

    parser.add_argument(
        "--config",
        required=True,
        help="Path to YAML configuration",
    )

    args = parser.parse_args()

    with open(args.config, encoding="utf-8") as file:
        config = yaml.safe_load(file)

    Engine(config).run()


if __name__ == "__main__":
    main()
