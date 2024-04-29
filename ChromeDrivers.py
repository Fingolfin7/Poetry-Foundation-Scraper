import json
import shutil
import zipfile
import subprocess
import os, sys
import re
import requests
from ColourText import format_text
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


class ChromeDrivers:
    def __init__(self):
        self.CHROMEDRIVER_PATH = "chromedriver"
        self.PLATFORM = "win64" if sys.maxsize > 2 ** 32 else "win32"

    def __download_version(self, version_number):
        api_path = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
        response = requests.get(api_path)
        data = response.json().get('versions')

        download_url = ""

        for entry in data:
            if ".".join(version_number.split(".")[:-1]) in entry.get('version'):  # compare the first 3 numbers
                for item in entry.get('downloads').get('chromedriver'):
                    if item.get('platform') == self.PLATFORM:
                        download_url = item.get('url')
                        break
                break

        if download_url == "":
            print(format_text(f"[bright red]Couldn't find download URL for version {version_number}[reset]"))
            return False

        # download zip file
        with requests.get(download_url) as response:
            if response.status_code == 200:
                with open(f"{self.CHROMEDRIVER_PATH}/chromedriver.zip", "wb") as file:
                    file.write(response.content)
            else:
                return False

        latest_driver_zip = f"{self.CHROMEDRIVER_PATH}/chromedriver.zip"

        # extract the zip file
        with zipfile.ZipFile(latest_driver_zip, 'r') as downloaded_zip:
            for member in downloaded_zip.namelist():
                filename = os.path.basename(member)
                # skip directories
                if not filename:
                    continue

                # copy file (taken from zipfile's extract)
                source = downloaded_zip.open(member)
                target = open(os.path.join(self.CHROMEDRIVER_PATH, filename), "wb")
                with source, target:
                    shutil.copyfileobj(source, target)

        os.remove(latest_driver_zip)

        # if everything went well, return True
        return True

    def __get_browser_version(self):
        try:
            # Check if the Chrome folder exists in the x32 or x64 Program Files folders.
            path = 'C:\\Program Files' + (' (x86)' if self.PLATFORM == 'win64' else '') + '\\Google\\Chrome\\Application'
            if os.path.isdir(path):
                paths = [f.path for f in os.scandir(path) if f.is_dir()]
                for path in paths:
                    filename = os.path.basename(path)
                    pattern = '\d+\.\d+\.\d+\.\d+'
                    match = re.search(pattern, filename)
                    if match and match.group():
                        # Found a Chrome version.
                        return match.group(0)

        except Exception as e:
            print("Error:", e)
            return None

        return None

    def __get_driver_versions(self):
        # check for local chromedriver version
        result = subprocess.run([f"{self.CHROMEDRIVER_PATH}/chromedriver.exe", "--version"], capture_output=True, text=True)
        output = result.stdout.strip()
        local_driver_version = output.split(" ")[1]  # get the version number
        print(f"Local chromedriver version: {local_driver_version}")

        # check for Chrome browser version
        browser_version = self.__get_browser_version()
        print(f"Browser version: {browser_version}")

        # check for latest chromedriver version online
        api_path = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
        response = requests.get(api_path)
        data = response.json().get('versions')

        online_driver_version = data[-1].get('version')
        print(f"Latest online chromedriver version: {online_driver_version}")

        return browser_version, online_driver_version, local_driver_version

    def download_chromedriver(self):
        browser_version, online_version, _ = self.__get_driver_versions()

        if ".".join(browser_version.split(".")[:-1]) in online_version:  # compare the first 3 numbers of actual version
            print(f"\nDownloading browser version {browser_version}...")

            if self.__download_version(browser_version):
                print(format_text(f"[bright green]Download successful[reset]"))
            else:
                print(format_text(f"[bright red]Download failed[reset]"))
        else:
            print(format_text(f"[bright green]\nLocal chromedriver is up to date[reset]"))

    def get_driver(self, options=None):
        """
        Get the chromedriver with the specified options. Downloads driver compatible with the current Chrome version if
        default driver is not found.
        :param options: Custom options for the chromedriver, by default it is set to headless (no window)
        :return:
        """

        if options is None:
            # set chromedriver options to not open the Chrome window
            options = webdriver.ChromeOptions()
            options.add_argument('headless')  # don't open the browser window

        try:
            return webdriver.Chrome(ChromeDriverManager().install(), options=options)
        except ValueError:
            print(format_text(
                f"[bright red]Couldn't find chrome driver for latest version, trying downloaded version\n[reset]"))

            print(format_text(f"[cyan]Downloading chromedriver...[reset]"))
            self.download_chromedriver()

            return webdriver.Chrome(executable_path='chromedriver/chromedriver.exe', options=options)



if __name__ == "__main__":
    manager = ChromeDrivers()
    driver = manager.get_driver()
