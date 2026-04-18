from config.settings import FILE_PATH
from ingestion.reader import read_log
from parsing.parser import split_log_line
from processing.transform import to_dataframe
from output.csv_exporter import export_item_tables


def main():
    lines = read_log(FILE_PATH)
    data = []
    for line in lines:
        try:
            data.append(split_log_line(line))
        except ValueError as e:
            print(e)

    df = to_dataframe(data)

    # OUTPUT LAYER
    export_item_tables(df, "outputs")
    
if __name__ == "__main__":
    main()