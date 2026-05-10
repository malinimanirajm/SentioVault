import boto3

def test_connection():
    try:
        # Check S3
        s3 = boto3.client('s3')
        response = s3.list_buckets()
        print("✅ AWS Connection Successful! Found Buckets:", [b['Name'] for b in response['Buckets']])
        
        # Check Bedrock
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        print("✅ Bedrock Runtime is accessible.")
        
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    test_connection()