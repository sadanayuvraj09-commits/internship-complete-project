import os
from dotenv import load_dotenv
load_dotenv()

email_from = os.getenv("EMAIL_FROM")
email_pass = os.getenv("EMAIL_APP_PASSWORD")

print("EMAIL_FROM repr:", repr(email_from))
print("EMAIL_APP_PASSWORD repr:", repr(email_pass))
print("EMAIL_APP_PASSWORD length:", len(email_pass) if email_pass else 0)