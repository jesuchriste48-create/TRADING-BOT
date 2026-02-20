import logging
import numpy as np
from typing import Dict, List, Optional
from config import Config

logger = logging.getLogger(__name__)

class StrategyManager:
    """Manages multiple trading strategies"""
    
    def __init__(self, config: Config):
        self.config = config
        self.current_strategy = config.STRATEGY
    
    def get_signal(self, pair: str, ohlcv: List, indicators: Dict) -> Optional[str]:
        """Get trading signal from selected strategy"""
        try:
            if self.current_strategy == 'MACD':
                return self.macd_strategy(pair, ohlcv, indicators)
            elif self.current_strategy == 'RSI':
                return self.rsi_strategy(pair, ohlcv, indicators)
            elif self.current_strategy == 'BOLLINGER':
                return self.bollinger_strategy(pair, ohlcv, indicators)
            elif self.current_strategy == 'SUPPORT_RESISTANCE':
                return self.support_resistance_strategy(pair, ohlcv, indicators)
            else:
                logger.warning(f"Unknown strategy: {self.current_strategy}")
                return None
        except Exception as e:
            logger.error(f"Error getting signal for {pair}: {str(e)}", exc_info=True)
            return None
    
    def macd_strategy(self, pair: str, ohlcv: List, indicators: Dict) -> Optional[str]:
        """MACD (Moving Average Convergence Divergence) Strategy"""
        try:
            macd = indicators.get('macd')
            signal_line = indicators.get('signal_line')
            histogram = indicators.get('macd_histogram')
            
            if macd is None or signal_line is None or histogram is None:
                return None
            
            # Buy signal: MACD crosses above signal line
            if len(macd) >= 2 and len(signal_line) >= 2:
                if macd[-2] <= signal_line[-2] and macd[-1] > signal_line[-1]:
                    logger.info(f"MACD BUY signal for {pair}")
                    return 'BUY'
                
                # Sell signal: MACD crosses below signal line
                if macd[-2] >= signal_line[-2] and macd[-1] < signal_line[-1]:
                    logger.info(f"MACD SELL signal for {pair}")
                    return 'SELL'
            
            return None
        except Exception as e:
            logger.error(f"Error in MACD strategy: {str(e)}")
            return None
    
    def rsi_strategy(self, pair: str, ohlcv: List, indicators: Dict) -> Optional[str]:
        """RSI (Relative Strength Index) Strategy"""
        try:
            rsi = indicators.get('rsi')
            
            if rsi is None or len(rsi) < 2:
                return None
            
            current_rsi = rsi[-1]
            previous_rsi = rsi[-2]
            
            # Buy signal: RSI crosses above 30 (oversold)
            if previous_rsi <= 30 and current_rsi > 30:
                logger.info(f"RSI BUY signal for {pair} (RSI: {current_rsi:.2f})")
                return 'BUY'
            
            # Sell signal: RSI crosses below 70 (overbought)
            if previous_rsi >= 70 and current_rsi < 70:
                logger.info(f"RSI SELL signal for {pair} (RSI: {current_rsi:.2f})")
                return 'SELL'
            
            return None
        except Exception as e:
            logger.error(f"Error in RSI strategy: {str(e)}")
            return None
    
    def bollinger_strategy(self, pair: str, ohlcv: List, indicators: Dict) -> Optional[str]:
        """Bollinger Bands Strategy"""
        try:
            bb_upper = indicators.get('bb_upper')
            bb_lower = indicators.get('bb_lower')
            bb_middle = indicators.get('bb_middle')
            
            if bb_upper is None or bb_lower is None:
                return None
            
            current_price = ohlcv[-1][4]  # Close price
            
            # Buy signal: Price touches lower band
            if current_price <= bb_lower[-1]:
                logger.info(f"Bollinger BUY signal for {pair} (Price: {current_price}, Lower: {bb_lower[-1]:.2f})")
                return 'BUY'
            
            # Sell signal: Price touches upper band
            if current_price >= bb_upper[-1]:
                logger.info(f"Bollinger SELL signal for {pair} (Price: {current_price}, Upper: {bb_upper[-1]:.2f})")
                return 'SELL'
            
            return None
        except Exception as e:
            logger.error(f"Error in Bollinger strategy: {str(e)}")
            return None
    
    def support_resistance_strategy(self, pair: str, ohlcv: List, indicators: Dict) -> Optional[str]:
        """Support & Resistance Breakout Strategy"""
        try:
            if len(ohlcv) < 20:
                return None
            
            closes = np.array([candle[4] for candle in ohlcv[-20:]])
            
            # Calculate support and resistance
            support = np.min(closes)
            resistance = np.max(closes)
            midpoint = (support + resistance) / 2
            
            current_price = ohlcv[-1][4]
            previous_price = ohlcv[-2][4]
            
            # Buy signal: Price breaks above resistance
            if previous_price <= resistance and current_price > resistance:
                logger.info(f"S/R BUY signal for {pair} (Breakout: {current_price})")
                return 'BUY'
            
            # Sell signal: Price breaks below support
            if previous_price >= support and current_price < support:
                logger.info(f"S/R SELL signal for {pair} (Breakdown: {current_price})")
                return 'SELL'
            
            return None
        except Exception as e:
            logger.error(f"Error in S/R strategy: {str(e)}")
            return None
    
    def switch_strategy(self, new_strategy: str):
        """Switch to a different trading strategy"""
        if new_strategy in ['MACD', 'RSI', 'BOLLINGER', 'SUPPORT_RESISTANCE']:
            self.current_strategy = new_strategy
            logger.info(f"Switched to {new_strategy} strategy")
        else:
            logger.warning(f"Unknown strategy: {new_strategy}")