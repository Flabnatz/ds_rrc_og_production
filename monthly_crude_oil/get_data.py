import os
import requests
import csv

from bs4 import BeautifulSoup
import pandas as pd

from PDF_Parsers.pdfplumber import parse_pdf_for_table


"""
Return a DataFrame with all of the combined data from the RRC Monthly Crude Oil data page.
Save a CSV file `data.csv` with all of the combined data from the RRC Monthly Crude Oil data page.

To do so:
  - Extract the list of URLs from the RRC webpage
  - Download each PDF from the RRC webpage
  - Parse the table for data using pdfplumber and save that to CSV
  - Combine the individual CSVs into a combined data file
"""


def _get_data_source_urls(urls_path, save_data=True):
  try:
    url = 'https://www.rrc.texas.gov/oil-and-gas/research-and-statistics/production-data/monthly-crude-oil-production-by-district-and-field/'
    response = requests.get(url)
    response.raise_for_status()  # Raise an HTTPError for bad responses
    soup = BeautifulSoup(response.text, 'html.parser')
    source_links = [a['href'] for a in soup.find_all('a', href=True) if '_rrc180_' in a['href']] # Just want Final Production files
  except requests.exceptions.RequestException as e:
    print(f"Error: {e}")

  # Create list of data source urls  
  data_source_urls = []
  for link in source_links:
    if link[0:6] == '/media': link = 'https://www.rrc.texas.gov'+link
    data_source_urls.append(link)

  # If requested, save list of data source urls to CSV (Default to save)
  if save_data:
    with open(urls_path, 'w', newline='') as file:
      writer = csv.writer(file)
      for link in data_source_urls:
        writer.writerow([link])

  return data_source_urls


def _download_pdf(url, save_path):
  response = requests.get(url)
  with open(save_path, 'wb') as file:
    file.write(response.content)


def get_data(save_data=True):
  # Return DataFrame if CSV already saved locally
  dataset_path = 'data.csv'
  if os.path.isfile(dataset_path):
    return pd.read_csv(dataset_path)

  # Get list of data source urls from RRC Website, if not already saved locally
  data_source_urls_path = 'data_source_urls.csv'
  try:
    with open(data_source_urls_path, 'r', newline='') as file:
      urls = [url[0] for url in csv.reader(file)]
  except OSError:
    urls = _get_data_source_urls(data_source_urls_path, save_data=save_data)
  
  # Read through the list of data source urls and parse the data into the list of DataFrames
  dfs = [] # Initialize a list for collecting each DataFrame
  csvs_dir = 'Parsed_data'
  for url in urls:
    # Download and parse the data, if not already saved locally
    csv_save_path = os.path.join(csvs_dir,f"{url[-27:-4]}.csv")
    try:
      df = pd.read_csv(csv_save_path)
    except OSError:
      _download_pdf(url, 'data.pdf')
      parsed_table = parse_pdf_for_table('data.pdf')
      df = pd.DataFrame.from_records(parsed_table)
      if save_data: df.to_csv(csv_save_path)
    dfs.append(df) # Append the DataFrame to the dfs list
  
  # Combine data
  combined_df = pd.concat(dfs, ignore_index=True)
  if save_data: combined_df.to_csv(dataset_path, index=False)
  
  return combined_df
