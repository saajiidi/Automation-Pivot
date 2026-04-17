import pandas as pd
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from BackEnd.core.categories import get_category_for_sales, apply_category_expert_rules
from BackEnd.utils.sales_schema import ensure_sales_schema

try:
    print("Testing get_category_for_sales...")
    print(get_category_for_sales("FS Flannel Shirt"))
    
    print("\nTesting ensure_sales_schema...")
    df = pd.DataFrame({"Item Name": ["Denim Shirt"], "Order ID": ["123"], "Qty": [1], "Total": [100]})
    out = ensure_sales_schema(df)
    print(out[["item_name", "Category"]])
    
    print("\nSuccess!")
except Exception as e:
    print(f"\nCaught Error: {e}")
    import traceback
    traceback.print_exc()
