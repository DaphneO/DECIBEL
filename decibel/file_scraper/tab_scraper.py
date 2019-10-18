"""
This module contains all the methods you need for scraping either a single tab file or a predefined set of tab files
from the Internet.
"""

from selenium import webdriver
from os import path


def download_tab(tab_url: str, tab_directory: str, tab_name: str) -> (bool, str):
    """
    Download a tab file from the Internet, using the tab_url and place it in the tab_directory, called tab_name.
    Return a message indicating success or failure.

    :param tab_url: Location of the tab file on the Internet
    :param tab_directory: Local directory where the tab file should be placed on your machine
    :param tab_name: File name of your tab file
    :return: Boolean and str message, indicating success or failure
    """

    target_path = path.join(tab_directory, tab_name)
    if path.isfile(target_path):
        return False, 'This file already exists'

    try:
        browser = webdriver.Firefox()
        browser.get(tab_url)
        tab_text = browser.find_element_by_xpath('//pre[@class="_1YgOS"]').text
        browser.close()

        with open(target_path, 'wb') as f:
            f.write(tab_text)
    except:
        return False, 'Error downloading ' + tab_name
    return True, 'Download succeeded'


def download_data_set_from_csv(csv_path: str, tab_directory: str):
    """
    Download a data set of tab files, as specified by the csv file in csv_path, and put them into tab_directory.
    If a tab file cannot be downloaded successfully, for example because the file already existed or because the
    Internet connection broke down, then the function continues with downloading the other tab files. After trying to
    download all prescribed tab files, this function returns a message indicating the number of tab files that were
    downloaded successfully and the number of tab files for which the download failed.

    :param csv_path: Path to the csv file with lines in format [url];[name];[key];[filename] (for example IndexTabs.csv)
    :param tab_directory: Local location for the downloaded files
    """
    nr_successful = 0
    nr_unsuccessful = 0

    # Open the csv file
    with open(csv_path, 'r') as read_file:
        csv_content = read_file.readlines()
    for line in csv_content:
        parts = line.rstrip().split(';')
        tab_url = parts[0]
        tab_name = parts[3]
        success, message = download_tab(tab_url, tab_directory, tab_name)
        if success:
            nr_successful += 1
        else:
            nr_unsuccessful += 1
            print(message)

    print(str(nr_successful) + ' tab files were downloaded successfully. ' + str(nr_unsuccessful) + ' failed.')
