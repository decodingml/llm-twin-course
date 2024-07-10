from typing import Any, Callable, Dict, List, Optional

import pandas as pd
from pydantic import BaseModel

from models.clean import CleanedModel


def pydantic_models_to_dataframe(
    models: List[BaseModel], index_column: Optional[str] = "id"
) -> pd.DataFrame:
    """
    Converts a list of Pydantic models to a Pandas DataFrame.

    Args:
    models (List[BaseModel]): List of Pydantic models.

    Returns:
    pd.DataFrame: DataFrame containing the data from the Pydantic models.
    """

    if not models:
        return pd.DataFrame()

    # Convert each model to a dictionary and create a list of dictionaries
    data = [model.model_dump() for model in models]

    # Create a DataFrame from the list of dictionaries
    df = pd.DataFrame(data)

    if index_column in df.columns:
        df["index"] = df[index_column]
    else:
        raise RuntimeError(f"Index column '{index_column}' not found in DataFrame.")

    return df


def group_by_type(documents: list[CleanedModel]) -> Dict[str, list[CleanedModel]]:
    return _group_by(documents, selector=lambda doc: doc.type)


def _group_by(documents: list[CleanedModel], selector: Callable) -> Dict[Any, list]:
    grouped = {}
    for doc in documents:
        key = selector(doc)

        if key not in grouped:
            grouped[key] = []
        grouped[key].append(doc)

    return grouped
