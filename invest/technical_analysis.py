import piecewise_regression
from sklearn import linear_model, model_selection
from invest.plot import plot_candle, trendline, piecewise_regression_results
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

def compute_longterm_trend(mystock, train_size=0.8):
    data = mystock.hist.head(len(mystock.hist)-1)
    data = data.loc[pd.to_datetime(data.index).year>2002]
    first_trading_day = data.index.min()
    data['days_since_quot'] = (data.index - first_trading_day)/np.timedelta64(1, 'D')
    
    ransac = linear_model.RANSACRegressor()
    if train_size < 1:
        train_data, test_data = model_selection.train_test_split(data, 
                                                                 train_size = train_size,
                                                                 shuffle = False)
    else:
        train_data, test_data = data, data
    y_train = train_data['Adjclose'].apply(np.log).values
    X_train = train_data['days_since_quot'].values.reshape(-1, 1) 
    
    y_test = test_data['Adjclose'].apply(np.log).values
    X_test = test_data['days_since_quot'].values.reshape(-1, 1) 
    
    X = data['days_since_quot'].values.reshape(-1, 1) 
    
    ransac.fit(X_train, y_train)
    inlier_mask = ransac.inlier_mask_
    outlier_mask = np.logical_not(inlier_mask)
    
    # Compare estimated coefficients
    score = ransac.estimator_.score(X_train, y_train)
    print(f"Estimated RANSAC quality: {score}")
    roe = ransac.estimator_.coef_.item()*365
    print(f"Theorical ROE: {roe}")
    
    line_y_ransac = ransac.predict(X)
    data['TheoricalValue'] = np.exp(line_y_ransac)
    vol = ((data['Adjclose'] - data['TheoricalValue'])/data['TheoricalValue']).std()
    print(f"Theorical VOL: {vol}")
    
    plt.scatter(
        train_data.index[inlier_mask], np.exp(y_train[inlier_mask]), color="yellowgreen", marker=".", label="Inliers"
    )
    plt.scatter(
        train_data.index[outlier_mask], np.exp(y_train[outlier_mask]), color="gold", marker=".", label="Outliers"
    )
    
    if train_size < 1:
        plt.scatter(test_data.index, 
                    np.exp(y_test), 
                    color="red", 
                    marker=".", 
                    label="Prediction")
    
    plt.plot(
        data.index,
        np.exp(line_y_ransac),
        color="cornflowerblue",
        linewidth=2,
        label="RANSAC regressor",
    )
    plt.legend(loc="lower right")
    plt.xlabel("Input")
    plt.ylabel("Response")
    plt.show()
    return score, roe, vol, data

def detect_trend(full_hist, train_length = 120, verbose=True):
    data_norm = max(full_hist.reset_index()['index'])
    full_hist = full_hist.reset_index()
    norm_price = full_hist['Close'].tail(1).item()
    
    x = (full_hist['index'].tail(train_length)/data_norm).values
    y = (full_hist['Close'].tail(train_length)/norm_price).apply(np.log).values
    
    pw_fit = piecewise_regression.Fit(x, y, n_breakpoints=1)
    
    try:
        result = pw_fit.get_results()
        best_b = result['estimates']['breakpoint1']['estimate']*data_norm
    except Exception as e:
        print(e)
        best_b = full_hist['index'].tail(train_length).values[0]
        
    clean_trend = full_hist.loc[full_hist['index'] > int(best_b)]
    
    x_linear = (clean_trend.index/data_norm).values.reshape(-1, 1)
    y_linear = (clean_trend['Close']/norm_price).apply(np.log).values.reshape(-1, 1)
    
    ts_model = linear_model.TheilSenRegressor()
    ts_model.fit(x_linear, y_linear.ravel())
    
    current_trend = full_hist.loc[full_hist.index > best_b].copy()
    x_predict = (current_trend.index/data_norm).values.reshape(-1, 1)
    current_trend['predicted_trend'] = np.squeeze(ts_model.predict(x_predict))
    current_trend['predicted_trend'] = current_trend['predicted_trend'].apply(np.exp)*norm_price
    
    projection = np.exp(ts_model.predict([[(365+data_norm)/data_norm]]))
    actual = np.exp(ts_model.predict([[(data_norm)/data_norm]]))
    trend_magnitude = (projection - actual)/actual
    if verbose:
        pw_fit.summary()
        piecewise_regression_results(pw_fit)
        plot_candle(current_trend, trendline).show()
    return trend_magnitude.item(), pd.concat([full_hist.loc[full_hist.index <= best_b].copy(),
                                              current_trend])