import logging
import boto3
from botocore.exceptions import ClientError


def create_bucket(bucket_name, region=None):
    """Create an S3 bucket in a specified region

    If a region is not specified, the bucket is created by default in the region (us-east-1).

    :param bucket_name: Bucket to create
    :param region: String region to create bucket in, e.g., 'us-west-2'
    :return: True if bucket created, else False
    """

    # Create bucket
    try:
        if region is None:
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name,
                                    CreateBucketConfiguration=location)
    except ClientError as e:
        logging.error(e)
        return False
    return True
    
    

def list_buckets():
    # Retrieve the list of existing buckets
    s3_client = boto3.client('s3')
    response = s3_client.list_buckets()

    # Output the bucket names
    print('Existing buckets:')
    for bucket in response['Buckets']:
        print('\t', bucket["Name"])
    
    
def upload_file(file_name, bucket, object_key=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param key: S3 object key. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 key was not specified, use file_name
    if object_key is None:
        object_key = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_key)
        '''
        # an example of using the ExtraArgs optional parameter to set the ACL (access control list) value 'public-read' to the S3 object
        response = s3_client.upload_file(file_name, bucket, key, 
            ExtraArgs={'ACL': 'public-read'})
        '''
        
    except ClientError as e:
        logging.error(e)
        return False
    return True
    
    
    
def delete_object(region, bucket_name, object_key):
    """Delete a given object from an S3 bucket
    """
    s3_client = boto3.client('s3')
    response = s3_client.delete_object(Bucket=bucket_name, Key=object_key)
    


def delete_bucket(region, bucket_name):
    """Delete a given S3 bucket
    """
    s3_client = boto3.client('s3')
  
    # first delete all the objects from a bucket, if any objects exist
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    if response['KeyCount'] != 0:
          for content in response['Contents']:
            object_key = content['Key']
            print('\t Deleting object...', object_key)
            s3_client.delete_object(Bucket=bucket_name, Key=object_key)


    # delete the bucket
    print('\t Deleting bucket...', bucket_name)
    response = s3_client.delete_bucket(Bucket=bucket_name)
  
    list_buckets()
  
 
 
 
    
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('bucket_name', help='The name of the bucket.')
    parser.add_argument('--region', default='us-east-1', help='The region of the bucket.')
    parser.add_argument('--file_name', help='The name of the file to upload.')
    parser.add_argument('--object_key', help='The object key')

    region = 'us-east-1'
  
    args = parser.parse_args()
    # create_bucket(args.bucket_name)
    list_buckets()
    upload_file(args.file_name,args.bucket_name, args.object_key)
    #delete_object(region, args.bucket_name, args.object_key)
    #delete_bucket(args.region, args.bucket_name)
 
 

if __name__ == '__main__':
 main()