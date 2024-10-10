from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import sys
import os

# Add the script folder to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the transform function from your script
from scripts.transform_data import transform_to_star_schema_and_save

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 9, 27),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    'csv_to_star_schema_to_s3_to_redshift',
    default_args=default_args,
    description='A DAG to transform CSV to star schema, upload to S3, and overwrite Redshift tables',
    schedule_interval=timedelta(days=30),
)

input_file = '/opt/airflow/data/E-commerce Dataset.csv'
output_dir = '/opt/airflow/data/star_schema'
s3_bucket = Variable.get("s3_bucket_name")
s3_prefix = Variable.get("s3_prefix")
redshift_schema = Variable.get("redshift_schema")

transform_task = PythonOperator(
    task_id='transform_to_star_schema',
    python_callable=transform_to_star_schema_and_save,
    op_kwargs={'input_file': input_file, 'output_dir': output_dir},
    dag=dag,
)

create_schema_task = SQLExecuteQueryOperator(
    task_id='create_schema',
    sql=f"CREATE SCHEMA IF NOT EXISTS {redshift_schema};",
    conn_id='redshift_default',
    dag=dag
)

tables = ['dim_customer', 'dim_product', 'dim_date', 'fact_sales']

for table in tables:
    create_table_task = SQLExecuteQueryOperator(
        task_id=f'create_{table}_table',
        sql=f"""
        CREATE TABLE IF NOT EXISTS {redshift_schema}.{table} (
            {{{{ task_instance.xcom_pull(task_ids='transform_to_star_schema', key='table_definitions')['{table}'] }}}}
        );
        """,
        conn_id='redshift_default',
        dag=dag
    )
    
    truncate_table_task = SQLExecuteQueryOperator(
        task_id=f'truncate_{table}_table',
        sql=f"TRUNCATE TABLE {redshift_schema}.{table};",
        conn_id='redshift_default',
        dag=dag
    )
    
    upload_to_s3_task = LocalFilesystemToS3Operator(
        task_id=f'upload_{table}_to_s3',
        filename=f"{{{{ task_instance.xcom_pull(task_ids='transform_to_star_schema')['{table}'] }}}}",
        dest_key=f"{s3_prefix}/{table}.csv",
        dest_bucket=s3_bucket,
        aws_conn_id='aws_default',
        dag=dag,
        replace=True
    )
    
    transfer_to_redshift_task = S3ToRedshiftOperator(
        task_id=f'transfer_{table}_to_redshift',
        schema=redshift_schema,
        table=table,
        s3_bucket=s3_bucket,
        s3_key=f"{s3_prefix}/{table}.csv",
        copy_options=['CSV', 'IGNOREHEADER 1'],
        aws_conn_id='aws_default',
        redshift_conn_id='redshift_default',
        dag=dag
    )
    
    transform_task >> create_schema_task >> create_table_task >> truncate_table_task >> upload_to_s3_task >> transfer_to_redshift_task