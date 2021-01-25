#!/usr/bin/env python
# coding: utf-8

# question: What if a person can climb any number from a set X, for example if X = {1,2,4}, then he/she
# can climb 1, 2 or 4 stairs at a time. How many ways he/she can climb from bottom to top?


# original implementation
from time import process_time_ns


def recursive_helper(step_left, choices):
    count = 0
    for step in choices:
        if step == step_left:
            count += 1
        elif step > step_left:
            continue
        else:
            count += recursive_helper(step_left - step, choices)
    return count


def number_of_steps(n, fn_choices):
    count = recursive_helper(n, fn_choices)
    return count


# after some research online, discovered that the performance can be improved by implementing cache
def number_of_steps_with_cache(n, fn_choices):
    cache = [None] * (n + 1)
    count = recursive_helper_with_cache(n, fn_choices, cache)
    return count


def recursive_helper_with_cache(step_left, fn_choices, cache):
    if cache[step_left] is not None:
        count = cache[step_left]
    else:
        count = 0
        for step in fn_choices:
            if step == step_left:
                count += 1
            elif step > step_left:
                continue
            else:
                count += recursive_helper_with_cache(step_left - step, fn_choices, cache)
        cache[step_left] = count
    return count


# In[48]:
# one can climb either 1, 2 or 4 steps
choices = [1, 2, 4]
# the stairs are 40 steps high
steps = 30

ns = process_time_ns()
print("Number of combinations with cache: " + str(number_of_steps_with_cache(steps, choices)))
# process too quick that the time elapsed is not correctly captured
print("With Cache elapsed time: " + str((process_time_ns() - ns) / 1000000000) + " (s)")

ns = process_time_ns()
print("Number of combinations without cache: " + str(number_of_steps(steps, choices)))
print("Without Cache elapsed time: " + str((process_time_ns() - ns) / 1000000000) + " (s)")
