#!/usr/bin/env python

import sys
from optparse import OptionParser
import boto3
import botocore.exceptions

parser = OptionParser()
parser.add_option('--id', dest="id")
parser.add_option('--region', dest="region")

(options, args) = parser.parse_args()

if (options.region != None):
    aws_region = 'us-east-1'
else:
    aws_region = options.region

if options.id == None:
    print("Image ID not provided!")
    sys.exit(1)

client = boto3.client('ec2', region_name=aws_region)

try:
    response = client.describe_images(ImageIds=[options.id])
    devices = response['Images'][0]['BlockDeviceMappings']
    snap_ids = [ device['Ebs']['SnapshotId'] for device in devices ]
    

    # Delete the image itself
    client.deregister_image(ImageId=options.id)
    print("Deregistered %s" % options.id)

    # Delete any associated snapshots
    for snap_id in snap_ids:
        client.delete_snapshot(SnapshotId=snap_id)
        print("Deleted snapshot %s" % snap_id)
except botocore.exceptions.ClientError:
    print("An error occured deleting the image "+options.id)
    sys.exit(1)