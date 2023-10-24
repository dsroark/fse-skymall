# fse-skymall
Plane Price Tracker Lambda for Flight Sim Economy. This is a super simple lambda function that checks a list of planes with max price points against the master list of planes for sale from FSE. If there is a match and email is configured, a message will be sent notifying the user of the planes that match the search criteria.

## Installation

Follow the instructions in the [lambda installation guide for Python](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html) and deploy to your lambda (TODO: I plan to add Pulumi support). Use the `requirments.txt` file when installing packages for your lambda deployment.

For email notification, you will need to set up your own SES identity to mail to and from. Without email the function will send the email body to STDOUT, and can be used that way.

## Running

### Lambda

Set up an Eventbridge schedule that is compatible with the API limits set by FSE (I chose 1 invocation/hour). The event needs to be sent with the following payload

```json
{
  "criteria_list": [
    {"MakeModel": "<Plane model as it appears in FSE>", "MaxPrice": <integer price point>},
    {'MakeModel': 'Cessna 172', 'MaxPrice': 250000}
  ]
}
```

The following environment variables are expected to be set:

```
FSE_API_KEY (required)
EMAIL_TO_ADDRESS (optional)
EMAIL_FROM_ADDRESS (optional)
```

### Local execution

Modify the `simulated_event` variable in the `__main__` guard, activate your virtualenv, and run with `python3 lambda_function.py`.

The same env vars will need to be set in your terminal that need to be set for the lambda.

## Development

1. Clone the repository
2. Set up and source your virtualenv (I use `python3 -m venv venv/ && source venv/bin/activate`)
3. Install packages with `pip install -r dev-requirements.txt`
