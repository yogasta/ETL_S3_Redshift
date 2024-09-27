# Airflow Data Pipeline: CSV to S3 to Redshift

## Project Status: Incomplete

**Note:** This project is currently incomplete. The AWS account setup and configuration are still pending. The following README outlines the planned architecture and setup process.

## Architecture Overview

This project implements a data pipeline using Apache Airflow to extract data from a local CSV file, transform it, upload it to Amazon S3, and finally load it into Amazon Redshift. Here's a high-level overview of the architecture:

1. **Data Source**: Local CSV file in the `data` folder
2. **Transformation**: Python script in the `scripts` folder
3. **Intermediate Storage**: Amazon S3 bucket
4. **Data Warehouse**: Amazon Redshift cluster
5. **Orchestration**: Apache Airflow

The pipeline follows these steps:
1. Read data from the local CSV file
2. Apply transformations using a custom Python script
3. Upload the transformed data to an S3 bucket
4. Copy the data from S3 to a Redshift table

## Prerequisites

- Python 3.7+
- Apache Airflow 2.0+
- AWS account (not set up yet)
- Required Python packages (install via `pip install -r requirements.txt`):
  - apache-airflow
  - apache-airflow-providers-amazon
  - pandas
  - boto3

## Project Structure

```
project_root/
│
├── dags/
│   └── csv_to_s3_to_redshift_dag.py
│
├── scripts/
│   └── transform_data.py
│
├── data/
│   └── E-commerece Dataset.csv
│
└── README.md
```

## Setup Instructions

1. Clone this repository:
   ```
   git clone <repository-url>
   cd <project-directory>
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up Airflow (if not already done):
   ```
   export AIRFLOW_HOME=~/airflow
   airflow db init
   airflow users create --username admin --firstname YourName --lastname YourLastName --role Admin --email your@email.com
   ```

4. Copy the DAG file to your Airflow DAGs folder:
   ```
   cp dags/csv_to_s3_to_redshift_dag.py ~/airflow/dags/
   ```

5. AWS Setup (Pending):
   - Create an AWS account
   - Set up IAM user with appropriate permissions
   - Create an S3 bucket
   - Set up a Redshift cluster
   - Configure VPC and security groups as needed

6. Configure Airflow connections for AWS and Redshift (via Airflow UI)

## Running the Pipeline

1. Start the Airflow webserver:
   ```
   airflow webserver --port 8080
   ```

2. In another terminal, start the Airflow scheduler:
   ```
   airflow scheduler
   ```

3. Access the Airflow UI at `http://localhost:8080`

4. Enable the DAG in the Airflow UI

5. The DAG will run based on the schedule interval defined (default is daily)

# Airflow Data Pipeline: CSV to S3 to Redshift

[Previous sections remain unchanged]

## Expected Output

When this project is fully set up and running correctly, you should expect the following outputs:

1. **Airflow DAG Execution**:
   - In the Airflow UI, you should see successful executions of the DAG "csv_to_s3_to_redshift" on the schedule you've set (default is daily).
   - The DAG should show three tasks completing successfully:
     1. `transform_data`
     2. `upload_to_s3`
     3. `transfer_to_redshift`

2. **Data Transformation**:
   - A new CSV file should be created in your local `data` folder, containing the transformed data.
   - This file should include the following changes from the original data:
     - `Order_Date` converted to datetime format
     - New `Total_Revenue` column (calculated as `Sales * Quantity`)
     - New `Profit_Margin` column (calculated as `Profit / Sales`)
     - New `Profit_Category` column categorizing profit margins

3. **S3 Bucket**:
   - In your AWS S3 console, you should see the transformed CSV file uploaded to the specified bucket.
   - The file should be updated daily (or as per your defined schedule).

4. **Redshift Table**:
   - In your Redshift cluster, you should see a table populated with the data from the transformed CSV.
   - This table should be updated daily (or as per your defined schedule).
   - The table should contain all columns from the transformed CSV, including the new calculated columns.

5. **Logs and Monitoring**:
   - Airflow logs should show successful completion of each task, including any data processing metrics (e.g., number of rows processed).
   - AWS CloudWatch (if set up) should show logs for S3 object creation and Redshift COPY commands.

6. **Data Consistency**:
   - The data in the transformed CSV, S3 object, and Redshift table should all be consistent with each other.

7. **Incremental Updates** (if implemented):
   - On subsequent runs, only new or updated data should be processed and added to the Redshift table.

To verify the output:
1. Check the Airflow UI for successful DAG runs.
2. Inspect the transformed CSV file in your local `data` folder.
3. Use the AWS S3 console to verify the presence of the uploaded file.
4. Connect to your Redshift cluster and query the target table to ensure data has been loaded correctly.
5. Review Airflow logs for detailed execution information.

Note: The exact structure and content of the output data will depend on your specific transformation logic and input data. Adjust your expectations accordingly based on your implemented transformations and business logic.

[Remaining sections stay the same]

## Monitoring and Troubleshooting

- Monitor DAG runs via the Airflow UI
- Check Airflow logs for detailed information on task execution
- For AWS-related issues, check CloudWatch logs and the AWS Management Console

## Future Improvements

- Implement error handling and retry logic
- Add data quality checks
- Implement incremental loading for efficiency
- Set up proper monitoring and alerting