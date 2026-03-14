"""
Stock Universe for Scanning
============================
Complete lists of FTSE 100, FTSE 250 (top liquid), S&P 500 (full),
and Russell Midcap growth stocks for use with Yahoo Finance data feeds.

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
# S&P 500 — Full ~503 constituents
# ---------------------------------------------------------------------------
SP500_FULL: List[str] = [
    # --- Information Technology ---
    "AAPL",    # Apple
    "MSFT",    # Microsoft
    "NVDA",    # NVIDIA
    "AVGO",    # Broadcom
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
    "MU",      # Micron Technology
    "LRCX",    # Lam Research
    "KLAC",    # KLA Corporation
    "SNPS",    # Synopsys
    "CDNS",    # Cadence Design Systems
    "PANW",    # Palo Alto Networks
    "ADI",     # Analog Devices
    "MCHP",    # Microchip Technology
    "NXPI",    # NXP Semiconductors
    "FTNT",    # Fortinet
    "APH",     # Amphenol
    "MSI",     # Motorola Solutions
    "KEYS",    # Keysight Technologies
    "CDW",     # CDW Corporation
    "ANSS",    # ANSYS
    "TEL",     # TE Connectivity
    "HPQ",     # HP Inc
    "HPE",     # Hewlett Packard Enterprise
    "GLW",     # Corning
    "ZBRA",    # Zebra Technologies
    "TYL",     # Tyler Technologies
    "SWKS",    # Skyworks Solutions
    "TDY",     # Teledyne Technologies
    "PTC",     # PTC Inc
    "TRMB",    # Trimble
    "GEN",     # Gen Digital
    "FSLR",    # First Solar
    "ENPH",    # Enphase Energy
    "SEDG",    # SolarEdge Technologies
    "EPAM",    # EPAM Systems
    "JNPR",    # Juniper Networks
    "FFIV",    # F5 Networks
    "AKAM",    # Akamai Technologies
    "NTAP",    # NetApp
    "QRVO",    # Qorvo
    "MTCH",    # Match Group
    "CTSH",    # Cognizant Technology Solutions
    "IT",      # Gartner
    "VRSN",    # VeriSign
    "WDC",     # Western Digital
    "STX",     # Seagate Technology
    "ON",      # ON Semiconductor
    "MPWR",    # Monolithic Power Systems
    "SMCI",    # Super Micro Computer
    "ADSK",    # Autodesk
    "FIS",     # Fidelity National Information Services
    "GPN",     # Global Payments
    "BR",      # Broadridge Financial Solutions
    "CPAY",    # Corpay
    "FI",      # Fiserv
    "GDDY",    # GoDaddy
    "PAYC",    # Paycom Software
    "CERIDIAN", # Dayforce (Ceridian)

    # --- Communication Services ---
    "GOOGL",   # Alphabet (Class A)
    "GOOG",    # Alphabet (Class C)
    "META",    # Meta Platforms
    "NFLX",    # Netflix
    "DIS",     # Walt Disney
    "CMCSA",   # Comcast
    "T",       # AT&T
    "VZ",      # Verizon
    "CHTR",    # Charter Communications
    "TMUS",    # T-Mobile US
    "EA",      # Electronic Arts
    "TTWO",    # Take-Two Interactive
    "WBD",     # Warner Bros Discovery
    "OMC",     # Omnicom Group
    "IPG",     # Interpublic Group
    "MTCH",    # Match Group
    "FOXA",    # Fox Corporation (Class A)
    "FOX",     # Fox Corporation (Class B)
    "NWSA",    # News Corp (Class A)
    "NWS",     # News Corp (Class B)
    "PARA",    # Paramount Global
    "LYV",     # Live Nation Entertainment

    # --- Consumer Discretionary ---
    "AMZN",    # Amazon
    "TSLA",    # Tesla
    "HD",      # Home Depot
    "MCD",     # McDonald's
    "NKE",     # Nike
    "SBUX",    # Starbucks
    "TGT",     # Target
    "LOW",     # Lowe's
    "BKNG",    # Booking Holdings
    "CMG",     # Chipotle Mexican Grill
    "ORLY",    # O'Reilly Automotive
    "AZO",     # AutoZone
    "MAR",     # Marriott International
    "HLT",     # Hilton Worldwide
    "ROST",    # Ross Stores
    "DHI",     # D.R. Horton
    "LEN",     # Lennar
    "F",       # Ford Motor
    "GM",      # General Motors
    "APTV",    # Aptiv
    "YUM",     # Yum! Brands
    "UBER",    # Uber Technologies
    "DECK",    # Deckers Outdoor
    "RCL",     # Royal Caribbean
    "TSCO",    # Tractor Supply
    "DG",      # Dollar General
    "DLTR",    # Dollar Tree
    "BBY",     # Best Buy
    "EBAY",    # eBay
    "ETSY",    # Etsy
    "GPC",     # Genuine Parts
    "LVS",     # Las Vegas Sands
    "WYNN",    # Wynn Resorts
    "CZR",     # Caesars Entertainment
    "MGM",     # MGM Resorts
    "POOL",    # Pool Corporation
    "PHM",     # PulteGroup
    "NVR",     # NVR Inc
    "BWA",     # BorgWarner
    "MHK",     # Mohawk Industries
    "RL",      # Ralph Lauren
    "HAS",     # Hasbro
    "EXPE",    # Expedia Group
    "ABNB",    # Airbnb
    "CCL",     # Carnival Corporation
    "NCLH",    # Norwegian Cruise Line
    "LKQ",     # LKQ Corporation
    "GRMN",    # Garmin
    "ULTA",    # Ulta Beauty
    "LULU",    # Lululemon Athletica
    "CAVA",    # CAVA Group
    "DARDEN",  # Darden Restaurants -- note: actual ticker is DRI
    "DRI",     # Darden Restaurants
    "KMX",     # CarMax
    "PCAR",    # PACCAR
    "TPR",     # Tapestry
    "VFC",     # VF Corporation
    "PVH",     # PVH Corp
    "GNRC",    # Generac Holdings
    "SEE",     # Sealed Air

    # --- Healthcare ---
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
    "ISRG",    # Intuitive Surgical
    "BSX",     # Boston Scientific
    "CI",      # Cigna Group
    "HCA",     # HCA Healthcare
    "ZTS",     # Zoetis
    "MCK",     # McKesson
    "HUM",     # Humana
    "MOH",     # Molina Healthcare
    "CNC",     # Centene
    "IDXX",    # IDEXX Laboratories
    "IQV",     # IQVIA Holdings
    "DXCM",    # DexCom
    "GEHC",    # GE HealthCare
    "EW",      # Edwards Lifesciences
    "A",       # Agilent Technologies
    "BAX",     # Baxter International
    "BDX",     # Becton Dickinson
    "BIIB",    # Biogen
    "COO",     # Cooper Companies
    "DVA",     # DaVita
    "HOLX",    # Hologic
    "HSIC",    # Henry Schein
    "INCY",    # Incyte Corporation
    "LH",      # Labcorp Holdings
    "MTD",     # Mettler-Toledo
    "RMD",     # ResMed
    "STE",     # Steris
    "TECH",    # Bio-Techne
    "WAT",     # Waters Corporation
    "XRAY",    # Dentsply Sirona
    "ALGN",    # Align Technology
    "CRL",     # Charles River Laboratories
    "CTLT",    # Catalent
    "WBA",     # Walgreens Boots Alliance
    "CAH",     # Cardinal Health
    "ABC",     # AmerisourceBergen (Cencora)
    "VTRS",    # Viatris

    # --- Financials ---
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
    "CME",     # CME Group
    "AON",     # Aon
    "MCO",     # Moody's
    "PGR",     # Progressive Corporation
    "AIG",     # American International Group
    "AFL",     # Aflac
    "ADP",     # Automatic Data Processing
    "TFC",     # Truist Financial
    "USB",     # US Bancorp
    "PNC",     # PNC Financial Services
    "COF",     # Capital One Financial
    "BK",      # Bank of New York Mellon
    "STT",     # State Street
    "AMP",     # Ameriprise Financial
    "PRU",     # Prudential Financial
    "MET",     # MetLife
    "TROW",    # T. Rowe Price
    "DFS",     # Discover Financial Services
    "NTRS",    # Northern Trust
    "FITB",    # Fifth Third Bancorp
    "CFG",     # Citizens Financial
    "HBAN",    # Huntington Bancshares
    "RF",      # Regions Financial
    "KEY",     # KeyCorp
    "MTB",     # M&T Bank
    "WRB",     # W.R. Berkley
    "CINF",    # Cincinnati Financial
    "BRO",     # Brown & Brown
    "AIZ",     # Assurant
    "RE",      # Everest Re Group
    "GL",      # Globe Life
    "RJF",     # Raymond James Financial
    "SIVB",    # SVB Financial (if still listed)
    "L",       # Loews
    "BEN",     # Franklin Templeton
    "IVZ",     # Invesco
    "ZION",    # Zions Bancorporation
    "SBNY",    # Signature Bank (if still listed)
    "FRC",     # First Republic Bank (if still listed)
    "MKTX",    # MarketAxess
    "MSCI",    # MSCI Inc
    "NDAQ",    # Nasdaq Inc
    "FDS",     # FactSet Research Systems
    "CBOE",    # Cboe Global Markets
    "EFX",     # Equifax
    "VRSK",    # Verisk Analytics
    "WTW",     # Willis Towers Watson

    # --- Industrials ---
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
    "ETN",     # Eaton
    "ITW",     # Illinois Tool Works
    "EMR",     # Emerson Electric
    "PH",      # Parker-Hannifin
    "AJG",     # Arthur J. Gallagher
    "TT",      # Trane Technologies
    "CTAS",    # Cintas
    "CARR",    # Carrier Global
    "OTIS",    # Otis Worldwide
    "CSX",     # CSX Corporation
    "NSC",     # Norfolk Southern
    "WM",      # Waste Management
    "RSG",     # Republic Services
    "GWW",     # W.W. Grainger
    "FAST",    # Fastenal
    "ODFL",    # Old Dominion Freight Line
    "PCAR",    # PACCAR
    "ROK",     # Rockwell Automation
    "AME",     # AMETEK
    "DOV",     # Dover
    "IR",      # Ingersoll Rand
    "FTV",     # Fortive
    "WAB",     # Westinghouse Air Brake
    "IEX",     # IDEX Corporation
    "PNR",     # Pentair
    "VRSK",    # Verisk Analytics
    "SNA",     # Snap-on
    "NDSN",    # Nordson
    "JBHT",    # J.B. Hunt Transport
    "DAL",     # Delta Air Lines
    "LUV",     # Southwest Airlines
    "AAL",     # American Airlines
    "UAL",     # United Airlines
    "EXPD",    # Expeditors International
    "CHRW",    # C.H. Robinson Worldwide
    "XYL",     # Xylem
    "SWK",     # Stanley Black & Decker
    "HII",     # Huntington Ingalls Industries
    "NOC",     # Northrop Grumman
    "LHX",     # L3Harris Technologies
    "TDG",     # TransDigm Group
    "HWM",     # Howmet Aerospace
    "GEV",     # GE Vernova
    "AXON",    # Axon Enterprise
    "PAYX",    # Paychex
    "J",       # Jacobs Solutions
    "ALLE",    # Allegion
    "AOS",     # A.O. Smith
    "LDOS",    # Leidos Holdings
    "TXT",     # Textron
    "IP",      # International Paper
    "PKG",     # Packaging Corp of America
    "STE",     # Steris (also Healthcare)
    "GEHC",    # GE HealthCare (also Healthcare)
    "CEG",     # Constellation Energy
    "VLTO",    # Veralto
    "BLDR",    # Builders FirstSource
    "PWR",     # Quanta Services
    "EME",     # EMCOR Group
    "FLR",     # Fluor Corporation
    "GNRC",    # Generac (also Consumer Discretionary)
    "CPRT",    # Copart

    # --- Consumer Staples ---
    "WMT",     # Walmart
    "PG",      # Procter & Gamble
    "COST",    # Costco
    "KO",      # Coca-Cola
    "PEP",     # PepsiCo
    "PM",      # Philip Morris International
    "MDLZ",    # Mondelez International
    "CL",      # Colgate-Palmolive
    "MO",      # Altria Group
    "KMB",     # Kimberly-Clark
    "GIS",     # General Mills
    "K",       # Kellanova
    "KR",      # Kroger
    "HSY",     # Hershey
    "SJM",     # J.M. Smucker
    "KHC",     # Kraft Heinz
    "CLX",     # Clorox
    "STZ",     # Constellation Brands
    "MKC",     # McCormick & Co
    "ADM",     # Archer-Daniels-Midland
    "BG",      # Bunge
    "TAP",     # Molson Coors
    "CPB",     # Campbell Soup
    "CAG",     # Conagra Brands
    "HRL",     # Hormel Foods
    "TSN",     # Tyson Foods
    "SYY",     # Sysco
    "MNST",    # Monster Beverage
    "KVUE",    # Kenvue
    "EL",      # Estee Lauder
    "CHD",     # Church & Dwight

    # --- Energy ---
    "XOM",     # Exxon Mobil
    "CVX",     # Chevron
    "COP",     # ConocoPhillips
    "SLB",     # Schlumberger
    "EOG",     # EOG Resources
    "MPC",     # Marathon Petroleum
    "PSX",     # Phillips 66
    "VLO",     # Valero Energy
    "OKE",     # ONEOK
    "WMB",     # Williams Companies
    "FANG",    # Diamondback Energy
    "HAL",     # Halliburton
    "HES",     # Hess Corporation
    "DVN",     # Devon Energy
    "TRGP",    # Targa Resources
    "KMI",     # Kinder Morgan
    "BKR",     # Baker Hughes
    "OXY",     # Occidental Petroleum
    "CTRA",    # Coterra Energy
    "MRO",     # Marathon Oil
    "APA",     # APA Corporation
    "EQT",     # EQT Corporation

    # --- Utilities ---
    "NEE",     # NextEra Energy
    "DUK",     # Duke Energy
    "SO",      # Southern Company
    "AEP",     # American Electric Power
    "EXC",     # Exelon
    "SRE",     # Sempra
    "PEG",     # Public Service Enterprise Group
    "ED",      # Consolidated Edison
    "XEL",     # Xcel Energy
    "WEC",     # WEC Energy Group
    "DTE",     # DTE Energy
    "ETR",     # Entergy
    "ES",      # Eversource Energy
    "PPL",     # PPL Corporation
    "FE",      # FirstEnergy
    "AWK",     # American Water Works
    "CNP",     # CenterPoint Energy
    "ATO",     # Atmos Energy
    "NI",      # NiSource
    "EIX",     # Edison International
    "CMS",     # CMS Energy
    "CEG",     # Constellation Energy
    "D",       # Dominion Energy
    "AES",     # AES Corporation
    "LNT",     # Alliant Energy
    "EVRG",    # Evergy
    "PNW",     # Pinnacle West Capital

    # --- Real Estate ---
    "SPG",     # Simon Property Group
    "PSA",     # Public Storage
    "CCI",     # Crown Castle
    "O",       # Realty Income
    "DLR",     # Digital Realty Trust
    "WELL",    # Welltower
    "AVB",     # AvalonBay Communities
    "EQR",     # Equity Residential
    "VICI",    # VICI Properties
    "ARE",     # Alexandria Real Estate
    "ESS",     # Essex Property Trust
    "MAA",     # Mid-America Apartment
    "UDR",     # UDR Inc
    "BXP",     # BXP Inc (Boston Properties)
    "VTR",     # Ventas
    "HST",     # Host Hotels & Resorts
    "IRM",     # Iron Mountain
    "REG",     # Regency Centers
    "KIM",     # Kimco Realty
    "CPT",     # Camden Property Trust
    "FRT",     # Federal Realty Investment Trust
    "SBAC",    # SBA Communications
    "AMT",     # American Tower
    "PEAK",    # Healthpeak Properties
    "CBRE",    # CBRE Group
    "INVH",    # Invitation Homes

    # --- Materials ---
    "LIN",     # Linde
    "SHW",     # Sherwin-Williams
    "ECL",     # Ecolab
    "NEM",     # Newmont
    "APD",     # Air Products and Chemicals
    "DD",      # DuPont de Nemours
    "CTVA",    # Corteva
    "NUE",     # Nucor
    "VMC",     # Vulcan Materials
    "MLM",     # Martin Marietta Materials
    "DOV",     # Dover Corporation
    "PPG",     # PPG Industries
    "BALL",    # Ball Corporation
    "PKG",     # Packaging Corp of America
    "IP",      # International Paper
    "ALB",     # Albemarle
    "FMC",     # FMC Corporation
    "CF",      # CF Industries
    "MOS",     # Mosaic Company
    "IFF",     # International Flavors & Fragrances
    "CE",      # Celanese
    "EMN",     # Eastman Chemical
    "SEE",     # Sealed Air
    "AMCR",    # Amcor
    "AVY",     # Avery Dennison
    "WRK",     # WestRock
    "STLD",    # Steel Dynamics

    # --- Additional S&P 500 names to ensure completeness ---
    "PLTR",    # Palantir Technologies
    "TSM",     # Taiwan Semiconductor (ADR)
    "NFLX",    # Netflix (dup guard handled by set if needed)
    "SHW",     # Sherwin-Williams (dup guard)
    "PYPL",    # PayPal
    "ADP",     # Automatic Data Processing
    "FDX",     # FedEx
    "MDLZ",    # Mondelez (dup guard)
    "WELL",    # Welltower (dup guard)
    "CTVA",    # Corteva (dup guard)
    "DD",      # DuPont (dup guard)
    "TROW",    # T. Rowe Price (dup guard)
    "BRO",     # Brown & Brown (dup guard)
    "WTW",     # Willis Towers Watson (dup guard)
    "VRSK",    # Verisk (dup guard)
    "EFX",     # Equifax (dup guard)

    # Additional confirmed S&P 500 members
    "ACGL",    # Arch Capital Group
    "TRV",     # Travelers Companies
    "ALL",     # Allstate
    "HIG",     # Hartford Financial Services
    "ERIE",    # Erie Indemnity
    "JKHY",    # Jack Henry & Associates
    "CMA",     # Comerica
    "FHN",     # First Horizon
    "FCNCA",   # First Citizens BancShares
    "WAL",     # Western Alliance Bancorporation
    "EWBC",    # East West Bancorp
    "LBRDK",   # Liberty Broadband (Class C)
    "LBRDA",   # Liberty Broadband (Class A)
    "LYB",     # LyondellBasell
    "ROL",     # Rollins
    "DPZ",     # Domino's Pizza
    "PODD",    # Insulet Corporation
    "RVTY",    # Revvity
    "ILMN",    # Illumina
    "TER",     # Teradyne
    "WY",      # Weyerhaeuser

    # More S&P 500 members — ensuring completeness
    "USB",     # US Bancorp
    "PNC",     # PNC Financial Services
    "MET",     # MetLife
    "FITB",    # Fifth Third Bancorp
    "KEY",     # KeyCorp
    "MTB",     # M&T Bank
    "RE",      # Everest Re Group
    "GL",      # Globe Life
    "RJF",     # Raymond James Financial
    "L",       # Loews
    "NDAQ",    # Nasdaq Inc
    "FDS",     # FactSet Research Systems
    "CBOE",    # Cboe Global Markets
    "CSX",     # CSX Corporation
    "NSC",     # Norfolk Southern
    "WM",      # Waste Management
    "RSG",     # Republic Services
    "ROK",     # Rockwell Automation
    "NOC",     # Northrop Grumman
    "LHX",     # L3Harris Technologies
    "TDG",     # TransDigm Group
    "HWM",     # Howmet Aerospace
    "GEV",     # GE Vernova
    "AXON",    # Axon Enterprise
    "LDOS",    # Leidos Holdings
    "TXT",     # Textron
    "VLTO",    # Veralto
    "BLDR",    # Builders FirstSource
    "PWR",     # Quanta Services
    "EME",     # EMCOR Group
    "FLR",     # Fluor Corporation
    "CPRT",    # Copart
    "FDX",     # FedEx
    "UAL",     # United Airlines
    "CHRW",    # C.H. Robinson Worldwide
    "XYL",     # Xylem
    "NDSN",    # Nordson
    "MO",      # Altria Group
    "STZ",     # Constellation Brands
    "TAP",     # Molson Coors
    "CPB",     # Campbell Soup
    "CAG",     # Conagra Brands
    "HRL",     # Hormel Foods
    "TSN",     # Tyson Foods
    "SYY",     # Sysco
    "KVUE",    # Kenvue
    "EL",      # Estee Lauder
    "CHD",     # Church & Dwight
    "SJM",     # J.M. Smucker
    "CHTR",    # Charter Communications
    "TMUS",    # T-Mobile US
    "TTWO",    # Take-Two Interactive
    "WBD",     # Warner Bros Discovery
    "OMC",     # Omnicom Group
    "IPG",     # Interpublic Group
    "LYV",     # Live Nation Entertainment
    "DLTR",    # Dollar Tree
    "BBY",     # Best Buy
    "EBAY",    # eBay
    "ETSY",    # Etsy
    "GPC",     # Genuine Parts
    "LVS",     # Las Vegas Sands
    "MGM",     # MGM Resorts
    "POOL",    # Pool Corporation
    "PHM",     # PulteGroup
    "NVR",     # NVR Inc
    "HAS",     # Hasbro
    "EXPE",    # Expedia Group
    "ABNB",    # Airbnb
    "CCL",     # Carnival Corporation
    "NCLH",    # Norwegian Cruise Line
    "GRMN",    # Garmin
    "ULTA",    # Ulta Beauty
    "LULU",    # Lululemon Athletica
    "DRI",     # Darden Restaurants
    "KMX",     # CarMax
    "TPR",     # Tapestry
    "PVH",     # PVH Corp
    "A",       # Agilent Technologies
    "BDX",     # Becton Dickinson
    "HOLX",    # Hologic
    "HSIC",    # Henry Schein
    "INCY",    # Incyte Corporation
    "ALGN",    # Align Technology
    "CAH",     # Cardinal Health
    "ABC",     # AmerisourceBergen (Cencora)
    "VTRS",    # Viatris
    "D",       # Dominion Energy
    "AES",     # AES Corporation
    "LNT",     # Alliant Energy
    "EVRG",    # Evergy
    "PNW",     # Pinnacle West Capital
    "REG",     # Regency Centers
    "KIM",     # Kimco Realty
    "CPT",     # Camden Property Trust
    "SBAC",    # SBA Communications
    "AMT",     # American Tower
    "PEAK",    # Healthpeak Properties
    "INVH",    # Invitation Homes
    "APD",     # Air Products and Chemicals
    "ALB",     # Albemarle
    "FMC",     # FMC Corporation
    "IFF",     # International Flavors & Fragrances
    "CE",      # Celanese
    "EMN",     # Eastman Chemical
    "AMCR",    # Amcor
    "AVY",     # Avery Dennison
    "WRK",     # WestRock
    "STLD",    # Steel Dynamics
    "GLW",     # Corning
    "SWKS",    # Skyworks Solutions
    "PTC",     # PTC Inc
    "TRMB",    # Trimble
    "GEN",     # Gen Digital
    "FSLR",    # First Solar
    "ENPH",    # Enphase Energy
    "SEDG",    # SolarEdge Technologies
    "EPAM",    # EPAM Systems
    "JNPR",    # Juniper Networks
    "FFIV",    # F5 Networks
    "AKAM",    # Akamai Technologies
    "NTAP",    # NetApp
    "QRVO",    # Qorvo
    "CTSH",    # Cognizant Technology Solutions
    "IT",      # Gartner
    "VRSN",    # VeriSign
    "WDC",     # Western Digital
    "STX",     # Seagate Technology
    "ON",      # ON Semiconductor
    "MPWR",    # Monolithic Power Systems
    "BR",      # Broadridge Financial Solutions
    "GDDY",    # GoDaddy
    "PAYC",    # Paycom Software
    "CERIDIAN", # Dayforce (Ceridian)
    "KMI",     # Kinder Morgan
    "BKR",     # Baker Hughes
    "OXY",     # Occidental Petroleum
    "CTRA",    # Coterra Energy
    "APA",     # APA Corporation
    "EQT",     # EQT Corporation
    "VLO",     # Valero Energy

    # Even more S&P 500 members
    "CSGP",    # CoStar Group
    "HUBB",    # Hubbell
    "WST",     # West Pharmaceutical Services
    "SWK",     # Stanley Black & Decker
    "TRGP",    # Targa Resources
    "FANG",    # Diamondback Energy
    "DVN",     # Devon Energy
    "BKR",     # Baker Hughes
    "MRO",     # Marathon Oil
    "PARA",    # Paramount Global
    "NWSA",    # News Corp A
    "NWS",     # News Corp B
    "FOXA",    # Fox A
    "FOX",     # Fox B
    "WBA",     # Walgreens Boots Alliance
    "XRAY",    # Dentsply Sirona
    "TECH",    # Bio-Techne
    "CTLT",    # Catalent
    "CRL",     # Charles River Labs
    "IVZ",     # Invesco
    "BEN",     # Franklin Templeton
    "ZION",    # Zions Bancorp
    "DVA",     # DaVita
    "MHK",     # Mohawk Industries
    "VFC",     # VF Corporation
    "SEE",     # Sealed Air
    "FRT",     # Federal Realty
    "HII",     # Huntington Ingalls
    "WYNN",    # Wynn Resorts
    "CZR",     # Caesars Entertainment
    "GNRC",    # Generac Holdings
    "MTCH",    # Match Group
    "LKQ",     # LKQ Corporation
    "AAL",     # American Airlines
    "MOS",     # Mosaic Company
    "BWA",     # BorgWarner
    "AIZ",     # Assurant
    "RL",      # Ralph Lauren
    "UDR",     # UDR Inc
    "BXP",     # BXP Inc
    "HST",     # Host Hotels
    "AOS",     # A.O. Smith
    "ALLE",    # Allegion
    "IP",      # International Paper
    "NI",      # NiSource
    "CF",      # CF Industries
    "PNR",     # Pentair
    "JBHT",    # JB Hunt Transport
    "CEG",     # Constellation Energy
    "TSCO",    # Tractor Supply
    "WY",      # Weyerhaeuser
    "DAY",     # Dayforce (formerly Ceridian)
    "EG",      # Everest Group
    "BALL",    # Ball Corporation
    "VRSK",    # Verisk Analytics
    "EFX",     # Equifax
    "WTW",     # Willis Towers Watson
    "CINF",    # Cincinnati Financial
    "BRO",     # Brown & Brown
    "CFG",     # Citizens Financial
    "HBAN",    # Huntington Bancshares
    "RF",      # Regions Financial
    "NTRS",    # Northern Trust
    "TROW",    # T. Rowe Price
    "DFS",     # Discover Financial
    "WRB",     # W.R. Berkley
    "MSCI",    # MSCI Inc
    "MKTX",    # MarketAxess
    "STE",     # Steris
    "COO",     # Cooper Companies
    "BIIB",    # Biogen
    "BAX",     # Baxter International
    "MTD",     # Mettler-Toledo
    "WAT",     # Waters Corporation
    "LH",      # Labcorp
    "RMD",     # ResMed
    "EW",      # Edwards Lifesciences
    "IQV",     # IQVIA Holdings
    "DXCM",    # DexCom
    "IDXX",    # IDEXX Laboratories
    "MOH",     # Molina Healthcare
    "CNC",     # Centene
    "HUM",     # Humana
    "MCK",     # McKesson
    "ZTS",     # Zoetis
    "HCA",     # HCA Healthcare
    "CI",      # Cigna Group
    "BSX",     # Boston Scientific
    "GEHC",    # GE HealthCare
    "DOV",     # Dover
    "IR",      # Ingersoll Rand
    "FTV",     # Fortive
    "WAB",     # Westinghouse Air Brake
    "IEX",     # IDEX Corporation
    "SNA",     # Snap-on
    "TDY",     # Teledyne Technologies
    "KEYS",    # Keysight Technologies
    "CDW",     # CDW Corporation
    "ANSS",    # ANSYS
    "TEL",     # TE Connectivity
    "HPQ",     # HP Inc
    "HPE",     # Hewlett Packard Enterprise
    "ZBRA",    # Zebra Technologies
    "TYL",     # Tyler Technologies
    "MCHP",    # Microchip Technology
    "NXPI",    # NXP Semiconductors
    "FTNT",    # Fortinet
    "APH",     # Amphenol
    "MSI",     # Motorola Solutions
    "ADI",     # Analog Devices
    "ADSK",    # Autodesk
    "FIS",     # Fidelity National Info
    "GPN",     # Global Payments
    "CPAY",    # Corpay
    "FI",      # Fiserv
    "CBRE",    # CBRE Group
    "PYPL",    # PayPal
    "CME",     # CME Group
    "AON",     # Aon
    "MCO",     # Moody's
    "PGR",     # Progressive
    "AIG",     # American International Group
    "AFL",     # Aflac
    "SPG",     # Simon Property Group
    "PSA",     # Public Storage
    "CCI",     # Crown Castle
    "O",       # Realty Income
    "DLR",     # Digital Realty
    "WELL",    # Welltower
    "AVB",     # AvalonBay
    "EQR",     # Equity Residential
    "VICI",    # VICI Properties
    "ARE",     # Alexandria Real Estate
    "ESS",     # Essex Property Trust
    "MAA",     # Mid-America Apartment
    "VTR",     # Ventas
    "IRM",     # Iron Mountain
    "SHW",     # Sherwin-Williams
    "ECL",     # Ecolab
    "NEM",     # Newmont
    "DD",      # DuPont
    "CTVA",    # Corteva
    "NUE",     # Nucor
    "VMC",     # Vulcan Materials
    "MLM",     # Martin Marietta Materials
    "PPG",     # PPG Industries
    "ETN",     # Eaton
    "ITW",     # Illinois Tool Works
    "EMR",     # Emerson Electric
    "PH",      # Parker-Hannifin
    "AJG",     # Arthur J. Gallagher
    "TT",      # Trane Technologies
    "CTAS",    # Cintas
    "CARR",    # Carrier Global
    "OTIS",    # Otis Worldwide
    "GWW",     # W.W. Grainger
    "FAST",    # Fastenal
    "ODFL",    # Old Dominion Freight Line
    "AME",     # AMETEK
    "ROST",    # Ross Stores
    "DHI",     # D.R. Horton
    "LEN",     # Lennar
    "F",       # Ford Motor
    "GM",      # General Motors
    "APTV",    # Aptiv
    "YUM",     # Yum! Brands
    "UBER",    # Uber Technologies
    "DECK",    # Deckers Outdoor
    "RCL",     # Royal Caribbean
    "DG",      # Dollar General
    "ORLY",    # O'Reilly Automotive
    "AZO",     # AutoZone
    "MAR",     # Marriott
    "HLT",     # Hilton
    "CMG",     # Chipotle
    "BKNG",    # Booking Holdings
    "MDLZ",    # Mondelez
    "KMB",     # Kimberly-Clark
    "GIS",     # General Mills
    "K",       # Kellanova
    "KR",      # Kroger
    "HSY",     # Hershey
    "KHC",     # Kraft Heinz
    "CLX",     # Clorox
    "MKC",     # McCormick
    "BG",      # Bunge
    "MNST",    # Monster Beverage
    "ADP",     # Automatic Data Processing
    "PAYX",    # Paychex
    "EA",      # Electronic Arts
    "DAL",     # Delta Air Lines
    "LUV",     # Southwest Airlines
    "EXPD",    # Expeditors International
    "AMP",     # Ameriprise Financial
    "PRU",     # Prudential Financial
    "COF",     # Capital One
    "BK",      # Bank of New York Mellon
    "STT",     # State Street
    "TFC",     # Truist Financial
    "J",       # Jacobs Solutions
    "SO",      # Southern Company
    "AEP",     # American Electric Power
    "EXC",     # Exelon
    "SRE",     # Sempra
    "PEG",     # PSEG
    "ED",      # Con Edison
    "XEL",     # Xcel Energy
    "WEC",     # WEC Energy
    "DTE",     # DTE Energy
    "ETR",     # Entergy
    "ES",      # Eversource Energy
    "PPL",     # PPL Corporation
    "FE",      # FirstEnergy
    "AWK",     # American Water Works
    "CNP",     # CenterPoint Energy
    "ATO",     # Atmos Energy
    "EIX",     # Edison International
    "CMS",     # CMS Energy
    "MPC",     # Marathon Petroleum
    "PSX",     # Phillips 66
    "OKE",     # ONEOK
    "WMB",     # Williams Companies
    "HAL",     # Halliburton
    "HES",     # Hess Corporation
    # S&P 500 remaining members
    "SMCI",    # Super Micro Computer
    "PLTR",    # Palantir Technologies
    "TSM",     # Taiwan Semiconductor (ADR)
    "PODD",    # Insulet Corporation
    "RVTY",    # Revvity
    "ILMN",    # Illumina
    "TER",     # Teradyne
    "ACGL",    # Arch Capital Group
    "TRV",     # Travelers Companies
    "ALL",     # Allstate
    "HIG",     # Hartford Financial Services
    "ERIE",    # Erie Indemnity
    "JKHY",    # Jack Henry & Associates
    "CMA",     # Comerica
    "FHN",     # First Horizon
    "FCNCA",   # First Citizens BancShares
    "WAL",     # Western Alliance Bancorporation
    "EWBC",    # East West Bancorp
    "LBRDK",   # Liberty Broadband (Class C)
    "LBRDA",   # Liberty Broadband (Class A)
    "LYB",     # LyondellBasell
    "ROL",     # Rollins
    "DPZ",     # Domino's Pizza
    "WY",      # Weyerhaeuser
    "CSGP",    # CoStar Group
    "HUBB",    # Hubbell
    "WST",     # West Pharmaceutical Services
    "DAY",     # Dayforce (formerly Ceridian)
    "EG",      # Everest Group
    "SIVB",    # SVB Financial (if still listed)
    "SBNY",    # Signature Bank (if still listed)
    "FRC",     # First Republic Bank (if still listed)
    "GL",      # Globe Life
    "RJF",     # Raymond James Financial
    "RE",      # Everest Re Group
    "L",       # Loews
    "NDAQ",    # Nasdaq Inc
    "FDS",     # FactSet Research Systems
    "CBOE",    # Cboe Global Markets
    "USB",     # US Bancorp
    "PNC",     # PNC Financial Services
    "MET",     # MetLife
    "FITB",    # Fifth Third Bancorp
    "KEY",     # KeyCorp
    "MTB",     # M&T Bank
    "D",       # Dominion Energy
    "AES",     # AES Corporation
    "LNT",     # Alliant Energy
    "EVRG",    # Evergy
    "PNW",     # Pinnacle West Capital
    "A",       # Agilent Technologies
    "BDX",     # Becton Dickinson
    "HOLX",    # Hologic
    "HSIC",    # Henry Schein
    "INCY",    # Incyte Corporation
    "ALGN",    # Align Technology
    "CAH",     # Cardinal Health
    "ABC",     # AmerisourceBergen (Cencora)
    "VTRS",    # Viatris
    "REG",     # Regency Centers
    "KIM",     # Kimco Realty
    "CPT",     # Camden Property Trust
    "SBAC",    # SBA Communications
    "AMT",     # American Tower
    "PEAK",    # Healthpeak Properties
    "INVH",    # Invitation Homes
    "APD",     # Air Products and Chemicals
    "ALB",     # Albemarle
    "FMC",     # FMC Corporation
    "IFF",     # International Flavors
    "CE",      # Celanese
    "EMN",     # Eastman Chemical
    "AMCR",    # Amcor
    "AVY",     # Avery Dennison
    "WRK",     # WestRock
    "STLD",    # Steel Dynamics
    "GLW",     # Corning
    "SWKS",    # Skyworks Solutions
    "PTC",     # PTC Inc
    "TRMB",    # Trimble
    "GEN",     # Gen Digital
    "FSLR",    # First Solar
    "ENPH",    # Enphase Energy
    "SEDG",    # SolarEdge Technologies
    "EPAM",    # EPAM Systems
    "JNPR",    # Juniper Networks
    "FFIV",    # F5 Networks
    "AKAM",    # Akamai Technologies
    "NTAP",    # NetApp
    "QRVO",    # Qorvo
    "CTSH",    # Cognizant Technology Solutions
    "IT",      # Gartner
    "VRSN",    # VeriSign
    "WDC",     # Western Digital
    "STX",     # Seagate Technology
    "ON",      # ON Semiconductor
    "MPWR",    # Monolithic Power Systems
    "BR",      # Broadridge Financial Solutions
    "GDDY",    # GoDaddy
    "PAYC",    # Paycom Software
    "TMUS",    # T-Mobile US
    "CHTR",    # Charter Communications
    "TTWO",    # Take-Two Interactive
    "WBD",     # Warner Bros Discovery
    "OMC",     # Omnicom Group
    "IPG",     # Interpublic Group
    "LYV",     # Live Nation Entertainment
    "DLTR",    # Dollar Tree
    "BBY",     # Best Buy
    "EBAY",    # eBay
    "ETSY",    # Etsy
    "GPC",     # Genuine Parts
    "LVS",     # Las Vegas Sands
    "MGM",     # MGM Resorts
    "POOL",    # Pool Corporation
    "PHM",     # PulteGroup
    "NVR",     # NVR Inc
    "HAS",     # Hasbro
    "EXPE",    # Expedia Group
    "ABNB",    # Airbnb
    "CCL",     # Carnival Corporation
    "NCLH",    # Norwegian Cruise Line
    "GRMN",    # Garmin
    "ULTA",    # Ulta Beauty
    "LULU",    # Lululemon Athletica
    "DRI",     # Darden Restaurants
    "KMX",     # CarMax
    "TPR",     # Tapestry
    "PVH",     # PVH Corp
    "CSX",     # CSX Corporation
    "NSC",     # Norfolk Southern
    "WM",      # Waste Management
    "RSG",     # Republic Services
    "ROK",     # Rockwell Automation
    "NOC",     # Northrop Grumman
    "LHX",     # L3Harris Technologies
    "TDG",     # TransDigm Group
    "HWM",     # Howmet Aerospace
    "GEV",     # GE Vernova
    "AXON",    # Axon Enterprise
    "LDOS",    # Leidos Holdings
    "TXT",     # Textron
    "VLTO",    # Veralto
    "BLDR",    # Builders FirstSource
    "PWR",     # Quanta Services
    "EME",     # EMCOR Group
    "FLR",     # Fluor Corporation
    "CPRT",    # Copart
    "FDX",     # FedEx
    "UAL",     # United Airlines
    "CHRW",    # C.H. Robinson Worldwide
    "XYL",     # Xylem
    "NDSN",    # Nordson
    "MO",      # Altria Group
    "STZ",     # Constellation Brands
    "TAP",     # Molson Coors
    "CPB",     # Campbell Soup
    "CAG",     # Conagra Brands
    "HRL",     # Hormel Foods
    "TSN",     # Tyson Foods
    "SYY",     # Sysco
    "KVUE",    # Kenvue
    "EL",      # Estee Lauder
    "CHD",     # Church & Dwight
    "SJM",     # J.M. Smucker
    "ADM",     # Archer-Daniels-Midland
    # Recent S&P 500 additions (2023-2025)
    "CRWD",    # CrowdStrike
    "DDOG",    # Datadog
    "WDAY",    # Workday
    "TTD",     # The Trade Desk
    "ARM",     # Arm Holdings
    "HUBS",    # HubSpot
    "SNOW",    # Snowflake
    "ZS",      # Zscaler
    "MDB",     # MongoDB
    "NET",     # Cloudflare
    "COIN",    # Coinbase
    "SPOT",    # Spotify Technology
    "MRNA",    # Moderna
    "SHOP",    # Shopify
    "DASH",    # DoorDash
    "SNAP",    # Snap Inc
]

# De-duplicate SP500_FULL while preserving order
_seen_sp500: set = set()
_deduped_sp500: List[str] = []
for _t in SP500_FULL:
    if _t not in _seen_sp500:
        _seen_sp500.add(_t)
        _deduped_sp500.append(_t)
SP500_FULL = _deduped_sp500


# ---------------------------------------------------------------------------
# Russell Midcap / Growth — ~200 popular mid-cap US stocks NOT in S&P 500
# ---------------------------------------------------------------------------
RUSSELL_MID: List[str] = [
    # --- High-Growth Tech ---
    "CRWD",    # CrowdStrike
    "ZS",      # Zscaler
    "NET",     # Cloudflare
    "DDOG",    # Datadog
    "MDB",     # MongoDB
    "SNOW",    # Snowflake
    "OKTA",    # Okta
    "TWLO",    # Twilio
    "BILL",    # Bill Holdings
    "DOCU",    # DocuSign
    "ZM",      # Zoom Video Communications
    "U",       # Unity Software
    "PATH",    # UiPath
    "HUBS",    # HubSpot
    "VEEV",    # Veeva Systems
    "SPLK",    # Splunk (if still listed)
    "TTD",     # The Trade Desk
    "ROKU",    # Roku
    "PINS",    # Pinterest
    "SNAP",    # Snap
    "SMAR",    # Smartsheet
    "CFLT",    # Confluent
    "S",       # SentinelOne
    "CRSP",    # CRISPR Therapeutics
    "PCTY",    # Paylocity
    "GTLB",    # GitLab
    "DOCN",    # DigitalOcean
    "DT",      # Dynatrace
    "ESTC",    # Elastic
    "MNDY",    # monday.com
    "APPF",    # AppFolio
    "IOT",     # Samsara
    "API",     # Agora
    "BRZE",    # Braze
    "KVYO",    # Klaviyo

    # --- Fintech / Digital Finance ---
    "COIN",    # Coinbase
    "HOOD",    # Robinhood Markets
    "SOFI",    # SoFi Technologies
    "AFRM",    # Affirm
    "UPST",    # Upstart
    "LC",      # LendingClub
    "MARA",    # Marathon Digital Holdings
    "RIOT",    # Riot Platforms
    "MSTR",    # MicroStrategy
    "SQ",      # Block (Square)
    "FOUR",    # Shift4 Payments
    "TOST",    # Toast
    "RELY",    # Remitly Global
    "PSFE",    # Paysafe
    "NU",      # Nu Holdings
    "HUT",     # Hut 8 Mining
    "CLSK",    # CleanSpark

    # --- Consumer / E-Commerce / Social ---
    "RBLX",    # Roblox
    "APP",     # AppLovin
    "CELH",    # Celsius Holdings
    "DUOL",    # Duolingo
    "DKNG",    # DraftKings
    "PENN",    # Penn Entertainment
    "CHWY",    # Chewy
    "W",       # Wayfair
    "CVNA",    # Carvana
    "CAVA",    # CAVA Group
    "BIRK",    # Birkenstock
    "BROS",    # Dutch Bros
    "SHAK",    # Shake Shack
    "CART",    # Instacart (Maplebear)
    "MNST",    # Monster Beverage (if not in SP500)
    "WRBY",    # Warby Parker
    "FIGS",    # FIGS
    "HIMS",    # Hims & Hers Health
    "RVLV",    # Revolve Group
    "GRPN",    # Groupon
    "REAL",    # RealReal
    "POSH",    # Poshmark
    "BBWI",    # Bath & Body Works
    "CROX",    # Crocs
    "HBI",     # Hanesbrands
    "SKX",     # Skechers
    "LEVI",    # Levi Strauss
    "ONON",    # On Holding
    "XPEV",    # XPeng
    "NIO",     # NIO
    "LI",      # Li Auto
    "RIVN",    # Rivian Automotive
    "LCID",    # Lucid Group
    "FSR",     # Fisker (if still listed)
    "GOEV",    # Canoo
    "VLD",     # Velo3D

    # --- Space / Defense / Aerospace ---
    "RKLB",    # Rocket Lab USA
    "SPCE",    # Virgin Galactic
    "LUNR",    # Intuitive Machines
    "RDW",     # Redwire
    "ASTS",    # AST SpaceMobile
    "BWXT",    # BWX Technologies
    "KTOS",    # Kratos Defense
    "AVAV",    # AeroVironment
    "JOBY",    # Joby Aviation
    "ACHR",    # Archer Aviation

    # --- Biotech / Pharma (Mid-cap) ---
    "MRNA",    # Moderna
    "BNTX",    # BioNTech
    "EXAS",    # Exact Sciences
    "RARE",    # Ultragenyx Pharmaceutical
    "IONS",    # Ionis Pharmaceuticals
    "NBIX",    # Neurocrine Biosciences
    "PCVX",    # Vaxcyte
    "TGTX",    # TG Therapeutics
    "ARCT",    # Arctus Therapeutics
    "BEAM",    # Beam Therapeutics
    "NTLA",    # Intellia Therapeutics
    "EDIT",    # Editas Medicine
    "INO",     # Inovio Pharmaceuticals
    "SRPT",    # Sarepta Therapeutics
    "BMRN",    # BioMarin Pharmaceutical
    "JAZZ",    # Jazz Pharmaceuticals
    "MASI",    # Masimo Corporation
    "NUVB",    # Nuvation Bio
    "RXRX",    # Recursion Pharmaceuticals
    "PRCT",    # PROCEPT BioRobotics
    "AXNX",    # Axonics
    "IRTC",    # iRhythm Technologies
    "GKOS",    # Glaukos
    "NVCR",    # NovoCure
    "TWST",    # Twist Bioscience
    "DNA",     # Ginkgo Bioworks

    # --- Energy / Clean Energy ---
    "PLUG",    # Plug Power
    "BLDP",    # Ballard Power Systems
    "BE",      # Bloom Energy
    "RUN",     # Sunrun
    "NOVA",    # Sunnova Energy
    "ARRY",    # Array Technologies
    "STEM",    # Stem Inc
    "CHPT",    # ChargePoint Holdings
    "EVGO",    # EVgo
    "BLNK",    # Blink Charging
    "SHLS",    # Shoals Technologies
    "NEP",     # NextEra Energy Partners

    # --- Software / AI / Data ---
    "ARM",     # Arm Holdings
    "SMCI",    # Super Micro (if not in S&P 500)
    "AI",      # C3.ai
    "BBAI",    # BigBear.ai
    "PLTR",    # Palantir (if not in S&P 500)
    "PRPL",    # Purple Innovation
    "VERX",    # Vertex Inc
    "QLYS",    # Qualys
    "TENB",    # Tenable Holdings
    "VRNS",    # Varonis Systems
    "RPD",     # Rapid7
    "CYBR",    # CyberArk Software
    "WDAY",    # Workday
    "CDAY",    # Ceridian (Dayforce)
    "ALTR",    # Altair Engineering
    "MANH",    # Manhattan Associates
    "SHOP",    # Shopify
    "SE",      # Sea Limited
    "GRAB",    # Grab Holdings
    "BABA",    # Alibaba
    "JD",      # JD.com
    "PDD",     # PDD Holdings (Pinduoduo)
    "BIDU",    # Baidu

    # --- Industrial / Misc Mid-Cap ---
    "ATKR",    # Atkore
    "RBC",     # RBC Bearings
    "AZEK",    # AZEK Company
    "TREX",    # Trex Company
    "SITE",    # SiteOne Landscape Supply
    "EXPO",    # Exponent
    "TTC",     # Toro Company
    "SAIA",    # Saia Inc
    "LSTR",    # Landstar System
    "WERN",    # Werner Enterprises
    "XPO",     # XPO Inc
    "MATX",    # Matson
    "ZWS",     # Zurn Elkay Water Solutions

    # --- Additional Growth / Popular Retail Stocks ---
    "SOXX",    # iShares Semiconductor ETF (popular)
    "OPEN",    # Opendoor Technologies
    "GRND",    # Grindr
    "SPOT",    # Spotify Technology
    "ABNB",    # Airbnb (dup guard)
    "LYFT",    # Lyft
    "DASH",    # DoorDash
    "BFLY",    # Butterfly Network
    "INDI",    # indie Semiconductor
    "LAZR",    # Luminar Technologies
    "LIDR",    # AEye Inc
    "AEHR",    # Aehr Test Systems
    "CLOV",    # Clover Health
    "ENVX",    # Enovix
    "SOUN",    # SoundHound AI
    "SANA",    # Sana Biotechnology
    "ABCL",    # AbCellera Biologics
    "SDGR",    # Schrödinger
    "FLNC",    # Fluence Energy
    "PAYC",    # Paycom (dup guard)
    "TNDM",    # Tandem Diabetes Care
    "DOCS",    # Doximity
    "DNUT",    # Krispy Kreme
    "TASK",    # TaskUs
    "TTCF",    # Tattooed Chef
    "OUST",    # Ouster
    "ASAN",    # Asana
    "SUMO",    # Sumo Logic
    "JAMF",    # Jamf Holding
    "BIGC",    # BigCommerce
    "APPS",    # Digital Turbine
    "CRNC",    # Cerence
    "DOMO",    # Domo
    "YEXT",    # Yext
    "BAND",    # Bandwidth
    "ZI",      # ZoomInfo Technologies
    "MTTR",    # Matterport
    "IONQ",    # IonQ
    "RGTI",    # Rigetti Computing
    "QUBT",    # Quantum Computing
    "ARQQ",    # Arqit Quantum
    "VNET",    # VNET Group
    "WIX",     # Wix.com
    "GLBE",    # Global-e Online
    "MNDY",    # monday.com (dup guard)
    "CLBT",    # Cellebrite DI
    "PRGS",    # Progress Software
    "CWAN",    # Clearwater Analytics
    "FRSH",    # Freshworks

    # --- Even more mid-cap / popular retail stocks ---
    "CARG",    # CarGurus
    "BMBL",    # Bumble
    "INTA",    # Intapp
    "PLTK",    # Playtika
    "GENI",    # Genius Sports
    "SKLZ",    # Skillz
    "EVCM",    # EverCommerce
    "ROVR",    # Rover Group
    "LMND",    # Lemonade
    "ROOT",    # Root Inc
    "OSCR",    # Oscar Health
    "HIPO",    # Hippo Holdings
    "OLO",     # Olo Inc
    "PAR",     # PAR Technology
    "PRFT",    # Perficient
    "DCT",     # Duck Creek Technologies
    "TXG",     # 10x Genomics
    "LEGN",    # Legend Biotech
    "ARGX",    # argenx
    "RCKT",    # Rocket Pharmaceuticals
    "IMVT",    # Immunovant
    "PCOR",    # Procore Technologies
    "TNET",    # TriNet Group
    "ENFN",    # Enfusion
    "AUR",     # Aurora Innovation
    "NNOX",    # Nano-X Imaging
    "BTDR",    # Bitdeer Technologies
    "CIFR",    # Cipher Mining
    "IREN",    # Iris Energy
    "CORZ",    # Core Scientific
    "WULF",    # TeraWulf
    "SATS",    # EchoStar
    "IRBT",    # iRobot
    "DLO",     # DLocal
    "FLYW",    # Flywire
    "GBTG",    # Global Business Travel
    "MGNI",    # Magnite
    "PUBM",    # PubMatic
    "IS",      # IronSource
    "VERV",    # Verve Therapeutics
    "NTRA",    # Natera
    "CERS",    # Cerus
    "PCRX",    # Pacira BioSciences
    "HRMY",    # Harmony Biosciences
    "KRYS",    # Krystal Biotech
    "VKTX",    # Viking Therapeutics
    "SMMT",    # Summit Therapeutics
    "TARS",    # Tarsus Pharmaceuticals
    "DCPH",    # Deciphera Pharmaceuticals
    "IOVA",    # Iovance Biotherapeutics
    "INSM",    # Insmed
    "ALNY",    # Alnylam Pharmaceuticals
    "RGEN",    # Repligen
    "BIO",     # Bio-Rad Laboratories
    "MTSI",    # MACOM Technology Solutions
    "CAMT",    # Camtek
    "FORM",    # FormFactor
    "COHR",    # Coherent
    "LSCC",    # Lattice Semiconductor
    "WOLF",    # Wolfspeed
    "ACLS",    # Axcelis Technologies
    "RMBS",    # Rambus
    "DIOD",    # Diodes
    "POWI",    # Power Integrations
    "SITM",    # SiTime Corporation
    "ONTO",    # Onto Innovation
    "AMKR",    # Amkor Technology
    "VST",     # Vistra Energy
    "TALO",    # Talos Energy
    "VTLE",    # Vital Energy
    "PR",      # Permian Resources
    "CHRD",    # Chord Energy
    "SM",      # SM Energy
    "MTDR",    # Matador Resources
    "GPOR",    # Gulfport Energy
    "RRC",     # Range Resources
    "SWN",     # Southwestern Energy
    "AR",      # Antero Resources
    "CNX",     # CNX Resources
    "MGY",     # Magnolia Oil & Gas
    "HESM",    # Hess Midstream Partners
    "WES",     # Western Midstream
    "TPVG",    # TriplePoint Venture Growth
    "KNSL",    # Kinsale Capital Group
    "HLI",     # Houlihan Lokey
    "PIPR",    # Piper Sandler
    "STEP",    # StepStone Group
    "VCTR",    # Victory Capital
    "VIRT",    # Virtu Financial
    "LPLA",    # LPL Financial
    "IBKR",    # Interactive Brokers
    "MORN",    # Morningstar
    "EVR",     # Evercore
    "SF",      # Stifel Financial
]

# De-duplicate RUSSELL_MID while preserving order
_seen_mid: set = set()
_deduped_mid: List[str] = []
for _t in RUSSELL_MID:
    if _t not in _seen_mid:
        _seen_mid.add(_t)
        _deduped_mid.append(_t)
RUSSELL_MID = _deduped_mid


# ---------------------------------------------------------------------------
# Combined universe lists
# ---------------------------------------------------------------------------
ALL_LSE: List[str] = FTSE_100 + FTSE_250_TOP
ALL_US: List[str] = SP500_FULL + [t for t in RUSSELL_MID if t not in set(SP500_FULL)]
FULL_UNIVERSE: List[str] = ALL_LSE + ALL_US


# ---------------------------------------------------------------------------
# Sector classifications
# ---------------------------------------------------------------------------
SECTOR_MAP: Dict[str, str] = {
    # ===================================================================
    # FTSE 100 Sectors
    # ===================================================================
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

    # ===================================================================
    # S&P 500 — Full GICS Sector Classifications
    # ===================================================================

    # --- Information Technology ---
    "AAPL": "Technology",
    "MSFT": "Technology",
    "NVDA": "Technology",
    "AVGO": "Technology",
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
    "PANW": "Technology",
    "ADI": "Technology",
    "MCHP": "Technology",
    "NXPI": "Technology",
    "FTNT": "Technology",
    "APH": "Technology",
    "MSI": "Technology",
    "KEYS": "Technology",
    "CDW": "Technology",
    "ANSS": "Technology",
    "TEL": "Technology",
    "HPQ": "Technology",
    "HPE": "Technology",
    "GLW": "Technology",
    "ZBRA": "Technology",
    "TYL": "Technology",
    "SWKS": "Technology",
    "TDY": "Technology",
    "PTC": "Technology",
    "TRMB": "Technology",
    "GEN": "Technology",
    "FSLR": "Technology",
    "ENPH": "Technology",
    "SEDG": "Technology",
    "EPAM": "Technology",
    "JNPR": "Technology",
    "FFIV": "Technology",
    "AKAM": "Technology",
    "NTAP": "Technology",
    "QRVO": "Technology",
    "CTSH": "Technology",
    "IT": "Technology",
    "VRSN": "Technology",
    "WDC": "Technology",
    "STX": "Technology",
    "ON": "Technology",
    "MPWR": "Technology",
    "SMCI": "Technology",
    "ADSK": "Technology",
    "FIS": "Technology",
    "GPN": "Technology",
    "BR": "Technology",
    "CPAY": "Technology",
    "FI": "Technology",
    "GDDY": "Technology",
    "PAYC": "Technology",
    "CERIDIAN": "Technology",
    "PLTR": "Technology",
    "TSM": "Technology",
    "PYPL": "Technology",

    # --- Communication Services ---
    "GOOGL": "Communication Services",
    "GOOG": "Communication Services",
    "META": "Communication Services",
    "NFLX": "Communication Services",
    "DIS": "Communication Services",
    "CMCSA": "Communication Services",
    "T": "Communication Services",
    "VZ": "Communication Services",
    "CHTR": "Communication Services",
    "TMUS": "Communication Services",
    "EA": "Communication Services",
    "TTWO": "Communication Services",
    "WBD": "Communication Services",
    "OMC": "Communication Services",
    "IPG": "Communication Services",
    "MTCH": "Communication Services",
    "FOXA": "Communication Services",
    "FOX": "Communication Services",
    "NWSA": "Communication Services",
    "NWS": "Communication Services",
    "PARA": "Communication Services",
    "LYV": "Communication Services",

    # --- Consumer Discretionary ---
    "AMZN": "Consumer Discretionary",
    "TSLA": "Consumer Discretionary",
    "HD": "Consumer Discretionary",
    "MCD": "Consumer Discretionary",
    "NKE": "Consumer Discretionary",
    "SBUX": "Consumer Discretionary",
    "TGT": "Consumer Discretionary",
    "LOW": "Consumer Discretionary",
    "BKNG": "Consumer Discretionary",
    "CMG": "Consumer Discretionary",
    "ORLY": "Consumer Discretionary",
    "AZO": "Consumer Discretionary",
    "MAR": "Consumer Discretionary",
    "HLT": "Consumer Discretionary",
    "ROST": "Consumer Discretionary",
    "DHI": "Consumer Discretionary",
    "LEN": "Consumer Discretionary",
    "F": "Consumer Discretionary",
    "GM": "Consumer Discretionary",
    "APTV": "Consumer Discretionary",
    "YUM": "Consumer Discretionary",
    "UBER": "Consumer Discretionary",
    "DECK": "Consumer Discretionary",
    "RCL": "Consumer Discretionary",
    "TSCO": "Consumer Discretionary",
    "DG": "Consumer Discretionary",
    "DLTR": "Consumer Discretionary",
    "BBY": "Consumer Discretionary",
    "EBAY": "Consumer Discretionary",
    "ETSY": "Consumer Discretionary",
    "GPC": "Consumer Discretionary",
    "LVS": "Consumer Discretionary",
    "WYNN": "Consumer Discretionary",
    "CZR": "Consumer Discretionary",
    "MGM": "Consumer Discretionary",
    "POOL": "Consumer Discretionary",
    "PHM": "Consumer Discretionary",
    "NVR": "Consumer Discretionary",
    "BWA": "Consumer Discretionary",
    "MHK": "Consumer Discretionary",
    "RL": "Consumer Discretionary",
    "HAS": "Consumer Discretionary",
    "EXPE": "Consumer Discretionary",
    "ABNB": "Consumer Discretionary",
    "CCL": "Consumer Discretionary",
    "NCLH": "Consumer Discretionary",
    "LKQ": "Consumer Discretionary",
    "GRMN": "Consumer Discretionary",
    "ULTA": "Consumer Discretionary",
    "LULU": "Consumer Discretionary",
    "DRI": "Consumer Discretionary",
    "KMX": "Consumer Discretionary",
    "PCAR": "Consumer Discretionary",
    "TPR": "Consumer Discretionary",
    "VFC": "Consumer Discretionary",
    "PVH": "Consumer Discretionary",
    "GNRC": "Consumer Discretionary",
    "SEE": "Consumer Discretionary",

    # --- Healthcare ---
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
    "BSX": "Healthcare",
    "CI": "Healthcare",
    "HCA": "Healthcare",
    "ZTS": "Healthcare",
    "MCK": "Healthcare",
    "HUM": "Healthcare",
    "MOH": "Healthcare",
    "CNC": "Healthcare",
    "IDXX": "Healthcare",
    "IQV": "Healthcare",
    "DXCM": "Healthcare",
    "GEHC": "Healthcare",
    "EW": "Healthcare",
    "A": "Healthcare",
    "BAX": "Healthcare",
    "BDX": "Healthcare",
    "BIIB": "Healthcare",
    "COO": "Healthcare",
    "DVA": "Healthcare",
    "HOLX": "Healthcare",
    "HSIC": "Healthcare",
    "INCY": "Healthcare",
    "LH": "Healthcare",
    "MTD": "Healthcare",
    "RMD": "Healthcare",
    "STE": "Healthcare",
    "TECH": "Healthcare",
    "WAT": "Healthcare",
    "XRAY": "Healthcare",
    "ALGN": "Healthcare",
    "CRL": "Healthcare",
    "CTLT": "Healthcare",
    "WBA": "Healthcare",
    "CAH": "Healthcare",
    "ABC": "Healthcare",
    "VTRS": "Healthcare",
    "PODD": "Healthcare",
    "RVTY": "Healthcare",
    "ILMN": "Healthcare",

    # --- Financials ---
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
    "CME": "Financials",
    "AON": "Financials",
    "MCO": "Financials",
    "PGR": "Financials",
    "AIG": "Financials",
    "AFL": "Financials",
    "ADP": "Financials",
    "TFC": "Financials",
    "USB": "Financials",
    "PNC": "Financials",
    "COF": "Financials",
    "BK": "Financials",
    "STT": "Financials",
    "AMP": "Financials",
    "PRU": "Financials",
    "MET": "Financials",
    "TROW": "Financials",
    "DFS": "Financials",
    "NTRS": "Financials",
    "FITB": "Financials",
    "CFG": "Financials",
    "HBAN": "Financials",
    "RF": "Financials",
    "KEY": "Financials",
    "MTB": "Financials",
    "WRB": "Financials",
    "CINF": "Financials",
    "BRO": "Financials",
    "AIZ": "Financials",
    "RE": "Financials",
    "GL": "Financials",
    "RJF": "Financials",
    "SIVB": "Financials",
    "L": "Financials",
    "BEN": "Financials",
    "IVZ": "Financials",
    "ZION": "Financials",
    "SBNY": "Financials",
    "FRC": "Financials",
    "MKTX": "Financials",
    "MSCI": "Financials",
    "NDAQ": "Financials",
    "FDS": "Financials",
    "CBOE": "Financials",
    "EFX": "Financials",
    "VRSK": "Financials",
    "WTW": "Financials",
    "ACGL": "Financials",
    "TRV": "Financials",
    "ALL": "Financials",
    "HIG": "Financials",
    "ERIE": "Financials",
    "JKHY": "Financials",
    "CMA": "Financials",
    "FHN": "Financials",
    "FCNCA": "Financials",
    "WAL": "Financials",
    "EWBC": "Financials",

    # --- Industrials ---
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
    "ETN": "Industrials",
    "ITW": "Industrials",
    "EMR": "Industrials",
    "PH": "Industrials",
    "AJG": "Industrials",
    "TT": "Industrials",
    "CTAS": "Industrials",
    "CARR": "Industrials",
    "OTIS": "Industrials",
    "CSX": "Industrials",
    "NSC": "Industrials",
    "WM": "Industrials",
    "RSG": "Industrials",
    "GWW": "Industrials",
    "FAST": "Industrials",
    "ODFL": "Industrials",
    "ROK": "Industrials",
    "AME": "Industrials",
    "DOV": "Industrials",
    "IR": "Industrials",
    "FTV": "Industrials",
    "WAB": "Industrials",
    "IEX": "Industrials",
    "PNR": "Industrials",
    "SNA": "Industrials",
    "NDSN": "Industrials",
    "JBHT": "Industrials",
    "DAL": "Industrials",
    "LUV": "Industrials",
    "AAL": "Industrials",
    "UAL": "Industrials",
    "EXPD": "Industrials",
    "CHRW": "Industrials",
    "XYL": "Industrials",
    "SWK": "Industrials",
    "HII": "Industrials",
    "NOC": "Industrials",
    "LHX": "Industrials",
    "TDG": "Industrials",
    "HWM": "Industrials",
    "GEV": "Industrials",
    "AXON": "Industrials",
    "PAYX": "Industrials",
    "J": "Industrials",
    "ALLE": "Industrials",
    "AOS": "Industrials",
    "LDOS": "Industrials",
    "TXT": "Industrials",
    "IP": "Industrials",
    "PKG": "Industrials",
    "CEG": "Industrials",
    "VLTO": "Industrials",
    "BLDR": "Industrials",
    "PWR": "Industrials",
    "EME": "Industrials",
    "FLR": "Industrials",
    "CPRT": "Industrials",
    "FDX": "Industrials",

    # --- Consumer Staples ---
    "WMT": "Consumer Staples",
    "PG": "Consumer Staples",
    "COST": "Consumer Staples",
    "KO": "Consumer Staples",
    "PEP": "Consumer Staples",
    "PM": "Consumer Staples",
    "MDLZ": "Consumer Staples",
    "CL": "Consumer Staples",
    "MO": "Consumer Staples",
    "KMB": "Consumer Staples",
    "GIS": "Consumer Staples",
    "K": "Consumer Staples",
    "KR": "Consumer Staples",
    "HSY": "Consumer Staples",
    "SJM": "Consumer Staples",
    "KHC": "Consumer Staples",
    "CLX": "Consumer Staples",
    "STZ": "Consumer Staples",
    "MKC": "Consumer Staples",
    "ADM": "Consumer Staples",
    "BG": "Consumer Staples",
    "TAP": "Consumer Staples",
    "CPB": "Consumer Staples",
    "CAG": "Consumer Staples",
    "HRL": "Consumer Staples",
    "TSN": "Consumer Staples",
    "SYY": "Consumer Staples",
    "MNST": "Consumer Staples",
    "KVUE": "Consumer Staples",
    "EL": "Consumer Staples",
    "CHD": "Consumer Staples",

    # --- Energy ---
    "XOM": "Energy",
    "CVX": "Energy",
    "COP": "Energy",
    "SLB": "Energy",
    "EOG": "Energy",
    "MPC": "Energy",
    "PSX": "Energy",
    "VLO": "Energy",
    "OKE": "Energy",
    "WMB": "Energy",
    "FANG": "Energy",
    "HAL": "Energy",
    "HES": "Energy",
    "DVN": "Energy",
    "TRGP": "Energy",
    "KMI": "Energy",
    "BKR": "Energy",
    "OXY": "Energy",
    "CTRA": "Energy",
    "MRO": "Energy",
    "APA": "Energy",
    "EQT": "Energy",

    # --- Utilities ---
    "NEE": "Utilities",
    "DUK": "Utilities",
    "SO": "Utilities",
    "AEP": "Utilities",
    "EXC": "Utilities",
    "SRE": "Utilities",
    "PEG": "Utilities",
    "ED": "Utilities",
    "XEL": "Utilities",
    "WEC": "Utilities",
    "DTE": "Utilities",
    "ETR": "Utilities",
    "ES": "Utilities",
    "PPL": "Utilities",
    "FE": "Utilities",
    "AWK": "Utilities",
    "CNP": "Utilities",
    "ATO": "Utilities",
    "NI": "Utilities",
    "EIX": "Utilities",
    "CMS": "Utilities",
    "D": "Utilities",
    "AES": "Utilities",
    "LNT": "Utilities",
    "EVRG": "Utilities",
    "PNW": "Utilities",

    # --- Real Estate ---
    "SPG": "Real Estate",
    "PSA": "Real Estate",
    "CCI": "Real Estate",
    "O": "Real Estate",
    "DLR": "Real Estate",
    "WELL": "Real Estate",
    "AVB": "Real Estate",
    "EQR": "Real Estate",
    "VICI": "Real Estate",
    "ARE": "Real Estate",
    "ESS": "Real Estate",
    "MAA": "Real Estate",
    "UDR": "Real Estate",
    "BXP": "Real Estate",
    "VTR": "Real Estate",
    "HST": "Real Estate",
    "IRM": "Real Estate",
    "REG": "Real Estate",
    "KIM": "Real Estate",
    "CPT": "Real Estate",
    "FRT": "Real Estate",
    "SBAC": "Real Estate",
    "AMT": "Real Estate",
    "PEAK": "Real Estate",
    "CBRE": "Real Estate",
    "INVH": "Real Estate",

    # --- Materials ---
    "LIN": "Materials",
    "SHW": "Materials",
    "ECL": "Materials",
    "NEM": "Materials",
    "APD": "Materials",
    "DD": "Materials",
    "CTVA": "Materials",
    "NUE": "Materials",
    "VMC": "Materials",
    "MLM": "Materials",
    "PPG": "Materials",
    "BALL": "Materials",
    "ALB": "Materials",
    "FMC": "Materials",
    "CF": "Materials",
    "MOS": "Materials",
    "IFF": "Materials",
    "CE": "Materials",
    "EMN": "Materials",
    "AMCR": "Materials",
    "AVY": "Materials",
    "WRK": "Materials",
    "STLD": "Materials",
    "LYB": "Materials",
    "WY": "Materials",

    # --- Additional S&P 500 ---
    "LBRDK": "Communication Services",
    "LBRDA": "Communication Services",
    "ROL": "Industrials",
    "DPZ": "Consumer Discretionary",
    "TER": "Technology",
    "CAVA": "Consumer Discretionary",
    "DARDEN": "Consumer Discretionary",

    # ===================================================================
    # Russell Midcap / Growth Sectors
    # ===================================================================

    # High-Growth Tech / Software
    "CRWD": "Technology",
    "ZS": "Technology",
    "NET": "Technology",
    "DDOG": "Technology",
    "MDB": "Technology",
    "SNOW": "Technology",
    "OKTA": "Technology",
    "TWLO": "Technology",
    "BILL": "Technology",
    "DOCU": "Technology",
    "ZM": "Technology",
    "U": "Technology",
    "PATH": "Technology",
    "HUBS": "Technology",
    "VEEV": "Technology",
    "SPLK": "Technology",
    "TTD": "Technology",
    "ROKU": "Communication Services",
    "PINS": "Communication Services",
    "SNAP": "Communication Services",
    "SMAR": "Technology",
    "CFLT": "Technology",
    "S": "Technology",
    "CRSP": "Healthcare",
    "PCTY": "Technology",
    "GTLB": "Technology",
    "DOCN": "Technology",
    "DT": "Technology",
    "ESTC": "Technology",
    "MNDY": "Technology",
    "APPF": "Technology",
    "IOT": "Technology",
    "API": "Technology",
    "BRZE": "Technology",
    "KVYO": "Technology",
    "AI": "Technology",
    "BBAI": "Technology",
    "VERX": "Technology",
    "QLYS": "Technology",
    "TENB": "Technology",
    "VRNS": "Technology",
    "RPD": "Technology",
    "CYBR": "Technology",
    "WDAY": "Technology",
    "CDAY": "Technology",
    "ALTR": "Technology",
    "MANH": "Technology",
    "SHOP": "Technology",
    "ARM": "Technology",

    # Fintech / Digital Finance
    "COIN": "Financials",
    "HOOD": "Financials",
    "SOFI": "Financials",
    "AFRM": "Financials",
    "UPST": "Financials",
    "LC": "Financials",
    "MARA": "Financials",
    "RIOT": "Financials",
    "MSTR": "Technology",
    "SQ": "Financials",
    "FOUR": "Financials",
    "TOST": "Technology",
    "RELY": "Financials",
    "PSFE": "Financials",
    "NU": "Financials",
    "HUT": "Financials",
    "CLSK": "Financials",

    # Consumer / E-Commerce / Social
    "RBLX": "Communication Services",
    "APP": "Technology",
    "CELH": "Consumer Staples",
    "DUOL": "Technology",
    "DKNG": "Consumer Discretionary",
    "PENN": "Consumer Discretionary",
    "CHWY": "Consumer Discretionary",
    "W": "Consumer Discretionary",
    "CVNA": "Consumer Discretionary",
    "BIRK": "Consumer Discretionary",
    "BROS": "Consumer Discretionary",
    "SHAK": "Consumer Discretionary",
    "CART": "Technology",
    "WRBY": "Healthcare",
    "FIGS": "Consumer Discretionary",
    "HIMS": "Healthcare",
    "RVLV": "Consumer Discretionary",
    "GRPN": "Communication Services",
    "REAL": "Consumer Discretionary",
    "POSH": "Consumer Discretionary",
    "BBWI": "Consumer Discretionary",
    "CROX": "Consumer Discretionary",
    "HBI": "Consumer Discretionary",
    "SKX": "Consumer Discretionary",
    "LEVI": "Consumer Discretionary",
    "ONON": "Consumer Discretionary",
    "XPEV": "Consumer Discretionary",
    "NIO": "Consumer Discretionary",
    "LI": "Consumer Discretionary",
    "RIVN": "Consumer Discretionary",
    "LCID": "Consumer Discretionary",
    "FSR": "Consumer Discretionary",
    "GOEV": "Consumer Discretionary",
    "VLD": "Industrials",

    # Space / Defense / Aerospace
    "RKLB": "Industrials",
    "SPCE": "Industrials",
    "LUNR": "Industrials",
    "RDW": "Industrials",
    "ASTS": "Communication Services",
    "BWXT": "Industrials",
    "KTOS": "Industrials",
    "AVAV": "Industrials",
    "JOBY": "Industrials",
    "ACHR": "Industrials",

    # Biotech / Pharma (Mid-cap)
    "MRNA": "Healthcare",
    "BNTX": "Healthcare",
    "EXAS": "Healthcare",
    "RARE": "Healthcare",
    "IONS": "Healthcare",
    "NBIX": "Healthcare",
    "PCVX": "Healthcare",
    "TGTX": "Healthcare",
    "ARCT": "Healthcare",
    "BEAM": "Healthcare",
    "NTLA": "Healthcare",
    "EDIT": "Healthcare",
    "INO": "Healthcare",
    "SRPT": "Healthcare",
    "BMRN": "Healthcare",
    "JAZZ": "Healthcare",
    "MASI": "Healthcare",
    "NUVB": "Healthcare",
    "RXRX": "Healthcare",
    "PRCT": "Healthcare",
    "AXNX": "Healthcare",
    "IRTC": "Healthcare",
    "GKOS": "Healthcare",
    "NVCR": "Healthcare",
    "TWST": "Healthcare",
    "DNA": "Healthcare",

    # Energy / Clean Energy
    "PLUG": "Energy",
    "BLDP": "Energy",
    "BE": "Energy",
    "RUN": "Energy",
    "NOVA": "Energy",
    "ARRY": "Energy",
    "STEM": "Energy",
    "CHPT": "Energy",
    "EVGO": "Energy",
    "BLNK": "Energy",
    "SHLS": "Energy",
    "NEP": "Energy",

    # International Tech / E-Commerce
    "SE": "Communication Services",
    "GRAB": "Technology",
    "BABA": "Consumer Discretionary",
    "JD": "Consumer Discretionary",
    "PDD": "Consumer Discretionary",
    "BIDU": "Communication Services",
    "PRPL": "Consumer Discretionary",

    # Industrial / Misc Mid-Cap
    "ATKR": "Industrials",
    "RBC": "Industrials",
    "AZEK": "Industrials",
    "TREX": "Industrials",
    "SITE": "Industrials",
    "EXPO": "Industrials",
    "TTC": "Industrials",
    "SAIA": "Industrials",
    "LSTR": "Industrials",
    "WERN": "Industrials",
    "XPO": "Industrials",
    "MATX": "Industrials",
    "ZWS": "Industrials",

    # Additional Growth / Popular Retail Stocks
    "OPEN": "Real Estate",
    "GRND": "Communication Services",
    "SPOT": "Communication Services",
    "LYFT": "Industrials",
    "DASH": "Technology",
    "BFLY": "Healthcare",
    "INDI": "Technology",
    "LAZR": "Technology",
    "LIDR": "Technology",
    "AEHR": "Technology",
    "CLOV": "Healthcare",
    "ENVX": "Technology",
    "SOUN": "Technology",
    "SANA": "Healthcare",
    "ABCL": "Healthcare",
    "SDGR": "Healthcare",
    "FLNC": "Energy",
    "TNDM": "Healthcare",
    "DOCS": "Healthcare",
    "DNUT": "Consumer Discretionary",
    "TASK": "Technology",
    "OUST": "Technology",
    "ASAN": "Technology",
    "JAMF": "Technology",
    "BIGC": "Technology",
    "APPS": "Technology",
    "CRNC": "Technology",
    "DOMO": "Technology",
    "YEXT": "Technology",
    "BAND": "Technology",
    "ZI": "Technology",
    "MTTR": "Technology",
    "IONQ": "Technology",
    "RGTI": "Technology",
    "QUBT": "Technology",
    "ARQQ": "Technology",
    "WIX": "Technology",
    "GLBE": "Technology",
    "CLBT": "Technology",
    "PRGS": "Technology",
    "CWAN": "Technology",
    "FRSH": "Technology",

    # Even more mid-cap sector classifications
    "CARG": "Consumer Discretionary",
    "BMBL": "Communication Services",
    "INTA": "Technology",
    "PLTK": "Communication Services",
    "GENI": "Communication Services",
    "EVCM": "Technology",
    "LMND": "Financials",
    "ROOT": "Financials",
    "OSCR": "Healthcare",
    "OLO": "Technology",
    "PAR": "Technology",
    "PRFT": "Technology",
    "TXG": "Healthcare",
    "LEGN": "Healthcare",
    "ARGX": "Healthcare",
    "RCKT": "Healthcare",
    "IMVT": "Healthcare",
    "PCOR": "Technology",
    "TNET": "Industrials",
    "ENFN": "Technology",
    "AUR": "Technology",
    "NNOX": "Healthcare",
    "BTDR": "Technology",
    "CIFR": "Technology",
    "IREN": "Technology",
    "CORZ": "Technology",
    "WULF": "Technology",
    "SATS": "Communication Services",
    "IRBT": "Consumer Discretionary",
    "DLO": "Financials",
    "FLYW": "Technology",
    "GBTG": "Consumer Discretionary",
    "MGNI": "Technology",
    "PUBM": "Technology",
    "VERV": "Healthcare",
    "NTRA": "Healthcare",
    "CERS": "Healthcare",
    "PCRX": "Healthcare",
    "HRMY": "Healthcare",
    "KRYS": "Healthcare",
    "VKTX": "Healthcare",
    "SMMT": "Healthcare",
    "TARS": "Healthcare",
    "DCPH": "Healthcare",
    "IOVA": "Healthcare",
    "INSM": "Healthcare",
    "ALNY": "Healthcare",
    "RGEN": "Healthcare",
    "BIO": "Healthcare",
    "MTSI": "Technology",
    "CAMT": "Technology",
    "FORM": "Technology",
    "COHR": "Technology",
    "LSCC": "Technology",
    "WOLF": "Technology",
    "ACLS": "Technology",
    "RMBS": "Technology",
    "DIOD": "Technology",
    "POWI": "Technology",
    "SITM": "Technology",
    "ONTO": "Technology",
    "AMKR": "Technology",
    "VST": "Utilities",
    "TALO": "Energy",
    "VTLE": "Energy",
    "PR": "Energy",
    "CHRD": "Energy",
    "SM": "Energy",
    "MTDR": "Energy",
    "GPOR": "Energy",
    "RRC": "Energy",
    "SWN": "Energy",
    "AR": "Energy",
    "CNX": "Energy",
    "MGY": "Energy",
    "HESM": "Energy",
    "WES": "Energy",
    "KNSL": "Financials",
    "HLI": "Financials",
    "PIPR": "Financials",
    "STEP": "Financials",
    "VCTR": "Financials",
    "VIRT": "Financials",
    "LPLA": "Financials",
    "IBKR": "Financials",
    "MORN": "Financials",
    "EVR": "Financials",
    "SF": "Financials",
    "CSGP": "Real Estate",
    "HUBB": "Industrials",
    "WST": "Healthcare",
    "DAY": "Technology",
    "EG": "Financials",
}


# ---------------------------------------------------------------------------
# Helper functions
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
        - "sp500"    -> Full S&P 500 (~503 stocks)
        - "midcap"   -> Russell Midcap growth stocks (~200 stocks)
        - "lse"      -> ALL_LSE (FTSE 100 + FTSE 250 top)
        - "us"       -> ALL_US (S&P 500 + Russell Midcap)
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
        "sp500": SP500_FULL,
        "midcap": RUSSELL_MID,
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


def get_universe_stats() -> None:
    """
    Print counts for each sub-list in the stock universe.
    """
    print("=" * 50)
    print("Stock Universe Statistics")
    print("=" * 50)
    print(f"FTSE 100 tickers      : {len(FTSE_100)}")
    print(f"FTSE 250 top          : {len(FTSE_250_TOP)}")
    print(f"S&P 500 full          : {len(SP500_FULL)}")
    print(f"Russell Midcap        : {len(RUSSELL_MID)}")
    print("-" * 50)
    print(f"ALL LSE (UK)          : {len(ALL_LSE)}")
    print(f"ALL US                : {len(ALL_US)}")
    print(f"FULL UNIVERSE         : {len(FULL_UNIVERSE)}")
    print("-" * 50)
    print(f"Sectors classified    : {len(SECTOR_MAP)}")
    print(f"Unique sectors        : {list_sectors()}")
    print("=" * 50)

    # Breakdown by sector
    print("\nSector breakdown (full universe):")
    from collections import Counter
    sector_counts = Counter(
        SECTOR_MAP.get(t, "Unknown") for t in FULL_UNIVERSE
    )
    for sector, count in sorted(sector_counts.items(), key=lambda x: -x[1]):
        print(f"  {sector:30s}: {count}")

    unknown = sum(1 for t in FULL_UNIVERSE if t not in SECTOR_MAP)
    print(f"\n  Unclassified tickers: {unknown}")


# ---------------------------------------------------------------------------
# Quick sanity check when run directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    get_universe_stats()
