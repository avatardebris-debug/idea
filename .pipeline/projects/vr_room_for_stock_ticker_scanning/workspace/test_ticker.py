"""Test ticker and mock data source."""
import sys
sys.path.insert(0, '.')

from src.ticker import Ticker
from src.mock_data import MockDataSource

# Test Ticker
t = Ticker(symbol='AAPL', name='Apple Inc', price=150.0, open_price=148.0)
print(f'Ticker: {t}')
print(f'Is up: {t.is_up}')
print(f'Change: {t.change}')

# Test MockDataSource
ds = MockDataSource(update_interval=0.5, volatility=0.01)
ds.add_ticker('AAPL')
ds.add_ticker('GOOGL')
ds.add_ticker('MSFT')

print(f'\nInitial tickers: {len(ds.get_tickers())}')
print(f'Status: {ds.get_status()}')

# Start the data source
ds.start()

# Simulate updates using force_update (bypasses time throttling)
for i in range(3):
    updated = ds.force_update()
    print(f'\nTick {i+1}:')
    for ticker in updated:
        print(f'  {ticker.symbol}: ${ticker.price:.2f} ({ticker.change:+.2f}, {ticker.change_percent:+.2f}%)')

print(f'\nFinal status: {ds.get_status()}')
