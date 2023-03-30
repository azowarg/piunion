import logging
import os
from datetime import datetime
from shutil import copy

import pandas as pd
import xlsxwriter as xw

import google_drive
import rates


if __name__ == '__main__':
    # os.chdir('')
    google_user = 'n.larionova@gmail.com'
    rate_file = 'token_price_new.xlsx'
    mime_type = \
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    # Create dictionary for future dataframe and Excel doc
    today_rate = {
        'Date': str(datetime.now().strftime('%d.%m.%y %H:%M')),
        'ETH/USDT': rates.kraken_get_rates('ETHUSDT'),
        'BTC/USDT': rates.kraken_get_rates('XBTUSDT'),
        'WEVER/USD': rates.flatqube_get_rates(
            '0:a49cd4e158a9a15555e624759e2e4e766d22600b7800d891e46f9291f044a93d'),
        'BRIDGE/USD': rates.flatqube_get_rates(
            '0:f2679d80b682974e065e03bf42bbee285ce7c587eb153b41d761ebfd954c45e1'),
        'QUBE/USD': rates.flatqube_get_rates(
            '0:9f20666ce123602fd7a995508aeaa0ece4f92133503c0dfbd609b3239f3901e2'),
        'PURR/USD': rates.flatqube_get_rates(
            '0:9d49206b0eaadc5125c6b5e30410505db7740f827857915922cdb7efe199b622'),
        'USD/EUR': rates.cb_get_rates('USD') / rates.cb_get_rates('EUR')
    }

    rate_from_dict = pd.DataFrame(today_rate, index=[0])

    """
    Check existing of file.
    Create if not exist or move a previous copy to archive.
    """
    try:
        open(rate_file, 'x').close()
    except FileExistsError:
        print(str(rate_file),  'already exists. Make a backup')
        copy(rate_file, 'archive/' + datetime.now().strftime('%d.%m.%y %H:%M_')
             + rate_file)
    else:
        workbook = xw.Workbook(rate_file)
        worksheet = workbook.add_worksheet('currency_rates')
        workbook.close()
        # writer = pd.ExcelWriter(rate_file) 
        # for column in rate_from_dict:
        #     column_width = max(rate_from_dict[column].astype(str).map(len).max(), len(column))
        #     col_idx = rate_from_dict.columns.get_loc(column)
        #     writer.sheets['currency_rates'].set_column(col_idx, col_idx, column_width)
        # writer.

    """
    Create dataframe from file and dictionary.
    Concatenate them and save with previous name.
    """
    new_rate_file = pd.read_excel(rate_file, sheet_name='currency_rates')
    new_rate_file = pd.concat([new_rate_file, rate_from_dict],
                              ignore_index=True)
    new_rate_file.to_excel(rate_file, index=False, sheet_name='currency_rates')
    """
    Upload file to Google Drive.
    Check authentification, check for file existense in
    cloud and add permitions for user if need.
    """
    google_drive.create_auth_token()
    check_file_id = google_drive.search_file(rate_file.rstrip('.xlsx'))
    if not check_file_id:
        new_id = google_drive.upload_basic(rate_file, mime_type)
        google_drive.share_file(new_id, google_user)
    else:
        google_drive.upload_revision(check_file_id, rate_file, mime_type)
