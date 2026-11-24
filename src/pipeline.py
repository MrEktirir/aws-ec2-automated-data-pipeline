import requests

API_URL = "https://dummyjson.com/products"

def extract():
    response = requests.get(
        API_URL,
        params={"limit": 0},
        timeout=30
    )
    response.raise_for_status()

    return response.json()


def transform(data):
    records = []

    for product in data["products"]:
        price = product.get("price")
        stock = product.get("stock")

        if price is None or stock is None:
            continue

        if price < 0 or stock < 0:
            continue

        records.append({
            "product_id": product["id"],
            "product_name": product["title"],
            "category": product["category"],
            "price": price,
            "stock": stock,
            "inventory_value": round(price * stock, 2)
        })

    return records


import boto3
import json
from datetime import datetime, timezone

BUCKET_NAME = "ec2-data-pipeline-mrektirir"


def load(raw_data, processed_data):
    s3 = boto3.client("s3", region_name="eu-central-1")

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%S%fZ"
    )

    datasets = {
        "raw": raw_data,
        "processed": processed_data
    }

    for layer, data in datasets.items():
        key = f"{layer}/{timestamp}/products.json"

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=json.dumps(data).encode("utf-8"),
            ContentType="application/json"
        )

        print(f"Uploaded: s3://{BUCKET_NAME}/{key}")


import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    logger.info("Pipeline started")

    try:
        raw_data = extract()
        logger.info(
            "Extracted %s products",
            len(raw_data["products"])
        )

        processed_data = transform(raw_data)
        logger.info(
            "Transformed %s products",
            len(processed_data)
        )

        load(raw_data, processed_data)

        logger.info("Pipeline completed successfully")

    except Exception:
        logger.exception("Pipeline failed")
        raise


if __name__ == "__main__":
    main()
