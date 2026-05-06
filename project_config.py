from enum import Enum

NUM_PORTFOLIOS = 100000
TRADING_DAYS_PER_YEAR = 252
DEFAULT_START = "2020-01-01"
DEFAULT_END = "2026-04-02"
DEFAULT_INTERVAL = "1d"


class Ticker(Enum):
    BTC = "BTC-USD"
    ETH = "ETH-USD"
    SPXTR = "^SP500TR"
    AAPL = "AAPL"
    XAU = "GC=F"
    MSFT = "MSFT"
    AMZN = "AMZN"
    GOOGL = "GOOGL"
    JPM = "JPM"
    XOM = "XOM"
    JNJ = "JNJ"
    PG = "PG"
    KO = "KO"
    DIS = "DIS"
    NVDA = "NVDA"
    SPY = "SPY"
    QQQ = "QQQ"
    GLD = "GLD"
    TLT = "TLT"
    IWM = "IWM"


ACTIVE_ASSETS = [
    Ticker.BTC,
    Ticker.ETH,
    Ticker.SPXTR,
    Ticker.AAPL,
    Ticker.XAU,
    Ticker.NVDA,
]
