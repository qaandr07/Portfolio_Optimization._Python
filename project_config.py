from enum import Enum

NUM_PORTFOLIOS = 10000
TRADING_DAYS_PER_YEAR = 252

DEFAULT_START = "2010-01-01"
DEFAULT_END = "2026-04-02"
DEFAULT_INTERVAL = "1d"

RISK_FREE_RATE = 0.02
LEVERAGE_RATIO = 10.0
MAX_KELLY_LEVERAGE = 3.0
RISK_AVERSION = 5.0

DEFAULT_RISK_FREE_RATE = 0.0
DEFAULT_LEVERAGE_RATIO = 2.0
DEFAULT_RISK_AVERSION = 3.0
DEFAULT_KELLY_MAX_LEVERAGE = 3.0


class Ticker(Enum):
    # --- Индексы и ETF (Широкий рынок, облигации, сырье) ---
    SPXTR = "^SP500TR"  # S&P 500 Total Return
    SPY = "SPY"         # S&P 500 ETF
    QQQ = "QQQ"         # NASDAQ 100 ETF
    DIA = "DIA"         # Dow Jones ETF
    IWM = "IWM"         # Russell 2000 (Small Cap)
    VTI = "VTI"         # Vanguard Total Stock Market
    VEA = "VEA"         # Vanguard Developed Markets
    VWO = "VWO"         # Vanguard Emerging Markets
    TLT = "TLT"         # 20+ Year Treasury Bond
    IEF = "IEF"         # 7-10 Year Treasury Bond
    SHY = "SHY"         # 1-3 Year Treasury Bond
    GLD = "GLD"         # Gold Trust
    XAU = "GC=F"        # Gold Futures
    SLV = "SLV"         # Silver Trust
    USO = "USO"         # US Oil Fund

    # --- Криптовалюты ---
    BTC = "BTC-USD"
    ETH = "ETH-USD"
    BNB = "BNB-USD"
    SOL = "SOL-USD"
    XRP = "XRP-USD"
    ADA = "ADA-USD"
    DOGE = "DOGE-USD"
    AVAX = "AVAX-USD"
    LINK = "LINK-USD"
    MATIC = "MATIC-USD"

    # --- Технологии (Big Tech & Semiconductors) ---
    AAPL = "AAPL"
    MSFT = "MSFT"
    GOOGL = "GOOGL"
    AMZN = "AMZN"       # <-- Оставлен только здесь
    META = "META"
    NVDA = "NVDA"
    TSLA = "TSLA"
    NFLX = "NFLX"
    AMD = "AMD"
    INTC = "INTC"

    # --- Финансы ---
    JPM = "JPM"
    BAC = "BAC"         # Bank of America
    WFC = "WFC"         # Wells Fargo
    C = "C"             # Citigroup
    GS = "GS"           # Goldman Sachs
    V = "V"             # Visa
    MA = "MA"           # Mastercard

    # --- Здравоохранение и Фармацевтика ---
    JNJ = "JNJ"
    UNH = "UNH"         # UnitedHealth
    PFE = "PFE"         # Pfizer
    LLY = "LLY"         # Eli Lilly

    # --- Потребительский сектор и Ритейл ---
    PG = "PG"           # Procter & Gamble
    KO = "KO"           # Coca-Cola
    WMT = "WMT"         # Walmart
    MCD = "MCD"         # McDonald's
    DIS = "DIS"         # Disney

    # --- Энергетика и Промышленность ---
    XOM = "XOM"         # ExxonMobil
    CVX = "CVX"         # Chevron
    BA = "BA"           # Boeing
    CAT = "CAT"         # Caterpillar

    # ==========================================
    # --- РОССИЙСКИЙ РЫНОК (MOEX) ---
    # Внимание: yfinance имеет данные по РФ только до начала 2022 года.
    # ==========================================
    SBER = "SBER.ME"    # Сбербанк
    GAZP = "GAZP.ME"    # Газпром
    LKOH = "LKOH.ME"    # Лукойл
    YNDX = "YNDX.ME"    # Яндекс
    GMKN = "GMKN.ME"    # Норильский никель
    NVTK = "NVTK.ME"    # Новатэк
    ROSN = "ROSN.ME"    # Роснефть
    PLZL = "PLZL.ME"    # Полюс
    MGNT = "MGNT.ME"    # Магнит
    TATN = "TATN.ME"    # Татнефть
    SNGS = "SNGS.ME"    # Сургутнефтегаз
    CHMF = "CHMF.ME"    # Северсталь
    NLMK = "NLMK.ME"    # НЛМК
    ALRS = "ALRS.ME"    # Алроса
    MOEX = "MOEX.ME"    # Московская биржа
    MTSS = "MTSS.ME"    # МТС
    IRAO = "IRAO.ME"    # Интер РАО
    VTBR = "VTBR.ME"    # ВТБ
    PIKK = "PIKK.ME"    # ПИК
    PHOR = "PHOR.ME"    # Фосагро


ACTIVE_ASSETS = [
    Ticker.BTC,
    Ticker.GOOGL,
    Ticker.AAPL,
    Ticker.GLD
]