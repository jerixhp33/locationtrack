import re
from typing import Dict, Any, Optional

# Mapping of common Android model code prefixes to brand & commercial name
# 300+ models covering all major brands popular in India and worldwide
MODEL_MAPPINGS = {
    # ======================== SAMSUNG ========================
    # Galaxy S Series
    "SM-S938": ("Samsung", "Galaxy S25 Ultra"),
    "SM-S936": ("Samsung", "Galaxy S25+"),
    "SM-S931": ("Samsung", "Galaxy S25"),
    "SM-S928": ("Samsung", "Galaxy S24 Ultra"),
    "SM-S926": ("Samsung", "Galaxy S24+"),
    "SM-S921": ("Samsung", "Galaxy S24"),
    "SM-S918": ("Samsung", "Galaxy S23 Ultra"),
    "SM-S916": ("Samsung", "Galaxy S23+"),
    "SM-S911": ("Samsung", "Galaxy S23"),
    "SM-S908": ("Samsung", "Galaxy S22 Ultra"),
    "SM-S906": ("Samsung", "Galaxy S22+"),
    "SM-S901": ("Samsung", "Galaxy S22"),
    "SM-G998": ("Samsung", "Galaxy S21 Ultra"),
    "SM-G996": ("Samsung", "Galaxy S21+"),
    "SM-G991": ("Samsung", "Galaxy S21"),
    "SM-G990": ("Samsung", "Galaxy S21 FE"),
    "SM-S711": ("Samsung", "Galaxy S23 FE"),
    "SM-S721": ("Samsung", "Galaxy S24 FE"),
    # Galaxy Z Fold / Flip
    "SM-F956": ("Samsung", "Galaxy Z Fold 6"),
    "SM-F946": ("Samsung", "Galaxy Z Fold 5"),
    "SM-F936": ("Samsung", "Galaxy Z Fold 4"),
    "SM-F926": ("Samsung", "Galaxy Z Fold 3"),
    "SM-F741": ("Samsung", "Galaxy Z Flip 6"),
    "SM-F731": ("Samsung", "Galaxy Z Flip 5"),
    "SM-F721": ("Samsung", "Galaxy Z Flip 4"),
    "SM-F711": ("Samsung", "Galaxy Z Flip 3"),
    # Galaxy A Series
    "SM-A566": ("Samsung", "Galaxy A56 5G"),
    "SM-A556": ("Samsung", "Galaxy A55 5G"),
    "SM-A546": ("Samsung", "Galaxy A54 5G"),
    "SM-A536": ("Samsung", "Galaxy A53 5G"),
    "SM-A528": ("Samsung", "Galaxy A52s 5G"),
    "SM-A526": ("Samsung", "Galaxy A52 5G"),
    "SM-A525": ("Samsung", "Galaxy A52 4G"),
    "SM-A356": ("Samsung", "Galaxy A35 5G"),
    "SM-A346": ("Samsung", "Galaxy A34 5G"),
    "SM-A336": ("Samsung", "Galaxy A33 5G"),
    "SM-A256": ("Samsung", "Galaxy A25 5G"),
    "SM-A245": ("Samsung", "Galaxy A24"),
    "SM-A236": ("Samsung", "Galaxy A23 5G"),
    "SM-A235": ("Samsung", "Galaxy A23"),
    "SM-A166": ("Samsung", "Galaxy A16 5G"),
    "SM-A165": ("Samsung", "Galaxy A16"),
    "SM-A156": ("Samsung", "Galaxy A15 5G"),
    "SM-A155": ("Samsung", "Galaxy A15"),
    "SM-A146": ("Samsung", "Galaxy A14 5G"),
    "SM-A145": ("Samsung", "Galaxy A14 4G"),
    "SM-A057": ("Samsung", "Galaxy A05s"),
    "SM-A055": ("Samsung", "Galaxy A05"),
    # Galaxy M Series
    "SM-M556": ("Samsung", "Galaxy M55 5G"),
    "SM-M546": ("Samsung", "Galaxy M54 5G"),
    "SM-M356": ("Samsung", "Galaxy M35 5G"),
    "SM-M346": ("Samsung", "Galaxy M34 5G"),
    "SM-M156": ("Samsung", "Galaxy M15 5G"),
    "SM-M146": ("Samsung", "Galaxy M14 5G"),
    "SM-M145": ("Samsung", "Galaxy M14 4G"),
    # Galaxy F Series (India exclusive)
    "SM-E546": ("Samsung", "Galaxy F54 5G"),
    "SM-E346": ("Samsung", "Galaxy F34 5G"),
    "SM-E156": ("Samsung", "Galaxy F15 5G"),
    "SM-E146": ("Samsung", "Galaxy F14 5G"),

    # ======================== OPPO ========================
    "CPH2659": ("OPPO", "Find X7 Ultra"),
    "CPH2651": ("OPPO", "Find X7"),
    "CPH2519": ("OPPO", "Find X6 Pro"),
    "CPH2503": ("OPPO", "Find X5 Pro"),
    "CPH2473": ("OPPO", "Find N3 Flip"),
    "CPH2591": ("OPPO", "Reno 12 Pro 5G"),
    "CPH2589": ("OPPO", "Reno 12 5G"),
    "CPH2551": ("OPPO", "Reno 11 Pro 5G"),
    "CPH2549": ("OPPO", "Reno 11 5G"),
    "CPH2525": ("OPPO", "Reno 11F 5G"),
    "CPH2507": ("OPPO", "Reno 10 Pro+ 5G"),
    "CPH2505": ("OPPO", "Reno 10 Pro 5G"),
    "CPH2509": ("OPPO", "Reno 10 5G"),
    "CPH2487": ("OPPO", "Reno 9 Pro+ 5G"),
    "CPH2485": ("OPPO", "Reno 9 Pro 5G"),
    "CPH2495": ("OPPO", "Reno 9 5G"),
    "CPH2459": ("OPPO", "Reno 8 Pro 5G"),
    "CPH2357": ("OPPO", "Reno 8 5G"),
    "CPH2363": ("OPPO", "Reno 8T 5G"),
    "CPH2365": ("OPPO", "Reno 8T"),
    "CPH2371": ("OPPO", "Reno 7 Pro 5G"),
    "CPH2373": ("OPPO", "Reno 7 5G"),
    "CPH2375": ("OPPO", "Reno 7"),
    "CPH2351": ("OPPO", "Reno 6 Pro 5G"),
    "CPH2247": ("OPPO", "Reno 6 5G"),
    "CPH2611": ("OPPO", "F27 Pro+ 5G"),
    "CPH2577": ("OPPO", "F25 Pro 5G"),
    "CPH2579": ("OPPO", "F23 5G"),
    "CPH2539": ("OPPO", "F21s Pro 5G"),
    "CPH2541": ("OPPO", "F21s Pro"),
    "CPH2613": ("OPPO", "K12x 5G"),
    "CPH2615": ("OPPO", "A3 Pro 5G"),
    "CPH2617": ("OPPO", "A3x"),
    "CPH2583": ("OPPO", "A79 5G"),
    "CPH2585": ("OPPO", "A78 5G"),
    "CPH2565": ("OPPO", "A78"),
    "CPH2567": ("OPPO", "A58 5G"),
    "CPH2563": ("OPPO", "A58"),
    "CPH2531": ("OPPO", "A38"),
    "CPH2533": ("OPPO", "A18"),
    "CPH2535": ("OPPO", "A17"),
    "CPH2477": ("OPPO", "A57 5G"),
    "CPH2471": ("OPPO", "A57"),
    "CPH2387": ("OPPO", "A77 5G"),
    "CPH2385": ("OPPO", "A77"),
    "CPH2389": ("OPPO", "A96"),
    "CPH2269": ("OPPO", "A76"),
    "CPH2271": ("OPPO", "A16"),
    "CPH2273": ("OPPO", "A16s"),
    "CPH2239": ("OPPO", "A55 5G"),
    "CPH2325": ("OPPO", "A56s 5G"),

    # ======================== VIVO ========================
    "V2316": ("Vivo", "X200 Pro"),
    "V2314": ("Vivo", "X200"),
    "V2219": ("Vivo", "X100 Pro"),
    "V2217": ("Vivo", "X100"),
    "V2171": ("Vivo", "X90 Pro"),
    "V2169": ("Vivo", "X90"),
    "V2145": ("Vivo", "X80 Pro"),
    "V2324": ("Vivo", "V40 Pro"),
    "V2322": ("Vivo", "V40"),
    "V2320": ("Vivo", "V40e"),
    "V2252": ("Vivo", "V30 Pro 5G"),
    "V2250": ("Vivo", "V30 5G"),
    "V2248": ("Vivo", "V30e 5G"),
    "V2238": ("Vivo", "V29 Pro 5G"),
    "V2236": ("Vivo", "V29 5G"),
    "V2234": ("Vivo", "V29e 5G"),
    "V2217A": ("Vivo", "V27 Pro 5G"),
    "V2215": ("Vivo", "V27 5G"),
    "V2214": ("Vivo", "V27e"),
    "V2195": ("Vivo", "V25 Pro 5G"),
    "V2193": ("Vivo", "V25 5G"),
    "V2191": ("Vivo", "V25e"),
    "V2310": ("Vivo", "T3x 5G"),
    "V2306": ("Vivo", "T3 Pro 5G"),
    "V2304": ("Vivo", "T3 5G"),
    "V2230": ("Vivo", "T2x 5G"),
    "V2226": ("Vivo", "T2 5G"),
    "V2233": ("Vivo", "T2 Pro 5G"),
    "V2202": ("Vivo", "T1 5G"),
    "V2330": ("Vivo", "Y300 Plus 5G"),
    "V2328": ("Vivo", "Y200 Pro 5G"),
    "V2326": ("Vivo", "Y200 5G"),
    "V2318": ("Vivo", "Y200e 5G"),
    "V2254": ("Vivo", "Y100 5G"),
    "V2257": ("Vivo", "Y100"),
    "V2247": ("Vivo", "Y28 5G"),
    "V2244": ("Vivo", "Y27 5G"),
    "V2302": ("Vivo", "Y18"),
    "V2225": ("Vivo", "Y56 5G"),
    "V2217B": ("Vivo", "Y35"),
    "V2207": ("Vivo", "Y22"),
    "V2204": ("Vivo", "Y22s"),
    "V2120": ("Vivo", "Y21"),
    "V2203": ("Vivo", "Y16"),
    "V2115": ("Vivo", "Y15s"),
    "PD2287":  ("Vivo", "X Fold 3 Pro"),
    "PD2283":  ("Vivo", "X Fold 3"),

    # ======================== iQOO ========================
    "I2211":  ("iQOO", "13"),
    "I2201":  ("iQOO", "12"),
    "I2126":  ("iQOO", "11"),
    "I2203":  ("iQOO", "Neo 9 Pro"),
    "I2127":  ("iQOO", "Neo 7 Pro 5G"),
    "I2125":  ("iQOO", "Neo 7 5G"),
    "I2208":  ("iQOO", "Z9x 5G"),
    "I2205":  ("iQOO", "Z9 5G"),
    "I2128":  ("iQOO", "Z7 Pro 5G"),
    "I2130":  ("iQOO", "Z7 5G"),
    "I2129":  ("iQOO", "Z7s 5G"),
    "I2012":  ("iQOO", "Z6 5G"),
    "I2011":  ("iQOO", "Z6 Pro 5G"),

    # ======================== REALME ========================
    "RMX3931": ("Realme", "GT 7 Pro"),
    "RMX3851": ("Realme", "GT 6"),
    "RMX3853": ("Realme", "GT 6T"),
    "RMX3708": ("Realme", "GT 5 Pro"),
    "RMX3706": ("Realme", "GT Neo 5"),
    "RMX3710": ("Realme", "GT Neo 5 SE"),
    "RMX3574": ("Realme", "GT Neo 3"),
    "RMX3570": ("Realme", "GT Neo 3T"),
    "RMX3363": ("Realme", "GT Master Edition"),
    "RMX3521": ("Realme", "GT 2 Pro"),
    "RMX3311": ("Realme", "GT"),
    "RMX3933": ("Realme", "14 Pro+ 5G"),
    "RMX3927": ("Realme", "14 Pro 5G"),
    "RMX3921": ("Realme", "14x 5G"),
    "RMX3871": ("Realme", "13 Pro+ 5G"),
    "RMX3873": ("Realme", "13 Pro 5G"),
    "RMX3875": ("Realme", "13+ 5G"),
    "RMX3830": ("Realme", "12 Pro+ 5G"),
    "RMX3832": ("Realme", "12 Pro 5G"),
    "RMX3834": ("Realme", "12+ 5G"),
    "RMX3836": ("Realme", "12 5G"),
    "RMX3840": ("Realme", "12x 5G"),
    "RMX3771": ("Realme", "11 Pro+ 5G"),
    "RMX3741": ("Realme", "11 Pro 5G"),
    "RMX3780": ("Realme", "11 5G"),
    "RMX3782": ("Realme", "11x 5G"),
    "RMX3630": ("Realme", "10 Pro+ 5G"),
    "RMX3660": ("Realme", "10 Pro 5G"),
    "RMX3686": ("Realme", "10 5G"),
    "RMX3615": ("Realme", "10"),
    "RMX3471": ("Realme", "9 Pro+ 5G"),
    "RMX3473": ("Realme", "9 Pro 5G"),
    "RMX3491": ("Realme", "9 5G"),
    "RMX3521A": ("Realme", "9 5G SE"),
    "RMX3393": ("Realme", "9"),
    "RMX3395": ("Realme", "9i 5G"),
    "RMX3491A": ("Realme", "9i"),
    "RMX3261": ("Realme", "8 Pro"),
    "RMX3241": ("Realme", "8 5G"),
    "RMX3085": ("Realme", "8"),
    "RMX3081": ("Realme", "8i"),
    "RMX3780A": ("Realme", "Narzo 60 5G"),
    "RMX3760": ("Realme", "Narzo 60 Pro 5G"),
    "RMX3630A": ("Realme", "Narzo 50 Pro 5G"),
    "RMX3610": ("Realme", "Narzo 50 5G"),
    "RMX3860": ("Realme", "Narzo 70 Pro 5G"),
    "RMX3862": ("Realme", "Narzo 70 5G"),
    "RMX3864": ("Realme", "Narzo 70x 5G"),
    "RMX3511": ("Realme", "C35"),
    "RMX3762": ("Realme", "C53"),
    "RMX3810": ("Realme", "C55"),
    "RMX3890": ("Realme", "C63 5G"),
    "RMX3892": ("Realme", "C65 5G"),
    "CPH2343": ("Realme", "9 Pro+ 5G"),

    # ======================== XIAOMI ========================
    "2407FPN8EG": ("Xiaomi", "15 Pro"),
    "2407FPN8DG": ("Xiaomi", "15"),
    "23117PN60G": ("Xiaomi", "14 Pro"),
    "23127PN0CG": ("Xiaomi", "14"),
    "24031PN0DC": ("Xiaomi", "14 Civi"),
    "2211133G":   ("Xiaomi", "13 Pro"),
    "2210132G":   ("Xiaomi", "13"),
    "2304FPN6DC": ("Xiaomi", "13T Pro"),
    "23078PND5G": ("Xiaomi", "13T"),
    "2209129SC":  ("Xiaomi", "12 Pro"),
    "2201123G":   ("Xiaomi", "12"),
    "2112123AG":  ("Xiaomi", "12X"),
    "2203129G":   ("Xiaomi", "12T Pro"),
    "22081212UG": ("Xiaomi", "12T"),
    "2206123SC":  ("Xiaomi", "12S Ultra"),
    "22041219G":  ("Xiaomi", "Civi 2"),
    "23046PND0G": ("Xiaomi", "Civi 3"),
    "23021RAAEG": ("Xiaomi", "13 Lite"),

    # ======================== REDMI ========================
    "24108RN84G": ("Redmi", "Note 14 Pro+ 5G"),
    "24094RN84G": ("Redmi", "Note 14 Pro 5G"),
    "24090RA88G": ("Redmi", "Note 14 5G"),
    "2312DRA50G": ("Redmi", "Note 13 Pro+ 5G"),
    "23090RA98G": ("Redmi", "Note 13 Pro 5G"),
    "2311DRK48G": ("Redmi", "Note 13 5G"),
    "23076RN4BI": ("Redmi", "Note 13"),
    "22101316G":  ("Redmi", "Note 12 Pro+ 5G"),
    "22101316I":  ("Redmi", "Note 12 Pro 5G"),
    "22111317I":  ("Redmi", "Note 12 5G"),
    "22101317G":  ("Redmi", "Note 12"),
    "2201116SI":  ("Redmi", "Note 11 Pro+ 5G"),
    "2201116SG":  ("Redmi", "Note 11 Pro 5G"),
    "2201116TI":  ("Redmi", "Note 11 Pro"),
    "2201117TI":  ("Redmi", "Note 11"),
    "2201117TG":  ("Redmi", "Note 11S"),
    "22011119UY": ("Redmi", "Note 11S 5G"),
    "24117RN87G": ("Redmi", "14 Pro+ 5G"),
    "24117RN86G": ("Redmi", "14 Pro 5G"),
    "24117RA8BG": ("Redmi", "14 5G"),
    "23106RN0DA": ("Redmi", "13 5G"),
    "23108RN04Y": ("Redmi", "13C 5G"),
    "23110RN82I": ("Redmi", "13C"),
    "22120RN86G": ("Redmi", "12 5G"),
    "23053RN02A": ("Redmi", "12"),
    "23028RNCAG": ("Redmi", "12C"),
    "23077RABDC": ("Redmi", "A3"),
    "23076RN8DY": ("Redmi", "A2+"),
    "220733SFG":  ("Redmi", "A1+"),
    "23076RNABU": ("Redmi", "A2"),

    # ======================== POCO ========================
    "24076PC4BI": ("POCO", "F7 Pro"),
    "24076PC4BG": ("POCO", "F7"),
    "23113PCD1G": ("POCO", "F6 Pro"),
    "24069PC21G": ("POCO", "F6"),
    "23049PCD8G": ("POCO", "F5"),
    "23049PCD1G": ("POCO", "F5 Pro"),
    "21121210G":  ("POCO", "F4"),
    "21091116AG": ("POCO", "F3"),
    "24090RA84G": ("POCO", "X7 Pro 5G"),
    "24090RA83G": ("POCO", "X7 5G"),
    "23122PCD1G": ("POCO", "X6 Pro 5G"),
    "23122PCD1I": ("POCO", "X6 5G"),
    "23122PCD1A": ("POCO", "X6 Neo 5G"),
    "23013PC75G": ("POCO", "X5 Pro 5G"),
    "22101320G":  ("POCO", "X5 5G"),
    "22041216G":  ("POCO", "X4 Pro 5G"),
    "2207117BPG": ("POCO", "X4 GT"),
    "24108RAA4G": ("POCO", "M7 Pro 5G"),
    "24108RAA3G": ("POCO", "M7 5G"),
    "2311DRK47G": ("POCO", "M6 Pro 5G"),
    "2311DRK46G": ("POCO", "M6 5G"),
    "23076PC4BI": ("POCO", "M5"),
    "23076PC4BL": ("POCO", "M5s"),
    "23021RAAEG": ("POCO", "C65"),
    "23108RN04A": ("POCO", "C55"),

    # ======================== ONEPLUS ========================
    "CPH2643": ("OnePlus", "13"),
    "CPH2641": ("OnePlus", "13R"),
    "CPH2581": ("OnePlus", "12"),
    "CPH2609": ("OnePlus", "12R"),
    "CPH2449": ("OnePlus", "11"),
    "CPH2451": ("OnePlus", "11R"),
    "NE2210":  ("OnePlus", "10 Pro"),
    "NE2215":  ("OnePlus", "10 Pro"),
    "CPH2413": ("OnePlus", "10T"),
    "CPH2399": ("OnePlus", "10R"),
    "LE2111":  ("OnePlus", "9"),
    "LE2115":  ("OnePlus", "9 Pro"),
    "LE2117":  ("OnePlus", "9R"),
    "LE2127":  ("OnePlus", "9RT"),
    "CPH2619": ("OnePlus", "Nord 4"),
    "CPH2517": ("OnePlus", "Nord 3 5G"),
    "CPH2407": ("OnePlus", "Nord 2T 5G"),
    "CPH2467": ("OnePlus", "Nord CE 3 Lite 5G"),
    "CPH2469": ("OnePlus", "Nord CE 3 5G"),
    "CPH2569": ("OnePlus", "Nord CE 4"),
    "CPH2571": ("OnePlus", "Nord CE 4 Lite"),
    "CPH2625": ("OnePlus", "Nord 4 CE"),
    "CPH2557": ("OnePlus", "Nord N30 5G"),

    # ======================== GOOGLE PIXEL ========================
    "Pixel 9 Pro XL": ("Google", "Pixel 9 Pro XL"),
    "Pixel 9 Pro":    ("Google", "Pixel 9 Pro"),
    "Pixel 9":        ("Google", "Pixel 9"),
    "Pixel 9a":       ("Google", "Pixel 9a"),
    "Pixel 8 Pro":    ("Google", "Pixel 8 Pro"),
    "Pixel 8":        ("Google", "Pixel 8"),
    "Pixel 8a":       ("Google", "Pixel 8a"),
    "Pixel 7 Pro":    ("Google", "Pixel 7 Pro"),
    "Pixel 7":        ("Google", "Pixel 7"),
    "Pixel 7a":       ("Google", "Pixel 7a"),
    "Pixel 6 Pro":    ("Google", "Pixel 6 Pro"),
    "Pixel 6":        ("Google", "Pixel 6"),
    "Pixel 6a":       ("Google", "Pixel 6a"),

    # ======================== MOTOROLA ========================
    "XT2347": ("Motorola", "Edge 50 Ultra"),
    "XT2345": ("Motorola", "Edge 50 Pro"),
    "XT2343": ("Motorola", "Edge 50 Fusion"),
    "XT2341": ("Motorola", "Edge 50 Neo"),
    "XT2301": ("Motorola", "Edge 40 Pro"),
    "XT2303": ("Motorola", "Edge 40"),
    "XT2305": ("Motorola", "Edge 40 Neo"),
    "XT2339": ("Motorola", "Moto G85 5G"),
    "XT2337": ("Motorola", "Moto G64 5G"),
    "XT2335": ("Motorola", "Moto G45 5G"),
    "XT2333": ("Motorola", "Moto G35 5G"),
    "XT2321": ("Motorola", "Moto G84 5G"),
    "XT2319": ("Motorola", "Moto G54 5G"),
    "XT2317": ("Motorola", "Moto G34 5G"),
    "XT2315": ("Motorola", "Moto G24"),
    "XT2307": ("Motorola", "Moto G73 5G"),

    # ======================== NOTHING ========================
    "A059":  ("Nothing", "Phone (1)"),
    "A065":  ("Nothing", "Phone (2)"),
    "A142":  ("Nothing", "Phone (2a)"),
    "A063":  ("Nothing", "Phone (2a) Plus"),

    # ======================== TECNO ========================
    "CK8n":  ("Tecno", "Phantom V Fold"),
    "CL8":   ("Tecno", "Phantom X2 Pro"),
    "CH9n":  ("Tecno", "Camon 20 Pro 5G"),
    "CK7n":  ("Tecno", "Camon 20"),
    "CI8":   ("Tecno", "Camon 30 Pro 5G"),
    "CK6n":  ("Tecno", "Camon 30 5G"),
    "CH6":   ("Tecno", "Spark 10 Pro"),
    "CJ8":   ("Tecno", "Spark 20 Pro+"),
    "BG7":   ("Tecno", "Pova 5 Pro 5G"),
    "BG6":   ("Tecno", "Pova 5"),
    "BF7":   ("Tecno", "Pova Neo 3"),

    # ======================== INFINIX ========================
    "X6871": ("Infinix", "GT 20 Pro"),
    "X6851": ("Infinix", "Note 40 Pro+ 5G"),
    "X6850": ("Infinix", "Note 40 Pro"),
    "X6831": ("Infinix", "Note 30 Pro"),
    "X6833": ("Infinix", "Note 30 5G"),
    "X6837": ("Infinix", "Hot 40 Pro"),
    "X6836": ("Infinix", "Hot 40"),
    "X6821": ("Infinix", "Smart 8 Plus"),
    "X6825": ("Infinix", "Smart 8"),

    # ======================== NOKIA ========================
    "TA-1568": ("Nokia", "X30 5G"),
    "TA-1484": ("Nokia", "G42 5G"),
    "TA-1486": ("Nokia", "G22"),
    "TA-1522": ("Nokia", "C32"),

    # ======================== HUAWEI / HONOR ========================
    "ANY-LX1":  ("Huawei", "P40 Pro"),
    "ELS-NX9":  ("Huawei", "P40 Pro"),
    "NOH-NX9":  ("Huawei", "Mate 40 Pro"),
    "ALT-L29":  ("Huawei", "Nova 12"),
    "REA-NX9":  ("Honor", "200 Pro"),
    "CRT-LX3":  ("Honor", "X9b"),
    "RKY-LX1":  ("Honor", "X7b"),
    "ANY-NX1":  ("Honor", "90"),
    "CRT-LX1":  ("Honor", "90 Lite"),
    "FNE-NX9":  ("Honor", "Magic 6 Pro"),
    "RMO-NX1":  ("Honor", "Magic V2"),

    # ======================== APPLE (Safari UA strings) ========================
    "iPhone16,2": ("Apple", "iPhone 15 Pro Max"),
    "iPhone16,1": ("Apple", "iPhone 15 Pro"),
    "iPhone15,5": ("Apple", "iPhone 15 Plus"),
    "iPhone15,4": ("Apple", "iPhone 15"),
    "iPhone15,3": ("Apple", "iPhone 14 Pro Max"),
    "iPhone15,2": ("Apple", "iPhone 14 Pro"),
    "iPhone14,8": ("Apple", "iPhone 14 Plus"),
    "iPhone14,7": ("Apple", "iPhone 14"),
    "iPhone14,3": ("Apple", "iPhone 13 Pro Max"),
    "iPhone14,2": ("Apple", "iPhone 13 Pro"),
    "iPhone14,5": ("Apple", "iPhone 13"),
    "iPhone14,4": ("Apple", "iPhone 13 Mini"),
    "iPhone13,4": ("Apple", "iPhone 12 Pro Max"),
    "iPhone13,3": ("Apple", "iPhone 12 Pro"),
    "iPhone13,2": ("Apple", "iPhone 12"),
    "iPhone13,1": ("Apple", "iPhone 12 Mini"),
    "iPhone12,5": ("Apple", "iPhone 11 Pro Max"),
    "iPhone12,3": ("Apple", "iPhone 11 Pro"),
    "iPhone12,1": ("Apple", "iPhone 11"),
    "iPhone17,1": ("Apple", "iPhone 16 Pro Max"),
    "iPhone17,2": ("Apple", "iPhone 16 Pro"),
    "iPhone17,3": ("Apple", "iPhone 16 Plus"),
    "iPhone17,4": ("Apple", "iPhone 16"),
}

GPU_CHIPSETS = [
    (r"Mali-G68", "Exynos 1280 / Dimensity 920"),
    (r"Mali-G77|Mali-G78", "Dimensity 1000/1200 / Exynos 2100"),
    (r"Mali-G710|Mali-G715|Immortalis", "Dimensity 9000/9200 / Google Tensor G2/G3"),
    (r"Mali-G57", "Dimensity 700/810 / Helio G95"),
    (r"Mali-G52", "Helio G80/G85/G88"),
    (r"Adreno.*?750", "Snapdragon 8 Gen 3"),
    (r"Adreno.*?740", "Snapdragon 8 Gen 2"),
    (r"Adreno.*?730", "Snapdragon 8 Gen 1"),
    (r"Adreno.*?660", "Snapdragon 888"),
    (r"Adreno.*?650", "Snapdragon 865/870"),
    (r"Adreno.*?642|643", "Snapdragon 778G / 780G"),
    (r"Adreno.*?619", "Snapdragon 695 / 750G"),
    (r"Adreno.*?618", "Snapdragon 720G / 730G"),
    (r"Adreno.*?610", "Snapdragon 665 / 680"),
    (r"Apple GPU", "Apple Bionic / Silicon"),
    (r"Intel.*?Iris|Intel.*?UHD", "Intel Core Processor"),
    (r"NVIDIA.*?RTX|NVIDIA.*?GTX", "NVIDIA GeForce"),
    (r"AMD.*?Radeon", "AMD Radeon / Ryzen"),
]


def _is_browser_version(ver: str) -> bool:
    """
    Detect if a 'platformVersion' is actually a browser major version
    rather than a real OS platform version.
    Chrome on Android with frozen UA sends browser version like '150.0.0'
    as platformVersion in some edge cases.
    Real Android platformVersion is 8.0.0 - 15.x.x (single-digit major).
    """
    if not ver:
        return False
    try:
        major = int(ver.split(".")[0])
        # Real Android versions are 8-16, real Windows are 0-15
        # Browser versions are typically 100+
        return major > 20
    except (ValueError, IndexError):
        return False


def resolve_real_os(os_family: str, os_version: str, client_platform_ver: Optional[str] = None) -> str:
    """
    Resolve true Android / Windows OS version from High-Entropy client hints.
    Handles the common case where Client Hints fail and only the frozen
    UA string 'Android 10' is available.
    """
    # Filter out browser version being mistakenly sent as platformVersion
    if _is_browser_version(client_platform_ver):
        client_platform_ver = None

    if os_family == "Android":
        if client_platform_ver:
            major = client_platform_ver.split(".")[0]
            names = {
                "16": "Android 16",
                "15": "Android 15 (Vanilla Ice Cream)",
                "14": "Android 14 (Upside Down Cake)",
                "13": "Android 13 (Tiramisu)",
                "12": "Android 12 (Snow Cone)",
                "11": "Android 11 (Red Velvet Cake)",
                "10": "Android 10 (Quince Tart)",
                "9":  "Android 9 (Pie)",
                "8":  "Android 8 (Oreo)",
            }
            if major in names:
                return names[major]
            return f"Android {major}"

        # If os_version is the frozen "10", mark it as unknown rather than misleading
        if os_version == "10":
            return "Android (Version hidden by browser)"
        if os_version:
            return f"Android {os_version}"
        return "Android"

    if os_family == "Windows":
        if client_platform_ver:
            try:
                major = int(client_platform_ver.split(".")[0])
                if major >= 13:
                    return "Windows 11"
                elif major > 0:
                    return "Windows 10"
            except Exception:
                pass
        return "Windows 10 / 11"

    if os_family == "iOS":
        return f"iOS {os_version}" if os_version else "iOS"
    if os_family == "Mac OS X":
        return f"macOS {os_version}" if os_version else "macOS"

    return f"{os_family} {os_version}".strip()


def resolve_device_identity(
    ua_brand: Optional[str],
    ua_model: Optional[str],
    client_model: Optional[str],
    webgl_renderer: Optional[str]
) -> Dict[str, Any]:
    """
    Combines User-Agent, Client Hints model, and WebGL GPU renderer to identify
    the accurate brand, phone model, and processor chipset.
    """
    brand = ua_brand or ""
    model = client_model or ua_model or ""
    chipset = None

    # Determine chipset from GPU
    if webgl_renderer:
        for pattern, chip_name in GPU_CHIPSETS:
            if re.search(pattern, webgl_renderer, re.IGNORECASE):
                chipset = chip_name
                break

    # If client hint model is available (e.g. "SM-A536B", "Pixel 7 Pro", "CPH2343")
    if client_model:
        model = client_model
        # Check direct lookup
        for key, (b, m) in MODEL_MAPPINGS.items():
            if client_model.upper().startswith(key.upper()):
                brand = b
                model = f"{m} ({client_model})"
                return {"brand": brand, "model": model, "chipset": chipset}

        # Prefix heuristics for models not in the lookup table
        if client_model.startswith("SM-"):
            brand = "Samsung"
            model = f"Samsung Galaxy ({client_model})"
        elif client_model.startswith("Pixel"):
            brand = "Google"
            model = client_model
        elif client_model.startswith("CPH"):
            brand = "OPPO / OnePlus"
            model = f"OPPO/OnePlus ({client_model})"
        elif client_model.startswith("NE2") or client_model.startswith("LE2"):
            brand = "OnePlus"
            model = f"OnePlus ({client_model})"
        elif client_model.startswith("RMX"):
            brand = "Realme"
            model = f"Realme ({client_model})"
        elif client_model.startswith("V2") or client_model.startswith("V23") or client_model.startswith("V22"):
            brand = "Vivo"
            model = f"Vivo ({client_model})"
        elif client_model.startswith("PD"):
            brand = "Vivo"
            model = f"Vivo ({client_model})"
        elif client_model.startswith("I2"):
            brand = "iQOO"
            model = f"iQOO ({client_model})"
        elif client_model.startswith("XT"):
            brand = "Motorola"
            model = f"Motorola ({client_model})"
        elif client_model.startswith("A0"):
            brand = "Nothing"
            model = f"Nothing ({client_model})"
        elif client_model.startswith("A1"):
            brand = "Nothing"
            model = f"Nothing ({client_model})"
        elif client_model.startswith("X68") or client_model.startswith("X6"):
            brand = "Infinix"
            model = f"Infinix ({client_model})"
        elif client_model.startswith("CK") or client_model.startswith("CH") or client_model.startswith("CI") or client_model.startswith("CJ") or client_model.startswith("CL") or client_model.startswith("BG") or client_model.startswith("BF"):
            brand = "Tecno"
            model = f"Tecno ({client_model})"
        elif client_model.startswith("TA-"):
            brand = "Nokia"
            model = f"Nokia ({client_model})"
        elif client_model.startswith("ANY") or client_model.startswith("ELS") or client_model.startswith("NOH") or client_model.startswith("ALT"):
            brand = "Huawei"
            model = f"Huawei ({client_model})"
        elif client_model.startswith("REA") or client_model.startswith("CRT") or client_model.startswith("RKY") or client_model.startswith("FNE") or client_model.startswith("RMO"):
            brand = "Honor"
            model = f"Honor ({client_model})"
        elif client_model.startswith("2") or client_model.startswith("M2"):
            brand = "Xiaomi / Redmi / POCO"
            model = f"Xiaomi/Redmi ({client_model})"
        elif "iPhone" in client_model:
            brand = "Apple"
            model = client_model

    # If UA brand is generic (e.g. Generic_Android K), refine with GPU/Chipset
    if brand in ["Generic_Android", "Generic", "", "unknown"]:
        if "ARM" in (webgl_renderer or "") or "Mali" in (webgl_renderer or ""):
            brand = "Android Device"
            if chipset:
                model = f"Android ({chipset})"
        elif "Adreno" in (webgl_renderer or ""):
            brand = "Snapdragon Android"
            if chipset:
                model = f"Android ({chipset})"
        elif "Apple" in (webgl_renderer or ""):
            brand = "Apple"
            model = "iPhone / iPad"

    return {
        "brand": brand or "Unknown Device",
        "model": model or "Mobile Device",
        "chipset": chipset
    }
