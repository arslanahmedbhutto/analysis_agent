"""
Sample dataset generator matching the Pakistani E-Commerce retail dataset.
Used for quick testing and 1-click demos in the GUI.
"""

import pandas as pd
import numpy as np


def generate_sample_ecommerce_data(n: int = 500, random_seed: int = 42) -> pd.DataFrame:
    """Generates synthetic e-commerce sales dataset with 500 records."""
    np.random.seed(random_seed)

    cities = ["Karachi", "Lahore", "Islamabad", "Sukkur", "Multan"]
    categories = ["Laptop", "Phone", "Tablet", "Headphones", "Smartwatch"]
    channels = ["Online", "Retail Store", "Reseller"]

    prices = {
        "Laptop": 850,
        "Phone": 420,
        "Tablet": 300,
        "Headphones": 60,
        "Smartwatch": 150,
    }

    df = pd.DataFrame({
        "order_id": range(10001, 10001 + n),
        "date": pd.date_range("2024-01-01", periods=n, freq="D"),
        "city": np.random.choice(cities, n),
        "category": np.random.choice(categories, n),
        "channel": np.random.choice(channels, n, p=[0.5, 0.3, 0.2]),
        "units": np.random.randint(1, 15, n),
        "customer_age": np.random.randint(18, 65, n),
        "rating": np.round(np.random.uniform(2.0, 5.0, n), 1),
        "returned": np.random.choice([0, 1], n, p=[0.9, 0.1]),
    })

    df["unit_price"] = df["category"].map(prices)
    df["discount_pct"] = np.random.choice([0, 5, 10, 15, 20], n)
    df["revenue"] = (df["units"] * df["unit_price"] * (1 - df["discount_pct"] / 100)).round(2)
    df["month"] = df["date"].dt.strftime("%Y-%m")

    return df
