from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from scraper import scrape_pages

def insert_into_db(ti):
    scraped_data = ti.xcom_pull(task_ids='scrape_page')

    if not scraped_data:
        print("No data to insert")
        return

    postgres_hook = PostgresHook(postgres_conn_id='postgres_localhost') 
    conn = postgres_hook.get_conn()
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO product_info (item_name, current_price, old_price, discount, link) 
    VALUES (%s, %s, %s, %s, %s)
    """

    try:
        cursor.executemany(insert_query, scraped_data)
        conn.commit()
        print(f"Inserted {len(scraped_data)} rows into product_info")
    except Exception as e:
        print("Error inserting into database:", e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

default_args = {
    'owner': 'Warren',
    'retries': 5,
    'retry_delay': timedelta(minutes=2)
}

with DAG(
    default_args=default_args,
    dag_id='jumia_scraper',
    description='Scraping first page of Jumia website',
    start_date=datetime(2024, 8, 30),
    schedule_interval='@daily',
    catchup=False
) as dag:

    task1 = SQLExecuteQueryOperator(
        task_id='create_table',
        conn_id='postgres_localhost',
        sql="""
            DROP TABLE IF EXISTS product_info;
            CREATE TABLE product_info(
                item_name VARCHAR(255),
                current_price VARCHAR(255),
                old_price VARCHAR(255),
                discount VARCHAR(255),
                link VARCHAR(255)
            );
        """,
        do_xcom_push=False
    )

    task2 = PythonOperator(
        task_id='scrape_page',
        python_callable=scrape_pages,
        op_kwargs={
            'base_url': 'https://www.jumia.co.ke/all-products/?page={}#catalog-listing',
            'starting_page': 1,
            'ending_page': 5
        }
    )

    task3 = PythonOperator(
        task_id='insert_values',
        python_callable=insert_into_db,
    )

    task1 >> task2 >> task3
