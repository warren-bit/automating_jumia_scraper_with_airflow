from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from scraper import scrape_pages

def insert_into_db(ti):
    # Pulling the scraped data from XCom
    scraped_data = ti.xcom_pull(task_ids='scrape_page')

    if not scraped_data:
        print("No data to insert")
        return

    # Establishing a connection to PostgreSQL
    postgres_hook = PostgresHook(postgres_conn_id='postgres_localhost')
    conn = postgres_hook.get_conn()
    cursor = conn.cursor()

    # SQL query for inserting data
    insert_query = """
    INSERT INTO product_info (item_name, current_price, old_price, discount, link) 
    VALUES (%s, %s, %s, %s, %s)
    """

    # Executing the insert query with the scraped data
    cursor.executemany(insert_query, scraped_data)
    conn.commit()

    cursor.close()
    conn.close()
    print(f"Inserted {len(scraped_data)} rows into product_info")

default_args = {
    'owner': 'Warren',
    'retries': '5',
    'retry_delay': timedelta(minutes=2)
}

with DAG(
    default_args=default_args,
    dag_id = 'jumia_scraper_v2',
    description = 'Scraping first page of Jumia website',
    start_date=datetime(2024, 8, 30),
    schedule_interval='@daily',
    catchup=False
) as dag:
    
    task1 = PostgresOperator(
        task_id = 'create_table',
        postgres_conn_id='postgres_localhost',
        sql = """
                    DROP TABLE IF EXISTS product_info;
                    CREATE TABLE product_info(
                    item_name VARCHAR(255),
                    current_price VARCHAR(255),
                    old_price VARCHAR(255),
                    discount VARCHAR(255),
                    link VARCHAR(255)
                    );
                """
    )

    task2 = PythonOperator(
        task_id = 'scrape_page',
        python_callable=scrape_pages,
        op_kwargs={'base_url':'https://www.jumia.co.ke/all-products/?page={}#catalog-listing',
                   'starting_page':1, 'ending_page':5}
    )

    task3  = PythonOperator(
        task_id = 'insert_values',
        python_callable= insert_into_db,
        provide_context = True
    )
    task1 >> task2 >> task3