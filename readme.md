# Golestan reporter
This project is a simple python3 script who helps Iranian university students and sends the latest news of their university Golestan system news via email

## Installation
first install requirements. you can install them by:
```bash
python3 -m pip install -r requerments.txt
```

then creat a file named as "mailconfig.py" contains your email address and password:
```python
sender_email = 'yourname@example.com'
password = 'yourpassword'
```
*Notice: if you're using gmail remember that alow low secure apps from google acount manager*

you can change common configuration from "config.py" file. change golestan_news_source to your university news source.
keep mind that you must read source of golestan pages to find news source. try using "curl". you can ask me for help on this one.

and at end add a mail-list. create "mail_list.txt" and add mails address (one per line). like this:
```
blabla@example.com
foobar@sample.com
```

then just run main.py with python3 on your server.