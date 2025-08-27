
"""
Iceberg table setup and management for the Picture Gallery application
"""

import boto3
from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import (
    NestedField,
    StringType,
    DateType,
    TimestampType
)
import os
from datetime import datetime

# Configuration
ICEBERG_BUCKET = os.environ.get('ICEBERG_BUCKET', 'your-iceberg-bucket')
ICEBERG_TABLE_PATH = os.environ.get('ICEBERG_TABLE_PATH', 'pictures_table')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

def create_iceberg_catalog():
    """
    Create and configure the Iceberg catalog
    """
    catalog_config = {
        'type': 'glue',
        'warehouse': f's3://{ICEBERG_BUCKET}/',
        'region': AWS_REGION
    }
    
    return load_catalog('glue', **catalog_config)

def create_pictures_table():
    """
    Create the pictures table in Iceberg format
    """
    try:
        catalog = create_iceberg_catalog()
        
        # Define the schema for the pictures table
        schema = Schema(
            NestedField(1, "picture_id", StringType(), required=True),
            NestedField(2, "picture_name", StringType(), required=True),
            NestedField(3, "picture_date", DateType(), required=True),
            NestedField(4, "picture_jpg", StringType(), required=True),
            NestedField(5, "upload_timestamp", TimestampType(), required=True),
            NestedField(6, "file_size", StringType(), required=False),
            NestedField(7, "image_width", StringType(), required=False),
            NestedField(8, "image_height", StringType(), required=False)
        )
        
        # Create the table
        table = catalog.create_table(
            identifier=f"default.{ICEBERG_TABLE_PATH}",
            schema=schema,
            location=f"s3://{ICEBERG_BUCKET}/{ICEBERG_TABLE_PATH}/"
        )
        
        print(f"✅ Successfully created Iceberg table: {ICEBERG_TABLE_PATH}")
        return table
        
    except Exception as e:
        print(f"❌ Error creating Iceberg table: {str(e)}")
        raise

def insert_picture_record(picture_id, picture_name, picture_date, picture_jpg, 
                         file_size=None, image_width=None, image_height=None):
    """
    Insert a picture record into the Iceberg table
    """
    try:
        catalog = create_iceberg_catalog()
        table = catalog.load_table(f"default.{ICEBERG_TABLE_PATH}")
        
        record = {
            'picture_id': picture_id,
            'picture_name': picture_name,
            'picture_date': picture_date,
            'picture_jpg': picture_jpg,
            'upload_timestamp': datetime.now(),
            'file_size': file_size,
            'image_width': image_width,
            'image_height': image_height
        }
        
        table.append([record])
        print(f"✅ Successfully inserted record for: {picture_name}")
        
    except Exception as e:
        print(f"❌ Error inserting picture record: {str(e)}")
        raise

def query_pictures(date_filter=None, name_filter=None, limit=100):
    """
    Query pictures from the Iceberg table
    """
    try:
        catalog = create_iceberg_catalog()
        table = catalog.load_table(f"default.{ICEBERG_TABLE_PATH}")
        
        # Build the query
        scan = table.scan()
        
        if date_filter:
            scan = scan.filter(f"picture_date = '{date_filter}'")
        
        if name_filter:
            scan = scan.filter(f"picture_name LIKE '%{name_filter}%'")
        
        # Execute the scan and return results
        results = []
        for record in scan.to_arrow().to_pylist():
            results.append(record)
            if len(results) >= limit:
                break
        
        return results
        
    except Exception as e:
        print(f"❌ Error querying pictures: {str(e)}")
        raise

def setup_glue_database():
    """
    Set up AWS Glue database for Iceberg catalog
    """
    try:
        glue_client = boto3.client('glue', region_name=AWS_REGION)
        
        # Create database if it doesn't exist
        try:
            glue_client.create_database(
                DatabaseInput={
                    'Name': 'default',
                    'Description': 'Default database for Picture Gallery Iceberg tables'
                }
            )
            print("✅ Created Glue database: default")
        except glue_client.exceptions.AlreadyExistsException:
            print("ℹ️  Glue database 'default' already exists")
        
    except Exception as e:
        print(f"❌ Error setting up Glue database: {str(e)}")
        raise

def main():
    """
    Main setup function
    """
    print("🚀 Setting up Iceberg table for Picture Gallery...")
    
    # Setup Glue database
    setup_glue_database()
    
    # Create the pictures table
    create_pictures_table()
    
    print("✅ Iceberg setup completed successfully!")

if __name__ == "__main__":
    main()


