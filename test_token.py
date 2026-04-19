from security.jwt_handler import create_access_token
from datetime import timedelta
print(create_access_token({'sub': 'cliente@example.com'}, expires_delta=timedelta(days=1)))
