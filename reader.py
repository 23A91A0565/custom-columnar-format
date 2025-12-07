import struct
import zlib
import csv

MAGIC = b"MCF1"

TYPE_INT32 = 1
TYPE_FLOAT64 = 2
TYPE_STRING = 3


def read_header(f):
    """Read MAGIC, HEADER_SIZE, and HEADER structure."""
    magic = f.read(4)
    if magic != MAGIC:
        raise ValueError("Invalid file format: MAGIC mismatch")

    header_size = struct.unpack("<I", f.read(4))[0]
    header_bytes = f.read(header_size)

    offset = 0

    # Fixed header fields
    version = header_bytes[offset]
    offset += 1

    col_count = header_bytes[offset]
    offset += 1

    offset += 2  # RESERVED

    row_count = struct.unpack_from("<Q", header_bytes, offset)[0]
    offset += 8

    columns = []

    # Parse per-column metadata
    for _ in range(col_count):
        name_len = header_bytes[offset]
        offset += 1

        name = header_bytes[offset:offset + name_len].decode("utf-8")
        offset += name_len

        type_code = header_bytes[offset]
        offset += 1

        offset += 2  # RESERVED

        data_offset = struct.unpack_from("<Q", header_bytes, offset)[0]
        offset += 8

        comp_size = struct.unpack_from("<Q", header_bytes, offset)[0]
        offset += 8

        uncomp_size = struct.unpack_from("<Q", header_bytes, offset)[0]
        offset += 8

        col_info = {
            "name": name,
            "type": type_code,
            "data_offset": data_offset,
            "compressed_size": comp_size,
            "uncompressed_size": uncomp_size,
            "offsets_offset": None,
            "offsets_comp_size": None,
            "offsets_uncomp_size": None
        }

        if type_code == TYPE_STRING:
            col_info["offsets_offset"] = struct.unpack_from("<Q", header_bytes, offset)[0]
            offset += 8

            col_info["offsets_comp_size"] = struct.unpack_from("<Q", header_bytes, offset)[0]
            offset += 8

            col_info["offsets_uncomp_size"] = struct.unpack_from("<Q", header_bytes, offset)[0]
            offset += 8

        columns.append(col_info)

    return {
        "version": version,
        "row_count": row_count,
        "columns": columns,
        "header_size": header_size,
    }


def decompress_block(f, offset, comp_size, uncomp_size):
    """Read and decompress a column block."""
    f.seek(offset)
    compressed = f.read(comp_size)
    raw = zlib.decompress(compressed)

    if len(raw) != uncomp_size:
        raise ValueError("Decompressed size mismatch")

    return raw


def parse_int32_column(raw, row_count):
    values = []
    for i in range(row_count):
        value = struct.unpack_from("<i", raw, i * 4)[0]
        values.append(value)
    return values


def parse_float64_column(raw, row_count):
    values = []
    for i in range(row_count):
        value = struct.unpack_from("<d", raw, i * 8)[0]
        values.append(value)
    return values


def parse_string_column(blob_raw, offsets_raw, row_count):
    offsets = []
    for i in range(row_count):
        end = struct.unpack_from("<I", offsets_raw, i * 4)[0]
        offsets.append(end)

    strings = []
    start = 0

    for end in offsets:
        s = blob_raw[start:end].decode("utf-8")
        strings.append(s)
        start = end

    return strings


def read_custom_format(file_path, selected_columns=None):
    """Read custom .mcf file and return dict of columns."""
    with open(file_path, "rb") as f:
        meta = read_header(f)
        row_count = meta["row_count"]

        result = {}

        for col in meta["columns"]:
            name = col["name"]

            # If selective read is requested
            if selected_columns and name not in selected_columns:
                continue

            # 1. Read main column block
            raw = decompress_block(
                f,
                col["data_offset"],
                col["compressed_size"],
                col["uncompressed_size"]
            )

            # 2. Parse depending on type
            if col["type"] == TYPE_INT32:
                values = parse_int32_column(raw, row_count)

            elif col["type"] == TYPE_FLOAT64:
                values = parse_float64_column(raw, row_count)

            elif col["type"] == TYPE_STRING:
                # Need to read second block (offsets)
                off_raw = decompress_block(
                    f,
                    col["offsets_offset"],
                    col["offsets_comp_size"],
                    col["offsets_uncomp_size"]
                )

                values = parse_string_column(raw, off_raw, row_count)

            result[name] = values

        return result


def write_csv(data, output_path):
    """Write reconstructed table to CSV file."""
    columns = list(data.keys())
    rows = len(data[columns[0]])

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)

        for i in range(rows):
            row = [data[col][i] for col in columns]
            writer.writerow(row)


# ----------------------------
# RUN READER (Example)
# ----------------------------
if __name__ == "__main__":
    file_path = "output.mcf"     # from writer
    csv_output = "reconstructed.csv"

    table = read_custom_format(file_path)
    write_csv(table, csv_output)

    print("File successfully decoded → saved as reconstructed.csv")
