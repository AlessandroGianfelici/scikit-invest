import plotly.graph_objects as go
from toolz.functoolz import juxt
import pandas as pd

def plot_candle(price_data, indicators=[]):

    layout = go.Layout(
        yaxis=dict(title="Price"),
        yaxis2=dict(title="Volume", overlaying="y", side="right"),
    )

    technical_indicators = juxt(indicators)(price_data)

    prices_date = pd.to_datetime(price_data["Date"])

    fig = go.Figure(
        layout=layout,
        data=[
            go.Candlestick(
                x=prices_date,
                open=price_data["Open"],
                high=price_data["High"],
                low=price_data["Low"],
                close=price_data["Close"],
                yaxis="y1",
                name="Price",
            ),
            go.Bar(
                x=prices_date,
                y=price_data["Volume"],
                name="Volume",
                marker={"color": "blue"},
                yaxis="y2",
            ),
        ]
        + list(technical_indicators),
    )

    fig.update(layout_yaxis_range=[0, max(price_data["High"] * 1.1)])
    return fig

def piecewise_regression_results(pw_fit):
    # Plot the data, fit, breakpoints and confidence intervals
    pw_fit.plot_data(color="grey", s=20)
    # Pass in standard matplotlib keywords to control any of the plots
    pw_fit.plot_fit(color="red", linewidth=4)
    pw_fit.plot_breakpoints()
    pw_fit.plot_breakpoint_confidence_intervals()
    return pw_fit

def trendline(price_data):
    return go.Scatter(
        x=pd.to_datetime(price_data["Date"]),
        y=(price_data["predicted_trend"]),
        name="Predicted_trend",
        yaxis="y1",
        showlegend=True,
    )    

def BB_up(price_data, timeperiod =20):
    price_data['up_band'], price_data['mid_band'], price_data['low_band'] = talib.BBANDS(price_data['Close'], timeperiod =timeperiod)
    return go.Scatter(
        x=pd.to_datetime(price_data["Date"]),
        y=(price_data["up_band"]),
        name="Bollinger Band U",
        yaxis="y1",
        showlegend=True)

def BB_m(price_data, timeperiod =20):
    price_data['up_band'], price_data['mid_band'], price_data['low_band'] = talib.BBANDS(price_data['Close'], timeperiod =timeperiod)
    return go.Scatter(
        x=pd.to_datetime(price_data["Date"]),
        y=(price_data["mid_band"]),
        name="Bollinger Band M",
        yaxis="y1",
        showlegend=True)

def BB_low(price_data, timeperiod =20):
    price_data['up_band'], price_data['mid_band'], price_data['low_band'] = talib.BBANDS(price_data['Close'], timeperiod =timeperiod)
    return go.Scatter(
        x=pd.to_datetime(price_data["Date"]),
        y=(price_data["low_band"]),
        name="Bollinger Band L",
        yaxis="y1",
        showlegend=True)