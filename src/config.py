import os
import os.path as path
from dotenv import load_dotenv
load_dotenv()

class CON():
    TOKEN = os.getenv('BOT_TOKEN')
    SHARED_DRIVE_ID = os.getenv('SHARED_DRIVE_ID')
    SHARED_DRIVE_FOLDER_ID = os.getenv('SHARED_DRIVE_FOLDER_ID')
    CWP = path.abspath(path.join(path.dirname(__file__),'..'))
