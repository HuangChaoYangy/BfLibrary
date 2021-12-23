userDic = {1: ['testuser0042','testuser004211'], 2: ['testuser0043'], 3: ['testuser0044'], 4: ['testuser0045'], 5: ['testuser0046'], 6: ['testuser0047']}
agent_list = []
for key in userDic:
    agent_list.extend(userDic[key])
print(agent_list)