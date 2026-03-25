import pandas as pd


def read_uploaded_file(uploaded_file):
    """Read CSV/XLSX from a Streamlit uploader or file-like object."""
    if not uploaded_file:
        return None
    try:
        uploaded_file.seek(0)
    except Exception:
        pass

    name = str(getattr(uploaded_file, "name", "")).lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    return pd.read_excel(uploaded_file)


def read_remote_csv(csv_url: str):
    """Fetch remote CSV and extract its Last-Modified timestamp."""
    from io import BytesIO
    from urllib.request import Request, urlopen
    from email.utils import parsedate_to_datetime

    req = Request(csv_url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req) as resp:
        raw = resp.read()
        lm = resp.headers.get("Last-Modified")

    df = pd.read_csv(BytesIO(raw))
    if lm:
        try:
            lm = parsedate_to_datetime(lm).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            lm = "Live Sync"
    else:
        lm = "Snapshot"
    return df, lm
