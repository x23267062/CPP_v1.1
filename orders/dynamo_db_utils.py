import boto3
from botocore.exceptions import ClientError
import logging
from werkzeug.security import generate_password_hash


from werkzeug.security import check_password_hash


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
        # table.put_item(
        # Item={
        #     'Delivery location': [],
        #     'Delivery status': 'Pending',  # This is the list
        # })
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
                'PasswordHash': password_hash,
                'Delivery location': [],
                'Delivery status': 'Pending',
                'Pickup location': [],
            }
        )
        logger.info(f"User '{username}' added successfully.")
    
    except ClientError as e:
        logger.error(f"Failed to add user: {e.response['Error']['Message']}")



# Set up DynamoDB

def authenticate_dynamodb_user(username, password):
    """
    Authenticates a user by checking DynamoDB for the username and verifying the password hash.
    """
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # Replace with your AWS region
        user_table = dynamodb.Table('Users')  # Ensure this table exists in DynamoDB
        
        if user_table is None:
            raise ValueError("DynamoDB user table is not initialized. Check your DynamoDB resource and table name.")
            
        # Retrieve user data from DynamoDB
        response = user_table.get_item(Key={'Username': username})
        user = response.get('Item')

        # Check if user exists and verify password
        if user and check_password_hash(user['PasswordHash'], password):
            logger.info("\nUser {} authenticated.".format(user))
            return user  # Return user data if authentication succeeds
        else:
            user = None
            logger.info("\nUser {} not authenticated.".format(user))
            logger.info(f"Authentication failed.")
            return user  # Authentication failed

    except ClientError as e:
        logging.error(f"Error fetching user: {e}")
        return None

def save_order_to_dynamodb(username, pickup_location, drop_location):
    """
    Save or update an order for a user in DynamoDB.
    """
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # Replace with your AWS region
        table = dynamodb.Table('Users')
        response = table.update_item(
            Key={
                'Username': username
            },
            UpdateExpression="""
                SET #pickup = list_append(if_not_exists(#pickup, :empty_list), :pickup_val),
                    #drop = list_append(if_not_exists(#drop, :empty_list), :drop_val)
            """,
            ExpressionAttributeNames={
                '#pickup': 'Pickup location',
                '#drop': 'Drop location'
            },
            ExpressionAttributeValues={
                ':pickup_val': [pickup_location],  # Appends as a list
                ':drop_val': [drop_location],      # Appends as a list
                ':empty_list': []                 # Initializes the list if it doesn't exist
            },
            ReturnValues="UPDATED_NEW"  # Returns updated attributes
        )
        print("Update succeeded:", response['Attributes'])
    except ClientError as e:
        print(f"Error updating item: {e.response['Error']['Message']}")
    
def get_user_orders(username):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Users')

    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('Username').eq(username)
    )
    
    items = response.get('Items', [])
    orders = []
    first_item = items[0]
    orders = zip(first_item['Pickup location'], first_item['Drop location'])
    logger.info("\n\n\n{}".format(orders))
    return orders

import boto3

def remove_element_from_db(username,index):
    """
    Removes the second element from 'Pickup location' and 'Drop location' lists in a DynamoDB item.
    
    Args:
        table_name (str): The name of the DynamoDB table.
        username (str): The primary key (Username) of the item to update.
    """
    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Users')

    # Define the key for the item
    key = {'Username': username}

    try:
        # Step 1: Fetch the existing item
        response = table.get_item(Key=key)
        item = response.get('Item', {})

        # Step 2: Check if 'Pickup location' and 'Drop location' exist and modify them
        if 'Pickup location' in item and 'Drop location' in item:
            pickup_list = item['Pickup location']
            drop_list = item['Drop location']

            if len(pickup_list) > 1:
                del pickup_list[index]  # Remove the second element (index 1)
            if len(drop_list) > 1:
                del drop_list[index]  # Remove the second element (index 1)

            # Step 3: Update the item in DynamoDB
            table.update_item(
                Key=key,
                UpdateExpression="SET #pickup = :new_pickup, #drop = :new_drop",
                ExpressionAttributeNames={
                    '#pickup': 'Pickup location',
                    '#drop': 'Drop location'
                },
                ExpressionAttributeValues={
                    ':new_pickup': pickup_list,
                    ':new_drop': drop_list
                },
                ReturnValues="UPDATED_NEW"
            )

            print("\n\nSuccessfully updated the item.")
        else:
            print("Either 'Pickup location' or 'Drop location' does not exist in the item.")

    except Exception as e:
        print(f"Error updating item: {e}")

# Usage example:
#remove_second_element_from_lists('YourTableName', 'Abimanyu')


def main():
    # Specify table name and AWS region
    table_name = "Users"
    region = "us-east-1"  # Adjust to your region
    
    # Step 1: Create the DynamoDB table for user authentication
    # table = create_dynamodb_table(table_name, region)
    # if table:
    #     logger.info(f"Table '{table_name}' is ready for use.")
    
    # Step 2: Add a sample user (for testing purposes)
    #add_user(table_name, "Abimanyu", "abimanyumurugan15@gmail.com", "admin", region)
    # add_user(table_name, "x23267062", "x23267062@student.ncirl.ie", "admin", region)
    # authenticate_dynamodb_user('x23267062','admin')

if __name__ == '__main__':
    main()
