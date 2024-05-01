import json
import logging
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
    def __init__(self, chromedriver_path="chromedriver", log_level=logging.ERROR):
        self.CHROMEDRIVER_PATH = chromedriver_path

        if not os.path.exists(self.CHROMEDRIVER_PATH):
            os.makedirs(self.CHROMEDRIVER_PATH)

        self.logger = logging.getLogger(__name__)
        logHandler = logging.StreamHandler(sys.stdout)
        logHandler.setFormatter(logging.Formatter('%(filename)s:%(lineno)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(logHandler)
        self.logger.setLevel(log_level)

        self.GOOGLE_API = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
        self.PLATFORM = "win64" if sys.maxsize > 2 ** 32 else "win32"

    def __download_version(self, version_number):
        response = requests.get(self.GOOGLE_API)
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
            self.logger.log(logging.ERROR,
                            format_text(f"[bright red]Couldn't find download URL for version {version_number}[reset]"))
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
            path = f'C:\\Program Files {("(x86)" if self.PLATFORM == "win64" else "")}\\Google\\Chrome\\Application'

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
            self.logger.log(logging.ERROR, format_text(f"[bright red]Error: {e}[reset]"))
            return None

        return None

    def __get_driver_versions(self):
        # check if chromedriver file exists
        if not os.path.exists(f"{self.CHROMEDRIVER_PATH}/chromedriver.exe"):
            self.logger.log(logging.WARNING, format_text(
                f"[bright red]Chromedriver not found in {self.CHROMEDRIVER_PATH} folder[reset]"))
            local_driver_version = "0.0.0"
        else:
            # check for local chromedriver version
            result = subprocess.run([f"{self.CHROMEDRIVER_PATH}/chromedriver.exe", "--version"], capture_output=True,
                                    text=True)
            output = result.stdout.strip()
            local_driver_version = output.split(" ")[1]  # get the version number
            self.logger.log(logging.DEBUG, format_text(f"Local chromedriver version: [cyan]{local_driver_version}[reset]"))

        # check for Chrome browser version
        browser_version = self.__get_browser_version()
        self.logger.log(logging.DEBUG, format_text(f"Browser version: [cyan]{browser_version}[reset]"))

        # check for latest chromedriver version online
        response = requests.get(self.GOOGLE_API)
        data = response.json().get('versions')

        online_driver_version = data[-1].get('version')
        self.logger.log(logging.DEBUG,
                        format_text(f"Latest online chromedriver version: [cyan]{online_driver_version}[reset]"))

        return browser_version, online_driver_version, local_driver_version

    def download_chromedriver(self):
        browser_version, online_version, local_version = self.__get_driver_versions()

        if ".".join(local_version.split(".")[:-1]) in browser_version:  # compare the first 3 numbers of actual version
            self.logger.log(logging.INFO,
                            format_text(f"[bright green]Local chromedriver is compatible with browser version[reset]")
                            )
        else:
            self.logger.log(logging.WARNING,
                            format_text(f"Local chromedriver is not compatible with browser version. "
                                        f"Downloading chromedriver for browser version [cyan]{browser_version}[reset]...")
                            )

            if self.__download_version(browser_version):
                self.logger.log(logging.INFO, format_text(f"[bright green]Download successful![reset]"))
            else:
                self.logger.log(logging.ERROR, format_text(
                    f"[bright red]Failed to download chromedriver for browser version {browser_version}[reset]"))

    def get_driver(self, options: webdriver.ChromeOptions = None):
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
            self.logger.log(logging.WARNING, format_text(
                f"[bright red]Couldn't find chrome driver for latest version, trying downloaded version[reset]"))

            self.download_chromedriver()

            return webdriver.Chrome(executable_path='chromedriver/chromedriver.exe', options=options)


if __name__ == "__main__":
    manager = ChromeDrivers(log_level=logging.DEBUG)
    driver = manager.get_driver()
