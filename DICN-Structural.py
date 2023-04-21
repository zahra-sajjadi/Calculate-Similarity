import math
import pandas as pd
import networkx as nx
import xlsxwriter
import time
st=time.time()


wb = xlsxwriter.Workbook('Indirect-DICN.xlsx')
ws = wb.add_worksheet()

ws.write(0, 0, 'node1')
ws.write(0, 1, 'node2')
ws.write(0, 2, 'Sim-Struct-Weight')

wb2 = xlsxwriter.Workbook('Direct-DICN.xlsx')
ws2 = wb2.add_worksheet()

ws2.write(0, 0, 'node1')
ws2.write(0, 1, 'node2')
ws2.write(0, 2, 'Sim-Struct-Weight')

wb3 = xlsxwriter.Workbook('Disconnect-DICN.xlsx')
ws3 = wb3.add_worksheet()

ws3.write(0, 0, 'node1')
ws3.write(0, 1, 'node2')
ws3.write(0, 2, 'Sim-Struct-Weight')

r = 1

data = pd.read_csv(r'result2.csv')
graph = nx.from_pandas_edgelist(data, 'auth1', 'auth2', edge_attr='num')

len_path = dict(nx.all_pairs_dijkstra_path_length(graph, weight='num'))

p = nx.shortest_path(graph)

allNodes = list(p.keys())
finalArray = {}
dictIndirectNodes = {}
dictDirectNodes = {}

for d in p.items():
    indirectNodes = []
    directNodes = []
    currentKey = d[0]
    arrayComNe = [0]*(max(allNodes)+1)
    nodeDictionary = {
        'node': currentKey,
        'commonNeighborsArray': arrayComNe
    }

    # print('paths: ', d)

    arrayComNe[currentKey] = graph.degree(currentKey, 'num')

    for i in allNodes:
        ConnectionType = ''
        
        if d[1].get(i, -1) != -1:
            path = d[1][i]

            if len(path) > 2:
                ConnectionType = 'Indirect'
                arrayComNe[i] = len_path[currentKey][i]
                indirectNodes.append(i)
            elif len(path) == 2:
                ConnectionType = 'Direct'
                arrayComNe[i] = graph.get_edge_data(currentKey, i)['num']
                directNodes.append(i)
                
            # print('paths from node {} to node {}'.format(currentKey, i))
            # print(path)
            # print(ConnectionType)

        else:
            ConnectionType = 'Disconnect'
            arrayComNe[i] = 0   
            ws3.write(r, 0, currentKey)
            ws3.write(r, 1, i)
            ws3.write(r, 2, 0)
            r += 1
            # print('There is no path between {} and {}'.format(currentKey, i))
            # print(ConnectionType)

    dictIndirectNodes[currentKey] = {
        'indirectNodes': indirectNodes
    }
    dictDirectNodes[currentKey] = {
        'directNodes': directNodes
    }
    finalArray[currentKey] = nodeDictionary

wb3.close()

# for i in finalArray.items():
#     print(i)


# for i in dictIndirectNodes.items():
#     print(i)

# for i in dictDirectNodes.items():
#     print(i)    


r = 1

for i in dictIndirectNodes.keys():
    currentNode = i
    currentArrayIndirectNodes = dictIndirectNodes[currentNode]['indirectNodes']
    currentCommonNeighborsArray = finalArray[i]['commonNeighborsArray']
    for j in currentArrayIndirectNodes:
        ComparisonNode = j
        ComparisonCommonNeighborsArray = finalArray[j]['commonNeighborsArray']
        arrayNodes = []
        for k in range(1, len(currentCommonNeighborsArray)):
            if currentCommonNeighborsArray[k] or ComparisonCommonNeighborsArray[k] != 0:
                arrayNodes.append(k)
        Denominator = len(arrayNodes)
        sumOfCommonNeighborsCurrentNodeValue = sum(
            currentCommonNeighborsArray[1:])
        FractionValueFirstNode = round(
            sumOfCommonNeighborsCurrentNodeValue / Denominator, 2)
        sumOfCommonNeighborsIndirectNodeValue = sum(
            ComparisonCommonNeighborsArray[1:])
        FractionValueIndirectNode = round(
            sumOfCommonNeighborsIndirectNodeValue / Denominator, 2)
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
        if multiple!=0 :
            
          CorrelationCoefficient = round(sumOfUnionOfNeighborhoodIndirectNodes /
                                       multiple, 2)
        # common_nbor = len(set([n for n in graph.neighbors(currentNode)]).intersection(
        #     set([n for n in graph.neighbors(ComparisonNode)])))
        num = 0
        DICN = (1+num) * (1 + CorrelationCoefficient)
        ws.write(r, 0, currentNode)
        ws.write(r, 1, ComparisonNode)
        ws.write(r, 2, DICN)

        r += 1

wb.close() 


r = 1

for i in dictDirectNodes.keys():
    currentNode = i
    currentArrayDirectNodes = dictDirectNodes[currentNode]['directNodes']
    currentCommonNeighborsArray = finalArray[i]['commonNeighborsArray']
    for j in currentArrayDirectNodes:
        ComparisonNode = j
        ComparisonCommonNeighborsArray = finalArray[j]['commonNeighborsArray']
        arrayNodes = []
        for k in range(1, len(currentCommonNeighborsArray)):
            if currentCommonNeighborsArray[k] or ComparisonCommonNeighborsArray[k] != 0:
                arrayNodes.append(k)
        Denominator = len(arrayNodes)
        sumOfCommonNeighborsCurrentNodeValue = sum(
            currentCommonNeighborsArray[1:])
        FractionValueFirstNode = round(
            sumOfCommonNeighborsCurrentNodeValue / Denominator, 2)
        sumOfCommonNeighborsDirectNodeValue = sum(
            ComparisonCommonNeighborsArray[1:])
        FractionValueDirectNode = round(
            sumOfCommonNeighborsDirectNodeValue / Denominator, 2)
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
        if multiple!=0 :
               
           CorrelationCoefficient = round(sumOfUnionOfNeighborhoodDirectNodes /
                                       multiple, 2)
        # common_nbor = len(set([n for n in graph.neighbors(currentNode)]).intersection(
        #     set([n for n in graph.neighbors(ComparisonNode)])))
        num = graph.get_edge_data(currentNode, ComparisonNode)['num']
        DICN = (1+num) * (1 + CorrelationCoefficient)
        ws2.write(r, 0, currentNode)
        ws2.write(r, 1, ComparisonNode)
        ws2.write(r, 2, DICN)

        r += 1

wb2.close()
et=time.time()
print("Et= ",et-st)
##Et=  1229.9677004814148   pblog-full
##Et=  6.565210342407227  pblog-200
##Et=  17.81165862083435    dblp-5000
##Et=  12.27910828590393  pblog-250
##Et=  128.56250548362732  pblog-800
##Et=  74.8252284526825  pblog-500
##Et=  4.6253931522369385   dblp-3000
##Et=  11.039279222488403   dblp-4000
##Et=  281.36997151374817  pblog-1000
##Et=  33.50891470909119  citeseer-500rec
## Et=  8046.4401733875275 citeseer-full
## Et=  86.2956931591034 citeseer -filtering




