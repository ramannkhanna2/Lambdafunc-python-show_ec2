import boto3
import csv
import urllib

# Connect S3 to client.
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    ls = []
    
    # Get all AWS regions
    ec2_regions = [region['RegionName'] for region in boto3.client('ec2').describe_regions()['Regions']]
    
    # Iterate over all regions and get running instances
    for region in ec2_regions:
        ec2_client = boto3.client('ec2', region_name=region)
        response = ec2_client.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        instances = response['Reservations']
        
        # Append running instances to the list
        for instance in instances:
            instance_id = instance['Instances'][0]['InstanceId']
            instance_type = instance['Instances'][0]['InstanceType']
            instance_region = region
            ls.append([instance_id, instance_type, instance_region])

    # Get the bucket and object key from the Event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    localFilename = '/tmp/test.csv'   #you can give any name.

    # Download the file from S3 to the local filesystem
    s3_client.download_file(bucket, key, localFilename)

    # Writing in CSV file
    with open('/tmp/test.csv', 'w', newline='') as f:
        w = csv.writer(f)
        sample=["InstanceId", "InstanceType", "Region"]
        w.writerow(sample)
        for i in ls:
            w.writerow(i)
    
    # Upload modified file
    s3_client.upload_file(localFilename, bucket, key)
