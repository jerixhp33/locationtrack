import re
from typing import Dict, Any, Optional

# Mapping of common Android model code prefixes to brand & commercial name
MODEL_MAPPINGS = {
    # Samsung Galaxy S series
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
    # Samsung Galaxy Z Fold / Flip
    "SM-F946": ("Samsung", "Galaxy Z Fold 5"),
    "SM-F731": ("Samsung", "Galaxy Z Flip 5"),
    "SM-F936": ("Samsung", "Galaxy Z Fold 4"),
    "SM-F721": ("Samsung", "Galaxy Z Flip 4"),
    # Samsung Galaxy A series
    "SM-A546": ("Samsung", "Galaxy A54 5G"),
    "SM-A536": ("Samsung", "Galaxy A53 5G"),
    "SM-A528": ("Samsung", "Galaxy A52s 5G"),
    "SM-A526": ("Samsung", "Galaxy A52 5G"),
    "SM-A525": ("Samsung", "Galaxy A52 4G"),
    "SM-A346": ("Samsung", "Galaxy A34 5G"),
    "SM-A336": ("Samsung", "Galaxy A33 5G"),
    "SM-A245": ("Samsung", "Galaxy A24"),
    "SM-A236": ("Samsung", "Galaxy A23 5G"),
    "SM-A146": ("Samsung", "Galaxy A14 5G"),
    "SM-A145": ("Samsung", "Galaxy A14 4G"),
    "SM-A057": ("Samsung", "Galaxy A05s"),
    "SM-A055": ("Samsung", "Galaxy A05"),
    "SM-M546": ("Samsung", "Galaxy M54 5G"),
    "SM-M346": ("Samsung", "Galaxy M34 5G"),
    "SM-M146": ("Samsung", "Galaxy M14 5G"),
    # OnePlus
    "CPH2581": ("OnePlus", "12"),
    "CPH2609": ("OnePlus", "12R"),
    "CPH2449": ("OnePlus", "11"),
    "CPH2451": ("OnePlus", "11"),
    "NE2210":  ("OnePlus", "10 Pro"),
    "CPH2413": ("OnePlus", "10T"),
    "CPH2467": ("OnePlus", "Nord CE 3 Lite"),
    "CPH2569": ("OnePlus", "Nord CE 4"),
    # Google Pixel
    "Pixel 8 Pro": ("Google", "Pixel 8 Pro"),
    "Pixel 8":     ("Google", "Pixel 8"),
    "Pixel 8a":    ("Google", "Pixel 8a"),
    "Pixel 7 Pro": ("Google", "Pixel 7 Pro"),
    "Pixel 7":     ("Google", "Pixel 7"),
    "Pixel 7a":    ("Google", "Pixel 7a"),
    "Pixel 6 Pro": ("Google", "Pixel 6 Pro"),
    "Pixel 6":     ("Google", "Pixel 6"),
    "Pixel 6a":    ("Google", "Pixel 6a"),
    # Xiaomi / Redmi / POCO
    "23117PN60G": ("Xiaomi", "14 Pro"),
    "23127PN0CG": ("Xiaomi", "14"),
    "2211133G":   ("Xiaomi", "13 Pro"),
    "23049PCD8G": ("POCO", "F5"),
    "23013PC75G": ("POCO", "X5 Pro 5G"),
    "2201116SI":  ("Xiaomi", "Redmi Note 11 Pro+ 5G"),
    "22101316G":  ("Xiaomi", "Redmi Note 12 Pro+ 5G"),
    "2312DRA50G": ("Xiaomi", "Redmi Note 13 Pro+ 5G"),
    # Realme
    "RMX3851": ("Realme", "GT 6"),
    "RMX3771": ("Realme", "11 Pro+ 5G"),
    "RMX3741": ("Realme", "11 Pro 5G"),
    "RMX3363": ("Realme", "GT Master Edition"),
    "CPH2343": ("Realme", "9 Pro+ 5G"),
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


def resolve_real_os(os_family: str, os_version: str, client_platform_ver: Optional[str] = None) -> str:
    """Resolve true Android / Windows OS version from High-Entropy client hints."""
    if os_family == "Android":
        if client_platform_ver:
            major = client_platform_ver.split(".")[0]
            if major in ["15", "14", "13", "12", "11", "10", "9", "8"]:
                names = {
                    "15": "Android 15 (Vanilla Ice Cream)",
                    "14": "Android 14 (Upside Down Cake)",
                    "13": "Android 13 (Tiramisu)",
                    "12": "Android 12 (Snow Cone)",
                    "11": "Android 11 (Red Velvet Cake)",
                    "10": "Android 10 (Quince Tart)"
                }
                return names.get(major, f"Android {major}")
        if os_version:
            return f"Android {os_version}"
        return "Android"

    if os_family == "Windows":
        # Windows 11 platformVersion is >= 13.0.0 in Client Hints
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

        # Prefix heuristics
        if client_model.startswith("SM-"):
            brand = "Samsung"
            model = f"Samsung Galaxy ({client_model})"
        elif client_model.startswith("Pixel"):
            brand = "Google"
            model = client_model
        elif client_model.startswith("CPH") or client_model.startswith("NE2"):
            brand = "OnePlus / OPPO"
            model = f"OnePlus/OPPO ({client_model})"
        elif client_model.startswith("RMX"):
            brand = "Realme"
            model = f"Realme ({client_model})"
        elif client_model.startswith("V2") or client_model.startswith("PD"):
            brand = "Vivo / iQOO"
            model = f"Vivo/iQOO ({client_model})"
        elif client_model.startswith("2") or client_model.startswith("M2"):
            brand = "Xiaomi / Redmi"
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
