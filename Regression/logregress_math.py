#Goal:  Perform a multinomial logistic regression on a grades data set#
#datset from kaggle, found here https://www.kaggle.com/janiobachmann/math-students

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from scipy.stats import normaltest
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics



data = pd.read_csv('kaggle_datasets/student-mat.csv')
data.info()
data.shape
#(395, 33)
#395 rows with 33 columns
data.isnull().sum()
#no null values

#We're interested in variable G3, is the final grade
data['G3'].describe()
np.median(data['G3'])

#The final grade it seems is out of 20
#Let's visualize:
y = data.G3
plt.title("Students Final Grades")
plt.ylabel("Number of Students")
plt.hist(y, 20, facecolor = 'b')
plt.show()

#what's the skew
data['G3'].skew()
#moderate -0.736

##does the sample come froma normal distribution?
#Let's check with D'Agostino's K^2 test
stat, p = normaltest(data['D3'])

##indicates p <.05, so not a normally distributed dataset,
###but what we really care about is if the residuals have normal distribution which is still
#possible even if our target variable is non-normal.

##Let's clean up some of the data columns, code the categorical variables

data = data.replace({"sex": {"F": 1, "M": 2},
              "Mjob": {"at_home" : 1, "health": 2, "services": 3, 'teacher' : 4, 'other': 5},
              "Fjob": {"at_home" : 1, "health": 2, "services": 3, 'teacher' : 4, 'other': 5},
              "address" : {"U" : 1, "R": 2},
              "reason" : {"course" : 1, "home" : 2, "reputation": 3, "other" : 4},
              "famsize" : {"LE3": 1, "GT3" : 2},
              "school" : {"GP": 1, "MS" : 2 },
              "internet" : {"yes": 1, "no": 2},
              "activities" : {"yes": 1, "no": 2},
              "nursery" : {"yes": 1, "no": 2},
              "higher" : {"yes": 1, "no": 2},
              "romantic" : {"yes": 1, "no": 2},
              "schoolsup": {"yes": 1, "no": 2},
              "famsup": {"yes": 1, "no": 2},
              "paid" : {"yes": 1, "no": 2},
              "Pstatus": {"A" : 1, "T" : 2},
              "guardian": {'mother': 1, 'father' : 2, 'other': 3}
              })

data.info()
#Looks like all the columns have converted from string to integer
#Great let's find the correlations with our target variable G3, especially those columns that show significance
#Unfortunately, pandas soesn't seem to have a function that returns correlations and p-values
#so this little for loop had to do the trick

corr_sig = []
for j in data.columns:
    val, p = pearsonr(data.G3, data.loc[:,j])
    if (p < 0.05):
            temp = [j, val, p]
            corr_sig.append(temp)


#now let's sort the corr_sig

def getkey(group):
    return group[1]

corr_sig.sort(key = getkey, reverse = True)


#Only 2 other variables seemd to have a greater than moderate correlation with G3 and that was G2, second exam grades
#and G1, first exam Grades

#let's visualize

plt.subplot(1,2,1)
plt.scatter(data.G1, data.G3, marker = 'o')
plt.title("First Exam Grades in Relation to Final Grades")
plt.ylabel("Final Grades")
plt.subplot(1,2,2)
plt.scatter(data.G2, data.G3, marker = 'X')
plt.title("Second Exam grades in Relation to Final Grades")
plt.ylabel("Final Grades")
plt.show()


### Let's drop the columns that show no significance with G3
sig_cols = []
for x in corr_sig:
    sig_cols.append(x[0])


def drop_cols():
    for c in data.columns:
        if c not in sig_cols:
            data.drop(columns = c, inplace =True)

drop_cols()

data.head()
##works well!

##Let's do a logistic regression
data['Final'] = data.G3

def collapse(val):
    if val <= 10:
        return 1
    elif val <=15:
        return 2
    else:
        return 3

data.Final = data.Final.apply(collapse)


y = data.Final
X = data.iloc[:, :-2]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LogisticRegression(solver='newton-cg', multi_class = 'ovr') 

#only newton cg seems to work, others did not converge
#need to do some feature scaling for G1 and G2 most likely.

model.fit(X_train, y_train)
pred_y = model.predict(X_test)
df = pd.DataFrame({'Predicted': pred_y, 'Actual': y_test})
model.score(X, y);



''''mse= metrics.mean_squared_error(y_test, pred_y)
mae= metrics.mean_absolute_error(y_test, pred_y)
rmse = np.sqrt(mse)
accuracy = metrics.r2_score(y_test, pred_y)
print("The MSE is", mse, "\nThe MAE is", mae, "\nThe RSME is", rmse, "\nThe accuracy is", accuracy)''''

#The accuracy is about 74% when I ran, which could be a lot better but performs well overall

