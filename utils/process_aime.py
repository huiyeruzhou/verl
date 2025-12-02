# Copyright 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Preprocess the GSM8k dataset to parquet format
"""

import argparse
import os
import re

import datasets

from verl.utils.hdfs_io import copy, makedirs


def extract_solution(solution_str):
    if isinstance(solution_str, int):
        return str(solution_str)
    solution_str = solution_str.replace("\\boxed{", "").replace("}", "")
    return str(solution_str)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    args.local_dir = "/mnt/hdfs/hongli/projects/verl_demo/data/"
    args.hdfs_dir = None
    args.local_dataset_path = None



    for data_source, dataname in [
        ("math-ai/aime24", "aime24"),
        ("math-ai/aime25", "aime25"),
        ("ByteDance-Seed/BeyondAIME", "aime_beyond"),
    ]:

        dataset = datasets.load_dataset(data_source)
        if "train" in dataset:
            train_dataset = dataset["train"]
        else:
            train_dataset = None
        test_dataset = dataset["test"]

        PE = "{problem} Let's think step by step and output the final answer within \\boxed{{}}."

        # add a row to each data item that represents a unique id
        def process_fn(example, idx):
            question_raw = example.pop("problem")

            question = PE.format(problem=question_raw)

            answer_raw = example.pop("solution", None)
            if answer_raw is None:
                answer_raw = example.pop("answer")
            solution = extract_solution(answer_raw)
            data = {
                "data_source": dataname,
                "prompt": [
                    {
                        "role": "user",
                        "content": question,
                    }
                ],
                "ability": "math",
                "reward_model": {"style": "rule", "ground_truth": solution},
                "extra_info": {
                    "split": "test",
                    "index": idx,
                    # "answer": answer_raw,
                    "question": question_raw,
                },
            }
            return data



        test_dataset = test_dataset.map(function=process_fn, with_indices=True, remove_columns=test_dataset.column_names)

        hdfs_dir = args.hdfs_dir
        local_save_dir = args.local_dir

        test_dataset.to_parquet(os.path.join(local_save_dir, f"{dataname}.parquet"))

        print(f"Preprocessed dataset saved to {local_save_dir}")

    import datasets
    a = datasets.load_dataset("parquet", data_files="/mnt/hdfs/hongli/projects/verl_demo/data/aime24.parquet")["train"]
    b = datasets.load_dataset("parquet", data_files="/mnt/hdfs/hongli/projects/verl_demo/data/aime25.parquet")["train"]
    d = datasets.load_dataset("parquet", data_files="/mnt/hdfs/hongli/projects/verl_demo/data/aime_beyond.parquet")["train"]
    c = datasets.concatenate_datasets([a, b, d])
    print(c[0])
