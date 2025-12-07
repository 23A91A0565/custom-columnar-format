import sys
from reader import read_custom_format, write_csv

def main():
    if len(sys.argv) != 3:
        print("Usage: python custom_to_csv.py <input.mcf> <output.csv>")
        sys.exit(1)

    input_mcf = sys.argv[1]
    output_csv = sys.argv[2]

    print(f"Decoding {input_mcf} → {output_csv} ...")
    table = read_custom_format(input_mcf)
    write_csv(table, output_csv)
    print("Done! ✔")

if __name__ == "__main__":
    main()
