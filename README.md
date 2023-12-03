This project does the following:

- Recieves alerts from Tradingview webhooks
- Executes orders for inversely correlated pairs in various exhanges via AWS Lambda

Important information:

- Market orders are assumed to execute instantaneously
- Only one position of an inversely paired trade is held at a time (recommended to use subaccounts to trade multiple inversely correlated pairs)

Dependencies:

- Tradingview is setup to send alerts to desired route (exchange based)
- AWS Chalice (Serverless Framework)
- AWS Account setup with AWS Lambda
- AWS DynamoDB instances to save data to
- Kucoin Python SDK

How to start project:

- Check python 3.7.3 is installed
- python3 --version
- Setup virtual environment
- python3 -m venv venv37
- . venv37/bin/activate
- Install AWS Chalice - https://github.com/aws/chalice
- python3 -m pip install chalice
- Install package dependencies
- pip3 install -r requirements.txt
- Run project locally
- chalice local

- Setup environment with AWS credentials
- cat >> ~/.aws/config
  [default]
  aws_access_key_id=YOUR_ACCESS_KEY_HERE
  aws_secret_access_key=YOUR_SECRET_ACCESS_KEY
  region=YOUR_REGION (such as us-west-2, us-west-1, etc)
- Deploy server
- chalice deploy

Accounts:

- Setup personal take rates, fill in blanks, etc by searching for <insert>

Kucoin:

- Add crendentils to the constants file in the relevant exchange

AWS:

DynamoDB:

- Setup DynamoDB instances that you would like to save data to by using Developer functions in Dynamo_DB file
