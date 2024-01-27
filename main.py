import pandas as pd

from get_data import get_data


if __name__ == '__main__':
  combined_df = get_data()

  print(combined_df.head())

  correlation = combined_df['reported_wells_flow'].corr(combined_df['reported_production_in_barrels_daily'])
  print(f"Correlation between wells and production: {correlation}")
