import sys
from writer import write_custom_format

def main():
    if len(sys.argv) != 3:
        print("Usage: python csv_to_custom.py <input.csv> <output.mcf>")
        sys.exit(1)

    input_csv = sys.argv[1]
    output_mcf = sys.argv[2]

    print(f"Converting {input_csv} → {output_mcf} ...")
    write_custom_format(input_csv, output_mcf)
    print("Done! ✔")

if __name__ == "__main__":
    main()
