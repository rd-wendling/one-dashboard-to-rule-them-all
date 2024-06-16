#%%
import finnhub

api_key = 'cpn3fc9r01qtggbacpegcpn3fc9r01qtggbacpf0'
finnhub_client = finnhub.Client(api_key=api_key)
symbols = finnhub_client.stock_symbols('US')


# Fetch historical data for DOW Index (example)
dow_data = finnhub_client.stock_candles(symbol='DJI', resolution='D', _from='2024-01-01', to='2024-06-15')

dow_data
# %%
