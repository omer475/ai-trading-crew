"""
Stock Universe for Scanning
============================
Complete lists of FTSE 100, FTSE 250 (top liquid), and S&P 500 (top 100)
tickers for use with Yahoo Finance data feeds.

London-listed stocks use the .L suffix (e.g., HSBA.L).
US-listed stocks use bare tickers (e.g., AAPL).
"""

from typing import List, Dict

# ---------------------------------------------------------------------------
# FTSE 100 — All 100 constituents (Yahoo Finance .L suffix)
# ---------------------------------------------------------------------------
FTSE_100: List[str] = [
    # A
    "AAF.L",   # Airtel Africa
    "AAL.L",   # Anglo American
    "ABF.L",   # Associated British Foods
    "ADM.L",   # Admiral Group
    "AHT.L",   # Ashtead Group
    "ANTO.L",  # Antofagasta
    "AUTO.L",  # Auto Trader Group
    "AV.L",    # Aviva
    "AZN.L",   # AstraZeneca
    # B
    "BA.L",    # BAE Systems
    "BARC.L",  # Barclays
    "BDEV.L",  # Barratt Developments
    "BEZ.L",   # Beazley
    "BKG.L",   # Berkeley Group
    "BME.L",   # B&M European Value Retail
    "BNZL.L",  # Bunzl
    "BP.L",    # BP
    "BRBY.L",  # Burberry
    "BT-A.L",  # BT Group
    # C
    "CCH.L",   # Coca-Cola HBC
    "CNA.L",   # Centrica
    "CPG.L",   # Compass Group
    "CRDA.L",  # Croda International
    # D
    "DARK.L",  # Darktrace
    "DCC.L",   # DCC
    "DGE.L",   # Diageo
    "DPLM.L",  # Diploma
    # E
    "EDV.L",   # Endeavour Mining
    "ENT.L",   # Entain
    "EXPN.L",  # Experian
    # F
    "FLTR.L",  # Flutter Entertainment
    "FRAS.L",  # Frasers Group
    "FRES.L",  # Fresnillo
    # G
    "GLEN.L",  # Glencore
    "GSK.L",   # GSK (GlaxoSmithKline)
    # H
    "HIK.L",   # Hikma Pharmaceuticals
    "HL.L",    # Hargreaves Lansdown
    "HLMA.L",  # Halma
    "HLN.L",   # Haleon
    "HSBA.L",  # HSBC Holdings
    "HWDN.L",  # Howden Joinery
    # I
    "ICG.L",   # Intermediate Capital Group
    "IHG.L",   # InterContinental Hotels Group
    "III.L",   # 3i Group
    "IMB.L",   # Imperial Brands
    "IMI.L",   # IMI
    "INF.L",   # Informa
    "ITRK.L",  # Intertek Group
    # J
    "JD.L",    # JD Sports Fashion
    "JMAT.L",  # Johnson Matthey
    # K
    "KGF.L",   # Kingfisher
    # L
    "LAND.L",  # Land Securities Group
    "LGEN.L",  # Legal & General
    "LLOY.L",  # Lloyds Banking Group
    "LSEG.L",  # London Stock Exchange Group
    # M
    "MKS.L",   # Marks & Spencer
    "MNDI.L",  # Mondi
    "MNG.L",   # M&G
    "MRO.L",   # Melrose Industries
    # N
    "NG.L",    # National Grid
    "NWG.L",   # NatWest Group
    "NXT.L",   # Next
    # P
    "PHNX.L",  # Phoenix Group
    "PRU.L",   # Prudential
    "PSH.L",   # Pershing Square Holdings
    "PSN.L",   # Persimmon
    "PSON.L",  # Pearson
    # R
    "REL.L",   # RELX
    "RIO.L",   # Rio Tinto
    "RKT.L",   # Reckitt Benckiser
    "RMV.L",   # Rightmove
    "RR.L",    # Rolls-Royce Holdings
    "RS1.L",   # RS Group
    "RTO.L",   # Rentokil Initial
    # S
    "SBRY.L",  # Sainsbury's (J)
    "SDR.L",   # Schroders
    "SGE.L",   # Sage Group
    "SGRO.L",  # Segro
    "SHEL.L",  # Shell
    "SKG.L",   # Smurfit Kappa Group
    "SMDS.L",  # Smith (DS)
    "SMIN.L",  # Smiths Group
    "SMT.L",   # Scottish Mortgage Investment Trust
    "SN.L",    # Smith & Nephew
    "SPX.L",   # Spirax Group
    "SSE.L",   # SSE
    "STAN.L",  # Standard Chartered
    "SVT.L",   # Severn Trent
    # T
    "TSCO.L",  # Tesco
    "TW.L",    # Taylor Wimpey
    # U
    "ULVR.L",  # Unilever
    "UTG.L",   # Unite Group
    "UU.L",    # United Utilities
    # V
    "VOD.L",   # Vodafone
    "VTY.L",   # Vistry Group
    "VSTO.L",  # Volution Group
    # W-extras added to reach 100
    "WISE.L",  # Wise (TransferWise)
    # W
    "WEIR.L",  # Weir Group
    "WPP.L",   # WPP
    "WTB.L",   # Whitbread
]


# ---------------------------------------------------------------------------
# FTSE 250 — Top ~100 most liquid constituents (Yahoo Finance .L suffix)
# ---------------------------------------------------------------------------
FTSE_250_TOP: List[str] = [
    "AGR.L",   # Assura
    "AJB.L",   # AJ Bell
    "APAX.L",  # Apax Global Alpha
    "ASC.L",   # ASOS
    "ATT.L",   # Allianz Technology Trust
    "AVON.L",  # Avon Protection
    "BAB.L",   # Babcock International
    "BGEO.L",  # Bank of Georgia Group
    "BOY.L",   # Bodycote
    "BREE.L",  # Breedon Group
    "BRWM.L",  # Brewin Dolphin
    "BYG.L",   # Big Yellow Group
    "CARD.L",  # Card Factory
    "CBG.L",   # Close Brothers Group
    "CHG.L",   # Chemring Group
    "CLDN.L",  # Caledonia Investments
    "CMCX.L",  # CMC Markets
    "CTEC.L",  # ConvaTec Group
    "CURY.L",  # Currys
    "DOCS.L",  # Dr. Martens
    "DOM.L",   # Domino's Pizza Group
    "DNLM.L",  # Dunelm Group
    "ELM.L",   # Elementis
    "EMG.L",   # Man Group
    "ENOG.L",  # Energean
    "ESNT.L",  # Essentra
    "FDM.L",   # FDM Group
    "FGP.L",   # FirstGroup
    "FOUR.L",  # 4imprint Group
    "FUTR.L",  # Future
    "GAW.L",   # Games Workshop
    "GNS.L",   # Genus
    "GPH.L",   # Grafton Group
    "GRI.L",   # Grainger
    "HBR.L",   # Harbour Energy
    "HFD.L",   # Halfords Group
    "HMSO.L",  # Hammerson
    "HTWS.L",  # Helios Towers
    "HYVE.L",  # Hyve Group
    "IGG.L",   # IG Group
    "INCH.L",  # Inchcape
    "IPO.L",   # IP Group
    "IPX.L",   # Impax Asset Management
    "ITV.L",   # ITV
    "JET2.L",  # Jet2
    "JUST.L",  # Just Group
    "KIER.L",  # Kier Group
    "LMP.L",   # Londonmetric Property
    "LXIL.L",  # LXI REIT
    "MNKS.L",  # Monks Investment Trust
    "MONY.L",  # Moneysupermarket.com
    "MTRO.L",  # Metro Bank
    "NCC.L",   # NCC Group
    "OSB.L",   # OSB Group
    "OXIG.L",  # Oxford Instruments
    "PAGE.L",  # PageGroup
    "PFC.L",   # Petrofac
    "PNN.L",   # Pennon Group
    "QQ.L",    # QinetiQ Group
    "RHI.L",   # RHI Magnesita
    "RSW.L",   # Renishaw
    "SCHR.L",  # Schroders (secondary listing)
    "SFOR.L",  # S4 Capital
    "SHI.L",   # SIG
    "SMWH.L",  # WH Smith
    "SRP.L",   # Serco Group
    "STVG.L",  # STV Group
    "SYNC.L",  # Syncona
    "TLW.L",   # Tullow Oil
    "TPK.L",   # Travis Perkins
    "TRIG.L",  # Renewables Infrastructure Group
    "TRN.L",   # Trainline
    "VCTX.L",  # Victrex
    "VMUK.L",  # Virgin Money UK
    "WAG.L",   # Watches of Switzerland
    "WIZZ.L",  # Wizz Air Holdings
    "WIX.L",   # Wickes Group
    "YNGA.L",  # Young & Co's Brewery
    "AGG.L",   # Aggregate Industries
    "AML.L",   # Aston Martin Lagonda
    "BCPT.L",  # Balanced Commercial Property Trust
    "BVT.L",   # BHP Group (secondary)
    "CAPD.L",  # Capital & Counties Properties
    "CCC.L",   # Computacenter
    "DSCV.L",  # Discoverie Group
    "FSTA.L",  # Fuller Smith & Turner
    "GCP.L",   # GCP Infrastructure Investments
    "HICL.L",  # HICL Infrastructure
    "HSTN.L",  # Helios Towers (alt)
    "HLCL.L",  # Helical
    "INPP.L",  # International Public Partnerships
    "KEL.L",   # Keller Group
    "MGNS.L",  # Morgan Sindall Group
    "MTO.L",   # Mitie Group
    "PHP.L",   # Primary Health Properties
    "PRTC.L",  # PureTech Health
    "RWS.L",   # RWS Holdings
    "SAFE.L",  # Safestore Holdings
    "SSPG.L",  # SSP Group
    "STEM.L",  # SThree
    "SUPR.L",  # Supermarket Income REIT
    "TRB.L",   # Tribal Group
]


# ---------------------------------------------------------------------------
# S&P 500 — Top 100 US stocks by market cap
# ---------------------------------------------------------------------------
SP500_TOP100: List[str] = [
    # Mega-cap technology
    "AAPL",    # Apple
    "MSFT",    # Microsoft
    "AMZN",    # Amazon
    "NVDA",    # NVIDIA
    "GOOGL",   # Alphabet (Class A)
    "GOOG",    # Alphabet (Class C)
    "META",    # Meta Platforms
    "TSLA",    # Tesla
    "AVGO",    # Broadcom
    "TSM",     # Taiwan Semiconductor (ADR)
    # Large-cap technology
    "ORCL",    # Oracle
    "CRM",     # Salesforce
    "AMD",     # Advanced Micro Devices
    "ADBE",    # Adobe
    "ACN",     # Accenture
    "CSCO",    # Cisco Systems
    "INTC",    # Intel
    "IBM",     # IBM
    "TXN",     # Texas Instruments
    "QCOM",    # Qualcomm
    "NOW",     # ServiceNow
    "INTU",    # Intuit
    "AMAT",    # Applied Materials
    "ISRG",    # Intuitive Surgical
    "MU",      # Micron Technology
    "LRCX",    # Lam Research
    "KLAC",    # KLA Corporation
    "SNPS",    # Synopsys
    "CDNS",    # Cadence Design Systems
    "PLTR",    # Palantir Technologies
    # Financials
    "BRK-B",   # Berkshire Hathaway (Class B)
    "JPM",     # JPMorgan Chase
    "V",       # Visa
    "MA",      # Mastercard
    "BAC",     # Bank of America
    "WFC",     # Wells Fargo
    "GS",      # Goldman Sachs
    "MS",      # Morgan Stanley
    "SPGI",    # S&P Global
    "BLK",     # BlackRock
    "C",       # Citigroup
    "AXP",     # American Express
    "SCHW",    # Charles Schwab
    "CB",      # Chubb
    "MMC",     # Marsh & McLennan
    "ICE",     # Intercontinental Exchange
    # Healthcare
    "UNH",     # UnitedHealth Group
    "LLY",     # Eli Lilly
    "JNJ",     # Johnson & Johnson
    "ABBV",    # AbbVie
    "MRK",     # Merck & Co
    "PFE",     # Pfizer
    "TMO",     # Thermo Fisher Scientific
    "ABT",     # Abbott Laboratories
    "DHR",     # Danaher
    "BMY",     # Bristol-Myers Squibb
    "AMGN",    # Amgen
    "GILD",    # Gilead Sciences
    "VRTX",    # Vertex Pharmaceuticals
    "SYK",     # Stryker
    "MDT",     # Medtronic
    "REGN",    # Regeneron Pharmaceuticals
    "ELV",     # Elevance Health
    # Consumer / Retail
    "WMT",     # Walmart
    "PG",      # Procter & Gamble
    "COST",    # Costco
    "KO",      # Coca-Cola
    "PEP",     # PepsiCo
    "HD",      # Home Depot
    "MCD",     # McDonald's
    "NKE",     # Nike
    "SBUX",    # Starbucks
    "TGT",     # Target
    "LOW",     # Lowe's
    "CL",      # Colgate-Palmolive
    # Industrials
    "GE",      # GE Aerospace
    "CAT",     # Caterpillar
    "UNP",     # Union Pacific
    "RTX",     # RTX (Raytheon Technologies)
    "HON",     # Honeywell
    "DE",      # Deere & Company
    "LMT",     # Lockheed Martin
    "UPS",     # United Parcel Service
    "BA",      # Boeing
    "GD",      # General Dynamics
    # Energy
    "XOM",     # Exxon Mobil
    "CVX",     # Chevron
    "COP",     # ConocoPhillips
    "SLB",     # Schlumberger
    "EOG",     # EOG Resources
    # Telecom & Utilities
    "T",       # AT&T
    "VZ",      # Verizon
    "NEE",     # NextEra Energy
    "DUK",     # Duke Energy
    # Other
    "NFLX",    # Netflix
    "DIS",     # Walt Disney
    "CMCSA",   # Comcast
    "LIN",     # Linde
    "PM",      # Philip Morris International
    "PANW",    # Palo Alto Networks
]


# ---------------------------------------------------------------------------
# Combined universe lists
# ---------------------------------------------------------------------------
ALL_LSE: List[str] = FTSE_100 + FTSE_250_TOP
ALL_US: List[str] = SP500_TOP100
FULL_UNIVERSE: List[str] = ALL_LSE + ALL_US


# ---------------------------------------------------------------------------
# Sector classifications
# ---------------------------------------------------------------------------
SECTOR_MAP: Dict[str, str] = {
    # --- FTSE 100 Sectors ---
    # Energy
    "BP.L": "Energy",
    "SHEL.L": "Energy",
    # Mining / Materials
    "AAL.L": "Materials",
    "ANTO.L": "Materials",
    "FRES.L": "Materials",
    "GLEN.L": "Materials",
    "RIO.L": "Materials",
    "MNDI.L": "Materials",
    "EDV.L": "Materials",
    "SKG.L": "Materials",
    # Financials
    "BARC.L": "Financials",
    "HSBA.L": "Financials",
    "LLOY.L": "Financials",
    "NWG.L": "Financials",
    "STAN.L": "Financials",
    "LSEG.L": "Financials",
    "III.L": "Financials",
    "ADM.L": "Financials",
    "AV.L": "Financials",
    "ICG.L": "Financials",
    "LGEN.L": "Financials",
    "MNG.L": "Financials",
    "PHNX.L": "Financials",
    "PRU.L": "Financials",
    "SDR.L": "Financials",
    "HL.L": "Financials",
    "PSH.L": "Financials",
    "BEZ.L": "Financials",
    "SMT.L": "Financials",
    # Healthcare / Pharmaceuticals
    "AZN.L": "Healthcare",
    "GSK.L": "Healthcare",
    "HLN.L": "Healthcare",
    "HIK.L": "Healthcare",
    "SN.L": "Healthcare",
    # Consumer Staples
    "ULVR.L": "Consumer Staples",
    "DGE.L": "Consumer Staples",
    "RKT.L": "Consumer Staples",
    "TSCO.L": "Consumer Staples",
    "ABF.L": "Consumer Staples",
    "IMB.L": "Consumer Staples",
    "SBRY.L": "Consumer Staples",
    # Consumer Discretionary
    "NXT.L": "Consumer Discretionary",
    "CPG.L": "Consumer Discretionary",
    "IHG.L": "Consumer Discretionary",
    "WTB.L": "Consumer Discretionary",
    "JD.L": "Consumer Discretionary",
    "BRBY.L": "Consumer Discretionary",
    "ENT.L": "Consumer Discretionary",
    "FLTR.L": "Consumer Discretionary",
    "FRAS.L": "Consumer Discretionary",
    "KGF.L": "Consumer Discretionary",
    "MKS.L": "Consumer Discretionary",
    "BME.L": "Consumer Discretionary",
    # Industrials
    "BA.L": "Industrials",
    "RR.L": "Industrials",
    "AHT.L": "Industrials",
    "BNZL.L": "Industrials",
    "MRO.L": "Industrials",
    "RS1.L": "Industrials",
    "SMIN.L": "Industrials",
    "SPX.L": "Industrials",
    "WEIR.L": "Industrials",
    "HWDN.L": "Industrials",
    "DPLM.L": "Industrials",
    "ITRK.L": "Industrials",
    "RTO.L": "Industrials",
    # Technology
    "DARK.L": "Technology",
    "SGE.L": "Technology",
    "HLMA.L": "Technology",
    # Telecommunications
    "BT-A.L": "Telecommunications",
    "VOD.L": "Telecommunications",
    "AAF.L": "Telecommunications",
    # Real Estate
    "LAND.L": "Real Estate",
    "SGRO.L": "Real Estate",
    "UTG.L": "Real Estate",
    # Utilities
    "NG.L": "Utilities",
    "SSE.L": "Utilities",
    "SVT.L": "Utilities",
    "UU.L": "Utilities",
    "CNA.L": "Utilities",
    # Media / Information
    "REL.L": "Industrials",
    "INF.L": "Industrials",
    "EXPN.L": "Industrials",
    "PSON.L": "Consumer Discretionary",
    "WPP.L": "Communication Services",
    "RMV.L": "Technology",
    "WISE.L": "Technology",
    "VSTO.L": "Industrials",
    # Housebuilders
    "BDEV.L": "Consumer Discretionary",
    "PSN.L": "Consumer Discretionary",
    "BKG.L": "Consumer Discretionary",
    "TW.L": "Consumer Discretionary",
    # Other
    "CRDA.L": "Materials",
    "DCC.L": "Industrials",
    "SMDS.L": "Materials",

    # --- FTSE 250 Sectors (selected) ---
    "AUTO.L": "Technology",
    "CCH.L": "Consumer Staples",
    "DOM.L": "Consumer Discretionary",
    "DNLM.L": "Consumer Discretionary",
    "GAW.L": "Consumer Discretionary",
    "HBR.L": "Energy",
    "IGG.L": "Financials",
    "IMI.L": "Industrials",
    "ITV.L": "Communication Services",
    "JMAT.L": "Materials",
    "JET2.L": "Consumer Discretionary",
    "NCC.L": "Technology",
    "QQ.L": "Industrials",
    "TLW.L": "Energy",
    "TPK.L": "Industrials",
    "WIZZ.L": "Consumer Discretionary",
    "SMWH.L": "Consumer Discretionary",
    "SRP.L": "Industrials",
    "VTY.L": "Consumer Discretionary",
    "WAG.L": "Consumer Discretionary",
    "WOSG.L": "Consumer Discretionary",

    # --- S&P 500 Sectors ---
    # Technology
    "AAPL": "Technology",
    "MSFT": "Technology",
    "NVDA": "Technology",
    "GOOGL": "Technology",
    "GOOG": "Technology",
    "META": "Technology",
    "AVGO": "Technology",
    "TSM": "Technology",
    "ORCL": "Technology",
    "CRM": "Technology",
    "AMD": "Technology",
    "ADBE": "Technology",
    "ACN": "Technology",
    "CSCO": "Technology",
    "INTC": "Technology",
    "IBM": "Technology",
    "TXN": "Technology",
    "QCOM": "Technology",
    "NOW": "Technology",
    "INTU": "Technology",
    "AMAT": "Technology",
    "MU": "Technology",
    "LRCX": "Technology",
    "KLAC": "Technology",
    "SNPS": "Technology",
    "CDNS": "Technology",
    "PLTR": "Technology",
    "PANW": "Technology",
    # Financials
    "BRK-B": "Financials",
    "JPM": "Financials",
    "V": "Financials",
    "MA": "Financials",
    "BAC": "Financials",
    "WFC": "Financials",
    "GS": "Financials",
    "MS": "Financials",
    "SPGI": "Financials",
    "BLK": "Financials",
    "C": "Financials",
    "AXP": "Financials",
    "SCHW": "Financials",
    "CB": "Financials",
    "MMC": "Financials",
    "ICE": "Financials",
    # Healthcare
    "UNH": "Healthcare",
    "LLY": "Healthcare",
    "JNJ": "Healthcare",
    "ABBV": "Healthcare",
    "MRK": "Healthcare",
    "PFE": "Healthcare",
    "TMO": "Healthcare",
    "ABT": "Healthcare",
    "DHR": "Healthcare",
    "BMY": "Healthcare",
    "AMGN": "Healthcare",
    "GILD": "Healthcare",
    "VRTX": "Healthcare",
    "SYK": "Healthcare",
    "MDT": "Healthcare",
    "REGN": "Healthcare",
    "ELV": "Healthcare",
    "ISRG": "Healthcare",
    # Consumer Discretionary
    "AMZN": "Consumer Discretionary",
    "TSLA": "Consumer Discretionary",
    "HD": "Consumer Discretionary",
    "MCD": "Consumer Discretionary",
    "NKE": "Consumer Discretionary",
    "SBUX": "Consumer Discretionary",
    "TGT": "Consumer Discretionary",
    "LOW": "Consumer Discretionary",
    # Consumer Staples
    "WMT": "Consumer Staples",
    "PG": "Consumer Staples",
    "COST": "Consumer Staples",
    "KO": "Consumer Staples",
    "PEP": "Consumer Staples",
    "CL": "Consumer Staples",
    "PM": "Consumer Staples",
    # Industrials
    "GE": "Industrials",
    "CAT": "Industrials",
    "UNP": "Industrials",
    "RTX": "Industrials",
    "HON": "Industrials",
    "DE": "Industrials",
    "LMT": "Industrials",
    "UPS": "Industrials",
    "BA": "Industrials",
    "GD": "Industrials",
    # Energy
    "XOM": "Energy",
    "CVX": "Energy",
    "COP": "Energy",
    "SLB": "Energy",
    "EOG": "Energy",
    # Communication Services
    "NFLX": "Communication Services",
    "DIS": "Communication Services",
    "CMCSA": "Communication Services",
    "T": "Communication Services",
    "VZ": "Communication Services",
    # Utilities
    "NEE": "Utilities",
    "DUK": "Utilities",
    # Materials
    "LIN": "Materials",
}


# ---------------------------------------------------------------------------
# Helper function
# ---------------------------------------------------------------------------
def get_universe(market: str = "all") -> List[str]:
    """
    Return a list of tickers for the requested market segment.

    Parameters
    ----------
    market : str
        One of:
        - "ftse100"  -> FTSE 100 constituents
        - "ftse250"  -> Top ~100 FTSE 250 constituents
        - "sp500"    -> Top 100 S&P 500 stocks
        - "lse"      -> ALL_LSE (FTSE 100 + FTSE 250 top)
        - "us"       -> ALL_US (S&P 500 top 100)
        - "all"      -> FULL_UNIVERSE (everything)

    Returns
    -------
    List[str]
        List of Yahoo Finance ticker strings.

    Raises
    ------
    ValueError
        If an unrecognised market string is provided.
    """
    market = market.strip().lower()

    universes = {
        "ftse100": FTSE_100,
        "ftse250": FTSE_250_TOP,
        "sp500": SP500_TOP100,
        "lse": ALL_LSE,
        "us": ALL_US,
        "all": FULL_UNIVERSE,
    }

    if market not in universes:
        valid = ", ".join(sorted(universes.keys()))
        raise ValueError(
            f"Unknown market '{market}'. Valid options: {valid}"
        )

    return universes[market]


def get_sector(ticker: str) -> str:
    """
    Return the sector classification for a given ticker.

    Parameters
    ----------
    ticker : str
        A Yahoo Finance ticker string (e.g. "AAPL" or "HSBA.L").

    Returns
    -------
    str
        Sector name, or "Unknown" if the ticker is not classified.
    """
    return SECTOR_MAP.get(ticker, "Unknown")


def get_tickers_by_sector(sector: str, market: str = "all") -> List[str]:
    """
    Return all tickers in a given sector within the specified market universe.

    Parameters
    ----------
    sector : str
        Sector name (e.g. "Technology", "Healthcare", "Energy").
    market : str
        Market universe to filter (default "all"). Same options as get_universe().

    Returns
    -------
    List[str]
        List of tickers belonging to the specified sector.
    """
    universe = get_universe(market)
    return [t for t in universe if SECTOR_MAP.get(t, "Unknown") == sector]


def list_sectors(market: str = "all") -> List[str]:
    """
    Return a sorted list of all unique sectors present in the specified market universe.

    Parameters
    ----------
    market : str
        Market universe to inspect (default "all"). Same options as get_universe().

    Returns
    -------
    List[str]
        Sorted list of unique sector names.
    """
    universe = set(get_universe(market))
    sectors = {SECTOR_MAP[t] for t in universe if t in SECTOR_MAP}
    return sorted(sectors)


# ---------------------------------------------------------------------------
# Quick sanity check when run directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"FTSE 100 tickers  : {len(FTSE_100)}")
    print(f"FTSE 250 top      : {len(FTSE_250_TOP)}")
    print(f"S&P 500 top 100   : {len(SP500_TOP100)}")
    print(f"ALL LSE            : {len(ALL_LSE)}")
    print(f"ALL US             : {len(ALL_US)}")
    print(f"FULL UNIVERSE      : {len(FULL_UNIVERSE)}")
    print(f"Sectors classified : {len(SECTOR_MAP)}")
    print(f"Unique sectors     : {list_sectors()}")
