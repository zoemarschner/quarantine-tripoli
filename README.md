# quarantine-tripoli
A socially distant way to deal hands for tripoli, through a web app that allows each person to view their cards.

## Development
This app is built in flask. To run it locally, first create a virtual enviorment and install the requirements with 
```
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
```
Then before first running the app in a new terminal session, set the enviorment variable up with
```
export FLASK_APP=tripoli.py
```
and then the app can be run with 
```
flask run
```
