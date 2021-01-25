#!/usr/bin/env python
# coding: utf-8

# In[45]:


# original implementation
def recursive_helper(step_left ,choices):
    count = 0
    for step in choices:
        if step == step_left:
            count += 1
        elif step > step_left:
            continue
        else:
            count += recursive_helper (step_left - step, choices)
    return count

def number_of_steps( n , choices):
    count = recursive_helper (n,choices)
    return count


# In[46]:


choices = [1,2,4]
steps = 6
print (number_of_steps(steps,choices))


# In[47]:


# after some research online, discovered that the performance can be improved by implementing cache
def number_of_steps_withcache( n , choices):
    cache = [None] * (n+1)
    count = recursive_helper_withcache (n,choices,cache)
    return count

def recursive_helper_withcache(step_left ,choices,cache):
    if cache[step_left] != None:
        count = cache[step_left]
    else:
        count = 0
        for step in choices:
            if step == step_left:
                count += 1
            elif step > step_left:
                continue
            else:
                count += recursive_helper_withcache (step_left - step, choices,cache)
        cache[step_left] = count
    return count


# In[48]:


choices = [1,2,4]
steps = 6
print (number_of_steps_withcache(steps,choices))

