# automating_jumia_scraper_with_airflow

The aim of this project was to automate a scraper to scrape data from jumia website and create a list of all products currently offered at a discount then save the data in a relational database.

The following tools aided this project
* Python
* Apache airflow
* Postgres 

The first step involves writing a pyhton function to scrape data from the website. The library used for scraping was Beautifulsoup. A for loop was used to iterate the script over 50 pages and the function returned a list containing product information. 

The next step involved using apache airflow to schedule the script to run daily. The first task was to create a new table in Postgres dbms with and define columns names. the second task was to run the scraper function and finally the third task was to insert the data returned by the scraper into the relational database.

Next, this data is cleaned and transformed first before performing EDA using SQL queries. Some of the operations carried out involves handling null values and filtering. The data was then loaded into pandas for Exploratory Data Analysis as a dataframe. Some of the libraries used for this include pandas, numpy and matplotlib.

Finaly, a python script was written to develop a strimlit application that displays the EDA insights performed on the dataset.