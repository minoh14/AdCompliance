import asyncio
import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from twelvelabs import TwelveLabs
from concurrent.futures import ThreadPoolExecutor
from prompts import PROMPT_RELEVANCE, PROMPT_COMPLIANCE


load_dotenv()

# Create TwelveLabs client
client = TwelveLabs(api_key=os.getenv("TL_API_KEY"))
if not client:
    raise RuntimeError("Failed to create TwelveLabs client!")

# Create ThreadPoolExecutor for concurrent processing
executor = ThreadPoolExecutor(max_workers=int(os.getenv("MAX_WORKERS", 5)))
if not executor:
    raise RuntimeError("Failed to create ThreadPoolExecutor!")


# Retrieve index or create one
def create_index(index_name: str):
    indexes = client.indexes.list()
    index = next((idx for idx in indexes if idx.index_name == index_name), None)
    if index is None:
        index = client.indexes.create(
            index_name=index_name,
            models=[
                {"model_name": "marengo3.0", "model_options": ["visual", "audio"]},
                {"model_name": "pegasus1.2", "model_options": ["visual", "audio"]}
            ]
        )
        if not index.id:
            raise RuntimeError("Failed to create an index!")
        print(f"Index created: id={index.id}")
    else:
        print(f"Index already exists: id={index.id} for {index_name}")
    return index


# Upload video file and wait for asset to be ready
def _upload(video_file: Path):
    print(f"Uploading video file: {video_file.name}")
    asset = client.assets.create(method="direct", file=open(video_file, "rb"))
    while True:
        asset = client.assets.retrieve(asset.id)
        if asset.status == "ready":
            break
        elif asset.status == "failed":
            raise RuntimeError(f"Asset processing failed: id={asset.id}")
        time.sleep(5)
    print(f"Asset created: id={asset.id} for file {video_file.name}")
    return asset


# Upload video file if not already uploaded
async def upload_video_file(video_file: Path):
    assets = client.assets.list()
    asset = next((a for a in assets if a.filename == video_file.name), None)
    if asset is None:
        loop = asyncio.get_event_loop()
        asset = await loop.run_in_executor(executor, _upload, video_file)
    else:
        print(f"Asset already exists: id={asset.id} for file {video_file.name}")
    return asset


# Index asset and wait for indexed asset to be ready
def _index(index, asset):
    indexed_asset = client.indexes.indexed_assets.create(
        index_id=index.id,
        asset_id=asset.id,
        enable_video_stream=True
    )
    while True:
        indexed_asset = client.indexes.indexed_assets.retrieve(
            index_id=index.id,
            indexed_asset_id=indexed_asset.id
        )
        if indexed_asset.status == "ready":
            break
        elif indexed_asset.status == "failed":
            raise RuntimeError(f"Indexing failed: id={indexed_asset.id}")
        time.sleep(5)
    print(f"Indexed asset created: id={indexed_asset.id} for asset {asset.id}")
    return indexed_asset


# Index video file if not already indexed
async def index_video_file(index, asset):
    indexed_assets = client.indexes.indexed_assets.list(index.id)
    indexed_asset = next((a for a in indexed_assets if a.asset_id == asset.id), None)
    if indexed_asset is None:
        loop = asyncio.get_event_loop()
        indexed_asset = await loop.run_in_executor(executor, _index, index, asset)
    else:
        print(f"Indexed asset already exists: id={indexed_asset.id} for asset {asset.id}")
    return indexed_asset


# Analyze indexed asset for campaign relevance and retrieve description
def _detect_campaign_relevance(indexed_asset):
    text = client.analyze(
        video_id=indexed_asset.id,
        prompt=PROMPT_RELEVANCE
    )
    return text.data


# Analyze indexed asset for campaign relevance and retrieve description
async def detect_campaign_relevance(filename: str, indexed_asset):
    print("Detecting campaign relevance...")
    loop = asyncio.get_event_loop()
    result_raw = await loop.run_in_executor(executor, _detect_campaign_relevance, indexed_asset)
    result = json.loads(result_raw)

    if result["is_relevant"].upper() == "YES":
        relevance = "ON-BRIEF"
    else:
        relevance = "OFF-BRIEF"

    return {
        "filename": filename,
        "asset_id": indexed_asset.asset_id,
        "indexed_asset_id": indexed_asset.id,
        "campaign_relevance": relevance,
        "relevance_score": result["score"],
        "video_description": result["summary"],
        "transcription": {
            "spoken": result["transcription"]["spoken"],
            "on_screen_text": result["transcription"]["on_screen_text"]
        }
    }


def _analyze_compliance(indexed_asset):
    text = client.analyze(
        video_id=indexed_asset.id,
        prompt=PROMPT_COMPLIANCE
    )
    return text.data


async def analyze_compliance(indexed_asset):
    print("Analyzing compliance risks...")
    loop = asyncio.get_event_loop()
    result_raw = await loop.run_in_executor(executor, _analyze_compliance, indexed_asset)
    return json.loads(result_raw)


# Process a single video file
async def process_video_file(video_file: Path, index, semaphore):
    async with semaphore:
        print(f"Processing file: {video_file.name}")
        try:
            asset = await upload_video_file(video_file)
            indexed_asset = await index_video_file(index, asset)
            result = await detect_campaign_relevance(video_file.name, indexed_asset)

            if result["campaign_relevance"] == "OFF-BRIEF":
                result["decision"] = "BLOCK"
                result["decision_reason"] = "Video is off-brief and not relevant to the campaign."
                result["violations"] = []
            else:
                compliance = await analyze_compliance(indexed_asset)
                result["decision"] = compliance["decision"]
                result["decision_reason"] = compliance["decision_reason"]
                result["violations"] = compliance["violations"]

            return result
        except Exception as e:
            print(f"Error processing {video_file.name}: {e}")


async def main():

    # Create index
    index = create_index(os.getenv("INDEX_NAME"))

    # Process video files concurrently
    video_files = list(Path(os.getenv("VIDEO_FOLDER_PATH")).glob("*.mp4"))
    print(f"Found {len(video_files)} video files to process.")
    semaphore = asyncio.Semaphore(int(os.getenv("MAX_WORKERS", 5)))
    results = await asyncio.gather(
        *[process_video_file(video_file, index, semaphore) for video_file in video_files]
    )

    # Print results
    for result in results:
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
