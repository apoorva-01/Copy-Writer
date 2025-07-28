import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class BrandDataManager:
    def __init__(self):
        self.SCOPES = [
            'https://www.googleapis.com/auth/spreadsheets.readonly',
            'https://www.googleapis.com/auth/documents.readonly'
        ]
        self.service = self._authenticate()
        self.docs_service = self._authenticate_docs()
        self.spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID')
        self.sheet_name = 'Sheet1'
        self.header_row = None
        self.brand_rows = None

    def _authenticate(self):
        creds = None
        credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        if credentials_json:
            try:
                import json
                from google.oauth2 import service_account
                credentials_info = json.loads(credentials_json)
                creds = service_account.Credentials.from_service_account_info(
                    credentials_info, scopes=self.SCOPES
                )
                print("✅ Google Sheets authenticated via credentials JSON")
            except Exception as e:
                print(f"Failed to load credentials from JSON: {str(e)}")
        if not creds:
            service_account_path = os.getenv('GOOGLE_SERVICE_ACCOUNT_PATH')
            if service_account_path and os.path.exists(service_account_path):
                try:
                    from google.oauth2 import service_account
                    creds = service_account.Credentials.from_service_account_file(
                        service_account_path, scopes=self.SCOPES
                    )
                    print("✅ Google Sheets authenticated via service account file")
                except Exception as e:
                    print(f"Failed to load credentials from file: {str(e)}")
        if not creds:
            token_path = 'token.json'
            credentials_path = 'credentials.json'
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if os.path.exists(credentials_path):
                        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.SCOPES)
                        creds = flow.run_local_server(port=0)
                        print("✅ Google Sheets authenticated via OAuth")
                if creds and hasattr(creds, 'to_json'):
                    with open(token_path, 'w') as token:
                        token.write(creds.to_json())
        if not creds:
            print("⚠️  No Google credentials found - brand data features will not work")
            return None
        try:
            return build('sheets', 'v4', credentials=creds)
        except Exception as e:
            print(f"Google Sheets API initialization failed: {str(e)}")
            return None

    def _authenticate_docs(self):
        creds = None
        credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        if credentials_json:
            try:
                import json
                from google.oauth2 import service_account
                credentials_info = json.loads(credentials_json)
                creds = service_account.Credentials.from_service_account_info(
                    credentials_info, scopes=self.SCOPES
                )
            except Exception as e:
                print(f"Failed to load credentials from JSON: {str(e)}")
        if not creds:
            service_account_path = os.getenv('GOOGLE_SERVICE_ACCOUNT_PATH')
            if service_account_path and os.path.exists(service_account_path):
                try:
                    from google.oauth2 import service_account
                    creds = service_account.Credentials.from_service_account_file(
                        service_account_path, scopes=self.SCOPES
                    )
                except Exception as e:
                    print(f"Failed to load credentials from file: {str(e)}")
        if not creds:
            token_path = 'token.json'
            credentials_path = 'credentials.json'
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if os.path.exists(credentials_path):
                        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.SCOPES)
                        creds = flow.run_local_server(port=0)
                if creds and hasattr(creds, 'to_json'):
                    with open(token_path, 'w') as token:
                        token.write(creds.to_json())
        if not creds:
            print("⚠️  No Google credentials found for Docs API")
            return None
        try:
            return build('docs', 'v1', credentials=creds)
        except Exception as e:
            print(f"Google Docs API initialization failed: {str(e)}")
            return None

    def _load_brand_sheet(self):
        if self.header_row and self.brand_rows:
            return self.header_row, self.brand_rows
        if not self.service or not self.spreadsheet_id:
            return [], []
        try:
            range_name = f"{self.sheet_name}!A1:Z1000"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id, range=range_name
            ).execute()
            values = result.get('values', [])
            if not values or len(values) < 2:
                return [], []
            self.header_row = values[0]
            self.brand_rows = values[1:]
            return self.header_row, self.brand_rows
        except Exception as e:
            print(f"Error loading brand sheet: {str(e)}")
            return [], []

    def get_available_brands(self):
        header, rows = self._load_brand_sheet()
        brands = [row[0] for row in rows if row and row[0]]
        return brands

    def get_brand_docs_context(self, brand_name):
        header, rows = self._load_brand_sheet()
        brand_row = None
        for row in rows:
            if row and row[0].strip().lower() == brand_name.strip().lower():
                brand_row = row
                break
        if not brand_row:
            return {}
        context = {}
        for idx, col_name in enumerate(header):
            if idx == 0:
                context['brand_name'] = brand_row[0]
                continue
            
            if col_name in ['Buying Persona Google Doc ID', 'Youtub Google Doc ID']:
                doc_id = brand_row[idx] if idx < len(brand_row) else ''
                if doc_id:
                    doc_content = self._fetch_google_doc_content(doc_id)
                   # Truncate to first 1000 characters to avoid context length issues
                    context[col_name] = doc_content[:1000] if doc_content else ''
        return context

    def _fetch_google_doc_content(self, doc_id):
        if not self.docs_service:
            return ''
        try:
            doc = self.docs_service.documents().get(documentId=doc_id).execute()
            content = self._extract_text_from_google_doc(doc)
            return content
        except Exception as e:
            print(f"Error fetching Google Doc {doc_id}: {str(e)}")
            return ''

    def _extract_text_from_google_doc(self, doc):
        text = ''
        try:
            for element in doc.get('body', {}).get('content', []):
                if 'paragraph' in element:
                    for elem in element['paragraph'].get('elements', []):
                        if 'textRun' in elem:
                            text += elem['textRun'].get('content', '')
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from Google Doc: {str(e)}")
            return '' 