from datetime import datetime
from get_bin_data import AbstractGetBinDataClass

import pandas as pd
import urllib.request


class CouncilClass(AbstractGetBinDataClass):
    """
    Concrete classes have to implement all abstract operations of the base
    class. They can also override some operations with a default
    implementation.
    """

    def parse_data(self, page: str) -> dict:
        """
        Parse council provided CSVs to get the latest bin collections for address
        """
        # URLs to data sources
        address_csv_url = "https://opendata.leeds.gov.uk/downloads/bins/dm_premises.csv"
        collections_csv_url = "https://opendata.leeds.gov.uk/downloads/bins/dm_jobs.csv"

        # Change these two
        user_postcode = ""  # Postcode
        user_paon = ""  # House number

        data = {"bins": []}  # dictionary for data
        prop_id = 0  # LCC use city wide URPNs in this dataset
        result_row = None  # store the property as a row

        # Get address csv and give it headers (pandas bypasses downloading the file)
        print("Getting address data...")
        with urllib.request.urlopen(address_csv_url) as response:
            addr = pd.read_csv(response, names=["PropertyId", "PropertyName", "PropertyNo", "Street",
                                                "Town", "City", "Postcode"], sep=",")

        # Get collections csv and give it headers
        print("Getting collection data...")
        with urllib.request.urlopen(collections_csv_url) as response:
            coll = pd.read_csv(response, names=["PropertyId", "BinType", "CollectionDate"], sep=",")

        # Find the property id from the address data
        print("Finding property reference...")
        for row in addr.itertuples():
            if str(row.Postcode).replace(" ", "") == user_postcode.replace(" ", ""):
                if row.PropertyNo == user_paon:
                    prop_id = row.PropertyId
                    result_row = row
                    print(f"Reference: {str(prop_id)}")
                    continue

        # For every match on the property id in the collections data, add the bin type and date to list
        # Note: time is 7am as that's when LCC ask bins to be out by
        job_list = []
        print(f"Finding collections for property reference: {result_row.PropertyNo} {result_row.Street} "
              f"{result_row.Postcode}...")
        for row in coll.itertuples():
            if row.PropertyId == prop_id:
                time = datetime.strptime('070000', '%H%M%S').time()
                date_obj = datetime.strptime(row.CollectionDate, '%d/%m/%y')
                combined_date = datetime.combine(date_obj, time).strftime('%d/%m/%y %H:%M:%S')
                job_list.append([row.BinType, combined_date])

        # If jobs exist, sort list by date order. Load list into dictionary to return
        print("Processing collections...")
        if len(job_list) > 0:
            job_list.sort(key=lambda x: datetime.strptime(x[1], '%d/%m/%y %H:%M:%S'))
            data.update({"bins": job_list})
        else:
            print("No bin collections found for property!")

        return data
