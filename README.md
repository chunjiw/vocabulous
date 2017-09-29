This app allows user to create their own Ebbinghaus English vocabulary review book.

Steps:
1. Go to https://takeout.google.com/settings/takeout, download your search data
2. Go to https://developer.oxforddictionaries.com/, get your own API id and key. Note that the free plan allows 3k requests per month.
3. Create a python file credentials.py with three lines:
    app_id = 'your_app_id'
    app_key = 'your_app_key'
    gdata_directory = "your_directory/Google Download Your Data/"
4. Run mainscript.py
5. Import the generated csv file to Anki.

TODO:
create usec.txt if not exist

