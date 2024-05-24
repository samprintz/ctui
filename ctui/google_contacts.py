from datetime import date,datetime
import pickle
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from objects import GoogleContact, GoogleAttribute, GoogleNote


class GoogleStore:

    def __init__(self, core, credentials_file, token_file):
        self.core = core
        # If modifying these scopes, delete the file token.pickle.
        # Scopes: https://developers.google.com/people#people
        SCOPES = ['https://www.googleapis.com/auth/contacts']

        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        #TODO token.pickle file path by config
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                #TODO credentials.json file path by config
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('people', 'v1', credentials=creds)


    def get_all_contact_names(self):
        results = self.service.people().connections().list(
            resourceName='people/me', pageSize=1000,
            personFields='names').execute()
        connections = results.get('connections', [])

        contact_names = []
        for person in connections:
            names = person.get('names', [])
            if names:
                name = names[0].get('displayName')
                name = name + " [G]"
                contact_names.append(name)
        return sorted(contact_names)

    def get_all_contacts(self):
        results = self.service.people().connections().list(
            resourceName='people/me', pageSize=1000,
            personFields='names,birthdays,addresses,emailAddresses,phoneNumbers,biographies').execute()
        connections = results.get('connections', [])

        contacts = []
        for person in connections:
            contact_id = person['resourceName']
            names = person.get('names', [])
            if names:
                display_name = names[0].get('displayName')
                family_name = names[0].get('familyName')
                given_name = names[0].get('givenName')
                honorific_prefix = names[0].get('honorificPrefix')

            attributes = []
            notes = []

            biographies = person.get('biographies', [])
            if biographies:
                for biography in biographies:
                    notes.append(GoogleNote(biography['value']))

            birthdays = person.get('birthdays', [])
            if birthdays:
                b = birthdays[0].get('date')
                if b is not None:
                    year = str(b['year']) if 'year' in b else ''
                    month = str(b['month']) if 'month' in b else ''
                    day = str(b['day']) if 'day' in b else ''
                    #b_date = datetime(year, month, day)
                    #b_string = datetime.strftime(b_date, '%d.%m,%Y')
                    b_string = '.'.join([day, month, year])
                else:
                    b_string = birthdays[0].get('text')
                    b_string = b_string.replace('/', '.')
                attributes.append(GoogleAttribute('birthday', b_string, 'birthdays'))

            #TODO
            #addresses = person.get('addresses', [])
            #if addresses:
            #for address in addresses:

            email_addresses = person.get('emailAddresses', [])
            if email_addresses:
                for email_address in email_addresses:
                    attributes.append(GoogleAttribute('email', email_address.get('value'), 'emailAddresses'))

            phone_numbers = person.get('phoneNumbers', [])
            if phone_numbers:
                for phone_number in phone_numbers:
                    attributes.append(GoogleAttribute('tel', phone_number.get('value'), 'phoneNumbers'))

            contact = GoogleContact(display_name, self.core, contact_id, attributes, notes)
            contacts.append(contact)

        return contacts


        # Fields of Person object: https://developers.google.com/people/api/rest/v1/people#Person
        # People API (deleteContact, createContact, ...): http://googleapis.github.io/google-api-python-client/docs/dyn/people_v1.people.html
        # Example of createContact: https://gist.github.com/samkit5495/ff8e2a6644363cadaec3fa22ddf38c90


    def add_contact(self, contact):
        res = self.service.people().createContact(body=contact).execute()

    def delete_contact(self, contact):
        res = self.service.people().deleteContact(
                resourceName=contact.google_id).execute()




    def edit_contact(self, contact, new_contact):
        # Test edit contact
        print("\nTest: Edit contact")
        updatedContact = res
        updatedContact["emailAddresses"] = [{
            "type": "home",
            "value": "test@test.il"
            }]

        res = self.service.people().updateContact(resourceName=contactId,
                body=updatedContact, updatePersonFields='emailAddresses').execute()
        print(str(res)[:60] + "...")


    def edit_email(self, contact, email, new_email):
        field = "emailAddresses"
        contact[field] = [{
            "type": "home",
            "value": "test@test.il"
            }]
        res = service.people().updateContact(resourceName=contact['resourceName'],
                body=updatedContact,
                updatePersonFields='emailAddresses').execute()

