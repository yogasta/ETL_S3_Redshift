# Airflow Data Pipeline: CSV to S3 to Redshift

This project implements a fully functional data pipeline using Apache Airflow to extract data from a local CSV file, transform it, upload it to Amazon S3, and finally load it into Amazon Redshift for analysis with Amazon QuickSight.

## Architecture Overview

The pipeline utilizes the following components:

1. **Data Source**: Local CSV file in the `data` folder
2. **Transformation**: Python script using Pandas in the `scripts` folder
3. **Orchestration**: Apache Airflow (containerized with Docker)
4. **Intermediate Storage**: Amazon S3 bucket
5. **Data Warehouse**: Amazon Redshift cluster
6. **Visualization**: Amazon QuickSight

The pipeline follows these steps:
1. Read data from the local CSV file
2. Apply transformations using a custom Python script
3. Upload the transformed data to an S3 bucket
4. Copy the data from S3 to Redshift tables (dimensional model)
5. Perform analytics and create visualizations using QuickSight

## Prerequisites

- Docker and Docker Compose
- AWS account with appropriate permissions
- AWS CLI configured with your credentials

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
│   └── E-commerce Dataset.csv
│
├── docker-compose.yaml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Setup Instructions

1. Clone this repository

2. Set up your AWS resources:
   - Ensure you have an S3 bucket created
   - Set up a Redshift cluster
   - Configure VPC and security groups as needed
   - Create an IAM user with appropriate permissions for S3 and Redshift access

3. Configure AWS credentials:
   ```
   aws configure
   ```

4. Update the `docker-compose.yaml` file with your AWS credentials and configuration:
   ```yaml
   environment:
     - AWS_ACCESS_KEY_ID=your_access_key
     - AWS_SECRET_ACCESS_KEY=your_secret_key
     - S3_BUCKET=your_bucket_name
     - REDSHIFT_CONN_ID=your_redshift_conn_id
   ```

5. Build and start the Docker containers:
   ```
   docker-compose up -d
   ```

## Running the Pipeline

1. Access the Airflow UI at `http://localhost:8090` (you can modify the port, user and password in the docker-compose file.)

2. Enable the DAG "csv_to_s3_to_redshift" in the Airflow UI

3. The DAG will run based on the schedule interval defined (default is monthly)

4. Monitor the progress in the Airflow UI

## Data Transformation

The `transform_data.py` script performs the following transformations:

- Converts `Order_Date` to datetime format
- Removes rows with null values
- Converts numeric columns to appropriate data types
- Removes duplicates
- Calculates `Profit_Margin` and adds a `Profit_Margin_Category`
- Creates dimension tables for customers, products, and dates
- Generates a fact table for sales with calculated metrics

## Redshift Data Model

The data is stored in Redshift using a star schema:

- Fact table: `fact_sales`
- Dimension tables: `dim_customer`, `dim_product`, `dim_date`

## QuickSight Visualizations

QuickSight connects to Redshift to create the following visualizations:

- Total Revenue grouped by Order Priority
- Total Revenue by Device Type
- Total Profit Over Time
- Total Revenue by Product Category

## Monitoring and Troubleshooting

- Monitor DAG runs via the Airflow UI
- Check Airflow logs for detailed information on task execution
- For AWS-related issues, check CloudWatch logs and the AWS Management Console
- QuickSight provides its own monitoring for dashboard performance

## Future Improvements

- Enhance error handling and notification system
- Implement CI/CD pipeline for automated testing and deployment