# Rental Data Collection

The python script **scraping_of_house_data.py** uses **Selenium** to interact with a popular European rental website and **BeautifulSoup** to extract useful data such as appartment price, number of bedrooms, location etc. The data is further recoreded in JSON file and stored on AWS S3 bucket.

## Features

- Automated web scraping using Selenium
- Data extraction and parsing with BeautifulSoup
- JSON data storage
- Integration with AWS S3 for data storage

## Requirements

- Python 3.10
- Selenium
- BeautifulSoup4
- Boto3 (for AWS S3 integration)
