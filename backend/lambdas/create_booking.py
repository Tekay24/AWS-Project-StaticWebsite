import json
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')
table = dynamodb.Table('BaiaBookings')

# Your SNS topic ARN (from Step 1)
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:130713583028:BaiaBookingNotifications'

def lambda_handler(event, context):
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': ''
        }
    
    try:
        # Parse body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        # Create booking record
        booking = {
            'bookingId': str(uuid.uuid4()),
            'fullName': body.get('fullName', ''),
            'email': body.get('email', ''),
            'phone': body.get('phone', ''),
            'bookingDate': body.get('bookingDate', ''),
            'bookingTime': body.get('bookingTime', ''),
            'partySize': int(body.get('partySize', 0)),
            'specialRequests': body.get('specialRequests', ''),
            'status': 'confirmed',
            'createdAt': datetime.now().isoformat()
        }
        
        # Save to DynamoDB
        table.put_item(Item=booking)
        
        # Send SNS notification
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject='Baía Seafood - New Booking Confirmed',
            Message=f"""
New Booking Received!

Customer: {booking['fullName']}
Email: {booking['email']}
Phone: {booking['phone']}
Date: {booking['bookingDate']}
Time: {booking['bookingTime']}
Party Size: {booking['partySize']}
Special Requests: {booking['specialRequests']}

Booking ID: {booking['bookingId']}
            """.strip()
        )
        
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'},
            'body': json.dumps({'success': True, 'message': 'Booking confirmed!', 'bookingId': booking['bookingId']})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'message': str(e)})
        }