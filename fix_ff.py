content = open('modules/factors.py').read()

old = """def get_ff_factors(period: str) -> pd.DataFrame:
    url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            zf = zipfile.ZipFile(io.BytesIO(r.read()))
            name = [n for n in zf.namelist() if n.endswith(".CSV")][0]
            raw = zf.read(name).decode("utf-8")
    except Exception:
        raise ValueError("Could not download Fama-French factor data. Check your internet connection.")"""

new = """def get_ff_factors(period: str) -> pd.DataFrame:
    urls = [
        "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip",
        "https://raw.githubusercontent.com/datasets/ff-factors/main/data/ff5_daily.csv",
    ]
    raw = None
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                data = r.read()
                if url.endswith(".zip"):
                    zf = zipfile.ZipFile(io.BytesIO(data))
                    name = [n for n in zf.namelist() if n.endswith(".CSV")][0]
                    raw = zf.read(name).decode("utf-8")
                else:
                    raw = data.decode("utf-8")
            break
        except Exception:
            continue
    if raw is None:
        raise ValueError("Could not download Fama-French factor data. Check your internet connection.")"""

open('modules/factors.py', 'w').write(content.replace(old, new))
print('Done')
