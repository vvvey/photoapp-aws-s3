# PhotoApp

## Description
PhotoApp is a simple application for managing and processing photos. This application allows users to upload, edit, and manage their photo libraries with ease.

## Requirements
Make sure you have the following installed:
- Python 3.x
- Required libraries

## Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/vvvey/photoapp-aws-s3.git
   cd photoapp

2. **Install Python Requirements**:
    - boto3
    - matplotlib
    - pymysql
3. **Edit the photoapp-config.init**:
    ```ini
    [s3]
    bucket_name = BUCKET_NAME

    [rds]
    endpoint = ENDPOINT_HOST
    port_number = 3306
    region_name = us-east-2
    user_name = USERNAME
    user_pwd = PASSWORD
    db_name = DB_NAME

    [s3readonly]
    region_name = us-east-2
    aws_access_key_id = ACCESS_KEY
    aws_secret_access_key = SECRET_KEY

    [s3readwrite]
    region_name = us-east-2
    aws_access_key_id = ACCESS_KEY
    aws_secret_access_key = SECRET_KEY

5. **Run Program**:
    ```bash
    python main.py
