#All credit to ShaneLynn.com for the datasets
# They have been cloned to the
# Goal: Clean up the datasets, do any necessary joins or merges, look at descriptive stats, then run a a one-way ANOVA 


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.formula.api import ols
import statsmodels.api as sm



users = pd.read_csv('Datasets/user_usage.csv')
device = pd.read_csv('Datasets/user_device.csv')
##andro = pd.read_csv('Datasets/android_devices.csv')

users['use_id'].isin(device.use_id).value_counts()
#check if values in users use_id column are present in device use_id column

device['use_id'].isin(users['use_id']).value_counts()
#what about the other way around?

#Merge users and devices
user_device = pd.merge(users,device [['use_id', 'platform', 'device']],
on = 'use_id', how = 'left') #merge of the left dataset, right dataset responsible for providing null columns
user_device.head()


###
user_device['device'].value_counts()
#So we have potential groups here but Device Types are labelled too specifically
#let's see if we can't use apply and functions to clean it up


#custom function for cleaning up  NANs and replace with Uknown for categorical data
def clean(value) :
    if isinstance(value, float) and value is np.nan :
        return "Unknown"
    else:
        return value

#function for reducing the granularity of Devices, collapsing accoring to brands.

def collapse(value):
    if (value.lower().startswith("moto")):
        return "Motorola"
    elif (value.lower().startswith("iphone")):
        return "Apple"
    elif (value.lower(). startswith("one")):
        return "OnePlus"
    elif (value.lower(). startswith("htc")):
        return "HTC"
    elif (value.lower(). startswith("hua") or value.lower(). startswith("eva") ):
            return "Huawei"
    elif (value.lower(). startswith("lg") or value.lower(). startswith("nexus") ):
            return "LG"
    elif (value.lower(). startswith("lenovo")):
        return "Lenovo"
    elif (value.lower(). startswith("vf") or value.lower(). startswith("voda")):
        return "Vodafone"
    elif (value.lower().startswith("gt") or value.lower().startswith("sm")):
        return "Samsung"
    elif (value[1:].isdigit()):
        return "Sony"
    else :
        return value

user_device['device'] = user_device['device'].apply(clean)

#Let's check if we've removed all the NANs
user_device['device'].value_counts(dropna = False)
#Yes we have

#Now let's clean up the devices, organizing them by Brands
user_device['device'] = user_device['device'].apply(collapse)
user_device.device.value_counts(dropna = False)


####ANOVA:
##H0: There is no a significant difference between devices and outgoing minutes
##Let's get a descriptive summary of the target column 'out-going minutes', but first let's make life easier and rename wordy columns

user_device.rename(columns = {'outgoing_mins_per_month': 'out_min', 'outgoing_sms_per_month' : 'out_sms' }, inplace = True )

np.mean(user_device['out_min'])
np.median(user_device['out_min'])
np.std(user_device['out_min'])

##There might be some outliers given the difference between median and mean
##let's visualize
y = user_device['out_min']
x = user_device.use_id
y_std = np.std(y)
outliers = user_device[np.abs(user_device['out_min'] -user_device['out_min'].mean()) > 3 * np.std(user_device['out_min']) ]
plt.title("Outgoing Minutes - Showing Outliers")
plt.ylabel("Outgoing minutes")
plt.xlabel("User ID")
plt.scatter(x, y, c = 'c', marker = 'X')
plt.scatter(outliers.use_id, outliers['out_min'], c = 'r', marker = 'X', s = 75)
plt.show()

### The outlier are those users with outgoing minutes above 1200. Let's drop them.
user_device = user_device[user_device.out_min <1200]

user_device[['out_min', 'device']].groupby('device').size()

#some of these groups are quite small so the residuals may not meet ANOVA assumptions
#which may have an affect on robustness of the ANOVA test
#So let's run ANOVA on larger group of known brands, those with counts closer to 20

model = ols('out_min ~ C(device)', user_device).fit()
table = sm.stats.anova_lm(model, typ=2)
print(table)
#So there seems to be a statistically significant difference between the device/brands. However,
#caveat is that some residuals are small, so it may affect robustness of test.
