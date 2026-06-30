"""
Download the UCI Credit Card Default dataset and extract it to data/raw/.

No login required — fetches directly from the UCI ML Repository.

Usage:
    python scripts/download_data.py
"""

import pathlib
import ssl
import urllib.request
import zipfile

URL = "https://archive.ics.uci.edu/static/public/350/default+of+credit+card+clients.zip"
OUT_DIR = pathlib.Path(__file__).resolve().parents[1] / "data" / "raw"
ZIP_PATH = OUT_DIR / "credit_default.zip"
EXPECTED_FILE = OUT_DIR / "default of credit card clients.xls"


def download():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if EXPECTED_FILE.exists():
        print(f"Already downloaded: {EXPECTED_FILE}")
        return

    print(f"Downloading from UCI ML Repository…")
    # macOS Python 3.x often lacks system CA certs; create an unverified context
    # only for this known, stable UCI URL.
    ctx = ssl.create_default_context()
    try:
        urllib.request.urlretrieve(URL, ZIP_PATH)
    except ssl.SSLCertVerificationError:
        print("SSL verification failed — retrying without verification (UCI URL only)")
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(URL, context=ctx) as r, open(ZIP_PATH, "wb") as f:
            f.write(r.read())

    print("Extracting…")
    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        z.extractall(OUT_DIR)

    ZIP_PATH.unlink()
    print(f"Done — dataset at {EXPECTED_FILE}")


if __name__ == "__main__":
    download()
