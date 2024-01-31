import os
import webbrowser

import numpy as np
import pandas as pd


"""

"""


def _download_source_files():
  print("Download the Gas Annual Report Field Table ASCII files")
  print("Store these files in a subfolder called `gas_data`")
  url = "https://mft.rrc.texas.gov/link/2aa7edb2-bbb0-4f1b-afe9-05af2da6ab73"
  webbrowser.open(url)
  
  print("Download the Oil Annual Report Field Table ASCII files")
  print("Store these files in a subfolder called `oil_data`")
  url = "https://mft.rrc.texas.gov/link/0f81208c-8ff4-4dee-a7a2-d816b743decb"
  webbrowser.open(url)


def _process_gas_data(data):
  # Columns defined in Manual PDF
  # https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/#oil-and-gas-field-data
  cols = [
    "YEAR",
    "DISTRICT",
    "ASSOCIATED FIELD FLAG",
    "FIELD NAME",
    "COUNTY NAME",
    "MULTIPLE COUNTY FLAG",
    "DISCOVERY DATE",
    "DEPTH",
    "TOTAL WELLS",
    "PRODUCING WELLS",
    "TOTAL GAS PRODUCED",
    "CYCLING FIELD", #does this need to switch with  Total Gas Produced???
    "TOTAL CONDENSATE PRODUCED",
    "FULL WELL STREAM TO A PLANT",
    "CUMULATIVE GAS PRODUCED",
    "REMARKS1",
    "REMARKS2",
    "REMARKS3",
    "REMARKS4",
    "REMARKS5",
    "REMARKS6",
    "REMARKS7",
    "REMARKS8",
    "REMARKS9",
    "REMARKS10",
    "REMARKS11",
    "REMARKS12",
    "REMARKS13",
    "REMARKS14",
    "REMARKS15",
    ""
  ]

  df = pd.DataFrame(data, columns=cols)
  df["ASSOCIATED FIELD FLAG"] = np.where(df["ASSOCIATED FIELD FLAG"] == "A", True, False)
  df["MULTIPLE COUNTY FLAG"] = np.where(df["MULTIPLE COUNTY FLAG"] == "M", True, False)
  df["CYCLING FIELD"] = np.where(df["CYCLING FIELD"] == "C", True, False)
  df["FULL WELL STREAM TO A PLANT"] = np.where(df["FULL WELL STREAM TO A PLANT"] == "F", True, False)

  return df


def _process_oil_data(data):
  # Columns defined in Manual PDF
  # https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/#oil-and-gas-field-data
  cols = [
    "YEAR",
    "DISTRICT",
    "FIELD NAME",
    "COUNTY NAME",
    "MULTIPLE COUNTY FLAG",
    "DISCOVERY DATE",
    "DEPTH",
    "OIL GRAVITY",
    "TOTAL WELLS",
    "PRODUCING WELLS",
    "TOTAL CASINGHEAD GAS PRODUCTION",
    "TOTAL OIL PRODUCTION",
    "CUMULATIVE OIL PRODUCTION",
    "REMARKS1",
    "REMARKS2",
    "REMARKS3",
    "REMARKS4",
    "REMARKS5",
    "REMARKS6",
    "REMARKS7",
    "REMARKS8",
    "REMARKS9",
    "REMARKS10",
    ""
  ]

  df = pd.DataFrame(data, columns=cols)
  df["MULTIPLE COUNTY FLAG"] = np.where(df["MULTIPLE COUNTY FLAG"] == "M", True, False)

  return df


def get_data(type='gas', save_data=True):
  # Return DataFrame if CSV already saved locally
  dataset_path = type+'_data.csv'
  if os.path.isfile(dataset_path):
    return pd.read_csv(dataset_path)
  
  dfs = []
  for filename in os.listdir(type):
    filepath = os.path.join(type+"_data",filename)
    with open(filepath, "r") as file:
      data = [line.strip().split("}") for line in file.readlines()]
      if type == "gas": dfs.append(_process_gas_data(data))
      if type == "oil": dfs.append(_process_oil_data(data))

  combined_df = pd.concat(dfs, ignore_index=True)
  if save_data: combined_df.to_csv(dataset_path, index=False)

  return combined_df