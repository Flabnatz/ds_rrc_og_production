import re
from datetime import datetime


import pdfplumber


def parse_value(x):
  """
  Convert strings into integers
  """
  if (x == ""): return None
  return int(x.replace(",", ""))

def parse_line(line, date):
  """
  Each file is expected to have data arrayed in the same position as the previous files.
  14 columns are expected with the 1st and 10th not needing any further parsing for completeness.
  
  The date needs to be parsed from the file's header and passed along with the data.
  """
  return {
    "Date": date,
    "RRC_Dist": line[:3].strip(),
    "number_of_leases_reported": parse_value(line[4:14].strip()),
    "number_of_leases_delq": parse_value(line[15:21].strip()),
    "reported_wells_flow": parse_value(line[22:29].strip()),
    "reported_wells_other": parse_value(line[30:37].strip()),
    "total_allow_in_barrels_monthly": parse_value(line[38:48].strip()),
    "delq_allow_in_barrels_monthly": parse_value(line[49:58].strip()),
    "reported_production_in_barrels_monthly": parse_value(line[59:70].strip()),
    "reported_production_in_barrels_daily": parse_value(line[71:80].strip()),
    "percent_under_produced": line[81:87].strip(),
    "method_of_disposition_monthly_barrels_pipeline": parse_value(line[88:99].strip()),
    "method_of_disposition_monthly_barrels_truck": parse_value(line[100:110].strip()),
    "method_of_disposition_monthly_barrels_other": parse_value(line[111:121].strip()),
    "close_stock_barrels": parse_value(line[122:].strip())
  }

def parse_pdf_for_table(pdf_path):
  """
  Each file has three pages and the second page has the FINAL STATEMENT for the reported month.
  The second page should look similar to the following:  

      (OWN423)          12/13/2023                        RAILROAD COMMISSION OF TEXAS                                        PAGE 2  OF 3
                                                              OIL AND GAS DIVISION
                                                      MONTHLY CRUDE OIL PRODUCTION REPORT
                                                  FINAL STATEMENT FOR THE MONTH OF SEPTEMBER, 2023
                NUMBER OF        REPORTED  TOTAL ALLOW  DELQ ALLOW  REPORTED PRODUCTION    %          METHOD OF DISPOSITION        CLOSING
      RRC         LEASES           WELLS    IN BARRELS  IN BARRELS       IN BARRELS      UNDER           MONTHLY BARRELS            STOCK
      DIST   REPORTED  DELQ    FLOW   OTHER  MONTHLY     MONTHLY      MONTHLY   DAILY  PRODUCED   PIPELINE    TRUCKS      OTHER    BARRELS
      ------------------------------------------------------------------------------------------------------------------------------------
      01       6,739    296   3,267  18,016 37,262,115 1,010,430  14,226,175   474,206  60.87   8,717,743  5,433,937     13,073  1,628,896
      02       3,077     57     970   5,955 26,901,227   129,450   9,680,908   322,697  63.84   7,567,518  2,102,375      3,437    642,342
      03       5,413    187   1,651   5,454  4,672,716   166,716   2,494,966    83,166  45.36     410,716  2,063,440      6,084  1,050,548
      04         972     35     186     893    295,424    15,900     137,786     4,593  51.48      12,935    131,087        250    122,979
      05         892     25     237   1,354    917,160     4,080     461,904    15,397  49.48                462,534        212    167,168
      06       2,200     63     415   2,653  1,013,248    64,697     677,616    22,587  30.89     194,774    481,408        193    465,615
      6E         982     29      35   4,339    427,477    13,590     162,306     5,410  60.92      22,201    146,859          4    157,383
      7B       4,281    176     358   7,291  1,104,664    33,676     513,523    17,117  52.45      39,080    465,246      1,932    558,707
      7C       6,797    186   1,038  13,855 24,362,077   437,430  12,442,713   414,757  48.30   9,802,108  2,614,589      6,545  1,269,727
      08      22,401    321   5,347  49,919 51,106,541 3,254,388  75,018,040 2,500,601  49.60  67,283,561  7,543,220    116,738  4,239,568
      8A       4,089    184     747  19,413  9,909,905   224,940   6,382,828   212,761  34.80   4,787,968  1,588,138      1,248    922,171
      09       6,297    267     430  14,322  1,305,548    69,848     614,588    20,486  51.05      19,614    597,086      1,994    793,116
      10       3,146     28     540   6,945  3,467,247    29,219     539,040    17,968  84.16      10,965    514,250        516    601,485
      ------------------------------------------------------------------------------------------------------------------------------------
      TOTAL   67,286  1,854  15,221 150,409 62,745,349 5,454,364 123,352,393 4,111,746  52.33  98,869,183 24,144,169    152,226 12,619,705
  
  Note how the data is arrayed positionally, and so data can be extracted using extract_text and retaining the blank characters.
  """
  with pdfplumber.open(pdf_path) as file:
    text = file.pages[1].extract_text(keep_blank_chars=True)

    # Use a regular expression search to find the date for this data
    date_pat = re.compile(r'FINAL STATEMENT FOR THE MONTH OF ([A-Z]+\s*,\s*\d{4})')
    date = re.search(date_pat, text)

    # Report an issue and return empty list if the date is not findable
    if not date:
      print(f'No table found for file {pdf_path}')
      return []
    
    # Convert the date to a datetime object
    parsed_date = datetime.strptime(date.group(1), "%B, %Y")
    formatted_date = parsed_date.strftime("%Y-%m")

    # Use a regular expression search to find the data between the dashed lines
    core_pat = re.compile(r"\-{2,}\n([\s\S]+?)\n\-{2,}", re.DOTALL)
    core = re.search(core_pat, text)

    # Report an issue and return an empty list if the data is not as expected between dashed lines
    if not core:
      print(f'No table found for file {pdf_path}')
      return []
    
    lines = core.group(1).split("\n")

  return [parse_line(line, formatted_date) for line in lines]