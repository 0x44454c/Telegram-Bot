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
    UNITS_MAPPING = [
	(1<<50, ' PB'),
	(1<<40, ' TB'),
	(1<<30, ' GB'),
	(1<<20, ' MB'),
	(1<<10, ' KB'),
	(1<<3, ' Bytes'),
    ]

    # auxiliary methods
    def gdAuth(self, gauth, credentialFile):
        gauth.LoadCredentialsFile(path.join(self.CWP, credentialFile))
        if gauth.access_token_expired:
            gauth.Refresh()
            gauth.SaveCredentialsFile(path.join(self.CWP, credentialFile))
        else:
            gauth.Authorize()

    def size(self, bytes):
        units = self.UNITS_MAPPING
        for factor, suffix in units:
            if bytes >= factor:
                break
        amount = round(bytes / factor, 2)
        return str(amount) + suffix