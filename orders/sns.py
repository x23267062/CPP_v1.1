import boto3
import logging
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)

"""
    Create an SNS topic.
    Args:topic_name (str): The name of the SNS topic.
    Returns(str): The ARN of the created topic.
"""
def create_sns_topic(topic_name):
    sns = boto3.client('sns', region_name='us-east-1')
    
    try:
        response = sns.create_topic(Name=topic_name)
        topic_arn = response['TopicArn']
        logging.info(f"Topic '{topic_name}' created successfully. ARN: {topic_arn}")
        return topic_arn
    except Exception as e:
        logging.error(f"Error creating topic: {e}")
        return None

"""
    Subscribe to an SNS topic.
    
    Args:
        topic_arn (str): The ARN of the SNS topic.
        protocol (str): The protocol (email, SMS, etc.).
        endpoint (str): The endpoint to send notifications (email address or phone number).
"""
def subscribe_to_topic(topic_arn, protocol, endpoint):
    sns = boto3.client('sns', region_name='us-east-1')
    
    try:
        response = sns.subscribe(
            TopicArn=topic_arn,
            Protocol=protocol,
            Endpoint=endpoint
        )
        subscription_arn = response['SubscriptionArn']
        logging.info(f"\n\n\nSubscription successful. Subscription ARN: {subscription_arn}")
    except Exception as e:
        logging.error(f"Error subscribing to topic: {e}")

"""
    Publish a message to an SNS topic.
    Args:
        topic_arn (str): The ARN of the SNS topic.
        message (str): The message to send.
        subject (str): Optional subject for the message (only for email).
"""
def publish_message(topic_arn, message, subject=None):
    sns = boto3.client('sns', region_name='us-east-1')
    
    try:
        sns.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject=subject
        )
        logging.info("Message published successfully.")
    except Exception as e:
        logging.error(f"Error publishing message: {e}")

def get_topic_by_name(topic_name):
    sns = boto3.client('sns', region_name='us-east-1')
    
    try:
        # List all topics
        response = sns.list_topics()
        topics = response.get('Topics', [])
        
        # Search for the topic with the specific name
        for topic in topics:
            topic_arn = topic['TopicArn']
            if topic_arn.endswith(f":{topic_name}"):
                print(f"Found Topic ARN: {topic_arn}")
                return topic_arn
        
        print(f"Topic '{topic_name}' not found.")
        return None
    except Exception as e:
        print(f"Error fetching topics: {e}")
       
        
def delete_sns_topic(topic_arn):
    sns = boto3.client('sns', region_name='us-east-1')
    try:
        sns.delete_topic(TopicArn=topic_arn)
        logging.info(f"Topic {topic_arn} deleted successfully.")
    except Exception as e:
        logging.error(f"Error deleting topic: {e}")

"""
    Send an email directly to an email address using AWS SNS.

    Args:
    - email_address (str): The recipient's email address.
    - subject (str): The subject of the email.
    - message (str): The body of the email.

    Returns:
    - Response from SNS or an error message.
"""
def send_email_via_sns(email_address, subject, message):
    # Initialize SNS client
    sns_client = boto3.client('sns', region_name='us-east-1')  # Replace with your region

    try:
        # Send the email
        response = sns_client.publish(
            TargetArn=email_address,  # Use the email address directly
            Message=message,
            Subject=subject
        )
        print(f"Email sent! Message ID: {response['MessageId']}")
        return response
    except ClientError as e:
        print(f"Failed to send email: {e.response['Error']['Message']}")
        return None

def send_order_confirmation_email_via_sns(username, pickup_location, drop_location, topic_arn):
    """
    Send order confirmation email using AWS SNS.
    """
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
    #send_email_via_sns(email_address, subject, message)
    #topic_arn = get_topic_by_name('order_notify')
    publish_message(topic_arn, message, subject)
        
# Usage
if __name__ == "__main__":
    # Create a topic
    # topic_name = 'order_notify'
    topic_arn = create_sns_topic('x23267062')

    # # if topic_arn:
    # #     # Subscribe an email endpoint
    subscribe_to_topic(topic_arn, 'email', 'x23267062@student.ncirl.ie')
        
        # Subscribe an SMS endpoint (phone number in E.164 format)
        # subscribe_to_topic(topic_arn, 'sms', '+1234567890')

        # Publish a message
    #publish_message(get_topic_by_name('order_notify'), "This is a test message.", subject="Test Subject")
        #delete_sns_topic(get_topic_by_name('order_notify'))
