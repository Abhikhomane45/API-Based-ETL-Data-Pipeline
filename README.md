<h1 align="center" style="font-size: 200%;">API-Based ETL Data Pipeline</h1>

<p align="center" style="font-size: 125%;">
  <strong>API-based ETL pipelines that extract cryptocurrency and product data, clean it, and load analytical datasets into Google BigQuery.</strong>
</p>

---

## Project Overview

This repository implements API-based ETL workflows using Python and Pandas. The primary pipeline retrieves live cryptocurrency market data from the CoinGecko API, cleans the response, saves a CSV backup, and loads the processed records into Google BigQuery. The Jupyter notebook also demonstrates a separate DummyJSON product workflow that extracts product records from `https://dummyjson.com/products`, transforms them into a clean dataset, and saves `cleaned_products.csv`. The repository includes SQL queries for common analysis.

## Data Flow

```text
CoinGecko API                         DummyJSON API
     |                                      |
     | Extract cryptocurrency JSON          | Extract product JSON
     v                                      v
Python / Pandas ----------------------> Python / Pandas
     |                                      |
     | Validate, clean, deduplicate          | Flatten, select, and clean fields
     v                                      v
crypto_market.csv + BigQuery          cleaned_products.csv
     |                                      |
     `-------------- SQL analysis ---------'
```

## Features

- Fetches the top 100 cryptocurrencies by market capitalization.
- Uses the optional CoinGecko Demo API key for authenticated requests.
- Validates required API fields and response formats.
- Converts values to appropriate numeric and nullable integer types.
- Removes invalid prices, duplicate coin identifiers, and incomplete records.
- Adds a UTC extraction timestamp to every record.
- Saves processed data locally as `crypto_market.csv`.
- Loads data into BigQuery using write-truncate behavior.
- Includes SQL queries for ranking, filtering, and duplicate analysis.
- Extracts product data from the public DummyJSON Products API in the notebook.
- Exposes cleaned product fields for category, price, discount, rating, stock, brand, and availability analysis.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | ETL orchestration |
| Requests | API data extraction |
| Pandas | Data transformation and validation |
| Google BigQuery | Cloud data warehouse |
| Google Cloud BigQuery SDK | Data loading and table management |
| PyArrow | Efficient DataFrame serialization |
| SQL | Data analysis |
| Jupyter Notebook | Interactive extraction and transformation exploration |
| DummyJSON | Public product data API |

## Project Structure

```text
API-Based-ETL-Data-Pipeline/
|-- main.py                # ETL pipeline implementation
|-- main.ipynb             # Interactive notebook
|-- queries.sql            # BigQuery analysis queries
|-- crypto_market.csv      # Latest processed API data
|-- cleaned_products.csv   # Example product dataset
|-- requirements.txt       # Python dependencies
|-- .gitignore             # Ignored local and environment files
`-- README.md              # Project documentation
```

## Dataset Schema

The transformed cryptocurrency table contains the following columns:

| Column | Description |
|---|---|
| `coin_id` | Unique CoinGecko cryptocurrency identifier |
| `symbol` | Cryptocurrency ticker symbol |
| `coin_name` | Human-readable cryptocurrency name |
| `price_usd` | Current USD price |
| `market_cap_usd` | Current USD market capitalization |
| `volume_24h_usd` | USD trading volume in the last 24 hours |
| `price_change_24h_pct` | Percentage price change in the last 24 hours |
| `circulating_supply` | Circulating supply of the cryptocurrency |
| `market_cap_rank` | Ranking by market capitalization |
| `extracted_at` | UTC extraction timestamp |

The DummyJSON notebook produces a product dataset with fields such as:

| Column | Description |
|---|---|
| `product_id` | DummyJSON product identifier |
| `product_name` | Product title |
| `category` | Product category |
| `price` | Product price |
| `discount_percentage` | Discount percentage |
| `rating` | Product rating |
| `stock` | Available inventory |
| `brand` | Product brand |
| `availability_status` | Stock availability status |

## Setup

### Prerequisites

- Python 3.9 or newer
- A Google Cloud project with BigQuery enabled
- Google Application Default Credentials configured
- A CoinGecko API key (optional for basic demo access)

### Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### Configure environment variables

Set the optional CoinGecko API key in PowerShell:

```powershell
$env:COINGECKO_API_KEY = "your_demo_api_key"
```

Configure Google Cloud credentials for the current shell:

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\path\to\service-account.json"
```

Before running the pipeline, update `PROJECT_ID`, `DATASET_ID`, and `TABLE_ID` in `main.py` if they differ from your BigQuery resources.

## Run the Pipeline

```powershell
python main.py
```

The pipeline will:

1. Call the CoinGecko markets endpoint.
2. Validate and transform the returned records.
3. Save `crypto_market.csv` in the project directory.
4. Replace the target BigQuery table with the cleaned data.
5. Print progress and execution status to the terminal.

### Run the DummyJSON Notebook

Open `main.ipynb` in Jupyter or VS Code and run the notebook cells in order. The notebook:

1. Requests product records from `https://dummyjson.com/products`.
2. Normalizes the nested product response.
3. Renames fields and selects analysis-ready columns.
4. Converts relevant fields to numeric types.
5. Saves the cleaned output to `cleaned_products.csv`.

The notebook does not require an API key for the public DummyJSON endpoint.

## Example Analysis

Run the queries in `queries.sql` from the BigQuery console or editor to:

- Count the loaded cryptocurrency records.
- Find the ten largest coins by market capitalization.
- Identify coins with positive 24-hour price movement.
- Check for duplicate coin IDs.
- Analyze product categories in the example product dataset.

The default destination is:

```text
promising-node-513006-f9.ecommerce.crypto_market
```

## Outputs

- **Cloud destination:** Google BigQuery cryptocurrency table
- **Local cryptocurrency backup:** `crypto_market.csv`
- **Local product dataset:** `cleaned_products.csv`
- **Transformation sample:** Prints cleaned rows and missing-value counts
- **Execution log:** Printed API, cleaning, loading, and error status

## Error Handling

The pipeline reports HTTP, network, API-format, validation, and general execution failures without stopping the surrounding Python process with an uncaught exception.

## Security Notes

- Never commit service account credentials or API keys.
- Store secrets in environment variables or Google Secret Manager.
- Keep generated CSV and credential files outside version control.
