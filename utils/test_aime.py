import pandas as pd
from utils.aio import async_main, call_llm
from utils.verifier import compute_score
async def test_sample(sample):
    prompt = sample["prompt"][0]["content"]
    model_response = await call_llm(args.model, prompt, n=args.n)
    scores = [
        compute_score("", rsp.message.content, sample['reward_model']["ground_truth"])
        for rsp in model_response.choices
    ]
    rsps = [rsp.message.content for rsp in model_response.choices]
    sample["prompt"] = list(sample["prompt"])
    sample["scores"] = scores
    sample["responses"] = rsps
    return sum(scores) / len(scores)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="/mnt/hdfs/hongli/model/Qwen3-4B")
    parser.add_argument("--file", type=str, default="aime24.parquet")
    parser.add_argument("-o", type=str, default="test_output.jsonl")
    parser.add_argument("-n", type=int, default=4)
    args = parser.parse_args()
    df = pd.read_parquet(args.file)
    print(df.iloc[0])
    samples = df.to_dict(orient="records")
    tasks = [test_sample(sample) for sample in samples]
    import asyncio
    res = asyncio.run(async_main(tasks))
    print(sum(res) / len(res))
    import json
    with open(args.o, "w") as f:
        for sample in samples:
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")
