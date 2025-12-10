"""
This module contains the RewardMathFn class, which evaluates mathematical answers
and assigns rewards based on their correctness. It utilizes a language model to 
validate answers when necessary.
"""
from typing import List, Union

from utils.mathutils import extract_answer, grade_answer_verl


THOUGHT_DELIMITER_END = "</think>"
def verify(model_response, ground_truth) -> float:
    if THOUGHT_DELIMITER_END in model_response:
        model_solution = model_response.split(THOUGHT_DELIMITER_END)[1]
    else:
        return -1.0

    if grade_answer_verl(model_response, ground_truth):
        return 1.0
    return -1.0

# custom_reward_function.path=/opt/tiger/open_verl/utils/verifier.py \
def compute_score(data_source, solution_str, ground_truth, extra_info=None, **extra_reward_kwargs):
    return verify(solution_str, ground_truth)

def compute_score_no_think(data_source, solution_str, ground_truth, extra_info=None, **extra_reward_kwargs):
    if grade_answer_verl(model_response, ground_truth):
        return 1.0
    return -1.0

if __name__ == "__main__":
    reward = verify(model_response="<think> I am omniscient. </think> The answer is \\boxed{24 + 14*x + (-13)*x^2 - 2*x^3 + x^4}.", ground_truth="$x^{4}-2 x^{3}-13 x^{2}+14 x+24$")
    print(reward)
