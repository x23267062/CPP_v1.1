import boto3
from botocore.exceptions import ClientError
import logging
from werkzeug.security import generate_password_hash

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_dynamodb_table(table_name, region="us-east-1"):
    """
    Creates a DynamoDB table for storing user authentication data.
    
    Args:
    - table_name (str): Name of the DynamoDB table to create.
    - region (str): AWS region to create the table in.
    
    Returns:
    - Table creation status or error message.
    """
    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb', region_name=region)
    
    # Define the key schema and attribute definitions
    key_schema = [
        {
            'AttributeName': 'Username',
            'KeyType': 'HASH'  # Partition key
        }
    ]
    
    attribute_definitions = [
        {
            'AttributeName': 'Username',
            'AttributeType': 'S'  # String
        },
        {
            'AttributeName': 'Email',
            'AttributeType': 'S'  # String
        },
        {
            'AttributeName': 'PasswordHash',
            'AttributeType': 'S'  # String (hashed password)
        }
    ]
    
    provisioned_throughput = {
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
    
    try:
        # Create the table
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions[:1],  # Only 'Username' needed in KeySchema
            ProvisionedThroughput=provisioned_throughput
        )
        
        # Wait until the table exists
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        
        logger.info(f"Table '{table_name}' created successfully.")
        return table
    
    except ClientError as e:
        logger.error(f"Failed to create table: {e.response['Error']['Message']}")
        return None


def add_user(table_name, username, email, password, region="us-east-1"):
    """
    Adds a new user to the DynamoDB table with a hashed password.
    
    Args:
    - table_name (str): Name of the DynamoDB table to insert the user into.
    - username (str): Username of the user.
    - email (str): Email of the user.
    - password (str): Plain-text password, which will be hashed before storing.
    """
    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table(table_name)
    
    # Hash the password before storing
    password_hash = generate_password_hash(password)
    
    # Add the new user
    try:
        table.put_item(
            Item={
                'Username': username,
                'Email': email,
                'PasswordHash': password_hash
            }
        )
        logger.info(f"User '{username}' added successfully.")
    
    except ClientError as e:
        logger.error(f"Failed to add user: {e.response['Error']['Message']}")

import boto3
from werkzeug.security import check_password_hash
from botocore.exceptions import ClientError
import logging

# Set up DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # Replace with your AWS region
user_table = dynamodb.Table('Users')  # Ensure this table exists in DynamoDB

def authenticate_dynamodb_user(username, password):
    """
    Authenticates a user by checking DynamoDB for the username and verifying the password hash.
    """
    try:
        # Retrieve user data from DynamoDB
        response = user_table.get_item(Key={'Username': username})
        user = response.get('Item')

        # Check if user exists and verify password
        if user and check_password_hash(user['PasswordHash'], password):
            return user  # Return user data if authentication succeeds
        else:
            return None  # Authentication failed

    except ClientError as e:
        logging.error(f"Error fetching user: {e}")
        return None


def main():
    # Specify table name and AWS region
    table_name = "Users"
    region = "us-east-1"  # Adjust to your region
    
    # Step 1: Create the DynamoDB table for user authentication
    table = create_dynamodb_table(table_name, region)
    if table:
        logger.info(f"Table '{table_name}' is ready for use.")
    
    # Step 2: Add a sample user (for testing purposes)
    add_user(table_name, "Abimanyu", "abimanyumurugan15@gmail.com", "admin", region)


if __name__ == '__main__':
    main()
