\# My Columnar File Format Specification



\## 1. Overview

This document defines a simplified custom columnar file format designed for

learning how modern analytical storage systems (such as Parquet and ORC) work

internally. The goal of this format is to efficiently store tabular data in a

column-oriented layout, support selective column reads, and compress each column

independently using zlib.



The format supports three data types:

\- int32 (32-bit integers)

\- float64 (64-bit floating-point numbers)

\- string (UTF-8 variable-length text)



This specification describes the exact binary layout of the file, including

the header structure, metadata, and column block layout.



\## 2. File Layout

The file consists of the following sections in order:



1\. MAGIC (4 bytes)

&nbsp;  A fixed 4-byte ASCII identifier (e.g., "MCF1").

&nbsp;  Used to validate that the file is in this format.



2\. HEADER\_SIZE (4 bytes, uint32 LE)

&nbsp;  The length of the HEADER section in bytes.

&nbsp;  Enables the reader to locate the start of the column blocks.



3\. HEADER (variable length)

&nbsp;  Contains:

&nbsp;    - File version

&nbsp;    - Column count

&nbsp;    - Row count

&nbsp;    - Schema (column names and type codes)

&nbsp;    - Per-column metadata:

&nbsp;         \* DATA\_OFFSET

&nbsp;         \* COMPRESSED\_SIZE

&nbsp;         \* UNCOMPRESSED\_SIZE

&nbsp;         \* (For strings) OFFSETS\_OFFSET,

&nbsp;           OFFSETS\_COMPRESSED\_SIZE,

&nbsp;           OFFSETS\_UNCOMPRESSED\_SIZE



4\. COLUMN\_BLOCK\_1

&nbsp;  Zlib-compressed byte block for column 1.



5\. COLUMN\_BLOCK\_2

&nbsp;  Zlib-compressed byte block for column 2.



6\. COLUMN\_BLOCK\_3

&nbsp;  ...



All column blocks follow directly after the HEADER, and their absolute

byte offsets are stored in the HEADER.



