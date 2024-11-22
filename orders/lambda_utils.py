import boto3
import zipfile
import os

def create_lambda_function():
    # AWS client for Lambda
    lambda_client = boto3.client('lambda', region_name='us-east-1')

    # Name of the Lambda function
    function_name = 'SendOrderConfirmation'

    # Role ARN for the Lambda function
    role_arn = 'arn:aws:iam::851725586731:role/LabRole'  #  role ARN

    # Code for the Lambda function
    lambda_code = '''
import boto3
import json

def lambda_handler(event, context):
    sns_client = boto3.client('sns', region_name='us-east-1')
    username = event['username']
    pickup_location = event['pickup_location']
    drop_location = event['drop_location']
    topic_arn = event['topic_arn']
    
    subject = "Order Confirmation - TrackItNow"
    message = f"""
    
    Hello {username},

    Your order has been placed successfully!

    Order Details:
    - Pickup Location: {pickup_location}
    - Drop Location: {drop_location}

    Thank you for using TrackItNow!

    Best regards,
    TrackItNow Team
    
    """
    
    sns_client.publish(
        TopicArn=topic_arn,
        Subject=subject,
        Message=message
    )
    
    return {"statusCode": 200, "message": "Email sent successfully"}
    '''

    # Save Lambda code to a zip file
    zip_file_name = 'lambda_function.zip'
    with zipfile.ZipFile(zip_file_name, 'w') as zf:
        with open('lambda_function.py', 'w') as f:
            f.write(lambda_code)
        zf.write('lambda_function.py')

    # Upload zip file and create Lambda function
    try:
        with open(zip_file_name, 'rb') as f:
            response = lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.8',  # Specify Python runtime
                Role=role_arn,
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': f.read()},
                Description='Lambda function for sending order confirmation emails using SNS',
                Timeout=15,
                MemorySize=128,
                Publish=True,
            )
        print("Lambda function created:", response)
    except Exception as e:
        print(f"Error creating Lambda function: {e}")

    # Cleanup local files
    os.remove('lambda_function.py')
    os.remove(zip_file_name)

def invoke_lambda(payload):
    # AWS Lambda client
    lambda_client = boto3.client('lambda', region_name='us-east-1')

    # Payload to send to Lambda function
    # payload = {
    #     "username": "john_doe",
    #     "pickup_location": "D12E9C7",
    #     "drop_location": "D15X8C9",
    #     "topic_arn": "arn:aws:sns:us-east-1:123456789012:john_doe"  # Replace with actual topic ARN
    # }

    try:
        # Invoke Lambda function
        response = lambda_client.invoke(
            FunctionName='SendOrderConfirmation',  # Replace with your Lambda function name
            InvocationType='RequestResponse',  # Wait for response
            Payload=payload
        )

        # Read response
        response_payload = json.loads(response['Payload'].read())
        print("Lambda Response:", response_payload)

    except Exception as e:
        print(f"Error invoking Lambda function: {e}")



if __name__ == "__main__":
    create_lambda_function()
