
import os
import requests
import pandas as pd
from datetime import datetime, timezone
from google.cloud import bigquery

# ==================================================
# 1. CONFIGURATION
# ==================================================

PROJECT_ID = "promising-node-513006-f9"
DATASET_ID = "ecommerce"
TABLE_ID = "crypto_market"

TABLE_PATH = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

# Set your CoinGecko Demo API key as an environment variable.
# Windows PowerShell:
# $env:COINGECKO_API_KEY = "your_demo_api_key"
API_KEY = os.getenv("COINGECKO_API_KEY")

API_URL = "https://api.coingecko.com/api/v3/coins/markets"


# ==================================================
# 2. EXTRACT: FETCH DATA FROM COINGECKO API
# ==================================================

def extract_data():
    print("Starting data extraction...")

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": False
    }

    headers = {}
    if API_KEY:
        headers["x-cg-demo-api-key"] = API_KEY

    response = requests.get(
        API_URL,
        params=params,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()
    data = response.json()

    if not isinstance(data, list):
        raise ValueError("Unexpected API response format.")

    if not data:
        raise ValueError("The API returned no cryptocurrency records.")

    print(f"Extracted {len(data)} cryptocurrency records.")
    return data


# ==================================================
# 3. TRANSFORM: CLEAN AND PREPARE DATA
# ==================================================

def transform_data(data):
    print("Starting data transformation...")

    df = pd.json_normalize(data)

    required_columns = [
        "id",
        "symbol",
        "name",
        "current_price",
        "market_cap",
        "total_volume",
        "price_change_percentage_24h",
        "circulating_supply",
        "market_cap_rank"
    ]

    # Check that the API response contains expected fields.
    missing_columns = [
        col for col in required_columns if col not in df.columns
    ]
    if missing_columns:
        raise ValueError(
            f"Missing expected API columns: {missing_columns}"
        )

    df = df[required_columns].copy()

    df.rename(columns={
        "id": "coin_id",
        "name": "coin_name",
        "current_price": "price_usd",
        "market_cap": "market_cap_usd",
        "total_volume": "volume_24h_usd",
        "price_change_percentage_24h": "price_change_24h_pct"
    }, inplace=True)

    # Clean text fields.
    for col in ["coin_id", "symbol", "coin_name"]:
        df[col] = df[col].astype("string").str.strip()

    # Convert numeric fields to numeric data types.
    numeric_columns = [
        "price_usd",
        "market_cap_usd",
        "volume_24h_usd",
        "price_change_24h_pct",
        "circulating_supply",
        "market_cap_rank"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Remove records without a coin ID or valid current price.
    df.dropna(subset=["coin_id", "price_usd"], inplace=True)

    # Prices and market values cannot be negative.
    df = df[df["price_usd"] >= 0]
    df = df[
        df["market_cap_usd"].isna() | (df["market_cap_usd"] >= 0)
    ]
    df = df[
        df["volume_24h_usd"].isna() | (df["volume_24h_usd"] >= 0)
    ]

    # Keep one record per coin.
    df.drop_duplicates(subset=["coin_id"], keep="last", inplace=True)

    # Add UTC extraction timestamp.
    df["extracted_at"] = datetime.now(timezone.utc)

    # Use nullable integer type for rank.
    df["market_cap_rank"] = df["market_cap_rank"].astype("Int64")

    df.reset_index(drop=True, inplace=True)

    if df.empty:
        raise ValueError("No valid records remain after cleaning.")

    print(f"Rows after cleaning: {len(df)}")
    print("\nSample transformed data:")
    print(df.head())

    print("\nMissing values:")
    print(df.isnull().sum())

    return df


# ==================================================
# 4. LOAD: UPLOAD DATA TO GOOGLE BIGQUERY
# ==================================================

def load_data(df):
    print("\nConnecting to Google BigQuery...")

    # Uses Google Application Default Credentials.
    client = bigquery.Client(project=PROJECT_ID)

    job_config = bigquery.LoadJobConfig(
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
    )

    print(f"Loading data into {TABLE_PATH}...")

    job = client.load_table_from_dataframe(
        df,
        TABLE_PATH,
        job_config=job_config
    )

    job.result()

    table = client.get_table(TABLE_PATH)

    print(f"Successfully loaded {table.num_rows} rows.")
    print(f"BigQuery table: {TABLE_PATH}")


# ==================================================
# 5. MAIN ETL PIPELINE
# ==================================================

def main():
    try:
        raw_data = extract_data()
        clean_df = transform_data(raw_data)

        # Save a local CSV backup.
        clean_df.to_csv("crypto_market.csv", index=False)
        print("\nCSV backup saved: crypto_market.csv")

        # Load the transformed data to BigQuery.
        load_data(clean_df)

        print("\nETL pipeline completed successfully!")

    except requests.exceptions.HTTPError as error:
        print(f"API HTTP error: {error}")
        if error.response is not None:
            print("Response:", error.response.text[:1000])

    except requests.exceptions.RequestException as error:
        print(f"API connection error: {error}")

    except Exception as error:
        print(f"ETL pipeline failed: {type(error).__name__}: {error}")


if __name__ == "__main__":
    main()
