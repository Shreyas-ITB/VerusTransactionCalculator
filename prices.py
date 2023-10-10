ONE_EPOCH_DAY = 86400

def get_price_for_time(prices, time):
    return prices.get(str(time - (time % ONE_EPOCH_DAY)))