import ast
with open('limits.txt', 'r') as file:
    limits = ast.literal_eval(file.read())
for i in range(14):
    print(list(limits.keys())[i])
