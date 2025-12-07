# Custom Columnar File Format Specification



## 1. Overview

This document defines a simplified custom columnar file format created to understand

how analytical storage systems like Parquet and ORC work internally.



The format stores data column-by-column instead of row-by-row, supports selective

column reads, and compresses each column using zlib.



Supported data types:

- int32 (32-bit integer)

- float64 (64-bit floating point)

- string (UTF-8 variable-length text)



This specification fully defines the file structure, header metadata,

column layout, and encoding rules.



---



## 2. File Layout



The file is stored in the following order:



1. MAGIC (4 bytes)

&nbsp;  A fixed 4-byte ASCII identifier (e.g., `"MCF1"`).  

&nbsp;  Used to validate the file format.



2. HEADER_SIZE (4 bytes, uint32 LE)

&nbsp;  Size of the HEADER section in bytes.  

&nbsp;  Allows the reader to jump directly to the start of column blocks.



3. HEADER (variable length)

&nbsp;  Contains:

&nbsp;  - File version  

&nbsp;  - Column count  

&nbsp;  - Row count  

&nbsp;  - Schema (column names + type codes)  

&nbsp;  - Per-column metadata:

&nbsp;      \* DATA\_OFFSET  

&nbsp;      \* COMPRESSED\_SIZE  

&nbsp;      \* UNCOMPRESSED\_SIZE  

&nbsp;      \* (For string columns additionally:)  

&nbsp;        - OFFSETS\_OFFSET  

&nbsp;        - OFFSETS\_COMPRESSED\_SIZE  

&nbsp;        - OFFSETS\_UNCOMPRESSED\_SIZE  



4. COLUMN_BLOCK_1

&nbsp;  Compressed (zlib) data block for column 1.



5. COLUMN_BLOCK_2

&nbsp;  Compressed zlib block for column 2.



6. COLUMN_BLOCK_3 

&nbsp;  …



All COLUMN\_BLOCKS appear immediately after the HEADER.

Their absolute byte offsets are recorded in the HEADER.



---



## 3. Header Structure



### 3.1 Fixed Header Fields

```

| VERSION (1 byte)                |

| COLUMN\_COUNT (1 byte)           |

| RESERVED (2 bytes = 0)          |

| ROW\_COUNT (8 bytes, uint64 LE)  |

```



### 3.2 Per-Column Metadata

```

| NAME\_LEN (1 byte)                      |

| NAME (NAME\_LEN bytes, UTF-8)           |

| TYPE\_CODE (1 byte)                     |

| RESERVED (2 bytes = 0)                 |

| DATA\_OFFSET (8 bytes, uint64 LE)       |

| COMPRESSED\_SIZE (8 bytes, uint64 LE)   |

| UNCOMPRESSED\_SIZE (8 bytes, uint64 LE) |

```



### String Column Extra Metadata (TYPE\_CODE = 3)

```

| OFFSETS\_OFFSET (8 bytes, uint64 LE)            |

| OFFSETS\_COMPRESSED\_SIZE (8 bytes, uint64 LE)   |

| OFFSETS\_UNCOMPRESSED\_SIZE (8 bytes, uint64 LE) |

```



### Type Codes

- `1` → int32  

- `2` → float64  

- `3` → string  



---



## 4. Column Block Format



### 4.1 int32 Columns

- Raw uncompressed layout: sequence of 4-byte little-endian integers  

- Entire byte sequence compressed using zlib  

- Stored at `DATA\_OFFSET`


### 4.2 float64 Columns

- Raw uncompressed layout: sequence of 8-byte IEEE-754 little-endian values  

- Compressed using zlib  

- Stored at `DATA\_OFFSET`



### 4.3 string Columns

Each string column uses \*\*two blocks\*\*:



#### 1. String Data Block  

Concatenation of all UTF-8 strings:



```

"AliceBobCat" → bytes

```



Compressed and stored at `DATA\_OFFSET`.



#### 2. Offsets Block  

Stores ending byte index of each string:



Example strings:

```

["Alice", "Bob", "Cat"]

```



UTF-8 lengths:

```

5, 3, 3

```



Offsets array:

```

[5, 8, 11]

```



Compressed separately and stored at `OFFSETS\_OFFSET`.



---



## 5. Endianness \& Compression



- All multi-byte integers and floats use \*\*little-endian\*\* encoding.  

- All column blocks (including string offsets) are compressed with \*\*zlib (DEFLATE)\*\*.



---



This specification defines everything required for implementing a writer,

reader, selective column access, and conversion utilities.



