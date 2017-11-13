#!/usr/bin/env python3
import datetime
import json
import os
import shutil
import matplotlib.pyplot as plt
from tqdm import tqdm

from settings import public_data

DATA_PATH = public_data
OUTPUT_PATH = "../output/visual/"
import matplotlib.dates as mdates


def directories(folder):
    dirs = [f for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f))]
    return dirs


def files(folder):
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    return files


def parseData(file):
    fileName = os.path.basename(file)
    date = datetime.datetime.strptime(fileName, '%Y-%m-%d.json')
    with open(file) as json_data:
        data = json.load(json_data)
        return date, data


def genAllTimePlots():
    for dir in tqdm(directories(DATA_PATH)):
        genAllTimePlotsDirectory(dir)


def genAllTimePlotsDirectory(dir):
    genTimePlot(dir, 'numNodes', 'Nodes')
    genTimePlot(dir, 'numEdges', 'Edges')
    genTimePlot(dir, 'numStrongComponents', 'Strong Components')
    genTimePlot(dir, 'sizeLargestStrong', 'Size Of Strong Component')
    genTimePlot(dir, 'numWeakComponents', 'Weak Components')
    genTimePlot(dir, 'sizeLargestWeak', 'Size Of Weak Component')
    genTimePlot(dir, 'radius', 'Radius')
    genTimePlot(dir, 'diameter', 'Diameter')
    genTimePlot(dir, 'averageInDegree', 'Avg Degree')
    genTimePlot(dir, 'maxOutDegree', 'Max Out Degree')
    genTimePlot(dir, 'maxInDegree', 'Max In Degree')


# Takes in the directory name from
def genTimePlot(dirName, fieldName, fieldLabel):
    directory = DATA_PATH + dirName + "/"

    dates = []
    yValues = []

    for f in files(directory):
        date, data = parseData(directory + f)
        dates.append(date)
        yVal = data[fieldName]
        yValues.append(yVal)

    makePlot(fieldLabel + " over Time", "Date", fieldLabel, dates, yValues, fieldName + "/" + dirName)


def makePlot(title, xaxis, yaxis, xdata, ydata, out):
    out_path = OUTPUT_PATH + out
    fig = plt.figure(figsize=(10, 8), dpi=100)
    fig.suptitle(title, fontsize=14, fontweight='bold')

    years = mdates.YearLocator()
    yearsFmt = mdates.DateFormatter('%Y')
    ax = plt.gca()
    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(yearsFmt)
    ax.autoscale_view()

    plt.xlabel(xaxis)
    plt.ylabel(yaxis)

    plt.scatter(x=xdata, y=ydata)

    directory = os.path.dirname(out_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    plt.savefig(out_path)
    plt.close()


if __name__ == '__main__':
    if os.path.exists(OUTPUT_PATH):
        shutil.rmtree(OUTPUT_PATH)
    os.makedirs(OUTPUT_PATH)

    genAllTimePlots()
