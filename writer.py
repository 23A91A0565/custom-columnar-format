import csv
import struct
import zlib

MAGIC = b"MCF1"  # 4 bytes magic prefix
VERSION = 1

TYPE_INT32 = 1
TYPE_FLOAT64 = 2
TYPE_STRING = 3


def pack_int32_list(values):
    """Pack list of integers into bytes (little-endian)."""
    return b"".join(struct.pack("<i", v) for v in values)


def pack_float64_list(values):
    """Pack list of floats into bytes (little-endian)."""
    return b"".join(struct.pack("<d", v) for v in values)


def pack_string_column(values):
    """
    Encode string column into:
    - concatenated UTF-8 byte blob
    - offsets array
    Returns (raw_blob_bytes, raw_offsets_bytes)
    """
    blob = b""
    offsets = []
    total = 0

    for s in values:
        encoded = s.encode("utf-8")
        blob += encoded
        total += len(encoded)
        offsets.append(total)

    offsets_bytes = b"".join(struct.pack("<I", x) for x in offsets)
    return blob, offsets_bytes


def read_csv_columns(csv_path):
    """Reads CSV and returns dict: column_name -> list of values."""
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columns = {col: [] for col in reader.fieldnames}

        for row in reader:
            for col in columns:
                columns[col].append(row[col])

    return columns


def infer_type(value):
    """Simple type inference."""
    try:
        int(value)
        return TYPE_INT32
    except:
        pass

    try:
        float(value)
        return TYPE_FLOAT64
    except:
        pass

    return TYPE_STRING


def convert_values(column_values, col_type):
    """Convert string CSV values into typed values."""
    if col_type == TYPE_INT32:
        return [int(v) for v in column_values]
    elif col_type == TYPE_FLOAT64:
        return [float(v) for v in column_values]
    elif col_type == TYPE_STRING:
        return [str(v) for v in column_values]


def write_custom_format(csv_path, output_path):
    columns = read_csv_columns(csv_path)
    col_names = list(columns.keys())
    row_count = len(next(iter(columns.values())))

    # Determine type for each column
    col_types = {}
    for col in col_names:
        col_types[col] = infer_type(columns[col][0])

    # Prepare blocks & metadata
    blocks = []  # list of dicts for each column's info
    current_offset = 0  # will fill later once HEADER_SIZE is known

    # Process each column
    for col in col_names:
        col_type = col_types[col]
        values = convert_values(columns[col], col_type)

        if col_type == TYPE_INT32:
            raw = pack_int32_list(values)
            comp = zlib.compress(raw)

            block = {
                "name": col,
                "type": col_type,
                "data": comp,
                "uncompressed_size": len(raw),
                "compressed_size": len(comp),
                "offsets_block": None  # for string columns only
            }

        elif col_type == TYPE_FLOAT64:
            raw = pack_float64_list(values)
            comp = zlib.compress(raw)

            block = {
                "name": col,
                "type": col_type,
                "data": comp,
                "uncompressed_size": len(raw),
                "compressed_size": len(comp),
                "offsets_block": None
            }

        elif col_type == TYPE_STRING:
            raw_blob, raw_offsets = pack_string_column(values)

            comp_blob = zlib.compress(raw_blob)
            comp_offsets = zlib.compress(raw_offsets)

            block = {
                "name": col,
                "type": col_type,
                "data": comp_blob,
                "uncompressed_size": len(raw_blob),
                "compressed_size": len(comp_blob),
                "offsets_block": {
                    "data": comp_offsets,
                    "uncompressed_size": len(raw_offsets),
                    "compressed_size": len(comp_offsets),
                }
            }

        blocks.append(block)

    # ------------------------------
    # BUILD HEADER
    # ------------------------------
    header = b""

    # Fixed header
    header += struct.pack("<B", VERSION)                      # VERSION
    header += struct.pack("<B", len(col_names))               # COLUMN_COUNT
    header += struct.pack("<H", 0)                            # RESERVED
    header += struct.pack("<Q", row_count)                    # ROW_COUNT

    # Per-column metadata
    offset_after_header = 0  # placeholder; updated after HEADER_SIZE known
    # We'll write final offsets later.

    # TEMPORARY list to store metadata for later patching
    metadata_entries = []

    for block in blocks:
        name_bytes = block["name"].encode("utf-8")
        header += struct.pack("<B", len(name_bytes))
        header += name_bytes

        header += struct.pack("<B", block["type"])
        header += struct.pack("<H", 0)  # RESERVED

        # Placeholder offsets (8 bytes each)
        header += struct.pack("<Q", 0)  # DATA_OFFSET
        header += struct.pack("<Q", block["compressed_size"])
        header += struct.pack("<Q", block["uncompressed_size"])

        if block["type"] == TYPE_STRING:
            header += struct.pack("<Q", 0)  # OFFSETS_OFFSET
            header += struct.pack("<Q", block["offsets_block"]["compressed_size"])
            header += struct.pack("<Q", block["offsets_block"]["uncompressed_size"])

        metadata_entries.append(block)

    # HEADER_SIZE is length of header
    HEADER_SIZE = len(header)

    # Compute actual offsets
    current_offset = 4 + 4 + HEADER_SIZE  # MAGIC + HEADER_SIZE + HEADER

    final_file = bytearray()
    final_file += MAGIC
    final_file += struct.pack("<I", HEADER_SIZE)
    final_file += header

    # Now write blocks and patch offsets
    patch_positions = []
    header_pos = 8  # MAGIC(4) + HEADER_SIZE(4)

    # Patch per-column offsets inside final_file
    for block in blocks:
        name_len = len(block["name"])
        entry_start = header_pos

        # Skip: VERSION, COLUMN_COUNT, RESERVED, ROW_COUNT (handled before)
        # Instead, find per-column metadata offset by scanning header
        
        # Move header_pos to this column's metadata entry
        # Metadata entry structure:
        #   NAME_LEN (1)
        #   NAME (NAME_LEN)
        #   TYPE_CODE (1)
        #   RESERVED (2)
        #   DATA_OFFSET (8)
        #   COMPRESSED_SIZE (8)
        #   UNCOMPRESSED_SIZE (8)
        #   (string extra fields optional)

        # Move header_pos to DATA_OFFSET position:
        # Actually easier: search for the correct location based on order
        
        # Correct approach: rewrite header separately with updated offsets
        # Simpler solution: rebuild final header after computing offsets
        # --------------------------------------------------------------

        pass  # We'll rebuild header below instead (clearer and easier)

    # -----------------------------------
    # Rebuild HEADER with correct offsets
    # -----------------------------------
    header = b""

    # Fixed header
    header += struct.pack("<B", VERSION)
    header += struct.pack("<B", len(col_names))
    header += struct.pack("<H", 0)
    header += struct.pack("<Q", row_count)

    # Rebuild per-column metadata with offsets
    data_start = 4 + 4  # MAGIC + HEADER_SIZE
    data_start += HEADER_SIZE  # actual header ends here
    offset_ptr = data_start

    columns_binary = b""

    for block in blocks:
        name_bytes = block["name"].encode("utf-8")

        # Common metadata
        header += struct.pack("<B", len(name_bytes))
        header += name_bytes
        header += struct.pack("<B", block["type"])
        header += struct.pack("<H", 0)

        # Data block offset
        header += struct.pack("<Q", offset_ptr)
        header += struct.pack("<Q", block["compressed_size"])
        header += struct.pack("<Q", block["uncompressed_size"])

        # Append data block to final output
        columns_binary += block["data"]
        offset_ptr += block["compressed_size"]

        # If string column → add offsets block
        if block["type"] == TYPE_STRING:
            header += struct.pack("<Q", offset_ptr)
            header += struct.pack("<Q", block["offsets_block"]["compressed_size"])
            header += struct.pack("<Q", block["offsets_block"]["uncompressed_size"])

            columns_binary += block["offsets_block"]["data"]
            offset_ptr += block["offsets_block"]["compressed_size"]

    # Recompute HEADER_SIZE
    HEADER_SIZE = len(header)

    # Final file assembly
    final = bytearray()
    final += MAGIC
    final += struct.pack("<I", HEADER_SIZE)
    final += header
    final += columns_binary

    with open(output_path, "wb") as f:
        f.write(final)

    print(f"Successfully wrote file: {output_path}")


# -----------------------------
# RUN EXAMPLE
# -----------------------------
if __name__ == "__main__":
    csv_path = "input.csv"         # change filename
    output_path = "output.mcf"     # final custom format file
    write_custom_format(csv_path, output_path)
