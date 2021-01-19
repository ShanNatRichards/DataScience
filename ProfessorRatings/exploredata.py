import pickle
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import style


#De-pickle our stores data and load
file = pickle.load(open("datasets/SFU_Data.p", 'rb'))
file2 = pickle.load(open("datasets/OC_Data.p", 'rb'))
file3 = pickle.load(open("datasets/UBCO_data.p", 'rb'))

sfu = pd.DataFrame(file)
oc = pd.DataFrame(file2)
ubc = pd.DataFrame(file3)

print(sfu.head(20))
print(sfu.info())
print(sfu.describe())
print(ubc.head(20))
print(ubc.info())
print(ubc.describe())
print(oc.head(20))
print(oc.info())
print(oc.describe())

##Let's add a column for the universities since we're eventually going to combine
##all 3 datframes into one
sfu['Uni'] = "SFU"
oc['Uni'] = "OC"
ubc['Uni'] = "UBCO"


#Let's have a look at the departments for each university and see if we can tidy
#up the categories to make for better comparissons
print(ubc.Department.unique())
print(sfu.Department.unique())
print(oc.Department.unique())

#There are a couple of broad categories that we can use Natural Sciences,
#Math & Statistics, Social Sciences, Computer Sciences, Engineering...etc
#Below, defined function to reorganize dept according to these categories

def tidy(val):
    if val.lower().find("engineering") != -1:
        return "Engineering"
    elif val.lower().find("math") != -1 or val.lower().find("statistics") != -1 :
        return "MathStats"
    elif val.lower().find("biology") != -1 or val.lower().find("chemistry") != -1 or\
    val.lower().find("physics") != -1 or  val.lower().find("astro") != -1:
        return "Sciences"
    elif val.lower().find("computer") != -1:
        return "CompSci"
    elif val.lower().find("business") != -1 or val.lower().find("management") != -1 or\
    val.lower().find("accounting") != -1 or val.lower().find("finance") != -1 or\
    val.lower().find("comm") != -1:
        return "Business"
    elif val.lower().find("medic") != -1 or val.lower().find("kine") != -1 or\
    val.lower().find("nursing") != -1 or val.lower().find("health") != -1 or\
    val.lower().find("dent") != -1:
        return "Health"
    elif val.lower().find("english") != -1 or val.lower().find("lang") != -1 or\
    val.lower().find("french") != -1 or val.lower().find("lingu") != -1 or\
    val.lower().find("spanish") != -1 or val.lower().find("italian") != -1 or\
    val.lower().find("german") != -1 or val.lower().find("liter") != -1 or\
    val.lower().find("japanese") != -1 or val.lower().find("mandarin") != -1:
        return "Languages"
    elif val.lower().find("polit") != -1 or val.lower().find("soci") != -1 or\
    val.lower().find("econ") != -1 or val.lower().find("philo") != -1 or\
    val.lower().find("psych") != -1 or val.lower().find("anthro") != -1:
        return "SocScience"
    elif val.lower().find("hist") != -1 or val.lower().find("film") != -1 or\
    val.lower().find("creative") != -1 or val.lower().find("art") != -1 or\
    val.lower().find("theatre") != -1 or val.lower().find("cultur") != -1:
        return "Arts"
    else:
        return "Other"



#Let's tidy the departments up with our function
oc['Department'] = oc['Department'].apply(tidy)
print(oc.Department.value_counts())
sfu['Department'] = sfu['Department'].apply(tidy)
print(sfu.Department.value_counts())
ubc['Department'] = ubc['Department'].apply(tidy)
print(ubc.Department.value_counts())

##the function seems to have worked well

###Great let's append all the dataframe together
oc = oc.drop('Campus', axis =1) #an extra column not needed
all = pd.DataFrame()
all = all.append(oc).append(sfu, ignore_index = True).append(ubc, ignore_index = True)
print(all.head(50))
all.sort_values('Name')


###Let's visualize distributions across department and universities
## with some formatting help from seaborn

set1 = all[['Grade', 'Uni', 'Department']].query('Department == "Sciences" or \
           Department =="Business" or Department =="Languages" or \
           Department == "Health" or Department == "Other" ')

set2 = all[['Grade', 'Uni', 'Department']].query('Department == "Arts" or \
           Department =="SocScience" or Department =="MathStats" or \
           Department == "CompSci" or Department == "Engineering"')


sns.set_palette('husl')
fig = plt.figure(figsize =(16,9))
ax1 = fig.add_subplot(111)
ax1.set_title("Professor Ratings By School-Department\nPart 2")
sns.catplot(x = 'Grade', y = 'Department', hue = 'Uni', legend = False, kind = 'box', data = set1, ax = ax1)
ax1.set_xlabel("Professor Ratings")
ax1.legend(loc = 1)

fig2 = plt.figure(figsize=(16,9))
ax2 = fig2.add_subplot(111)
ax2.set_title("Professor Ratings By School-Department\nPart 1")
sns.catplot(x = 'Grade', y = 'Department', hue = 'Uni', legend = False, kind = 'box', data = set2, ax = ax2)
ax2.legend(loc = 1)
ax2.set_xlabel("Professor Ratings")
plt.show()

## For each university/college, which departments had the highest avg ratings for professors?

##Let's group

uni_dept = all[['Grade', 'Uni', 'Department']].groupby(['Uni', 'Department'])
print(uni_dept.size())
print(uni_dept.mean())

all_grouped = uni_dept.mean().unstack(level =0)


oc_top5 = all_grouped.iloc[:,0].sort_values(ascending = False).head(5)
print(oc_top5)
sfu_top5 = all_grouped.iloc[:,1].sort_values(ascending = False).head(5)
print(sfu_top5)
ubc_top5 = all_grouped.iloc[:,2].sort_values(ascending = False).head(5)
print(sfu_top5)


#Using seaborn

sns.set_style('darkgrid')
plt.figure(figsize =(16,8))
ax1 = plt.subplot2grid((2,2), (0,0))
y = oc_top5.values
x = oc_top5.index
plt.bar(x,y,color = 'c', width = 0.5, label = 'OC')
plt.legend()
ax2 = plt.subplot2grid((2,2), (0,1))
y2 = sfu_top5.values
x2 = sfu_top5.index
plt.bar(x2,y2,color = 'm', width = 0.5,label = 'SFU')
plt.legend()
ax3 = plt.subplot2grid((2,4), (1,1), colspan =2)
y3 = ubc_top5.values
x3 = ubc_top5.index
plt.bar(x3,y3,color = 'r', width = 0.5, label = 'UBC')
plt.legend()
plt.subplots_adjust(wspace= 0.2, hspace = 0.4)
plt.show()
