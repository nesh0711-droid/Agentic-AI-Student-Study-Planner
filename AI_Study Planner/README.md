*** THINGS TO DO BEFORE RUN THE CODE ***

===============================

STEP 1: CREATE TOKEN IN CANVAS

===============================

a. Login into your canvas

b. Go to account, then settings

c. Scroll down until you see "New Access Token"

d. Click that and generate token

e. You will get API key, copy and paste in config.py

=========================================

STEP 2: CREATE API KEY IN GOOGLE CONSOLE

=========================================

a. Search for "Google Cloud Console"

b. Sign up using your email

c. Then click "New Project"

d. After create the project, search for "API Library"

e. Search for "Google Calendar", click and enable it.

f. After that it will show the Google Calendar API page

g. Then go to "credentials" and click "create credentials" button.

h. It will shows 3 option, select the "OAuth client ID"

i. Then it will show warning "you must configure consent screen"

j. Click "get started" 

k. Fill the app information (make sure use the same email used for login in support user section)

l. Select "External" in audience section , then fill in email address and click create

m. Once you clicked, it will show "OAuth Overview" . Click the "Create OAuth Client ID"

n. Select "Desktop app" as application type then click create

o. Once done ,it will show like the API key, don't download first , just click ok.

p. Go to Data Access section, then  click "add scopes"

q. Search "Google Calendar API" and select the first one (/auth/calendar) & (/auth/calendar.events), then click update

r. Now go audience section, click "add users" in test users section and write your same email (*if you didn't do this you cannot access the API*)

s. Then go to clients , click the name and download the client secrets (in json format)

t. Name as client_secret.json and replace it in credentials folder.

================================

STEP 3: RUN THE CODE IN VS CODE

================================

a. Install all the libraries (pip install pandas numpy scikit-learn xgboost joblib requests matplotlib google-api-python-client google-auth google-auth-oauthlib python-dateutil streamlit pandas)

b. Run "streamlit app.py" in terminal.

