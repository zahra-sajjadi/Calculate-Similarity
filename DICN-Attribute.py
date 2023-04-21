import pandas as pd
import networkx as nx
import math
import xlsxwriter
import time

st = time.time()

wb = xlsxwriter.Workbook('Indirect-DICN2.xlsx')
ws = wb.add_worksheet()

ws.write(0, 0, 'node1')
ws.write(0, 1, 'node2')
ws.write(0, 2, 'Sim-Attribe-Weight')

wb2 = xlsxwriter.Workbook('Direct-DICN2.xlsx')
ws2 = wb2.add_worksheet()

ws2.write(0, 0, 'node1')
ws2.write(0, 1, 'node2')
ws2.write(0, 2, 'Sim-Attribe-Weight')

wb3 = xlsxwriter.Workbook('Disconnect-DICN2.xlsx')
ws3 = wb3.add_worksheet()

ws3.write(0, 0, 'node1')
ws3.write(0, 1, 'node2')
ws3.write(0, 2, 'Sim-Attribe-Weight')

r = 1
m=1



g1 = pd.read_excel('New-OutPut3.xlsx')
g2 = pd.read_csv(r'result2.csv')

g1Columns = g1.columns

g1Graph = nx.from_pandas_edgelist(g1, g1Columns[0], g1Columns[1])
g2Graph = nx.from_pandas_edgelist(g2, 'auth1', 'auth2', edge_attr='num')

df_direct_connection = pd.read_excel('Direct-connection.xlsx')
df_indirect_connection = pd.read_excel('Indirect-connection.xlsx')
df_disconnect_connection = pd.read_excel('Disconnect-connection.xlsx')

s1 = set(g2['auth1']).union(set(g2['auth2']))
s2 = set(g1['auth'])

allNodes = list(s1.intersection(s2))

allNodes.sort()

numberOfElements = max(allNodes) + 1

dictOfNodesAndNeighbourArray = {currentNode: [0]*(numberOfElements) for currentNode in allNodes}

p = nx.shortest_path(g2Graph)

counter = 1

for currentNode in allNodes:

    dictOfNodesAndNeighbourArray[currentNode][currentNode] = g1Graph.degree(currentNode)

    for i in allNodes[counter:]:
        if p[currentNode].get(i, -1) != -1:
            path = p[currentNode][i]

            if len(path) > 2:
                currentValue = len(sorted(nx.common_neighbors(g1Graph, currentNode, i)))
                dictOfNodesAndNeighbourArray[currentNode][i] = currentValue
                dictOfNodesAndNeighbourArray[i][currentNode] = currentValue
            elif len(path) == 2:
                w = g2Graph.get_edge_data(currentNode, i)['num']
                currentValue = len(sorted(nx.common_neighbors(g1Graph, currentNode, i)))
                dictOfNodesAndNeighbourArray[currentNode][i] = currentValue + w
                dictOfNodesAndNeighbourArray[i][currentNode] = currentValue + w
        else:
            currentValue = len(sorted(nx.common_neighbors(g1Graph, currentNode, i)))
            dictOfNodesAndNeighbourArray[currentNode][i] = currentValue
            dictOfNodesAndNeighbourArray[i][currentNode] = currentValue

    counter += 1    

# for i in dictOfNodesAndNeighbourArray.items():
#     print(i)


for currentNode in allNodes:
    df = df_indirect_connection.query('auth1 == @currentNode')
    currentArrayIndirectNodes = list(set(df['auth2']))
    currentCommonNeighborsArray = dictOfNodesAndNeighbourArray[currentNode]

    for ComparisonNode in currentArrayIndirectNodes:
        try:
            ComparisonCommonNeighborsArray = dictOfNodesAndNeighbourArray[ComparisonNode]
        except:
            continue

        arrayNodes = []

        for i in range(1, len(currentCommonNeighborsArray)):
            if currentCommonNeighborsArray[i] or ComparisonCommonNeighborsArray[i] != 0:
                arrayNodes.append(i)

        Denominator = len(arrayNodes)

        sumOfCommonNeighborsCurrentNodeValue = sum(currentCommonNeighborsArray[1:])
        FractionValueFirstNode = round(sumOfCommonNeighborsCurrentNodeValue / Denominator, 2)

        sumOfCommonNeighborsIndirectNodeValue = sum(ComparisonCommonNeighborsArray[1:])
        FractionValueIndirectNode = round(sumOfCommonNeighborsIndirectNodeValue / Denominator, 2)

        sumOfUnionOfNeighborhoodIndirectNodes = 0
        a2 = 0
        b2 = 0

        for i in range(1, len(currentCommonNeighborsArray)):
            a = (currentCommonNeighborsArray[i] - FractionValueFirstNode)
            a2 += math.pow(a, 2)

            b = (ComparisonCommonNeighborsArray[i] - FractionValueIndirectNode)
            b2 += math.pow(b, 2)

            sumOfUnionOfNeighborhoodIndirectNodes += a*b

        sqA = math.sqrt(a2)
        sqB = math.sqrt(b2)
        multiple = (sqA) * (sqB)

        if multiple != 0:
            CorrelationCoefficient = round(sumOfUnionOfNeighborhoodIndirectNodes / multiple, 2)

        # common_nbor = len(set([n for n in g1Graph.neighbors(currentNode)]).intersection(
        #     set([n for n in g1Graph.neighbors(ComparisonNode)])))
        num = 0
        DICN = (1 + num) * (1 + CorrelationCoefficient) /m

        ws.write(r, 0, currentNode)
        ws.write(r, 1, ComparisonNode)
        ws.write(r, 2, DICN)

        r += 1
        
wb.close()   


r = 1

for currentNode in allNodes:
   df = df_direct_connection.query('auth1 == @currentNode')
   currentArrayDirectNodes = list(set(df['auth2']))
   currentCommonNeighborsArray = dictOfNodesAndNeighbourArray[currentNode]

   for ComparisonNode in currentArrayDirectNodes:
       try:
           ComparisonCommonNeighborsArray = dictOfNodesAndNeighbourArray[ComparisonNode]
       except:
           continue

       arrayNodes = []

       for i in range(1, len(currentCommonNeighborsArray)):
           if currentCommonNeighborsArray[i] or ComparisonCommonNeighborsArray[i] != 0:
               arrayNodes.append(i)

       Denominator = len(arrayNodes)

       sumOfCommonNeighborsCurrentNodeValue = sum(currentCommonNeighborsArray[1:])
       FractionValueFirstNode = round(sumOfCommonNeighborsCurrentNodeValue / Denominator, 2)

       sumOfCommonNeighborsDirectNodeValue = sum(ComparisonCommonNeighborsArray[1:])
       FractionValueDirectNode = round(sumOfCommonNeighborsDirectNodeValue / Denominator, 2)

       sumOfUnionOfNeighborhoodDirectNodes = 0
       a2 = 0
       b2 = 0

       for i in range(1, len(currentCommonNeighborsArray)):
           a = (currentCommonNeighborsArray[i] - FractionValueFirstNode)
           a2 += math.pow(a, 2)

           b = (ComparisonCommonNeighborsArray[i] - FractionValueDirectNode)
           b2 += math.pow(b, 2)

           sumOfUnionOfNeighborhoodDirectNodes += a*b

       sqA = math.sqrt(a2)
       sqB = math.sqrt(b2)
       multiple = (sqA) * (sqB)

       if multiple != 0:
           
           CorrelationCoefficient = round(sumOfUnionOfNeighborhoodDirectNodes / multiple, 2)

       # common_nbor = len(set([n for n in g1Graph.neighbors(currentNode)]).intersection(
       #     set([n for n in g1Graph.neighbors(ComparisonNode)])))
       num = g2Graph.get_edge_data(currentNode, ComparisonNode)['num']
       DICN = (1 + num) * (1 + CorrelationCoefficient) / m

       ws2.write(r, 0, currentNode)
       ws2.write(r, 1, ComparisonNode)
       ws2.write(r, 2, DICN)

       r += 1

wb2.close()


r = 1

for currentNode in allNodes:
   df = df_disconnect_connection.query('auth1 == @currentNode')
   currentArrayDisconnectNodes = list(set(df['auth2']))
   currentCommonNeighborsArray = dictOfNodesAndNeighbourArray[currentNode]

   for ComparisonNode in currentArrayDisconnectNodes:
       try:
           ComparisonCommonNeighborsArray = dictOfNodesAndNeighbourArray[ComparisonNode]
       except:
           continue
           
       arrayNodes = []

       for i in range(1, len(currentCommonNeighborsArray)):
           if currentCommonNeighborsArray[i] or ComparisonCommonNeighborsArray[i] != 0:
               arrayNodes.append(i)

       Denominator = len(arrayNodes)

       sumOfCommonNeighborsCurrentNodeValue = sum(currentCommonNeighborsArray[1:])
       FractionValueFirstNode = round(sumOfCommonNeighborsCurrentNodeValue / Denominator, 2)

       sumOfCommonNeighborsDisconnectNodeValue = sum(ComparisonCommonNeighborsArray[1:])
       FractionValueDisconnectNode = round(sumOfCommonNeighborsDisconnectNodeValue / Denominator, 2)

       sumOfUnionOfNeighborhoodDisconnectNodes = 0
       a2 = 0
       b2 = 0

       for i in range(1, len(currentCommonNeighborsArray)):
           a = (currentCommonNeighborsArray[i] - FractionValueFirstNode)
           a2 += math.pow(a, 2)

           b = (ComparisonCommonNeighborsArray[i] - FractionValueDisconnectNode)
           b2 += math.pow(b, 2)

           sumOfUnionOfNeighborhoodDisconnectNodes += a*b

       sqA = math.sqrt(a2)
       sqB = math.sqrt(b2)
       multiple = (sqA) * (sqB)

       if multiple != 0:
           
           CorrelationCoefficient = round(sumOfUnionOfNeighborhoodDisconnectNodes / multiple, 2)

       # common_nbor = len(set([n for n in g1Graph.neighbors(currentNode)]).intersection(
       #     set([n for n in g1Graph.neighbors(ComparisonNode)])))
       num = 0
       DICN = (1 + num) * (1 + CorrelationCoefficient) / m

       ws3.write(r, 0, currentNode)
       ws3.write(r, 1, ComparisonNode)
       ws3.write(r, 2, DICN)

       r += 1

wb3.close()

et = time.time()
print("Total Time= ",et-st)
##Total Time=  313.7326738834381   dblp-4000
##Total Time=  689.0732200145721   dblp-5000
##Total Time=  100.94166040420532      dblp-3000
##Total Time=  904.461484670639 pblog-full
##Total Time=  3.5186235904693604   dblp-1000
##Total Time=  15.867547750473022   pblog-250
##Total Time=  85.39042234420776     pblog-800
##Total Time=  9.203653573989868  pblog-200
##Total Time=  82.29248571395874  pblog-500
##Total Time=  196.37578535079956    pblog-1000
 ## Total Time=  17.98367714881897 citeseer -500rec

## Total Time=  3814.5086534023285
##Total Time=  164.98447966575623 citeseer -filtering
