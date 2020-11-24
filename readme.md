# Golestan reporter
[![License: LGPL v3](https://img.shields.io/static/v1?label=License&message=LGPL%20v3+&color=blue)](./license.md)
![python: 3.8](https://img.shields.io/static/v1?label=python&message=3.4%2B&color=yellow)

### What is golestan?
Golestan is a legacy system! most of Iranian universities use this system for news and storing students information.

### what does golestan reporter do?
Golestan Reporter is useful for Iranian students. This app uses an internal database to send the latest news uploaded to Golestan via email.

### Why we store students other information?
My idea is to use a single database for all of my future projects for university students.


## Installation
1. After clone or download source code; first install requirements.
```bash
python3 -m pip install -r requirements.txt
```

2. Then create your own copy of `config-example.ini` file and name it as `config.ini`
    - `config.ini` is ignored

3. Open `config.ini` and change smtp settings, email & password and ...

4. then run `main.py`
```bash
python3 main.py
```

***
#### Related docs
- [TODO](./doc/TODO.md)
- [License](./doc/license.md)