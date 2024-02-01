import plotly.express as px

from get_data import get_data


if __name__ == '__main__':
  gas_data = get_data(type="gas", save_data=True)
  oil_data = get_data(type="oil", save_data=True)

  item_a = "TOTAL WELLS"
  item_b = "TOTAL OIL PRODUCTION"

  correlation = oil_data[item_a].corr(oil_data[item_b])
  print(f"Correlation between columns {item_a} and {item_b}: {correlation}")

  fig = px.scatter(oil_data, x=item_a, y=item_b, log_x=True, log_y=True,)
  fig.show()

  item_a = "TOTAL WELLS"
  item_b = "TOTAL GAS PRODUCED"
  # item_b = "TOTAL CONDENSATE PRODUCED"

  correlation = gas_data[item_a].corr(gas_data[item_b])
  print(f"Correlation between columns {item_a} and {item_b}: {correlation}")

  fig = px.scatter(gas_data, x=item_a, y=item_b, log_x=True, log_y=True)
  fig.show()
