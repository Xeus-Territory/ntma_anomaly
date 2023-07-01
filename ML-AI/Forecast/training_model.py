import pandas as pd
import numpy as np
import glob

# Model
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import *
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.losses import MeanSquaredError
from tensorflow.keras.metrics import RootMeanSquaredError
from tensorflow.keras.optimizers import Adam

folder_path_1 = './2023-06-20/'
folder_path_2 = './2023-06-21/'
folder_path_3 = './2023-06-22/'

folder_paths = [folder_path_1, folder_path_2, folder_path_3]

csv_files = []
dataframes = []

for folder_path in folder_paths:
    folder_csv_files = sorted(glob.glob(folder_path + '*.csv'))
    csv_files.extend(folder_csv_files)

    for file in folder_csv_files:
        df = pd.read_csv(file)
        dataframes.append(df)

df = pd.concat(dataframes, ignore_index=True)

df['time'] = pd.to_datetime(df['time'])

df1 = pd.DataFrame(df, columns=['time',
                                'service_avg_cpu_usage_percentage',
                                'service_avg_memory_usage_percentage', 
                                'nginx_avg_respone_time', 
                                'nginx_requests_per_second'
                                ])
df1.index=df1["time"]
df1.drop("time", axis=1, inplace=True)

df1['nginx_avg_respone_time'] = df1['nginx_avg_respone_time'].fillna(0)

# print(df1)
def df_to_X_y(df, window_size=7):
  df_as_np = df.to_numpy()
  X = []
  y = []
  for i in range(len(df_as_np)-window_size):
    row = [r for r in df_as_np[i:i+window_size]]
    X.append(row)
    label = [df_as_np[i+window_size][0], df_as_np[i+window_size][1], df_as_np[i+window_size][2], df_as_np[i+window_size][3]]
    y.append(label)
  return np.array(X), np.array(y)

window_size = 30
X, y = df_to_X_y(df1, window_size)

train_size = int(len(X)*0.7)
val_size = int(len(X)*0.15)
# test_size = len(X) - train_size - val_size

X_train, y_train = X[:train_size], y[:train_size]
X_val, y_val = X[train_size: (train_size + val_size)], y[train_size: (train_size + val_size)]
X_test, y_test = X[(train_size + val_size):], y[(train_size + val_size):]

# print(X_train.shape, y_train.shape, X_val.shape, y_val.shape, X_test.shape, y_test.shape)

cpu_training_mean = np.mean(X_train[:, :, 0])
cpu_training_std = np.std(X_train[:, :, 0])

ram_training_mean = np.mean(X_train[:, :, 1])
ram_training_std = np.std(X_train[:, :, 1])

nginx_avg_respone_time_training_mean = np.mean(X_train[:, :, 2])
nginx_avg_respone_time_training_std = np.std(X_train[:, :, 2])

nginx_requests_per_second_training_mean = np.mean(X_train[:, :, 3])
nginx_requests_per_second_training_std = np.std(X_train[:, :, 3])

def preprocess(X):
  X[:, :, 0] = (X[:, :, 0] - cpu_training_mean) / cpu_training_std
  X[:, :, 1] = (X[:, :, 1] - ram_training_mean) / ram_training_std
  X[:, :, 2] = (X[:, :, 2] - nginx_avg_respone_time_training_mean) / nginx_avg_respone_time_training_std
  X[:, :, 3] = (X[:, :, 3] - nginx_requests_per_second_training_mean) / nginx_requests_per_second_training_std

def preprocess_output(y):
  y[:, 0] = (y[:, 0] - cpu_training_mean) / cpu_training_std
  y[:, 1] = (y[:, 1] - ram_training_mean) / ram_training_std
  y[:, 2] = (y[:, 2] - nginx_avg_respone_time_training_mean) / nginx_avg_respone_time_training_std
  y[:, 3] = (y[:, 3] - nginx_requests_per_second_training_mean) / nginx_requests_per_second_training_std
  return y


preprocess(X_train)
preprocess(X_val)
preprocess(X_test)

preprocess_output(y_train)
preprocess_output(y_val)
preprocess_output(y_test)


# Training
model = Sequential()
model.add(LSTM(units=64, input_shape=(X_train.shape[1], X_train.shape[2]), return_sequences=True))
model.add(LSTM(units=64))
model.add(Dropout(0.2))
model.add(Dense(8, 'relu'))
model.add(Dense(y_train.shape[1], 'linear'))

model.summary()

save_model = "save_model.hdf5"

best_model = ModelCheckpoint(save_model, save_best_only=True)
model.compile(loss=MeanSquaredError(), optimizer=Adam(learning_rate=0.0001), metrics=[RootMeanSquaredError()])

model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=20, batch_size=72, callbacks=[best_model])