class RiskManager:
    def __init__(self, account_balance, risk_per_trade, max_daily_loss):
        self.account_balance = account_balance
        self.risk_per_trade = risk_per_trade  # Percentage of account balance
        self.max_daily_loss = max_daily_loss  # Maximum allowable loss per day
        self.daily_loss = 0  # Track daily loss

    def position_size(self, entry_price, stop_loss_price):
        risk_amount_per_trade = self.account_balance * (self.risk_per_trade / 100)
        position_size = risk_amount_per_trade / (entry_price - stop_loss_price)
        return position_size

    def calculate_stop_loss(self, entry_price, stop_loss_percentage):
        stop_loss_price = entry_price * (1 - stop_loss_percentage / 100)
        return stop_loss_price

    def calculate_take_profit(self, entry_price, risk_reward_ratio):
        take_profit_price = entry_price + (entry_price - self.calculate_stop_loss(entry_price, risk_reward_ratio * 100)) * risk_reward_ratio
        return take_profit_price

    def track_daily_loss(self, loss_amount):
        self.daily_loss += loss_amount
        if self.daily_loss > self.max_daily_loss:
            print("Daily loss limit exceeded!")
            self.reset_daily_loss()

    def reset_daily_loss(self):
        self.daily_loss = 0

# Example usage:
# risk_manager = RiskManager(account_balance=10000, risk_per_trade=1, max_daily_loss=500)
# position_size = risk_manager.position_size(entry_price=100, stop_loss_price=95)
# stop_loss = risk_manager.calculate_stop_loss(entry_price=100, stop_loss_percentage=5)
# take_profit = risk_manager.calculate_take_profit(entry_price=100, risk_reward_ratio=2)
# risk_manager.track_daily_loss(loss_amount=200)