# Use Selenium driver to scrape the webpage for each professor's specific url 
# and then Beautiful soup to parse the html

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from requests import get
from random import randint
import pandas as pd
from user_agent import generate_user_agent
import time
import re
import pickle




###We use the webpage that lists all the rated teachers at the specific university.

url = "http://www.ratemyprofessors.com/search.jsp?queryoption=TEACHER&queryBy=schoolDetails&schoolID=5436&schoolName=University+of+British+Columbia+-+Okanagan&dept=select"
driver = webdriver.Chrome(executable_path = "chromedriver.exe")
driver.implicity_wait(30)
driver.get(url)

#handle the pop up
popup = driver.find_element_by_xpath('//a[@class= "close-notice close-this"]')
popup.click()

target = driver.find_element_by_xpath('//div[@class ="content"]')

#Click the load more button until the list is exhausted
while True:
    try:
        driver.execute_script("arguments[0].scrollIntoView()", target);
        target.click()
        time.sleep(randint(3,5))
    except Exception as e:
        print(e)
        break;

soup = BeautifulSoup(driver.page_source, 'lxml')
urls = []
names = []
grades = []

#use regex grab the containers with professors name and urls for the professors specific pages
for prof in soup.find_all('li', id = re.compile('^my-professor-')):
    rating = prof.find('span', class_ = 'rating').text
    if rating != 'N/A':
        urls.append(prof.a['href'])
        names.append(prof.find('span', class_="name").text)
        grades.append(float(rating))

for i, k in enumerate(urls):
    urls[i] = 'http://www.ratemyprofessors.com' + k.strip()

#let's clean up the names list, by stripping out white space at beginning
# returning only lastname, first name
#swapping lastname and firstname positions
for i,k in enumerate(names):
    temp1 =k.strip().splitlines()[0]
    temp2 = temp1.split(",")
    names[i] = temp2[1] + " " + temp2[0]

data = pd.DataFrame({"Name": names, "URL" : urls, "Grade": grades})
pickle.dump(data, open("MyPersonalProject/urls_ubco.p", 'wb'))

####
#Next, the script will visit every url we've collected, and grab additional
#information about each professor, including their most common tags and
#the department they teach in
###
i = 1
tagratings = []
dept = []
for url in urls:
    user = {'User-Agent' : generate_user_agent()}
    request = get(url, user)
    print("Request", i, " was made.")
    if request.status_code == 200:
        time.sleep(randint(3,8))
        print("Request ", i, " was successful")
        proftags = []
        soup = BeautifulSoup(request.text, 'lxml')
        dept.append(soup.find("div", class_="result-title").text.strip().splitlines()[0])
        containers = soup.find_all("span", class_= "tag-box-choosetags")
        if containers is not None:
            for each in containers:
                tag = each.text.split("(")[0].strip()
                proftags.append(tag)
        tagratings.append(proftags)
        i+=1

pickle.dump(tagratings, open("MyPersonalProject/tagratings_ubco.p", 'wb'))
pickle.dump(dept, open ("MyPersonalProject/dept_ubco.p", 'wb'))

def clean_dep(val):
    temp = val.strip().split()
    return " ".join(temp[3:-1])

for i,k in enumerate(dept):
    dept[i] = clean_dep(k)
##

#Let's look at the tags which speak most to the professors personality more so
##than the coursework itself.

care = []
hil = []
res = []
inspo = []
access = []

for each in tagratings:
    val = 0
    if 'Caring' in each:
        val = 1
    care.append(val)
    val = 0
    if 'Respected' in each:
        val = 1
    res.append(val)
    val = 0
    if 'Hilarious' in each:
        val = 1
    hil.append(val)
    val = 0
    if 'Inspirational' in each:
        val = 1
    inspo.append(val)
    val = 0
    if 'ACCESSIBLE OUTSIDE CLASS' in each:
        val = 1
    access.append(val)

data = pd.DataFrame({"Name": names, "Grade": grades, "Caring" : care, "Funny" : hil,
                      "Respect":res, "Inspire": inspo, "Access": access, "Department": dept})

pickle.dump(data, open("datasets/UBCO_data.p", 'wb'))

######
