import os
import os.path as path
from dotenv import load_dotenv
load_dotenv()


class AUX():
    # auxiliary objects
    TOKEN = os.getenv('BOT_TOKEN')
    SHARED_DRIVE_ID = os.getenv('SHARED_DRIVE_ID')
    SHARED_DRIVE_FOLDER_ID = os.getenv('SHARED_DRIVE_FOLDER_ID')
    CWP = path.abspath(path.join(path.dirname(__file__), '..'))

    # auxiliary methods
    def gdAuth(self, gauth):
        gauth.LoadCredentialsFile(path.join(self.CWP, 'credentials.json'))
        if gauth.access_token_expired:
            gauth.Refresh()
            gauth.SaveCredentialsFile(path.join(self.CWP, 'credentials.json'))
        else:
            gauth.Authorize()
