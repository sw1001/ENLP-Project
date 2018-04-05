import pandas as pd
import sklearn
import xgboost as xgb
from sklearn.metrics import accuracy_score
from textblob import TextBlob
import time
import datetime


TRAIN_DATA_FILE = 'train_extract.tsv'


def load_train_data(path):
    D = pd.read_csv(path, sep='\t', header=0)

    D['Sentiment'] = D['Sentiment'].map(lambda x: 0 if x == 0 else x)
    D['Sentiment'] = D['Sentiment'].map(lambda x: 1 if x == 2 else x)
    D['Sentiment'] = D['Sentiment'].map(lambda x: 2 if x == 4 else x)

    X_train = D[['Phrase', 'Sentiment']]

    return X_train


current_time = time.time()

X_train = load_train_data('../data/' + TRAIN_DATA_FILE)

load_time = time.time() - current_time

print('Time to Load ' + TRAIN_DATA_FILE + ': ' + str(load_time) + 's')

# Feature Engineering
X_train['text_len'] = X_train['Phrase'].apply(len)
X_train['Phrase'] = X_train['Phrase'].apply(lambda x: str(x).strip())

X_train['text_blob'] = X_train['Phrase'].map(lambda x: TextBlob(x).sentiment)
X_train['polarity'] = X_train['text_blob'].map(lambda x: x[0])
X_train['subjectivity'] = X_train['text_blob'].map(lambda x: x[1])

cols = ['text_len', 'polarity', 'subjectivity']

current_time = time.time()
num_round = 2000
test_size = 0.2

params = {
    'eta': 0.002,
    'objective': 'multi:softmax',
    'num_class': 3,
    'max_depth': 6,
    'eval_metric': 'mlogloss',
    'seed': 2017,
    'silent': True
}

x1, x2, y1, y2 = sklearn.model_selection.train_test_split(X_train[cols], X_train['Sentiment'], test_size=test_size,
                                                          random_state=19960214)
dtrain = xgb.DMatrix(x1, label=y1)
dvalid = xgb.DMatrix(x2, label=y2)

watchlist = [(dvalid, 'valid'), (dtrain, 'train')]

model = xgb.train(params, dtrain, num_round, watchlist, verbose_eval=5, early_stopping_rounds=5)

y_pred = model.predict(dvalid)
predictions = [round(value) for value in y_pred]
accuracy = accuracy_score(y2, predictions)

print('XGBoost_model_eta_' +
      str(params['eta']) +
      '_round_' +
      str(num_round) +
      '_NumberFeatures_' +
      str(len(cols)) +
      '_TestSize_' +
      str(test_size) +
      '_timestamp_' +
      str(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")))

print("Accuracy: %.2f%%" % (accuracy * 100.0))

print('Time to Train and Test: ' + str(time.time() - current_time) + 's')
