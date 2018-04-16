import csv
import filecmp
import os
import shutil

class MidiHelper:
    """"Removing double MIDIs, importing the match list"""

    if __name__ == '__main__':
        """"
        1) Import list of MIDI files and LAB keys
        2) Per LAB key:
            a) List corresponding MIDI files
            b) Check if all MIDIs are different; if not: throw copies away
        """
        myPath = "D:\\Data"
        csvPath = myPath + "\\Index.csv"

        # Load the content of the csv file into keyDict dictionary
        keyDict = {}
        for i in range(1, 239):
            keyDict[i] = []
        csvfile = open(csvPath, 'rt')
        reader = csv.reader(csvfile, delimiter=";")
        rownum = 0
        for row in reader:
           if rownum == 0:
               rownum += 1
           else:
               if int(row[2]) > 0:
                   keyDict[int(row[2])].append(row[1])

        # Iterate over the keys and remove duplicates
        # for i in range(1, 239):
        #     pathlist = keyDict[i]
        #     nrMidis = len(pathlist)
        #     removelist = []
        #     for a in range(0, nrMidis-1):
        #         for b in range(a+1, nrMidis):
        #             if filecmp.cmp(pathlist[a], pathlist[b]):
        #                 removelist.append(a)
        #     newpathlist = []
        #     for k in range(0, nrMidis):
        #         if not k in removelist:
        #             newpathlist.append(pathlist[k])
        #     keyDict[i] = newpathlist

        # Rename and move the files.
        # Name format: [key]-[nr].mid
        # Folder: D:\Data\MIDI

        for i in range(1, 239):
            oldpaths = keyDict[i]
            for j in range(0, len(oldpaths)):
                oldpath = oldpaths[j]
                if os.path.exists(oldpath):
                    newpath = "D:\\Data\\MIDI\\" + str.zfill(str(i), 3) + "-" + str.zfill(str(j + 1), 3) + ".mid"
                    shutil.move(oldpath, newpath)


        i = 5
