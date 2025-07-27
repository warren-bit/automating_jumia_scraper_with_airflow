# Jumia Scraper Airflow Project

## Overview
This project uses **Apache Airflow** to automate the scraping of product data from Jumia Kenya’s all-products pages and store it in a PostgreSQL database. The DAG (`jumia_scraper`) runs daily and consists of the following tasks:
- **`create_table`**: Drops and recreates the `product_info` table in the `jumia_data` database.
- **`scrape_page`**: Scrapes product details (item name, current price, old price, discount, link) from Jumia Kenya.
- **`insert_values`**: Inserts scraped data into the `product_info` table.

The project is containerized using **Docker**, with:
- A **host PostgreSQL** instance (`host.docker.internal:5432`, `jumia_data` database) for storing scraped data.
- A **containerized PostgreSQL** instance (`postgres` service) for Airflow’s metadata (`airflow` database).

## Prerequisites
- **Docker Desktop** (with Docker Compose)
- **PostgreSQL** (installed on the host machine)
- **Python 3.12** (used within Airflow containers)
- **Git**

## Project Structure
```
jumia_project_airflow/
├── dags/
│   ├── dag.py              # Airflow DAG definition
│   └── scraper.py          # Scraping logic
├── docker-compose.yml      # Docker configuration for Airflow and PostgreSQL
├── requirements.txt        # Python dependencies for Airflow
├── .gitignore              # Excludes sensitive files
├── .env                    # Environment variables (not committed)
└── README.md               # Project documentation
```

## Setup Instructions

### 1. Clone the Repository
Clone the project from GitHub:
```bash
git https://github.com/warren-bit/automating_jumia_scraper_with_airflow.git
cd jumia_project_airflow
```

### 2. Set Up Host PostgreSQL (for `jumia_data`)
Install PostgreSQL on your host machine and configure the jumia_data database using DBeaver:

Install PostgreSQL:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```
Open DBeaver and create a new connection:

Driver: PostgreSQL

Host: localhost or 127.0.0.1

Port: 5432

Database: postgres (default database for initial connection)

Username: postgres

Password: Set to your_secure_password

In DBeaver:Connect to the PostgreSQL server.

Create the jumia_data database:Right-click on the connection, select Create > Database.

Name: jumia_data.

Set the postgres user password:
Run in the SQL editor:
```sql
ALTER USER postgres WITH PASSWORD 'your_secure_password';
```

### 3. Configure Environment Variables
Create a `.env` file in the project root to define environment variables:
```bash
nano .env
```
Add the following, replacing placeholders with secure values:
```
AIRFLOW_UID=1000
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=jumia_data
AIRFLOW_DB_PASSWORD=your_airflow_db_password
_AIRFLOW_WWW_USER_USERNAME=your_airflow_username
_AIRFLOW_WWW_USER_PASSWORD=your_airflow_web_password
```
- **Notes**:
  - `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`: Credentials for the host PostgreSQL (`jumia_data`).
  - `AIRFLOW_DB_PASSWORD`: Password for the `airflow` user in the containerized PostgreSQL (`airflow` database).
  - `AIRFLOW_UID`: Set to your host user ID (`id -u`) for file permissions (e.g., `1000`).
  - `your_airflow_db_password` must match the password set for the `airflow` user in the `postgres` container.
  - Do not commit `.env` to Git.

### 4. Set Up Containerized PostgreSQL (for Airflow Metadata)
Start the `postgres` service and create the `airflow` user and database:
```bash
docker-compose up -d postgres
docker exec -it jumia_project_airflow-postgres-1 psql -U postgres
CREATE USER airflow WITH PASSWORD 'your_airflow_db_password';
CREATE DATABASE airflow OWNER airflow;
GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;
\q
```
- Ensure `your_airflow_db_password` matches `AIRFLOW_DB_PASSWORD` in `.env`.

### 5. Start Airflow Containers
Launch all services (PostgreSQL, Airflow webserver, scheduler, triggerer, and init):
```bash
docker-compose up -d
```

### 6. Access Airflow UI
- Open `http://localhost:8090` in a browser.
- Log in with `_AIRFLOW_WWW_USER_USERNAME` and `_AIRFLOW_WWW_USER_PASSWORD` from `.env`.
- Enable the `jumia_scraper` DAG by toggling the switch in the UI.

## DAG Details
- **DAG ID**: `jumia_scraper`
- **Schedule**: Daily (`@daily`)
- **Tasks**:
  - `create_table`: Drops and recreates the `product_info` table.
  - `scrape_page`: Scrapes product data using `requests` and `beautifulsoup4`.
  - `insert_values`: Inserts data into `product_info` using `PostgresHook(postgres_conn_id='postgres_localhost')`.
- **Databases**:
  - **Jumia Data**: Host PostgreSQL (`host.docker.internal:5432`, `POSTGRES_DB` database, user `POSTGRES_USER`, password `POSTGRES_PASSWORD`).
  - **Airflow Metadata**: Containerized PostgreSQL (`postgres` service, `airflow` database, user `airflow`, password from `AIRFLOW_DB_PASSWORD`).
- **Connection ID**: `postgres_localhost` (configured in Airflow UI or via `AIRFLOW_CONN_POSTGRES_LOCALHOST` in `docker-compose.yml`).

## Running the DAG
- **Manual Trigger**:
  ```bash
  docker exec -it jumia_project_airflow-airflow-webserver-1 airflow dags trigger jumia_scraper
  ```
- **Test Individual Tasks**:
  ```bash
  docker exec -it jumia_project_airflow-airflow-webserver-1 airflow tasks test jumia_scraper create_table 2025-07-27
  docker exec -it jumia_project_airflow-airflow-webserver-1 airflow tasks test jumia_scraper scrape_page 2025-07-27
  docker exec -it jumia_project_airflow-airflow-webserver-1 airflow tasks test jumia_scraper insert_values 2025-07-27
  ```

## Dependencies
The `requirements.txt` includes:
```
apache-airflow==2.10.0
apache-airflow-providers-postgres==5.11.1
psycopg2-binary==2.9.9
requests==2.32.3
beautifulsoup4==4.12.3
```