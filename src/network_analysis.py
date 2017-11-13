import json
import math
import os
import re
from collections import Counter
from statistics import mean

import matplotlib.pyplot as plt
import networkx as nx
from networkx.readwrite import json_graph


class NetworkAnalysis:
    def __init__(self, G, fileName, outputBase, time=None):  # TODO any settings for the network analysis
        self.G = G.copy()
        split = re.split('\\ /', fileName)
        fileName = split[0].split(".")[0]
        self.fileName = str(fileName)
        self.outputPath = outputBase + fileName + ('' if time is None else "_" + str(time)) + "/"
        if not os.path.exists(self.outputPath):
            os.makedirs(self.outputPath)

    def d3dump(self, output, curr_time=""):
        G = self.G.copy()
        # Augment Graph with Metadata
        for ix, deg in G.degree().items():
            G.node[ix]['degree'] = deg
            G.node[ix]['parity'] = (1 - deg % 2)
        G.nodes(data=True)
        data = json_graph.node_link_data(G)
        for node in data['nodes']:
            node['id'] = str(node['id'])
        # data['edges'] = data.pop('links')
        data['edges'] = list(map(lambda x: {"source": x[0].name, "target": x[1].name}, G.edges()))
        data['basic'] = self.returnBasicStats()
        try:
            data['basic']['averagePathLength'] = self.getAveragePathLength()
        except:
            pass

        fileName = output + self.fileName + '_' + curr_time + ".json"
        fileName = re.sub(r"\s+", '-', fileName)

        if not os.path.exists(output):
            os.makedirs(output)
        with open(fileName, 'w') as f:
            json.dump(data, f, indent=4)

        return data['basic']

    def write_permanent_data_json(self, outputFolder, fileName, data):
        fileName = re.sub(r"\s+", '-', fileName) + ".json"
        output = outputFolder + fileName
        if not os.path.exists(outputFolder):
            os.makedirs(outputFolder)
        with open(output, 'w') as f:
            json.dump(data, f, indent=2)

    def generateDrawing(self, outfile="graph.pdf"):
        nx.draw_networkx(self.G, pos=nx.spring_layout(self.G), arrows=False, with_labels=False, node_size=20)
        self.outputPlt(self.outputPath + outfile)

    def returnBasicStats(self):
        res = {}
        res['numNodes'] = nx.number_of_nodes(self.G)
        res['numEdges'] = nx.number_of_edges(self.G)
        indegree = list(nx.DiGraph.in_degree(self.G).values())
        outdegree = list(nx.DiGraph.out_degree(self.G).values())
        res['selfLinks'] = self.G.number_of_selfloops()
        res['numStrongComponents'] = nx.number_strongly_connected_components(self.G)
        res['numWeakComponents'] = nx.number_weakly_connected_components(self.G)

        largest_cc = max(nx.strongly_connected_components(self.G), key=len)
        res['sizeLargestStrong'] = len(largest_cc)

        largest_cc = max(nx.weakly_connected_components(self.G), key=len)
        res['sizeLargestWeak'] = len(largest_cc)

        Gc = max(nx.strongly_connected_component_subgraphs(self.G), key=len)
        res['radius'] = nx.radius(Gc)
        res['diameter'] = nx.diameter(Gc)

        try:
            res['averageInDegree'] = mean(indegree)
            res['averageOutDegree'] = mean(outdegree)
        except:
            res['averageInDegree'] = 0
            res['averageOutDegree'] = 0

        res['maxOutDegree'] = max(self.G.out_degree().values())
        res['maxInDegree'] = max(self.G.in_degree().values())

        stringified = {str(k): v for k, v in nx.pagerank(self.G, alpha=0.9).items()}
        res['pageRank'] = stringified

        hubs, auths = nx.hits(self.G)
        stringified = {str(k): v for k, v in hubs.items()}
        res['hitsHubs'] = stringified

        stringified = {str(k): v for k, v in auths.items()}
        res['hitsAuths'] = stringified

        return res

    def generateDegreeDistribution(self, graphpath="graphs/degreeDistribution.png"):
        output = open(self.outputPath + "degreeDistribution.txt", "w")

        degree = nx.degree(self.G)
        C = Counter(degree.values())

        maxDegree = degree[max(degree, key=lambda i: degree[i])]

        logx, logy = ([] for i in range(2))

        for i in range(0, maxDegree + 1):
            freq = C[i]
            output.write(str(i) + " " + str(freq) + "\n")
            if i > 0 and freq > 0:
                logx.append(math.log(i))
                logy.append(math.log(freq))

        output.close()
        self.makePlot('Log Histogram of Degree Frequencies', 'log j', 'log n_j', logx, logy, graphpath)

    def generatePathLengths(self, start, graphpath="graphs/pathLengths.png"):
        paths = nx.single_source_dijkstra_path_length(self.G, start)
        C = Counter(paths.values())
        maxPath = paths[max(paths, key=lambda i: paths[i])]

        x = []
        y = []

        with open(self.outputPath + "pathLengths.txt", "w") as output3:
            for i in range(1, maxPath + 1):
                output3.write(str(i) + " " + str(C[i]) + "\n")
                x.append(i)
                y.append(C[i])
        self.makePlot("Nodes at Distance j", 'j', 'r_j', x, y, graphpath)

    def getAveragePathLength(self):
        try:
            return nx.average_shortest_path_length(self.G)
        except:
            # subs = nx.strongly_connected_components(self.G)
            # subLengths = list(map(lambda x: len(x), subs))
            # print(subLengths)
            try:
                subs = max(nx.strongly_connected_component_subgraphs(self.G), key=len)
                return nx.average_shortest_path_length(subs)
            except:
                return 0

    def makePlot(self, title, xaxis, yaxis, xdata, ydata, path):
        fig = plt.figure()
        fig.suptitle(title, fontsize=14, fontweight='bold')

        ax = fig.add_subplot(111)
        fig.subplots_adjust(top=0.85)

        ax.set_xlabel(xaxis)
        ax.set_ylabel(yaxis)

        ax.scatter(x=xdata, y=ydata)
        plt.scatter(x=xdata, y=ydata)

        self.outputPlt(self.outputPath + path)

    def outputPlt(self, path):
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        plt.savefig(path)
        plt.close()


if __name__ == '__main__':
    pass
