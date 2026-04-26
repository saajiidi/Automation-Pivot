import pandas as pd

CATEGORY_MAPPING = {
    # --- T-Shirts ---
    'T-Shirt - Tank Top': ['tank top', 'tanktop', 'tank', 'top'],
    'T-Shirt - Drop Shoulder': ['drop shoulder'],
    'T-Shirt - Active Wear': ['active wear', 'activewear'],
    'T-Shirt - Jersey': ['jersy', 'jersey'],
    'T-Shirt - FS T-Shirt': ['full sleeve', 'long sleeve', 'fs', 'l/s'],
    'T-Shirt - HS T-Shirt': ['half sleeve', 'hs'],

    # --- Shirts & Polos ---
    'FS Shirt - Denim Shirt': ['denim'],
    'FS Shirt - Flannel Shirt': ['flannel'],
    'FS Shirt - Oxford Shirt': ['oxford'],
    'FS Shirt - Executive Formal Shirt': ['executive', 'formal'],
    'FS Shirt - Kaftan Shirt': ['kaftan'],
    'HS Shirt - Contrast Shirt': ['contrast'],
    'Polo Shirt': ['polo'],

    # --- Bottoms ---
    'Jeans': ['jeans'],
    'Trousers': ['trousers', 'pant', 'cargo', 'trouser', 'joggers', 'track pant', 'jogger'],
    'Twill Chino': ['twill chino'],

    # --- Outerwear & Winter ---
    'Sweatshirt': ['sweatshirt', 'hoodie', 'pullover'],
    'Jacket': ['jacket', 'outerwear', 'coat'],
    'Sweater': ['sweater', 'cardigan', 'knitwear'],
    'Turtleneck': ['turtleneck', 'mock neck'],

    # --- Ethnic ---
    'Panjabi': ['panjabi', 'punjabi'],

    # --- Innerwear ---
    'Boxer': ['boxer'],

    # --- Accessories ---
    'Wallet': ['wallet'],
    'Passport Holder': ['passport holder'],
    'Belt': ['belt'],
    'Cap': ['cap'],
    'Mask': ['mask'],
    'Water Bottle': ['water bottle'],
    'Leather Bag': ['bag', 'backpack'],

    # --- Bundles ---
    'Bundles - Choose Any': ['choose any'],
    'Bundles - Combo': ['combo', 'cambo'],
    'Bundles': ['bundle'],
}

def get_product_category(name: str) -> str:
    """Expert rule-based categorization for DEEN products."""
    if not name or not isinstance(name, str):
        return "Others"
        
    name_str = name.lower()
    for cat, keywords in CATEGORY_MAPPING.items():
        if any(kw.lower() in name_str for kw in keywords):
            if cat == 'Jeans':
                if any(kw in name_str for kw in ['slim']):
                    return "Jeans - Slim Fit"
                if any(kw in name_str for kw in ['regular']):
                    return "Jeans - Regular Fit"
                if any(kw in name_str for kw in ['straight']):
                    return "Jeans - Straight Fit"
            return cat
    
    # Special handling for T-Shirts and Shirts (Sleeve Logic)
    fs_keywords = ['full sleeve', 'long sleeve', 'fs', 'l/s']
    is_fs = any(kw in name_str for kw in fs_keywords)
    
    if any(kw in name_str for kw in ['t-shirt', 't shirt', 'tee']):
        return 'T-Shirt - FS T-Shirt' if is_fs else 'T-Shirt - HS T-Shirt'
    if 'shirt' in name_str:
        return 'FS Shirt' if is_fs else 'HS Shirt - HS Casual Shirt'
        
    return 'Others'

def apply_category_expert_rules(df: pd.DataFrame, name_col: str = "item_name") -> pd.DataFrame:
    """Applies the mapping to a dataframe and adds a 'Category' column."""
    if df.empty or name_col not in df.columns:
        return df
    df['Category'] = df[name_col].apply(get_product_category)
    return df
