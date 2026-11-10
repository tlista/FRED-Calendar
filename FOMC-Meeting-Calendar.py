"""
FOMC meeting dates by year, pulled from the FRED API.

Setup:
    pip install requests pandas streamlit
    export FRED_API_KEY="your-key"      # or edit API_KEY below
    streamlit run fomc_meeting_dates.py
"""

import datetime as dt
import os

import pandas as pd
import requests
import streamlit as st

# ---------------------------------------------------------------- CONFIG ----
BASE_URL = os.getenv("FRED_BASE_URL", "https://api.stlouisfed.org/fred")  # <-- fill in / confirm
API_KEY = os.getenv("FRED_API_KEY", "YOUR_API_KEY")                       # <-- fill in
RELEASE_ID = int(os.getenv("FOMC_RELEASE_ID", "101"))                     # <-- confirm FOMC release ID
FIRST_YEAR = 1994          # earliest year offered in the dropdown
YEARS_AHEAD = 2            # how many future years to offer
TIMEOUT = 15


# ------------------------------------------------------------ DATA LAYER ----
def _get(endpoint: str, **params) -> dict:
    params.update({"api_key": API_KEY, "file_type": "json"})
    resp = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


@st.cache_data(ttl=60 * 60 * 6, show_spinner="Fetching FOMC dates from FRED...")
def get_meeting_dates(year: int) -> list[dt.date]:
    """Return sorted FOMC release dates that fall within `year`."""
    start, end = f"{year}-01-01", f"{year}-12-31"
    dates, offset, limit = set(), 0, 1000

    while True:
        data = _get(
            "release/dates",
            release_id=RELEASE_ID,
            realtime_start=start,
            realtime_end=end,
            include_release_dates_with_no_data="true",  # includes future scheduled dates
            sort_order="asc",
            limit=limit,
            offset=offset,
        )
        for row in data.get("release_dates", []):
            d = dt.date.fromisoformat(row["date"])
            if d.year == year:
                dates.add(d)
        offset += limit
        if offset >= data.get("count", 0):
            break

    return sorted(dates)


# ---------------------------------------------------------------- UI --------
def main():
    st.set_page_config(page_title="FOMC Meeting Dates", page_icon="🏛️")
    st.title("FOMC Meeting Dates")

    if API_KEY == "YOUR_API_KEY":
        st.warning("Set FRED_API_KEY (or edit API_KEY in the CONFIG section).")
        st.stop()

    this_year = dt.date.today().year
    years = list(range(this_year + YEARS_AHEAD, FIRST_YEAR - 1, -1))
    year = st.selectbox("Select year", years, index=YEARS_AHEAD)

    try:
        meetings = get_meeting_dates(year)
    except requests.RequestException as e:
        st.error(f"FRED request failed: {e}")
        st.stop()

    if not meetings:
        st.info(f"No FOMC dates found for {year}.")
        st.stop()

    today = dt.date.today()
    df = pd.DataFrame(
        {
            "Meeting #": range(1, len(meetings) + 1),
            "Date": [d.strftime("%B %d, %Y") for d in meetings],
            "Weekday": [d.strftime("%A") for d in meetings],
            "Status": ["Completed" if d < today else "Upcoming" for d in meetings],
        }
    )

    st.subheader(f"{len(meetings)} dates in {year}")
    st.dataframe(df, hide_index=True, use_container_width=True)

    st.download_button(
        "Download CSV",
        df.to_csv(index=False),
        file_name=f"fomc_dates_{year}.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
