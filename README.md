# FSE SkyMall
FSE SkyMall is a plane price tracker Lambda for [FSEconomy](https://www.fseconomy.net/). This is a simple lambda function that checks a list of planes with max price points against the master list of planes publicly for sale on FSE. If there is a match and email is configured, a message will be sent notifying the user of the planes that match the search criteria.

## Installation

Follow the instructions in the [lambda installation guide for Python](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html) and deploy to your lambda (TODO: I plan to add Pulumi support). Use the `requirments.txt` file when installing packages for your lambda deployment.

For email notification, you will need to set up your own SES identity to mail to and from. Without email the function will send the email body to STDOUT, and can be used that way.

## Running

### Lambda

1. Set up an Eventbridge schedule that is compatible with the API limits set by FSE (I chose 1 invocation/hour).
2. The event needs to be sent with the following payload

```
{
  "criteria_list": [
    {"MakeModel": "<Plane model as it appears in FSE>", "MaxPrice": <integer price point>},
    {'MakeModel': 'Cessna 172', 'MaxPrice': 250000}
  ]
}
```

3. The following environment variables are expected to be set on the lambda:

```
FSE_API_KEY (required)
EMAIL_TO_ADDRESS (optional)
EMAIL_FROM_ADDRESS (optional)
```
4. The Lambda will require the following AWS Policy attached to its role to work with SES. Resources can be targeted to your "to" and "from" SES identities.
```
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "SESEmailSending",
			"Effect": "Allow",
			"Action": [
				"ses:SendEmail",
				"ses:SendRawEmail"
			],
			"Resource": "*"
		}
	]
}
```

### Local execution

1. Modify the `simulated_event` variable to your desired value in the `__main__` guard
2. Activate your virtualenv (`source venv/bin/activate`)
3. Run with `python3 lambda_function.py`.

The same env vars will need to be set in your terminal that need to be set for the lambda.

## Development

1. Clone the repository
2. Set up and source your virtualenv (I use `python3 -m venv venv/ && source venv/bin/activate`)
3. Install packages with `pip install -r dev-requirements.txt`

This project uses `pip` and `pip-tools` for package management.
