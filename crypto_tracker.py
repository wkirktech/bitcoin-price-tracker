import requests
import time
import json
from datetime import datetime
import os

class CryptoPriceTracker:
    def __init__(self, api_url="https://api.coingecko.com/api/v3"):
        self.api_url = api_url
        self.headers = {
            'Accept': 'application/json',
            'User-Agent': 'CryptoPriceTracker/1.0'
        }
        self.price_history = []
        self.history_file = "bitcoin_price_history.json"
        self.load_history()

    def load_history(self):
        """Load price history from file if it exists"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    self.price_history = json.load(f)
                print(f"Loaded {len(self.price_history)} historical price points")
            except Exception as e:
                print(f"Error loading history: {e}")

    def save_history(self):
        """Save price history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.price_history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")

    def fetch_price(self, coin_id="bitcoin", vs_currency="usd"):
        """Fetch current price of a cryptocurrency"""
        endpoint = f"/simple/price"
        params = {
            "ids": coin_id,
            "vs_currencies": vs_currency,
            "include_market_cap": "true",
            "include_24hr_change": "true"
        }
        
        url = f"{self.api_url}{endpoint}"
        
        try:
            print(f"Fetching data from {url}...")
            response = requests.get(url, params=params, headers=self.headers)
            
            # Check if we got rate limited
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                print(f"Rate limited. Waiting for {retry_after} seconds...")
                time.sleep(retry_after)
                return self.fetch_price(coin_id, vs_currency)
                
            # Check for other errors
            response.raise_for_status()
            
            data = response.json()
            
            if coin_id in data:
                timestamp = datetime.now().isoformat()
                price_data = {
                    "timestamp": timestamp,
                    "price_usd": data[coin_id][vs_currency],
                    "market_cap": data[coin_id].get(f"{vs_currency}_market_cap"),
                    "24h_change": data[coin_id].get(f"{vs_currency}_24h_change")
                }
                
                # Store in history
                self.price_history.append(price_data)
                self.save_history()
                
                # Format output
                print("\n" + "="*50)
                print(f"Bitcoin Price ({timestamp})")
                print("="*50)
                print(f"Price: ${price_data['price_usd']:,.2f} USD")
                
                if price_data['market_cap']:
                    print(f"Market Cap: ${price_data['market_cap']:,.2f} USD")
                    
                if price_data['24h_change']:
                    change = price_data['24h_change']
                    change_symbol = "📈" if change > 0 else "📉"
                    print(f"24h Change: {change:+.2f}% {change_symbol}")
                
                print("="*50 + "\n")
                
                return price_data
            
            else:
                print(f"Error: Data for {coin_id} not found in response")
                print(f"Response: {data}")
                return None
        
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def track_price_changes(self, interval=300, duration=3600):
        """Track price changes over time
        
        Args:
            interval: Time between checks in seconds (default: 5 minutes)
            duration: Total tracking duration in seconds (default: 1 hour)
        """
        num_checks = duration // interval
        print(f"Tracking Bitcoin price every {interval} seconds for {duration//60} minutes ({num_checks} checks)")
        
        for i in range(num_checks):
            print(f"\nCheck {i+1}/{num_checks}")
            self.fetch_price()
            
            if i < num_checks - 1:  # Don't sleep after the last check
                print(f"Waiting {interval} seconds until next check...")
                time.sleep(interval)
        
        print(f"\nPrice tracking complete. Recorded {len(self.price_history)} data points.")
        
        # Show simple stats
        if len(self.price_history) > 1:
            prices = [entry["price_usd"] for entry in self.price_history]
            min_price = min(prices)
            max_price = max(prices)
            avg_price = sum(prices) / len(prices)
            
            print("\nSummary Statistics:")
            print(f"Min Price: ${min_price:,.2f}")
            print(f"Max Price: ${max_price:,.2f}")
            print(f"Avg Price: ${avg_price:,.2f}")
            print(f"Price Range: ${max_price - min_price:,.2f}")

if __name__ == "__main__":
    tracker = CryptoPriceTracker()
    
    # Fetch current price
    tracker.fetch_price()
    
    # Uncomment to track price changes 
    # tracker.track_price_changes(interval=60, duration=300)  # Check every minute for 5 minutes