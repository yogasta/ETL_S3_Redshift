import pandas as pd

# Add Dimensional Modelling (Star Schema)
def transform_data(input_file, output_file):
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Convert Order_Date to datetime
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])
    
    # Calculate total revenue
    df['Total_Revenue'] = df['Sales'] * df['Quantity']
    
    # Calculate profit margin
    df['Profit_Margin'] = df['Profit'] / df['Sales']
    
    # Categorize orders based on profit margin
    df['Profit_Category'] = pd.cut(df['Profit_Margin'], 
                                   bins=[-float('inf'), 0.1, 0.2, 0.3, float('inf')],
                                   labels=['Low', 'Medium', 'High', 'Very High'])
    
    # Save the transformed data to a new CSV file
    df.to_csv(output_file, index=False)
    
    print(f"Data transformed and saved to {output_file}")

# This allows the function to be imported in the DAG file
if __name__ == "__main__":
    # This part is for testing the script independently
    input_file = '/path/to/your/data/folder/input_file.csv'
    output_file = '/path/to/your/data/folder/transformed_file.csv'
    transform_data(input_file, output_file)