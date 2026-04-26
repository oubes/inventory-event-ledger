from config.settings import FILE_PATH
from ingestion.reader import read_log
from parsing.parser import split_log_line
from processing.transform import to_dataframe
from output.csv_exporter import (
    export_aggregated_by_time,
    export_aggregated_by_selling,
    export_sales_trend,
    export_product_contribution,
    export_detect_sales_periods,
    export_sales_stability
)


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
    # aggregated time
    export_aggregated_by_time(df, "outputs/aggregated_time/days", "D")
    export_aggregated_by_time(df, "outputs/aggregated_time/months", "ME")

    # aggregated selling
    export_aggregated_by_selling(df, "outputs/aggregated_selling/days", "D")
    export_aggregated_by_selling(df, "outputs/aggregated_selling/months", "ME")

    # trend
    export_sales_trend(df, "outputs/trend/days", "D")
    export_sales_trend(df, "outputs/trend/months", "ME")

    # periods
    export_detect_sales_periods(df, "outputs/periods/days", "D")
    export_detect_sales_periods(df, "outputs/periods/months", "ME")

    # overall (no freq)
    export_product_contribution(df, "outputs/contribution")
    export_sales_stability(df, "outputs/stability")

if __name__ == "__main__":
    main()