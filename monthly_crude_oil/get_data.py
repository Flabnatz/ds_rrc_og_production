import os
import requests
import csv

from bs4 import BeautifulSoup
import pandas as pd

from PDF_Parsers.pdfplumber import parse_pdf_for_table


"""
Create a CSV file `data.csv` with all of the combined data from the RRC Oil and Gas webpage.

To do so:
  - Extract the list of URLs from the RRC webpage
  - Download each PDF from the RRC webpage
  - Parse the table for data using pdfplumber and save that to CSV
  - Combine the individual CSVs into a combined data file
"""


def _get_data_source_urls(url):
  try:
    response = requests.get(url)
    response.raise_for_status()  # Raise an HTTPError for bad responses
    soup = BeautifulSoup(response.text, 'html.parser')
    links = [a['href'] for a in soup.find_all('a', href=True) if '_rrc180_' in a['href']] # Just want Final Production files
    return links
  except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
    return []


def _download_pdf(url, save_path):
  response = requests.get(url)
  with open(save_path, 'wb') as file:
    file.write(response.content)


def _dict_to_csv(dict_data, csv_path):
    with open(csv_path, 'w', newline='') as file:
        writer = csv.DictWriter(file, dict_data[0].keys())
        writer.writeheader()
        writer.writerows(dict_data)


def get_data():
  data_source_urls_path = 'data_source_urls.csv'
  csvs_dir = 'Parsed_data'
  dataset_path = 'data.csv'

  # Get list of data source urls from RRC Website, if not acquired already
  if not os.path.isfile(data_source_urls_path):
    source_url = 'https://www.rrc.texas.gov/oil-and-gas/research-and-statistics/production-data/monthly-crude-oil-production-by-district-and-field/'
    data_source_urls = _get_data_source_urls(source_url)
    # Save list of data source urls to CSV
    with open(data_source_urls_path, 'w', newline='') as file:
      writer = csv.writer(file)
      for item in data_source_urls:
        if item[0:6] == '/media': item = 'https://www.rrc.texas.gov'+item
        writer.writerow([item])

  # Read through the list of data source urls and parse the data, if not already parsed
  with open(data_source_urls_path, 'r', newline='') as file:
    urls = csv.reader(file)
    for url in urls:
      pdf_url = url[0]
      csv_save_path = os.path.join(csvs_dir,f"{url[0][-27:-4]}.csv")
      if not os.path.isfile(csv_save_path):
        print(f'working on {url[0]}')
        _download_pdf(url[0], 'data.pdf')
        # Parse using pdfPlumber and write to csv
        parsed_table = parse_pdf_for_table('data.pdf')
        _dict_to_csv(parsed_table, csv_save_path)

  # Combine data
  if not os.path.isfile(dataset_path):
    dfs = []
    # Iterate through each CSV file in the data folder
    for file_name in os.listdir(csvs_dir):
      file_path = os.path.join(csvs_dir, file_name)
      df = pd.read_csv(file_path) # Read the CSV file into a DataFrame
      dfs.append(df) # Append the DataFrame to the dfs list

    combined_df = pd.concat(dfs, ignore_index=True)
    combined_df.to_csv(dataset_path, index=False)
  
  return pd.read_csv(dataset_path)
