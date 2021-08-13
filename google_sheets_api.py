from decouple import config
from apiclient import discovery
from google.oauth2 import service_account
import pandas as pd
from googleapiclient.errors import HttpError


class GoogleSheetsAPI:
    def __init__(self):
        self.scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file",
                       "https://www.googleapis.com/auth/spreadsheets"]
        self.env = {"type": config('GOOGLE_AUTH_TYPE'),
                    "project_id": config('GOOGLE_AUTH_PROJECT_ID'),
                    "private_key_id": config('GOOGLE_AUTH_PRIVATE_KEY_ID'),
                    "private_key": config('GOOGLE_AUTH_PRIVATE_KEY').replace('\\n', '\n'),
                    "client_email": config('GOOGLE_AUTH_CLIENT_EMAIL'),
                    "client_id": config('GOOGLE_AUTH_CLIENT_ID'),
                    "auth_uri": config('GOOGLE_AUTH_AUTH_URI'),
                    "token_uri": config('GOOGLE_AUTH_TOKEN_URI'),
                    "auth_provider_x509_cert_url": config('GOOGLE_AUTH_AUTH_PROVIDER_X509_CERT_URL'),
                    "client_x509_cert_url": config('GOOGLE_AUTH_CLIENT_X509_CENT_URL')}
        self.export_spreadsheet_id = config('EXPORT_SPREADSHEET_ID')
        self.range_prices = 'Prices!A3'
        self.range_events = 'ListOfEvents'
        self.range_events_manual = 'ListOfEventsManual'

    def export_prices(self, prices):
        print("Exporting Prices...")
        credentials = service_account.Credentials.from_service_account_info(self.env, scopes=self.scopes)
        service = discovery.build('sheets', 'v4', credentials=credentials)

        df_prices = pd.DataFrame(prices)
        df_prices.fillna('', inplace=True)

        try:
            service.spreadsheets().values().append(
                spreadsheetId=self.export_spreadsheet_id,
                range=self.range_prices,
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={
                    "values": df_prices.values.tolist()
                },
            ).execute()
        except HttpError as e:
            print(f"Got an error: {e.error_details}")

    def pull_events(self, choice_list):
        print("Pulling Betradar IDs")
        credentials = service_account.Credentials.from_service_account_info(self.env, scopes=self.scopes)
        service = discovery.build('sheets', 'v4', credentials=credentials)

        rows = service.spreadsheets().values().get(
            spreadsheetId=self.export_spreadsheet_id,
            range=choice_list,
        ).execute()
        data = rows.get('values')
        try:
            df = pd.DataFrame(data[1:], columns=data[0])
            betradar_ids = df['BetradarID'].tolist()
            return betradar_ids
        except TypeError:
            return []

    def pull_soccer_uof_codes(self):
        print("Pulling Betradar Soccer UOF codes")
        credentials = service_account.Credentials.from_service_account_info(self.env, scopes=self.scopes)
        service = discovery.build('sheets', 'v4', credentials=credentials)

        rows = service.spreadsheets().values().get(
            spreadsheetId=self.export_spreadsheet_id,
            range="SoccerUOFCodes",
        ).execute()
        data = rows.get('values')
        try:
            df = pd.DataFrame(data[1:], columns=data[0])
            soccer_uof = df['Soccer UOF Market Codes'].tolist()
            return soccer_uof
        except TypeError:
            return []

    def pull_tennis_uof_codes(self):
        print("Pulling Betradar Tennis UOF codes")
        credentials = service_account.Credentials.from_service_account_info(self.env, scopes=self.scopes)
        service = discovery.build('sheets', 'v4', credentials=credentials)

        rows = service.spreadsheets().values().get(
            spreadsheetId=self.export_spreadsheet_id,
            range="TennisUOFCodes",
        ).execute()
        data = rows.get('values')
        try:
            df = pd.DataFrame(data[1:], columns=data[0])
            tennis_uof = df['Tennis UOF Market Codes'].tolist()
            return tennis_uof
        except TypeError:
            return []