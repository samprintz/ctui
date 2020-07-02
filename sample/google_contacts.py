import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import pudb


class GoogleStore:

    def __init__(self, credentials_file, token_file):
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


    def get_all_contacts_names(self):
        results = self.service.people().connections().list(
            resourceName='people/me',
            personFields='names,emailAddresses').execute()
        connections = results.get('connections', [])

        contact_names = []
        for person in connections:
            names = person.get('names', [])
            if names:
                name = names[0].get('displayName')
                name = name + " [G]"
                contact_names.append(name)
        return sorted(contact_names)


    def add_contact(self, contact):
            # Fields of Person object: https://developers.google.com/people/api/rest/v1/people#Person
            # People API (deleteContact, createContact, ...): http://googleapis.github.io/google-api-python-client/docs/dyn/people_v1.people.html
            # Example of createContact: https://gist.github.com/samkit5495/ff8e2a6644363cadaec3fa22ddf38c90
            print("\nTest: Add contact")
            contact = {"names": [{
                "givenName": "Aaabbb",
                "familyName": "Aaaccc"
            }]}
            res = self.service.people().createContact(body=contact).execute()
            print(str(res)[:60] + "...")
            contactId = res['resourceName']

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


    def delete_contact(self, contact):
        # Test delete contact
        print("\nTest: Delete contact")
        res = self.service.people().deleteContact(resourceName=contactId).execute()
        print(str(res)[:60] + "...")

