# Demo Log Data

This directory contains the log files used by the example configuration.

## Input Files

| File              | Description                         |
| ----------------- | ----------------------------------- |
| `application.log` | Application-style HTTP request logs |

Additional `.log` files can be added to this directory. The example configuration discovers all matching files using:

```text
./data/logs/*.log
```

## Log Format

Each record contains:

* date
* log level
* HTTP status code
* HTTP method
* request path
* optional message

Example:

```text
2026-09-13 ERROR 500 GET /api/orders Database connection failed
```

### Run

From the project root:

```bash
python cli.py --config demo_log_data/example.yaml
```

The demo filters the input records so that only `ERROR` records are written to:

```text
demo_log_data/output/errors.csv
```
