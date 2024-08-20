import boto3
import os
import time
import paramiko

def init_aws_session(aws_access_key_id, aws_secret_access_key, region_name="ap-south-1"):
    return boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )
# Create a Ec2 Instance with launch_ec2_instance
def launch_ec2_instance(session, ami_id, instance_type="t2.micro"):
    ec2 = session.resource('ec2')
    try:
        instances = ec2.create_instances(
            ImageId=ami_id,     # OS Image Id
            MinCount=1,
            MaxCount=1,
            InstanceType=instance_type   #e.g.(t2.micro)
        )
        instance_id = instances[0].id
        print(f"EC2 instance {instance_id} launched successfully!")
        return instance_id
    except Exception as e:
        print(f"Failed to launch EC2 instance: {str(e)}")

def start_ec2_instance(session, instance_id):
    ec2_client = session.client('ec2')
    try:
        print(f"Starting EC2 instance {instance_id}...")
        response = ec2_client.start_instances(InstanceIds=[instance_id])
        current_state = response['StartingInstances'][0]['CurrentState']['Name']
        print(f"Instance {instance_id} is currently {current_state}.")
    except Exception as e:
        print(f"Failed to start EC2 instance {instance_id}: {str(e)}")

def stop_ec2_instance(session, instance_id):
    ec2_client = session.client('ec2')
    try:
        print(f"Stopping EC2 instance {instance_id}...")
        response = ec2_client.stop_instances(InstanceIds=[instance_id])
        current_state = response['StoppingInstances'][0]['CurrentState']['Name']
        print(f"Instance {instance_id} is currently {current_state}.")
    except Exception as e:
        print(f"Failed to stop EC2 instance {instance_id}: {str(e)}")

def terminate_ec2_instance(session, instance_id):
    ec2_client = session.client('ec2')
    try:
        print(f"Terminating EC2 instance {instance_id}...")
        response = ec2_client.terminate_instances(InstanceIds=[instance_id])
        current_state = response['TerminatingInstances'][0]['CurrentState']['Name']
        print(f"Instance {instance_id} is currently {current_state}.")
    except Exception as e:
        print(f"Failed to terminate EC2 instance {instance_id}: {str(e)}")

def get_ec2_console_output(session, instance_id):
    ec2 = session.client('ec2')
    try:
        response = ec2.get_console_output(InstanceId=instance_id)
        print(response['Output'])
    except Exception as e:
        print(f"Error retrieving EC2 console output: {str(e)}")

def create_s3_bucket(session, bucket_name, region="ap-south-1"):
    s3_client = session.client('s3')
    try:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': region}
        )
        print(f"Bucket {bucket_name} created successfully.")
    except Exception as e:
        print(f"Failed to create S3 bucket: {str(e)}")

def upload_to_s3(session, bucket_name, file_path, object_name=None):
    s3_client = session.client('s3')
    if object_name is None:
        object_name = os.path.basename(file_path)
    try:
        s3_client.upload_file(file_path, bucket_name, object_name)
        print(f"File {file_path} uploaded to S3 bucket {bucket_name}.")
        return object_name
    except Exception as e:
        print(f"Failed to upload file to S3: {str(e)}")
        return None

def start_transcription_job(session, job_name, bucket_name, file_name, language_code='en-US'):
    transcribe_client = session.client('transcribe')
    job_uri = f"s3://{bucket_name}/{file_name}"
    try:
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': job_uri},
            MediaFormat=file_name.split('.')[-1],
            LanguageCode=language_code,
            OutputBucketName=bucket_name,
            OutputKey=f"{file_name.split('.')[0]}-transcript.json"
        )
        print(f"Transcription job {job_name} started successfully.")
        return job_name
    except Exception as e:
        print(f"Failed to start transcription job: {str(e)}")
        return None

def get_transcription_result(session, job_name):
    transcribe_client = session.client('transcribe')
    while True:
        result = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
        status = result['TranscriptionJob']['TranscriptionJobStatus']
        if status in ['COMPLETED', 'FAILED']:
            break
        print("Waiting for transcription to complete...")
        time.sleep(5)

    if status == 'COMPLETED':
        transcript_file_uri = result['TranscriptionJob']['Transcript']['TranscriptFileUri']
        print(f"Transcription completed. You can download the transcript from {transcript_file_uri}")
        return transcript_file_uri
    else:
        print("Transcription job failed.")
        return None

def connect_to_mongoDB(session):
    ami_id = 'ami-0a4408457f9a03be3'  # Replace with your desired AMI ID
    instance_type = 't2.micro'
    key_name = 'my-key-pair'  # Replace with your key pair name
    key_file = r'C:\VS Code\Project\my-key-pair.pem'  # Replace with the path to your PEM file

    ec2 = session.resource('ec2')
    client = session.client('ec2')

    try:
        response = client.create_security_group(
            GroupName='mongodb-sg',
            Description='Security group for MongoDB instance'
        )
        security_group_id = response['GroupId']

        client.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[{
                'IpProtocol': 'tcp',
                'FromPort': 27017,
                'ToPort': 27017,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }]
        )

        instances = ec2.create_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            KeyName=key_name,
            SecurityGroupIds=[security_group_id],
            MinCount=1,
            MaxCount=1
        )

        instance = instances[0]
        instance.wait_until_running()

        instance.load()
        public_ip = instance.public_ip_address

        print(f"EC2 Instance launched. Public IP: {public_ip}")

        def install_mongodb(ip, key_file):
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username='ubuntu', key_filename=key_file)

            commands = [
                'sudo apt update',
                'sudo apt install -y mongodb',
                'sudo systemctl start mongodb',
                'sudo systemctl enable mongodb'
            ]

            for command in commands:
                stdin, stdout, stderr = ssh.exec_command(command)
                print(stdout.read().decode())
                print(stderr.read().decode())

            ssh.close()

        time.sleep(60)
        install_mongodb(public_ip, key_file)

        print(f"MongoDB is set up on your EC2 instance. Connect to it using the following command:")
        print(f"mongo --host {public_ip} --port 27017")

    except Exception as e:
        print(f"An error occurred: {e}")

def upload_file_to_s3(bucket_name, file_path, s3_key, session):
    s3_client = session.client('s3')
    try:
        s3_client.upload_file(file_path, bucket_name, s3_key)
        print(f"File {file_path} uploaded to {bucket_name}/{s3_key}")
    except Exception as e:
        print(f"Error uploading file to S3: {e}")

def retrieve_email_ids_from_s3(bucket_name, s3_key, session):
    s3_client = session.client('s3')
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
        content = response['Body'].read().decode('utf-8')
        email_ids = content.splitlines()
        return email_ids
    except Exception as e:
        print(f"Error retrieving email IDs from S3: {e}")
        return []

def send_emails_to_s3_list(bucket_name, s3_key, session, email_subject, email_body):
    email_ids = retrieve_email_ids_from_s3(bucket_name, s3_key, session)
    if not email_ids:
        print("No email IDs found.")
        return

    ses_client = session.client('ses')
    for email_id in email_ids:
        try:
            response = ses_client.send_email(
                Source=input("Enter sender's Email Id: "),
                Destination={'ToAddresses': [email_id]},
                Message={
                    'Subject': {'Data': email_subject},
                    'Body': {'Text': {'Data': email_body}}
                }
            )
            print(f"Email sent to {email_id}. Message ID: {response['MessageId']}")
        except Exception as e:
            print(f"Error sending email to {email_id}: {e}")

def menu():
    aws_access_key_id ="enter_your_access_key_id"
    aws_secret_access_key ="enter_your_secret_access_key"
    session = init_aws_session(aws_access_key_id, aws_secret_access_key)

    while True:
        print("\nAWS Resource Management")
        print("1. Launch EC2 Instance")
        print("2. Start EC2 Instance")
        print("3. Stop EC2 Instance")
        print("4. Terminate EC2 Instance")
        print("5. Get EC2 Console Output")
        print("6. Create S3 Bucket")
        print("7. Upload File to S3")
        print("8. Start Transcription Job")
        print("9. Get Transcription Result")
        print("10. Connect to MongoDB")
        print("11. Send Emails to S3 List")
        print("12. Exit")

        choice = input("Enter choice: ")

        if choice == '1':
            ami_id = input("Enter AMI ID e.g.(ami-0a4408457f9a03be3): ")
            launch_ec2_instance(session, ami_id)
            input("Press Enter to return to the main menu...")
        elif choice == '2':
            instance_id = input("Enter Instance ID: ")
            start_ec2_instance(session, instance_id)
            input("Press Enter to return to the main menu...")
        elif choice == '3':
            instance_id = input("Enter Instance ID: ")
            stop_ec2_instance(session, instance_id)
            input("Press Enter to return to the main menu...")
        elif choice == '4':
            instance_id = input("Enter Instance ID: ")
            terminate_ec2_instance(session, instance_id)
            input("Press Enter to return to the main menu...")
        elif choice == '5':
            instance_id = input("Enter Instance ID: ")
            get_ec2_console_output(session, instance_id)
            input("Press Enter to return to the main menu...")
        elif choice == '6':
            bucket_name = input("Enter Bucket Name: ")
            create_s3_bucket(session, bucket_name)
            input("Press Enter to return to the main menu...")
        elif choice == '7':
            bucket_name = input("Enter Unique Bucket Name: ")
            file_path = input("Enter File Path: ")
            s3_key = os.path.basename(file_path)
            upload_to_s3(session, bucket_name, file_path,s3_key)
            input("Press Enter to return to the main menu...")
        elif choice == '8':
            job_name = input("Enter Job Name: ")
            bucket_name = input("Enter Bucket Name: ")
            file_name = input("Enter File Name: ")
            start_transcription_job(session, job_name, bucket_name, file_name)
            input("Press Enter to return to the main menu...")
        elif choice == '9':
            job_name = input("Enter Job Name: ")
            get_transcription_result(session, job_name)
            input("Press Enter to return to the main menu...")
        elif choice == '10':
            connect_to_mongoDB(session)
            input("Press Enter to return to the main menu...")
        elif choice == '11':
            bucket_name = input("Enter Bucket Name: ")
            s3_key = input("Enter S3 Key e.g.(email_ids.txt): ")
            email_subject = input("Enter Email Subject: ")
            email_body = input("Enter Email Body: ")
            send_emails_to_s3_list(bucket_name, s3_key, session, email_subject, email_body)
            input("Press Enter to return to the main menu...")
        elif choice == '12':
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    menu()
