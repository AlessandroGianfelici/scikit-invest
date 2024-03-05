import piecewise_regression
from sklearn.linear_model import TheilSenRegressor
from invest.plot import plot_candle, trendline, piecewise_regression_results
import numpy as np


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
    
    ts_model = TheilSenRegressor()
    ts_model.fit(x_linear, y_linear.ravel())
    
    current_trend = full_hist.loc[full_hist.index > best_b].copy()
    x_predict = (current_trend.index/data_norm).values.reshape(-1, 1)
    current_trend['predicted_trend'] = np.squeeze(ts_model.predict(x_predict))
    current_trend['predicted_trend'] = current_trend['predicted_trend'].apply(np.exp)*norm_price
    
    projection = np.exp(ts_model.predict([[(365+data_norm)/data_norm]]))
    actual = np.exp(ts_model.predict([[(data_norm)/data_norm]]))
    trend_magnitude = (projection - actual)/actual
    trend_duration = len(current_trend)
    if verbose:
        pw_fit.summary()
        piecewise_regression_results(pw_fit)
        plot_candle(current_trend, trendline).show()
    return trend_magnitude.item(), current_trend.tail(1)['predicted_trend'].item(), trend_duration