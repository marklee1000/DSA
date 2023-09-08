#!/usr/bin/env python
# coding: utf-8

# Create a program using python that will fill-up an array with 10 dimensions of type character and will print the following:
# 
# 1. Number of letters 
# 
# 2. Number digits
# 
# 3. Word Count
# 
# 4. If terminated by period
# 
# 5. Print in reverse order
# 
# Sample list: ['word', 'we', 'you', '123.', 'a123b', 'a', 'A', '12', 'bH0.cKz$', 'skl.']

# In[40]:


inp = []
lett = 0
num = 0
word = 0
period = 0
for i in range (0,10):
    user = input("Enter here: ")
    if user.isalpha():
        if len(user)>1:
            word += 1
    if user[-1] == '.':
        period += 1
    inp.append(user)
for x in inp:
    for char in x:
        if char.isalpha():
            lett += 1
        elif char.isdigit():
            num += 1
print(f"\nThere are {lett} letters in the array you entered.")
print(f"There are {num} digits in the array you entered.")
print(f"There are {word} words in the array you entered.")
print(f"There are {period} inputs in the array that are terminated by a period.")
print(f"Here is your entered array but in reverse:\n")
for n in range(9,-1,-1):
    print(inp[n])


# In[ ]:




