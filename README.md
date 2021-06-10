# Programming vacancies compare
This program compares the salaries of programmers (Python, JavaScript,
Java, Rubby, PHP, C++, CSS, C#) in Moscow. 
Statistics are based on these sites:
1. <https://hh.ru/> 
2. <https://www.superjob.ru/>

## How to install

For the program to work, you need to get a 'SECRET_KEY' by registering on
[SuperJob.ru](https://api.superjob.ru/#) which is taken from the `.env` file.

```python
sj_token = os.getenv('SJ_TOKEN')
```

The `.env` file is located in the root directory
```
├── .env
└── main.py
```

In the `.env` file, the keys are written as follows:

```python
SJ_TOKEN=[secret key]
```
 
Python3 must already be installed. Then use pip (or pip3 if you have
conflict with Python3) to install dependencies:

```python
pip install -r requirements.txt
```

The program is started by the command:

```python
python main.py
```


## Project Goals
The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org).