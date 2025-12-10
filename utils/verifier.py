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
    if grade_answer_verl(solution_str, ground_truth):
        return 1.0
    return -1.0

if __name__ == "__main__":
    reward = verify(model_response="<think> I am omniscient. </think> The answer is \\boxed{24 + 14*x + (-13)*x^2 - 2*x^3 + x^4}.", ground_truth="$x^{4}-2 x^{3}-13 x^{2}+14 x+24$")
    print(reward)
    print(compute_score_no_think(
        data_source="",
        solution_str="To find the sum of all integer bases \\( b > 9 \\) for which \\( 17_b \\) is a divisor of \\( 97_b \\), we first need to understand the values of these numbers in base 10. The number \\( 17_b \\) in base \\( b \\) is equal to \\( 1 \\cdot b + 7 = b + 7 \\) in base 10. Similarly, the number \\( 97_b \\) in base \\( b \\) is equal to \\( 9 \\cdot b + 7 = 9b + 7 \\) in base 10. We need to find the values of \\( b \\) such that \\( b + 7 \\) is a divisor of \\( 9b + 7 \\). This can be written as:\n\\[ 9b + 7 = k(b + 7) \\]\nfor some integer \\( k \\). Rearranging the equation, we get:\n\\[ 9b + 7 = kb + 7k \\]\n\\[ 9b - kb = 7k - 7 \\]\n\\[ b(9 - k) = 7(k - 1) \\]\n\\[ b = \\frac{7(k - 1)}{9 - k} \\]\nSince \\( b \\) must be an integer greater than 9, \\( \\frac{7(k - 1)}{9 - k} \\) must be an integer greater than 9. We need to find the values of \\( k \\) that satisfy this condition. Let's test some values of \\( k \\):\n\n1. If \\( k = 10 \\):\n\\[ b = \\frac{7(10 - 1)}{9 - 10} = \\frac{63}{-1} = -63 \\] (not valid since \\( b > 9 \\))\n\n2. If \\( k = 8 \\):\n\\[ b = \\frac{7(8 - 1)}{9 - 8} = \\frac{49}{1} = 49 \\] (valid since \\( b > 9 \\))\n\n3. If \\( k = 7 \\):\n\\[ b = \\frac{7(7 - 1)}{9 - 7} = \\frac{42}{2} = 21 \\] (valid since \\( b > 9 \\))\n\n4. If \\( k = 6 \\):\n\\[ b = \\frac{7(6 - 1)}{9 - 6} = \\frac{35}{3} \\] (not an integer)\n\n5. If \\( k = 5 \\):\n\\[ b = \\frac{7(5 - 1)}{9 - 5} = \\frac{28}{4} = 7 \\] (not valid since \\( b > 9 \\))\n\n6. If \\( k = 4 \\):\n\\[ b = \\frac{7(4 - 1)}{9 - 4} = \\frac{21}{5} \\] (not an integer)\n\n7. If \\( k = 3 \\):\n\\[ b = \\frac{7(3 - 1)}{9 - 3} = \\frac{14}{6} \\] (not an integer)\n\n8. If \\( k = 2 \\):\n\\[ b = \\frac{7(2 - 1)}{9 - 2} = \\frac{7}{7} = 1 \\] (not valid since \\( b > 9 \\))\n\n9. If \\( k = 1 \\):\n\\[ b = \\frac{7(1 - 1)}{9 - 1} = \\frac{0}{8} = 0 \\] (not valid since \\( b > 9 \\))\n\nFrom the above, the valid values of \\( b \\) are 49 and 21. The sum of these values is:\n\\[ 49 + 21 = 70 \\]\nThus, the sum of all integer bases \\( b > 9 \\) for which \\( 17_b \\) is a divisor of \\( 97_b \\) is \\(\\boxed{70}\\).",
        ground_truth="70"
    ))
