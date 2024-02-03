import pandas as pd
import plotly.express as px

from get_data import get_data, _get_data_source_urls


if __name__ == '__main__':
  combined_df = get_data(save_data=False)

  combined_df["reported_wells"] = combined_df["reported_wells_flow"] + combined_df["reported_wells_other"]

  item_a = "reported_wells"
  item_b = "reported_production_in_barrels_monthly"

  correlation = combined_df[item_a].corr(combined_df[item_b])
  print(f"Correlation between columns {item_a} and {item_b}: {correlation}")

  fig = px.scatter(combined_df, x=item_a, y=item_b, log_x=True, log_y=True)
  fig.show()
