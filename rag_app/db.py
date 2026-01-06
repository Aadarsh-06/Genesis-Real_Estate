from sqlalchemy import create_engine, text
from pymongo import MongoClient
from config import POSTGRES_URI, MONGO_URI

pg_engine = create_engine(POSTGRES_URI)

mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["rag_db"]
explanations_col = mongo_db["property_explanations"]


def fetch_properties(sql_query: str, params: dict):
    with pg_engine.connect() as conn:
        result = conn.execute(text(sql_query), params)
        return [dict(row) for row in result]


def fetch_explanations(property_ids: list[int]):
    cursor = explanations_col.find(
        {"property_id": {"$in": property_ids}},
        {"_id": 0}
    )
    return list(cursor)
