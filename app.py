import streamlit as st
import requests
from datetime import datetime, timezone
from streamlit_autorefresh import st_autorefresh

# --------------------------------------------------
# Page setup
# --------------------------------------------------

st.set_page_config(
    page_title="Market Monitor",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Market Monitor")
st.caption("Finnhub market data • Auto-refreshes every 15 seconds")

# Refresh every 15 seconds
st_autorefresh(interval=15_000, key="market_refresh")

# --------------------------------------------------
# Finnhub setup
# --------------------------------------------------

FINNHUB_API_KEY = st.secrets["FINNHUB_API_KEY"]

QUOTE_URL = "https://finnhub.io/api/v1/quote"

HEADERS = {
    "X-Finnhub-Token": FINNHUB_API_KEY
}


def get_quote(symbol):
    response = requests.get(
        QUOTE_URL,
        headers=HEADERS,
        params={"symbol": symbol},
        timeout=10
    )

    response.raise_for_status()
    return response.json()


def format_timestamp(timestamp):
    if not timestamp:
        return "Timestamp unavailable"

    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)

    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


# --------------------------------------------------
# Symbol groups
# --------------------------------------------------

market_overview = [
    "SPY",
    "QQQ",
    "DIA"
]

watchlist = [
    "AAPL",
    "MSFT",
    "NVDA",
    "CVNA"
]

crypto = [
    "BINANCE:BTCUSDT",
    "BINANCE:ETHUSDT"
]


# --------------------------------------------------
# Display function
# --------------------------------------------------

def display_group(title, symbols):
    st.subheader(title)

    columns = st.columns(len(symbols))

    for column, symbol in zip(columns, symbols):

        with column:

            try:
                quote = get_quote(symbol)

                price = quote.get("c", 0)
                change = quote.get("d", 0)
                percent_change = quote.get("dp", 0)
                timestamp = quote.get("t")

                st.markdown(f"### {symbol}")

                st.metric(
                    label="Price",
                    value=f"${price:,.2f}",
                    delta=f"{change:+,.2f} ({percent_change:+.2f}%)"
                )

                st.caption(
                    f"As of: {format_timestamp(timestamp)}"
                )

            except requests.RequestException as error:
                st.error(f"Unable to retrieve {symbol}")
                st.caption(str(error))


# --------------------------------------------------
# Dashboard
# --------------------------------------------------

display_group(
    "Market Overview",
    market_overview
)

st.divider()

display_group(
    "Stock Watchlist",
    watchlist
)

st.divider()

display_group(
    "Crypto",
    crypto
)
