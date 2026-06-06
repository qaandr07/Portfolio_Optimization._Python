import datetime
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from backtest_analysis import backtest_strategies
from correlation_analysis import run_correlation_analysis
from data_loader import (
    build_daily_return_enum,
    download_open_prices,
    resolve_assets,
)
from efficient_frontier import build_efficient_frontier
from kelly_analysis import analyze_kelly
from leverage_analysis import analyze_leverage
from portfolio_simulation import simulate_random_portfolios
from portfolio_strategies import analyze_key_portfolios
from price_visualization import plot_asset_prices
from project_config import (
    ACTIVE_ASSETS,
    DEFAULT_END,
    DEFAULT_KELLY_MAX_LEVERAGE,
    DEFAULT_LEVERAGE_RATIO,
    DEFAULT_RISK_AVERSION,
    DEFAULT_RISK_FREE_RATE,
    DEFAULT_START,
    NUM_PORTFOLIOS,
    Ticker,
)
from risk_analysis import analyze_drawdowns
from utility_analysis import analyze_indifference_curve

# Настройка страницы (должна быть самой первой строчкой)
st.set_page_config(layout="wide", page_title="Portfolio Optimization Dashboard")

# База данных расшифровок для справочника
ASSET_DESCRIPTIONS = {
    # Индексы и ETF
    "SPXTR": "S&P 500 Total Return (Индекс полной доходности акций США)",
    "SPY": "SPDR S&P 500 ETF Trust (Биржевой фонд на индекс S&P 500)",
    "QQQ": "Invesco QQQ Trust (Биржевой фонд на технологический индекс NASDAQ 100)",
    "DIA": "SPDR Dow Jones Industrial Average ETF (Фонд на индекс Доу-Джонса)",
    "IWM": "iShares Russell 2000 ETF (Фонд на акции малых компаний США)",
    "VTI": "Vanguard Total Stock Market ETF (Фонд на весь рынок акций США широкого профиля)",
    "VEA": "Vanguard FTSE Developed Markets ETF (Акции развитых рынков без США)",
    "VWO": "Vanguard FTSE Emerging Markets ETF (Акции развивающихся рынков — Китай, Индия и др.)",
    "TLT": "iShares 20+ Year Treasury Bond ETF (Длинные государственные облигации США)",
    "IEF": "iShares 7-10 Year Treasury Bond ETF (Среднесрочные казначейские облигации США)",
    "SHY": "iShares 1-3 Year Treasury Bond ETF (Краткосрочные долговые обязательства США)",
    "GLD": "SPDR Gold Shares (Биржевой фонд со стопроцентным обеспечением физическим золотом)",
    "XAU": "Gold Futures (Фьючерсный контракт на золото)",
    "SLV": "iShares Silver Trust (ETF фонд на физическое серебро)",
    "USO": "United States Oil Fund (ETF на сырую нефть марки WTI)",
    # Криптовалюты
    "BTC": "Bitcoin / USD (Биткоин — главная криптовалюта)",
    "ETH": "Ethereum / USD (Эфириум — платформа смарт-контрактов)",
    "BNB": "BNB / USD (Внутренний коин экосистемы криптобиржи Binance)",
    "SOL": "Solana / USD (Высокоскоростной блокчейн со смарт-контрактами)",
    "XRP": "XRP / USD (Криптовалюта платежного протокола Ripple)",
    "ADA": "Cardano / USD (Децентрализованная блокчейн-платформа Кардано)",
    "DOGE": "Dogecoin / USD (Мем-токен на собственном блокчейне)",
    "AVAX": "Avalanche / USD (Платформа для запуска децентрализованных финансов)",
    "LINK": "Chainlink / USD (Децентрализованная сеть оракулов)",
    "MATIC": "Polygon / USD (Сеть масштабирования второго уровня для Ethereum)",
    # Технологии
    "AAPL": "Apple Inc. (Производитель электроники, смартфонов и ПО)",
    "MSFT": "Microsoft Corporation (Разработчик софта, облачных систем и экосистемы Windows)",
    "GOOGL": "Alphabet Inc. / Google (Поисковая система, реклама, YouTube, Android)",
    "AMZN": "Amazon.com, Inc. (Крупнейшая e-commerce платформа и облачный провайдер AWS)",
    "META": "Meta Platforms (Социальные сети Facebook, Instagram, WhatsApp)",
    "NVDA": "NVIDIA Corporation (Лидер в сфере графических процессоров и чипов для ИИ)",
    "TSLA": "Tesla, Inc. (Производитель электромобилей и систем хранения энергии)",
    "NFLX": "Netflix, Inc. (Стриминговый развлекательный сервис фильмов и сериалов)",
    "AMD": "Advanced Micro Devices (Производитель микропроцезоров и видеокарт)",
    "INTC": "Intel Corporation (Крупнейший разработчик полупроводников и процессоров)",
    # Финансы
    "JPM": "JPMorgan Chase & Co. (Крупнейший инвестиционный и коммерческий банк США)",
    "BAC": "Bank of America (Один из ведущих финансовых конгломератов США)",
    "WFC": "Wells Fargo & Company (Крупный американский банк, лидер по ипотечным кредитам)",
    "C": "Citigroup Inc. (Международный финансовый и банковский холдинг)",
    "GS": "Goldman Sachs Group (Ведущий мировой инвестиционный банк)",
    "V": "Visa Inc. (Глобальная платежная технологическая система)",
    "MA": "Mastercard Incorporated (Международная межбанковская платежная система)",
    # Здравоохранение
    "JNJ": "Johnson & Johnson (Производитель медицинских изделий и лекарственных средств)",
    "UNH": "UnitedHealth Group (Крупнейшая компания США в сфере medical страхования)",
    "PFE": "Pfizer Inc. (Глобальная фармацевтическая корпорация)",
    "LLY": "Eli Lilly and Company (Международная фармацевтическая компания)",
    # Потребительский сектор
    "PG": "Procter & Gamble (Товары бытовой химии, личной гигиены и косметики)",
    "KO": "The Coca-Cola Company (Мировой производитель безалкогольных напитков)",
    "WMT": "Walmart Inc. (Крупнейшая в мире сеть оптовой и розничной торговли)",
    "MCD": "McDonald's Corporation (Глобальная сеть ресторанов быстрого питания)",
    "DIS": "The Walt Disney Company (Медиаконгломерат развлечений, киностудии и парки)",
    # Энергетика
    "XOM": "Exxon Mobil Corporation (Нефтегазовая супермейджор корпорация)",
    "CVX": "Chevron Corporation (Интегрированная энергетическая и нефтехимическая компания)",
    "BA": "The Boeing Company (Авиастроительная и аэрокосмическая корпорация)",
    "CAT": "Caterpillar Inc. (Производитель строительной и горнодобывающей техники)",
    # Российский рынок (MOEX)
    "SBER": "Сбербанк (Крупнейший банк России и экосистема)",
    "GAZP": "Газпром (Энергетическая компания, экспорт природного газа)",
    "LKOH": "ЛУКОЙЛ (Одна из крупнейших нефтегазовых компаний РФ)",
    "YNDX": "Яндекс (Технологический лидер: поиск, такси, маркетплейсы, еда)",
    "GMKN": "Норильский никель (Мировой лидер по производству никеля и палладия)",
    "NVTK": "НОВАТЭК (Крупнейший независимый производитель природного газа в РФ)",
    "ROSN": "Роснефть (Лидер российской нефтяной отрасли)",
    "PLZL": "Полюс (Крупнейший производитель золота в России)",
    "MGNT": "Магнит (Одна из ведущих розничных сетей по торговле продуктами)",
    "TATN": "Татнефть (Нефтяная компания Татарстана)",
    "SNGS": "Сургутнефтегаз (Нефтегазовая компания с крупными ликвидными резервами)",
    "CHMF": "Северсталь (Горно-металлургическая компания, сталелитейное производство)",
    "NLMK": "НЛМК (Новолипецкий металлургический комбинат)",
    "ALRS": "АЛРОСА (Мировой лидер по объемду добычи алмазов)",
    "MOEX": "Московская Биржа (Организатор торгов акциями, валютой и деривативами)",
    "MTSS": "МТС (Телекоммуникационный оператор и экосистема цифровых сервисов)",
    "IRAO": "Интер РАО (Энергетический холдинг, управление электростанциями)",
    "VTBR": "ВТБ (Второй по величине коммерческий банк РФ)",
    "PIKK": "Группа ПИК (Крупнейшая девелоперская и строительная компания жилья)",
    "PHOR": "Фосагро (Мировой лидер в производстве фосфоросодержащих удобрений)",
}


@st.cache_data
def get_cached_data(asset_names, start_date, end_date, **kwargs):
    resolved = resolve_assets(*asset_names)
    return download_open_prices(
        *resolved, start=start_date, end=end_date, **kwargs
    )


DailyReturnArray = None
CorrelationMatrix = None


def main(
    active_assets=None,
    risk_free_rate=DEFAULT_RISK_FREE_RATE,
    leverage_ratio=DEFAULT_LEVERAGE_RATIO,
    risk_aversion=DEFAULT_RISK_AVERSION,
    kelly_max_leverage=DEFAULT_KELLY_MAX_LEVERAGE,
    show_plots=True,
    **download_kwargs,
):
    global DailyReturnArray
    global CorrelationMatrix

    st.title("📊 Панель оптимизации инвестиционного портфеля")

    # ==============================================================================
    # БОКОВАЯ ПАНЕЛЬ НАСТРОЕК
    # ==============================================================================
    st.sidebar.header("⚙️ Панель управления")

    all_ticker_names = [t.name for t in Ticker]
    default_ticker_names = [t.name for t in (active_assets or ACTIVE_ASSETS)]
    selected_asset_names = st.sidebar.multiselect(
        "Выбор активов:",
        options=all_ticker_names,
        default=default_ticker_names,
    )

    st.sidebar.markdown("---")

    st.sidebar.subheader("📅 Временной период")
    init_start = datetime.datetime.strptime(DEFAULT_START, "%Y-%m-%d").date()
    init_end = datetime.datetime.strptime(DEFAULT_END, "%Y-%m-%d").date()

    start_date = st.sidebar.date_input("Дата начала (Start Date):", init_start)
    end_date = st.sidebar.date_input("Дата окончания (End Date):", init_end)

    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    st.sidebar.markdown("---")

    # ВАЛИДАЦИЯ ДАТ И РОССИЙСКИХ АКТИВОВ
    if start_date >= end_date:
        st.error("❌ Ошибка: Дата начала не может быть больше или равна дате окончания.")
        st.stop()

    # Список всех российских тикеров для проверки
    russian_tickers = {
        "SBER", "GAZP", "LKOH", "YNDX", "GMKN", "NVTK", "ROSN", "PLZL", 
        "MGNT", "TATN", "SNGS", "CHMF", "NLMK", "ALRS", "MOEX", "MTSS", 
        "IRAO", "VTBR", "PIKK", "PHOR"
    }
    
    # Проверяем, выбрал ли пользователь хотя бы один актив из РФ
    has_russian_assets = any(asset in russian_tickers for asset in selected_asset_names)
    
    # Если выбраны активы РФ и дата окончания выходит за пределы марта 2022 года
    if has_russian_assets and end_date > datetime.date(2022, 3, 1):
        st.sidebar.warning(
            "⚠️ **Внимание!** Вы выбрали акции РФ и дату позже марта 2022 года. "
            "Yahoo Finance прекратил поддержку котировок MOEX с весны 2022 г. "
            "Загрузка может завершиться ошибкой. Измените End Date на дату до 2022-03-01."
        )

    st.sidebar.subheader("💰 Параметры риска и плеча")
    risk_free_rate = st.sidebar.number_input(
        "Безрисковая ставка (Rf):",
        min_value=0.0,
        max_value=0.5,
        value=float(risk_free_rate),
        step=0.01,
    )
    leverage_ratio = st.sidebar.number_input(
        "Фиксированное плечо (Leverage):",
        min_value=1.0,
        max_value=10.0,
        value=float(leverage_ratio),
        step=0.5,
    )
    kelly_max_leverage = st.sidebar.slider(
        "Макс. плечо для Келли (Max Kelly Cap):",
        min_value=1.0,
        max_value=5.0,
        value=float(kelly_max_leverage),
        step=0.1,
    )

    st.sidebar.markdown("---")

    st.sidebar.subheader("🔬 Параметры симуляции")
    risk_aversion = st.sidebar.slider(
        "Неприятие риска инвестора (A):",
        min_value=0.5,
        max_value=10.0,
        value=float(risk_aversion),
        step=0.5,
    )
    num_portfolios_input = st.sidebar.number_input(
        "Кол-во портфелей Монте-Карло:",
        min_value=1000,
        max_value=50000,
        value=int(NUM_PORTFOLIOS),
        step=1000,
    )

    if len(selected_asset_names) < 2:
        st.warning(
            "⚠️ Пожалуйста, выберите как минимум **2 актива** в боковой панели, чтобы запустить расчеты."
        )
        st.stop()

    chosen_tickers = [Ticker[name] for name in selected_asset_names]

    # ==============================================================================
    # ЗАГРУЗКА ДАННЫХ (КЭШИРУЕМАЯ)
    # ==============================================================================
    with st.spinner("Загрузка исторических данных из Yahoo Finance..."):
        try:
            raw_data, open_prices, daily_returns = get_cached_data(
                selected_asset_names,
                start_date=start_str,
                end_date=end_str,
                **download_kwargs,
            )
        except Exception as e:
            st.error(
                f"❌ Не удалось загрузить данные за выбранный период. "
                f"Если вы выбрали активы РФ, убедитесь, что дата окончания установлена не позднее 2022-03-01. Ошибка: {e}"
            )
            st.stop()

    DailyReturnArray = build_daily_return_enum(daily_returns, *chosen_tickers)
    print("#part 1: Loaded open prices and calculated daily returns.")

    # ==============================================================================
    # ВКЛАДКИ С ГРАФИКАМИ И СПРАВОЧНИКОМ
    # ==============================================================================
    tab_titles = [
        "📋 Обзор конфигурации",
        "🔍 Справочник активов",
        "📈 Цены активов",
        "🧮 Корреляции",
        "🎲 Монте-Карло",
        "🎯 Efficient Frontier",
        "🔑 Ключевые портфели",
        "🔄 Бэктест стратегий",
        "⚖️ Кредитное плечо",
        "📉 Кривые безразличия",
        "🦅 Критерий Келли",
        "⚠️ Анализ просадок",
    ]
    tabs = st.tabs(tab_titles)

    # Вкладка 0: Информационный обзор
    with tabs[0]:
        st.subheader("Текущие параметры анализа")
        st.info(
            f"**Выбранные активы:** {', '.join(selected_asset_names)}  \n"
            f"**Временной интервал:** c `{start_str}` по `{end_str}`  \n"
            f"**Безрисковая ставка:** `{risk_free_rate * 100:.1f}%` | "
            f"**Целевое плечо:** `{leverage_ratio}x` | "
            f"**Ограничение плеча Келли:** `{kelly_max_leverage}x` | "
            f"**Неприятие риска (A):** `{risk_aversion}`"
        )
        st.write(
            "Используйте горизонтальные вкладки выше для переключения между результатами расчетов и графиками."
        )

    # Вкладка 1: Справочник активов
    with tabs[1]:
        st.header("🔍 Интерактивный справочник доступных тикеров")
        st.markdown(
            " Вы можете искать активы по любой части слова, воспользовавшись **кнопкой поиска в верхнем правом углу таблицы**."
        )

        ref_rows = []
        for t in Ticker:
            full_descr = ASSET_DESCRIPTIONS.get(t.name, "Описание отсутствует")
            ref_rows.append(
                {
                    "Аббревиатура (Тикер)": t.name,
                    "Код в Yahoo Finance": t.value,
                    "Полное название / Описание актива": full_descr,
                }
            )

        df_ref = pd.DataFrame(ref_rows)
        st.dataframe(df_ref, use_container_width=True, hide_index=True)

    # Вкладка 2: Цены активов
    with tabs[2]:
        st.header("История цен открытия активов")
        plot_asset_prices(
            open_prices,
            *chosen_tickers,
            max_plots_per_figure=len(chosen_tickers),
        )
        if show_plots:
            st.pyplot(plt.gcf())
            plt.close()

    # Вкладка 3: Таблица корреляций
    with tabs[3]:
        st.header("Корреляционный анализ")
        correlation_table, CorrelationMatrix = run_correlation_analysis(
            daily_returns,
            *chosen_tickers,
            show_plot=show_plots,
        )
        if show_plots:
            st.pyplot(plt.gcf())
            plt.close()

    # Вкладка 4: Симуляция Монте-Карло
    with tabs[4]:
        st.header("Случайная генерация множества портфелей")
        simulation = simulate_random_portfolios(
            daily_returns,
            *chosen_tickers,
            num_portfolios=num_portfolios_input,
            risk_free_rate=risk_free_rate,
            show_plot=show_plots,
        )
        if show_plots:
            st.pyplot(plt.gcf())
            plt.close()

    # Вкладка 5: Эффективная граница
    with tabs[5]:
        st.header("Построение эффективной границы (Efficient Frontier)")
        frontier = build_efficient_frontier(
            simulation,
            show_plot=show_plots,
        )
        if show_plots:
            st.pyplot(plt.gcf())
            plt.close()

    # Вкладка 6: Ключевые портфели
    with tabs[6]:
        st.header("Оптимальные точки: Tangency, Min Variance и Max Sortino")
        key_portfolios = analyze_key_portfolios(
            simulation,
            frontier,
            show_plot=show_plots,
        )
        if show_plots:
            st.pyplot(plt.gcf())
            plt.close()

    # Вкладка 7: Бэктест
    with tabs[7]:
        st.header("Исторический бэктест выбранных стратегий")
        backtest = backtest_strategies(
            simulation,
            key_portfolios,
            show_plot=show_plots,
        )
        if show_plots:
            st.pyplot(plt.gcf())
            plt.close()

    # Вкладка 8: Кредитное плечо
    with tabs[8]:
        st.header("Применение кредитного плеча к касательному портфелю")
        leverage = analyze_leverage(
            simulation,
            key_portfolios,
            leverage_ratio=leverage_ratio,
            risk_free_rate=risk_free_rate,
            show_plot=show_plots,
        )
        if show_plots:
            st.pyplot(plt.gcf())
            plt.close()

    # Вкладка 9: Кривая безразличия
    with tabs[9]:
        st.header("Функция полезности и оптимальный выбор инвестора")
        utility = analyze_indifference_curve(
            simulation,
            frontier,
            risk_aversion=risk_aversion,
            show_plot=show_plots,
        )
        if show_plots:
            st.pyplot(plt.gcf())
            plt.close()

    # Вкладка 10: Критерий Келли
    with tabs[10]:
        st.header("Расчет оптимального плеча по критерию Келли")
        kelly = analyze_kelly(
            simulation,
            key_portfolios,
            risk_free_rate=risk_free_rate,
            fixed_leverage_ratio=leverage_ratio,
            max_leverage=kelly_max_leverage,
            show_plot=show_plots,
        )
        if show_plots:
            st.pyplot(plt.gcf())
            plt.close()

    # Вкладка 11: Максимальная просадка
    with tabs[11]:
        st.header("Анализ максимальных просадок (Max Drawdown)")
        drawdowns = analyze_drawdowns(
            backtest,
            risk_free_rate=risk_free_rate,
            extra_strategy_returns={
                f"{leverage_ratio}x Tangency": leverage["daily_returns"],
                "Kelly Tangency": kelly["daily_returns"],
            },
            show_plot=show_plots,
        )
        if show_plots:
            st.pyplot(plt.gcf())
            plt.close()

    return {
        "raw_data": raw_data,
        "open_prices": open_prices,
        "daily_returns": daily_returns,
        "correlation_table": correlation_table,
        "simulation": simulation,
        "frontier": frontier,
        "key_portfolios": key_portfolios,
        "backtest": backtest,
        "leverage": leverage,
        "utility": utility,
        "kelly": kelly,
        "drawdowns": drawdowns,
        "DailyReturnArray": DailyReturnArray,
        "CorrelationMatrix": CorrelationMatrix,
    }


if __name__ == "__main__":
    RESULTS = main()