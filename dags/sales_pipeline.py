from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from datetime import datetime, timedelta
import sys
import os

# Add the script folder to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the transform function from your script
from scripts.transform_data import transform_data

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 9, 27),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'csv_to_s3_to_redshift',
    default_args=default_args,
    description='A DAG to move data from CSV to S3 to Redshift',
    schedule_interval=timedelta(days=1),
)

# Define the path to your input and output data
input_file = '/path/to/your/data/folder/input_file.csv'
output_file = '/path/to/your/data/folder/transformed_file.csv'

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    op_kwargs={'input_file': input_file, 'output_file': output_file},
    dag=dag,
)

upload_to_s3_task = LocalFilesystemToS3Operator(
    task_id='upload_to_s3',
    filename=output_file,
    dest_key='path/in/s3/transformed_file.csv',
    dest_bucket='your-s3-bucket-name',
    aws_conn_id='aws_default',
    dag=dag,
)

transfer_to_redshift_task = S3ToRedshiftOperator(
    task_id='transfer_to_redshift',
    schema='your_redshift_schema',
    table='your_redshift_table',
    s3_bucket='your-s3-bucket-name',
    s3_key='path/in/s3/transformed_file.csv',
    copy_options=['CSV', 'IGNOREHEADER 1'],
    aws_conn_id='aws_default',
    redshift_conn_id='redshift_default',
    dag=dag,
)

transform_task >> upload_to_s3_task >> transfer_to_redshift_task