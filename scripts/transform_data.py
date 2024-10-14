import pandas as pd
import numpy as np
import os

def transform_to_star_schema_and_save(input_file: str, output_dir: str):
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    print("Original number of rows:", len(df))
    print("Columns in the input file:", df.columns.tolist())
    
    # Data Cleaning Steps
    # Convert Order_Date to datetime
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], errors='coerce')
    
    # Remove rows with null values
    df.dropna(inplace=True)
    
    print("Number of rows after removing nulls:", len(df))
    
    # Convert numeric columns and handle potential errors
    numeric_columns = ['Sales', 'Quantity', 'Discount', 'Profit', 'Shipping_Cost']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Remove duplicates
    df.drop_duplicates(inplace=True)
    
    print("Final number of rows:", len(df))
    
    # Calculate Profit Margin
    df['Profit_Margin'] = df['Profit'] / df['Sales']
    
    # Add Profit Margin Category
    df['Profit_Margin_Category'] = pd.cut(
        df['Profit_Margin'],
        bins=[-np.inf, 0, 0.1, 0.2, 0.3, np.inf],
        labels=['Loss', 'Low', 'Medium', 'High', 'Very High']
    )
    
    # Create dimension tables
    dim_customer = df[['Customer_Id', 'Gender', 'Customer_Login_type']].drop_duplicates().reset_index(drop=True)
    dim_customer['customer_key'] = dim_customer.index + 1

    dim_product = df[['Product_Category', 'Product']].drop_duplicates().reset_index(drop=True)
    dim_product['product_key'] = dim_product.index + 1

    dim_date = pd.DataFrame({
        'date_key': df['Order_Date'].dt.strftime('%Y%m%d').astype(int),
        'full_date': df['Order_Date'].dt.date,
        'year': df['Order_Date'].dt.year,
        'month': df['Order_Date'].dt.month,
        'day': df['Order_Date'].dt.day,
        'weekday': df['Order_Date'].dt.weekday
    }).drop_duplicates().reset_index(drop=True)

    # Create fact table
    fact_sales = df.merge(dim_customer, on=['Customer_Id', 'Gender', 'Customer_Login_type'])
    fact_sales = fact_sales.merge(dim_product, on=['Product_Category', 'Product'])
    fact_sales['date_key'] = fact_sales['Order_Date'].dt.strftime('%Y%m%d').astype(int)
    
    fact_columns = ['customer_key', 'product_key', 'date_key', 'Time', 'Aging', 'Device_Type', 
                    'Sales', 'Quantity', 'Discount', 'Profit', 'Shipping_Cost', 
                    'Order_Priority', 'Payment_method', 'Profit_Margin', 'Profit_Margin_Category']
    
    fact_sales = fact_sales[fact_columns]
    
    # Calculate additional metrics
    fact_sales['Total_Revenue'] = fact_sales['Sales'] * fact_sales['Quantity']
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Save dimension and fact tables to CSV files
    table_files = {}
    for table_name, df in {
        'dim_customer': dim_customer,
        'dim_product': dim_product,
        'dim_date': dim_date,
        'fact_sales': fact_sales
    }.items():
        file_path = os.path.join(output_dir, f"{table_name}.csv")
        df.to_csv(file_path, index=False)
        table_files[table_name] = file_path

    # Generate column definitions for Redshift tables
    table_definitions = {}
    for table_name, df in {
        'dim_customer': dim_customer,
        'dim_product': dim_product,
        'dim_date': dim_date,
        'fact_sales': fact_sales
    }.items():
        column_defs = []
        for col, dtype in df.dtypes.items():
            if dtype == 'object':
                column_defs.append(f"{col} VARCHAR(255)")
            elif dtype == 'int64':
                column_defs.append(f"{col} INT")
            elif dtype == 'float64':
                column_defs.append(f"{col} FLOAT")
            elif dtype == 'datetime64[ns]':
                column_defs.append(f"{col} TIMESTAMP")
            else:
                column_defs.append(f"{col} VARCHAR(255)")  # Default to VARCHAR for unknown types
        table_definitions[table_name] = ", ".join(column_defs)
    
    # Return the file paths and definitions of the saved CSV files
    return {
        'table_files': table_files,
        'table_definitions': table_definitions
    }