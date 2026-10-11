import csv
import json
from pathlib import Path


def generate_multi_scenario_files():
    data_dir = Path("examples/data")
    data_dir.mkdir(parents=True, exist_ok=True)

    # 1. CSV Variant 1: Basic user schema
    with open(
        data_dir / "users_v1.csv",
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["user_id", "username", "score"])
        writer.writerow([1, "alice", "95.5"])
        writer.writerow([2, "bob", "82.0"])

    # 2. CSV Variant 2: Extended user schema
    with open(
        data_dir / "users_v2.csv",
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)
        writer.writerow([
            "user_id",
            "username",
            "score",
            "country",
            "signup_date",
        ])
        writer.writerow([3, "charlie", "88.0", "USA", "2026-01-10"])
        writer.writerow([4, "david", "91.2", "CAN", "2026-02-15"])

    # 3. JSON Variant 1: Basic event records
    with open(
        data_dir / "events_v1.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            [
                {
                    "event_id": 101,
                    "action": "login",
                    "timestamp": 1710000000,
                },
                {
                    "event_id": 102,
                    "action": "click",
                    "timestamp": 1710000060,
                },
            ],
            file,
            indent=2,
        )

    # 4. JSON Variant 2: Extended event schema
    with open(
        data_dir / "events_v2.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            [
                {
                    "event_id": 103,
                    "action": "logout",
                    "timestamp": 1710003600,
                    "session_duration": 3600,
                }
            ],
            file,
            indent=2,
        )

    # 5. Nested JSON: Optional fields and nested objects
    with open(
        data_dir / "orders_nested.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            [
                {
                    "order_id": 1001,
                    "customer": {
                        "customer_id": 1,
                        "name": "Alice",
                    },
                    "total": 125.50,
                },
                {
                    "order_id": 1002,
                    "customer": {
                        "customer_id": 2,
                        "name": "Bob",
                    },
                    "total": 80,
                    "discount": True,
                },
            ],
            file,
            indent=2,
        )

    # 6. NDJSON: Records with different fields
    with open(
        data_dir / "events_stream.ndjson",
        "w",
        encoding="utf-8",
    ) as file:
        records = [
            {"event_id": 201, "action": "login"},
            {"event_id": 202, "action": "purchase", "amount": 49.99},
            {"event_id": 203, "action": "logout"},
        ]

        for record in records:
            file.write(json.dumps(record) + "\n")

    # 7. Pipe-delimited TXT
    with open(
        data_dir / "employees_pipe.txt",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(
            "employee_id|name|department|salary\n"
            "101|Alice|Engineering|75000\n"
            "102|Bob|Finance|68000\n"
        )

    # 8. Semicolon-delimited TXT
    with open(
        data_dir / "products_semicolon.txt",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(
            "product_id;product_name;price;stock\n"
            "501;Keyboard;49.99;25\n"
            "502;Mouse;19.50;40\n"
        )

    # 9. Tab-separated values
    with open(
        data_dir / "inventory.tsv",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(
            "item_id\titem_name\tquantity\n"
            "1001\tMonitor\t12\n"
            "1002\tLaptop\t8\n"
        )

    # 10. Key-value TXT
    with open(
        data_dir / "system_config.txt",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(
            "service=payment;port=8080;enabled=true\n"
            "service=notification;port=9090;enabled=false\n"
        )

    # 11. Fixed-width TXT
    with open(
        data_dir / "accounts_fixed.txt",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(
            "1001 Alice      00025\n"
            "1002 Benjamin   00030\n"
            "1003 Charlotte  00028\n"
        )

    # 12. Plain TXT: No reliable tabular schema
    with open(
        data_dir / "application_log.txt",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(
            "Application started successfully.\n"
            "\n"
            "Loading configuration files.\n"
            "Database connection established.\n"
            "Application is ready.\n"
        )

    # 13. CSV with missing values
    with open(
        data_dir / "users_nullable.csv",
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["user_id", "username", "age", "city"])
        writer.writerow([10, "emma", 29, "London"])
        writer.writerow([11, "liam", "", ""])
        writer.writerow([12, "olivia", 34, "Toronto"])

    # 14. CSV with inconsistent record widths
    with open(
        data_dir / "transactions_inconsistent.csv",
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["transaction_id", "amount", "status"])
        writer.writerow([1, 125.50, "completed"])
        writer.writerow([2, 75.00])
        writer.writerow([3, 300.00, "pending", "unexpected"])

    print(f"[SUCCESS] Test files generated in '{data_dir.resolve()}/'")
    print("\nGenerated scenarios:")

    for path in sorted(data_dir.iterdir()):
        if path.is_file():
            print(f" - {path.name}")


if __name__ == "__main__":
    generate_multi_scenario_files()