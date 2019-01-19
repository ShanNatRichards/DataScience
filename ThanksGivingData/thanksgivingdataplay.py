#One of my first follow alongs. All credit to
#https://www.dataquest.io/blog/pandas-tutorial-python-2/
#original data set can be found at this link.
#most comments are my little head notes about what's going on for specific line

##One spot of difference from the original tutorial:
#I decided to run Chi2 test to test the null hypothesis
#that there was no significant difference among age_groups and whether or not they
#went shopping on blackfriday.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plot
from scipy.stats import chi2_contingency
import matplotlib.pyplot as plt
import math

tg_data = pd.read_csv('Datasets/thanksgiving-2015-poll-data.csv', encoding = 'Latin-1')
tg_data.columns
tg_data.columns[50:]
tg_data['Do you celebrate Thanksgiving?'].unique()
tg_data['What is your gender?'].unqiue()
tg_data['What is your gender?'].value_counts(dropna = False)
#Dataframes do not have value_count objects
#just series, so you must return a series in order to use value_counts


def gender_code(gender_string): #isnan has to be passed a num not a string
    if isinstance(gender_string, float) and math.isnan(gender_string):
        return gender_string
    return int(gender_string == "Female")

tg_data['gender'] = tg_data['What is your gender?'].apply(gender_code)
tg_data['gender'].value_counts(dropna = False)

#what if we want to check the datatype of each column?
tg_data.apply(lambda x: x.dtype)

###let's clean up the income column ####
tg_data['How much total combined money did all members of your HOUSEHOLD earn last year?']
def clean_income(value):
    if value == "Prefer not to answer":
        return 0;
    elif value == "$0 to $9,999":
        return 1;
    elif value == "$10,000 to $24,999":
        return 2;
    elif value == "$25,000 to $49,999":
        return 3;
    elif value == "$50,000 to $74,999":
        return 4;
    elif value == "$75,000 to $99,999":
        return 5;
    elif value == "$100,000 to $124,999":
        return 6;
    elif value == "$125,000 to $149,999":
        return 7;
    elif value == "$150,000 to $174,999":
        return 8;
    elif value == "$175,000 to $199,999":
        return 9;
    elif value == "$200,000 and up":
        return 10;
    elif math.isnan(value):
        return np.nan    #remember to indent your blocks

tg_data['income'] = tg_data['How much total combined money did all members of your HOUSEHOLD earn last year?'].apply(clean_income)
income_groups = tg_data[['gender', 'income']].groupby('income')
##must include groupby column in the index slice in order for groupby to work well

#to plot use series.plot.bar()
income_groups['income'].count().plot.bar()
plt.show()

## Are there differences between age groups and whether or not they shop on BlackFriday.
####black friday###
tg_data['Will you shop any Black Friday sales on Thanksgiving Day?'].unique()
##age - ordinal, blackfriday shopping - nominal, chi squared
age_shop = tg_data[['Age', 'Will you shop any Black Friday sales on Thanksgiving Day?']]
age_shop.head()

##transform age_shop, to get rid of n/a
age_shop = age_shop.dropna()
age_shop.isna()
#now rename label to just shop, please
age_shop = age_shop.rename(columns= { 'Will you shop any Black Friday sales on Thanksgiving Day?' : 'Shop'})
### make all column labels lowercase
age_shop = age_shop.rename(str.lower, axis = 1)
age_shop.groupby(['age','shop']).size()


##great now we can see age vs black friday shopping habits
##Let's visualize
plt.subplot(1,2,1)
age_shop.groupby(['age','shop']).size().unstack()['No'].plot.pie()
plt.subplot(1,2,2)
age_shop.groupby(['age','shop']).size().unstack()['Yes'].plot.pie()
plt.show()

####let's do the chi2chi2_contingency
chi2, p, dof, expected  = chi2_contingency(age_shop.groupby(['age','shop']).size().unstack())
## p value of 4.524473265477908e-08.
#There is a significant difference among age groups and whether or not they do blackfriday shopping.
print("The p-value of the chi2 test is:", p)
