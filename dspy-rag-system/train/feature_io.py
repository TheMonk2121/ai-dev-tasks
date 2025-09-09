from pydantic import TypeAdapter

from dspy_modules.retriever.feature_schema import FusionFeatures

TA_FusionFeatures = TypeAdapter(FusionFeatures)


def read_feature(line: str) -> FusionFeatures:
    return TA_FusionFeatures.validate_json(line)


def write_feature(ff: FusionFeatures) -> str:
    # Array fields serialize to JSON lists via tolist()
    return ff.model_dump_json()
