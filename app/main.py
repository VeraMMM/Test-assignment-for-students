from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from .data_loader import load_csv
from .calculations import process_gnss_dataframe
from .query_engine import QueryEngine
from pathlib import Path
import logging
from .llm_client import LLMClient
from dotenv import load_dotenv
from .response_builder import build_response

load_dotenv()

llm = LLMClient()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)

RESULT_COLUMNS = [
    "_timestamp_local",
    "latitude",
    "longitude",
    "horizontal_speed",
    "acceleration"
]


def format_result(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    return df[RESULT_COLUMNS]

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "data.csv"

app = FastAPI()

df = load_csv(DATA_PATH)
df = process_gnss_dataframe(df)
logger.info(f"Data loaded successfully. Rows count: {len(df)}")

engine = QueryEngine.default()

class QueryRequest(BaseModel):
    query: str


@app.post("/query")
async def query_data(request: QueryRequest):
    try:
        logger.info(f"Received query: {request.query}")

        action = await llm.classify_query(request.query)
        logger.info(f"LLM classified as: {action}")
        # NaN из-за ускорения убираем еще в выч, иначе гео падает
        # формат вывода, гео 800+ не вар
        result_df = engine.run(action, df)
        # result_df = format_result(result_df)
        #result = build_response(action, result_df, df)
        response_data = build_response(action, result_df, df)

        return {
            "status": "success",
            "query": request.query,
            "result": response_data
        }

    except ValueError as e:
        logger.warning(f"Invalid query: {request.query}")
        return {
            "status": "error",
            "message": str(e)
        }
    except Exception as e:
        logger.exception("Unexpected server error")
        return {
            "status": "error",
            "message": str(e)
        }


@app.get("/health")
def health():
    return {"status": "ok"}