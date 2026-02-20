import logging
import time
import signal
import sys
from datetime import datetime
from config import (
    TRADING_PAIR, TIMEFRAME, INITIAL_CAPITAL, MAX_POSITION_SIZE,
    CHECK_INTERVAL, RISK_PER_TRADE, EXCHANGE_ID, API_KEY, API_SECRET
)
from exchange_client import ExchangeClient
from data_handler import DataHandler
from strategies import StrategyManager
from risk_manager import RiskManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self):
        """Initialize the trading bot with all components."""
        logger.info("Initializing Trading Bot...")
        
        self.exchange = ExchangeClient(EXCHANGE_ID, API_KEY, API_SECRET)
        self.data_handler = DataHandler(self.exchange)
        self.strategy_manager = StrategyManager()
        self.risk_manager = RiskManager(INITIAL_CAPITAL, RISK_PER_TRADE)
        
        self.trading_pair = TRADING_PAIR
        self.timeframe = TIMEFRAME
        self.check_interval = CHECK_INTERVAL
        self.is_running = True
        self.trade_count = 0
        self.total_trades = 0
        self.wins = 0
        self.losses = 0
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        
        logger.info(f"Bot initialized. Trading pair: {self.trading_pair}, Timeframe: {self.timeframe}")
    
    def shutdown(self, signum, frame):
        """Graceful shutdown handler."""
        logger.info("Shutdown signal received. Closing positions...")
        self.is_running = False
        self.print_summary()
        sys.exit(0)
    
    def get_market_data(self):
        """Fetch current market data."""
        try:
            ohlcv = self.data_handler.get_ohlcv(self.trading_pair, self.timeframe, limit=100)
            if ohlcv is None or len(ohlcv) == 0:
                logger.warning("No OHLCV data available")
                return None
            return ohlcv
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return None
    
    def generate_signals(self, ohlcv):
        """Generate trading signals using strategy manager."""
        try:
            signal = self.strategy_manager.get_signal(ohlcv)
            return signal
        except Exception as e:
            logger.error(f"Error generating signals: {e}")
            return None
    
    def execute_trade(self, signal, current_price):
        """Execute a trade based on the signal."""
        try:
            if signal is None or current_price is None:
                return False
            
            balance = self.exchange.get_balance()
            if balance is None:
                logger.warning("Could not get balance")
                return False
            
            position_size = self.risk_manager.calculate_position_size(
                balance, current_price, signal.get('stop_loss', current_price * 0.95)
            )
            
            if position_size <= 0:
                logger.warning("Position size is invalid")
                return False
            
            if signal['action'] == 'BUY':
                order = self.exchange.place_limit_order(
                    self.trading_pair, 'buy', position_size, current_price
                )
                if order:
                    logger.info(f"BUY order placed: {position_size} @ {current_price}")
                    self.total_trades += 1
                    return True
            
            elif signal['action'] == 'SELL':
                order = self.exchange.place_limit_order(
                    self.trading_pair, 'sell', position_size, current_price
                )
                if order:
                    logger.info(f"SELL order placed: {position_size} @ {current_price}")
                    self.total_trades += 1
                    return True
        
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return False
    
    def check_open_orders(self):
        """Check and update open orders."""
        try:
            orders = self.exchange.get_open_orders(self.trading_pair)
            if orders:
                logger.info(f"Open orders: {len(orders)}")
                return orders
            return []
        except Exception as e:
            logger.error(f"Error checking open orders: {e}")
            return []
    
    def monitor_portfolio(self):
        """Monitor and log portfolio performance."""
        try:
            balance = self.exchange.get_balance()
            if balance:
                logger.info(f"Current balance: ${balance:.2f}")
                pnl = ((balance - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100
                logger.info(f"P&L: {pnl:.2f}%")
                return balance
            return None
        except Exception as e:
            logger.error(f"Error monitoring portfolio: {e}")
            return None
    
    def print_summary(self):
        """Print trading summary."""
        logger.info("=" * 50)
        logger.info("TRADING BOT SUMMARY")
        logger.info(f"Total Trades: {self.total_trades}")
        logger.info(f"Strategy: {self.strategy_manager.current_strategy}")
        logger.info(f"Trading Pair: {self.trading_pair}")
        logger.info("=" * 50)
    
    def run(self):
        """Main bot loop."""
        logger.info("Starting trading bot main loop...")
        
        while self.is_running:
            try:
                # Fetch market data
                ohlcv = self.get_market_data()
                if ohlcv is None:
                    time.sleep(self.check_interval)
                    continue
                
                current_price = ohlcv[-1][4]  # Close price
                
                # Generate trading signal
                signal = self.generate_signals(ohlcv)
                
                if signal and signal['action'] != 'HOLD':
                    logger.info(f"Signal generated: {signal['action']} at {current_price}")
                    self.execute_trade(signal, current_price)
                
                # Check open orders
                self.check_open_orders()
                
                # Monitor portfolio
                self.monitor_portfolio()
                
                # Sleep before next check
                time.sleep(self.check_interval)
            
            except KeyboardInterrupt:
                self.shutdown(None, None)
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                time.sleep(self.check_interval)

def main():
    """Main entry point."""
    bot = TradingBot()
    bot.run()

if __name__ == "__main__":
    main()