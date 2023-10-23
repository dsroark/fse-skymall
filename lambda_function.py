import os
import requests
import boto3
import xmltodict
import logging

logging.basicConfig()

try:
    fse_api_key = os.environ['FSE_API_KEY']
except KeyError as e:
    logging.error(f"Error: FSE_API_KEY environment variable not set, exiting")
    logging.error(f"Error message: {e}")
    exit(1)

def aircraft_for_sale(api_key):
    response = requests.get(f"https://server.fseconomy.net/data?userkey={api_key}&format=xml&query=aircraft&search=forsale")
    if response.status_code != 200:
        logging.error("Error fetching FSE data")
        logging.error(f"Response code: {response.status_code}")
        logging.error(f"Response text: {response.text}")
        return []
    aircraft_list = xmltodict.parse(response.content)['AircraftItems']['Aircraft']
    return aircraft_list

def check_aircraft_prices(criteria_list, aircraft_list):
    matching_aircraft = []

    for aircraft in aircraft_list:
        make_model = aircraft['MakeModel']
        sale_price = int(float(aircraft['SalePrice']))
        for criteria in criteria_list:
            if criteria['MakeModel'] == make_model and sale_price <= criteria['MaxPrice']:
                matching_aircraft.append({
                    'MakeModel': make_model,
                    'Equipment': aircraft['Equipment'],
                    'Registration': aircraft['Registration'],
                    'Location': aircraft['Location'],
                    'SalePrice': sale_price
                })
    
    return matching_aircraft

def construct_email_body(matching_aircraft):
    email_body = "Hello,\n\nHere are the aircraft that match your search criteria:\n\n"

    for i, aircraft in enumerate(matching_aircraft, 1):
        email_body += f"{i}. Make and Model: {aircraft['MakeModel']}\n"
        email_body += f"   - Registration: {aircraft['Registration']}\n"
        email_body += f"   - Equipment: {aircraft['Equipment']}\n"
        email_body += f"   - Location: {aircraft['Location']}\n"
        email_body += f"   - Sale Price: ${aircraft['SalePrice']}\n"
        email_body += "\n"

    email_body += "Best regards,\nYour friendly FSE SkyMall"

    return email_body

def send_email_with_ses(matching_aircraft_list):
    # Construct the email body
    email_body = construct_email_body(matching_aircraft_list)

    # Initialize the boto3 SES client
    client = boto3.client('ses', region_name='us-east-2')

    # Email details
    subject = 'Aircraft Search Results'
    sender_email = os.environ['EMAIL_FROM_ADDRESS']
    recipient_email = os.environ['EMAIL_TO_ADDRESS']

    response = client.send_email(
        Source=sender_email,
        Destination={
            'ToAddresses': [
                recipient_email,
            ]
        },
        Message={
            'Subject': {
                'Data': subject
            },
            'Body': {
                'Text': {
                    'Data': email_body
                },
            }
        }
    )

    return response

def lambda_handler(event, context):
    try:
        criteria_list = event['criteria_list']
    except KeyError as e:
        logging.error(f"Error: event does not contain a criteria_list object")
        logging.error(f"Error message: {e}")
        exit(1)

    aircraft_list = aircraft_for_sale(fse_api_key)

    if not aircraft_list:
        logging.info('No aircraft found!')
        return None
    
    matching_aircraft = check_aircraft_prices(criteria_list, aircraft_list) 

    email_body = construct_email_body(matching_aircraft)

    if matching_aircraft:
        if os.environ.get('EMAIL_TO_ADDRESS') and os.environ.get('EMAIL_FROM_ADDRESS'):
            return send_email_with_ses(matching_aircraft)
        else:
            print(email_body)
    else:
        logging.warning("No aircraft match search criteria!")


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    simulated_event = {
        'criteria_list': [
            {'MakeModel': 'Piper PA-24 Comanche (A2A)', 'MaxPrice': 350000},
            {'MakeModel': 'Cessna 172', 'MaxPrice': 200000}
        ]
    }
    simulated_context = {}

    result = lambda_handler(simulated_event, simulated_context)

    print("Lambda function returned:", result)
