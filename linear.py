import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression

def linear(df,x):
    df = df[['Close']]
    df = df.dropna() # Drop missing values
    df = df.reset_index(drop=True) # Reset the index

    # Split the data into training, testing, and validation sets
    train_size = int(0.7 * len(df))
    test_size = int(0.2 * len(df))
    val_size = len(df) - train_size - test_size

    train_data = df[:train_size]
    test_data = df[train_size:train_size+test_size]
    val_data = df[train_size+test_size:]

    # 3. Quá trình Training
    x_train = np.array(train_data.index).reshape(-1, 1)
    y_train = np.array(train_data['Close'])

    # Train the linear regression model
    model = LinearRegression()
    model.fit(x_train, y_train)

    # 4. Quá trình testing
    x_test = np.array(test_data.index).reshape(-1, 1)
    y_test = np.array(test_data['Close'])
    y_pred = model.predict(x_test)

    # 5. Quá trình Validate
    x_val= np.array(val_data.index).reshape(-1, 1)
    y_val = np.array(val_data['Close'])
    y_pred_val =  model.predict(x_val)

    # 6. Quá trình tạo index predict 30 ngày tiếp theo
    last_index =  df.index[-1]
    last_data = pd.RangeIndex(start=last_index, stop=last_index+x, step=1)

    # Create an array of 30 consecutive integers starting from last_index
    x_next_30_days = np.array(range(last_index+1, last_index+x+1)).reshape(-1, 1)

    # Predict the closing prices for the next 30 days
    y_next_30_days = model.predict(x_next_30_days)

    # Print the predicted closing prices for the next 30 days
    print('Predicted closing prices for the next 30 days:')
    print(y_next_30_days)

    # 7. Đánh giá độ chính xác validate, test
    #valid_rmse = np.sqrt(np.mean((y_pred_val - y_val)**2))
    #test_rmse = np.sqrt(np.mean((y_pred - y_test)**2))
    #print('Validation RMSE:', valid_rmse)
    #print('Testing RMSE:', test_rmse)

    # 9.Vẽ hình
    plt.plot(train_data.index, train_data['Close'])
    plt.plot(test_data.index, test_data['Close'])
    plt.plot(test_data.index, y_pred)
    plt.plot(val_data.index, y_pred_val)
    plt.plot(last_data,y_next_30_days)
    plt.legend(['Train', 'Test', 'Predictions','Validate','Next30Day'])
    plt.show()