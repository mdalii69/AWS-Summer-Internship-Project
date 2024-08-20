# AWS-Summer-Internship-Project

## AWS Automation with Python

This repository contains a comprehensive Python script designed to automate various AWS services. The script is modular, allowing you to manage different AWS resources such as EC2 instances, S3 buckets, AWS Transcribe, MongoDB setup on EC2, and sending emails via SES.

## Features

### 1. **EC2 Instance Management**
   - **Launch EC2 Instances**: The script allows you to launch EC2 instances with a specified AMI ID and instance type. 
   - **Start/Stop/Terminate Instances**: Easily start, stop, or terminate EC2 instances by providing the instance ID.
   - **Retrieve Console Output**: View the console output of an EC2 instance for debugging purposes.

### 2. **S3 Operations**
   - **Create S3 Buckets**: Quickly create an S3 bucket in your specified region.
   - **Upload Files to S3**: Upload files to your S3 bucket with just a few lines of code. The script handles the file path and object name seamlessly.

### 3. **AWS Transcribe Integration**
   - **Start Transcription Jobs**: Upload an audio file to S3 and start an AWS Transcribe job to convert it to text. The script will monitor the job until it completes.
   - **Retrieve Transcription Results**: Automatically fetch the transcription result once the job is done, providing a download link for the transcript.

### 4. **MongoDB Setup on EC2**
   - **Launch EC2 for MongoDB**: The script can launch an EC2 instance, configure security groups, and set up MongoDB automatically using SSH commands.
   - **Automated MongoDB Installation**: After the instance is running, the script installs MongoDB, starts the service, and enables it on startup.

### 5. **SES Email Automation**
   - **Send Emails Using SES**: The script retrieves email addresses from an S3 file and sends emails to each address using AWS SES. It allows you to specify the subject and body of the email.

## Usage

1. **AWS Session Initialization:**  
   Initialize the AWS session using your access key, secret key, and region.

   ```python
   session = init_aws_session('your_access_key_id', 'your_secret_access_key')
   ```
2. **Launch an EC2 Instance:**  
   ```python
   instance_id = launch_ec2_instance(session, 'ami-0a4408457f9a03be3')
   ```
3. **Create and Upload to S3:**  
   ```python
   create_s3_bucket(session, 'your-unique-bucket-name')
   upload_to_s3(session, 'your-unique-bucket-name', 'path/to/your/file')
   ```
4. **Start a Transcription Job:**  
   ```python
   job_name = start_transcription_job(session, 'your-job-name', 'your-bucket-name', 'your-audio-file.wav')
   ```
5. **Set Up MongoDB on EC2:**  
   ```python
   connect_to_mongoDB(session)
   ```
6. **Send Emails Using SES:**  
   ```python
   send_emails_to_s3_list('your-bucket-name', 'email_ids.txt', session, 'Your Email Subject', 'Your Email Body')
   ```

### Menu-Driven Interface

The script comes with an interactive menu that guides you through each function step by step, making it easy to manage your AWS resources without needing to write additional code.

```plaintext
**AWS Resource Management**
1. Launch EC2 Instance
2. Start EC2 Instance
3. Stop EC2 Instance
4. Terminate EC2 Instance
5. Get EC2 Console Output
6. Create S3 Bucket
7. Upload File to S3
8. Start Transcription Job
9. Get Transcription Result
10. Connect to MongoDB
11. Send Emails to S3 List
12. Exit
```

### Prerequisites

- Python 3.x
- boto3 for AWS SDK
- paramiko for SSH communication
- AWS credentials (Access Key ID and Secret Access Key)
- PEM file for SSH access to EC2

### Installation

Clone this repository and install the necessary dependencies:

```bash
git clone https://github.com/yourusername/aws-automation-python.git
cd aws-automation-python
pip install boto3 paramiko
```
### Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request if you have suggestions for improvements or additional features.

### License

This project is licensed under the MIT License.
