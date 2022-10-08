import json
from elasticsearch import AsyncElasticsearch
import aiofiles


async def create_es_index(elastic: AsyncElasticsearch, index_name: str, mapping_file: str):
    async with aiofiles.open(mapping_file, "r") as r_f:
        index_def = json.loads(await r_f.read())
    await elastic.indices.create(index=index_name, body=index_def)
