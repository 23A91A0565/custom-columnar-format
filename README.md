# 🧩 Custom Columnar File Format (Mini-Parquet Project)

This project implements a simplified columnar storage format inspired by analytical data engines such as **Apache Parquet** and **ORC**.  
The goal is to understand how modern analytical file formats are built internally, including:

- Binary layout design  
- Metadata and headers  
- Columnar storage  
- Compression using zlib  
- Selective column reads (column pruning)  

This repository includes:

- `SPEC.md` — Complete format specification  
- `writer.py` — Converts CSV → custom `.mcf` format  
- `reader.py` — Loads `.mcf` and reconstructs table data  
- CLI tools:  
  - `csv_to_custom.py`  
  - `custom_to_csv.py`  

---

# 📘 Project Overview

Traditional CSV files store data **row by row**, making them inefficient for analytics workloads.  
Columnar formats store each column **separately**, enabling:

✔ Faster reads  
✔ Selective access to only needed columns  
✔ Better compression  
✔ Faster analytical queries  

This project demonstrates those principles with a fully working system.

---

# 📦 Features

### ✅ Columnar Storage  
Each column is stored as a separate contiguous block.

### ✅ Zlib Compression  
Every block is compressed individually for high efficiency.

### ✅ Metadata Header  
The header stores:  
- Schema  
- Column types  
- Offsets  
- Compressed & uncompressed sizes  

### ✅ Selective Column Reads  
The reader can load **only specific columns**, improving speed.

### ✅ CSV → MCF → CSV  
Round-trip conversion works reliably.

---

# 📚 Specification Overview

The full binary format is documented in **SPEC.md**, including:

- MAGIC bytes  
- HEADER structure  
- Column metadata  
- Type codes  
- String encoding (offsets + blob)  
- Compression methods  

Please read **SPEC.md** for complete details.

---

# 🚀 Usage Guide

## 1️⃣ Convert CSV → Custom Columnar Format

```cmd
python csv_to_custom.py input.csv output.mcf
```

This generates a file like:

```
output.mcf
```
Example:

<img width="1006" height="119" alt="Screenshot 2025-12-07 192259" src="https://github.com/user-attachments/assets/56fd32ec-b9be-4d6d-baf0-918d33008c71" />

---

## 2️⃣ Convert Custom Format → CSV

```cmd
python custom_to_csv.py output.mcf reconstructed.csv
```

Produces:

```
reconstructed.csv
```

This file should match your original CSV exactly.

Example:

<img width="1067" height="94" alt="Screenshot 2025-12-07 192331" src="https://github.com/user-attachments/assets/acad3edf-498d-4061-895c-20c169603980" />

---

# 📂 Folder Structure

```
custom-columnar-format/
│
├── writer.py               # Writer implementation (CSV → MCF)
├── reader.py               # Reader implementation (MCF → CSV)
├── csv_to_custom.py        # CLI wrapper for writer
├── custom_to_csv.py        # CLI wrapper for reader
├── SPEC.md                 # Full file format specification
├── README.md               # This file
└── __pycache__/            # Auto-generated
```

Example:

<img width="1158" height="635" alt="Screenshot 2025-12-07 192727" src="https://github.com/user-attachments/assets/4c669c33-b68c-4093-a9e4-94a41cb88da4" />

---

# 🛠 Requirements

- Python 3.8+
- No external libraries required  
Only uses:
- `csv`
- `struct`
- `zlib`

---

# 🧪 Testing

1. Create `input.csv`  
2. Run the writer  
3. Run the reader  
4. Compare `input.csv` and `reconstructed.csv`

If both match → ✔ Your implementation works!

---

# 🏁 Summary

This project demonstrates the key principles behind modern analytical data formats by implementing:

- A custom binary file format  
- Columnar storage  
- Compressed data blocks  
- Metadata-rich headers  
- Selective column reading  

It is a hands-on, portfolio-ready demonstration of **low-level data engineering**, binary file handling, and compression techniques.

