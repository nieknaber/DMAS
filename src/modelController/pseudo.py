

agentList = makeAgents(n) #ordered array of agent, where the index = ID = phoneNumber of agent

def solve() :
    i = 1

    while(not(allSecretsKnown(agentList))):
        for (x = i; x != i - 1; x += 1):
            if (not(alreadyCalled(agentList[x]))):
                determineCall(agentList[x], x * i)

        i += 1

#recursive function
def determineCall(agent, agentCallId):

    if(not(alreadyCalled(agentList[agentCallId]))):
        call(agent, agenList[agentCallId])

    determineCall(agent, agentCallId + 1)

