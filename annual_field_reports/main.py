from get_data import get_data


if __name__ == '__main__':
  gas_data = get_data(type="gas")
  oil_data = get_data(type="oil")

  print(gas_data)
  print(oil_data)
