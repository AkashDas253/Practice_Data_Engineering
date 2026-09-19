from typing import Dict, Any, Optional
import pyarrow as pa
import pyarrow.csv as pa_csv

from core.base import BaseReader


class CSVReader(BaseReader):
    """High-throughput CSV reader leveraging PyArrow's streaming C++ parser."""

    stage = "reader"
    type = "csv"

    def read_batches(self, batch_size: int) -> pa.RecordBatchReader:
        """Opens CSV file and streams RecordBatches directly."""
        read_options = pa_csv.ReadOptions(
            block_size=self.config.get("block_size", 16 * 1024 * 1024),  # 16 MB chunks
            encoding=self.config.get("encoding", "utf-8"),
            autogenerate_column_names=self.config.get("autogenerate_column_names", False),
        )

        parse_options = pa_csv.ParseOptions(
            delimiter=self.config.get("delimiter", ","),
            quote_char=self.config.get("quote_char", '"'),
            double_quote=self.config.get("double_quote", True),
            escape_char=self.config.get("escape_char", None),
            newlines_in_values=self.config.get("newlines_in_values", False),
        )

        convert_options = pa_csv.ConvertOptions(
            check_utf8=self.config.get("check_utf8", True),
            strings_can_be_null=self.config.get("strings_can_be_null", True),
            column_types=self.config.get("explicit_schema", None),
        )

        # returns PyArrow's native CSVStreamingReader (subclass of pa.RecordBatchReader)
        return pa_csv.open_csv(
            self.file_path,
            read_options=read_options,
            parse_options=parse_options,
            convert_options=convert_options,
        )