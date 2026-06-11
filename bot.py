message = """1. Prays
2. Study
3. Boxing"""

def parse_daily_goals(message):
    
    lines = message.splitlines()

    expected_number = 1
    is_valid = True
    goals = []

    for line in lines:
        
        if line[0] == str(expected_number) and line[1] == ".":


         parts = line.split(".")
         goal =  parts[1].strip()

         goals.append(goal)

         expected_number += 1

        else:
           is_valid = False
           print("Invalid submission")
           break
        
    return goals

result = parse_daily_goals(message)

print("calling function")  
print("I reached the end of the file")
print(result)


