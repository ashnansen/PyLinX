'''
Created on 11.07.2016

@author: wplaum
'''
import csv

#import PyLinXCoreDataObjects

class CSVObject(object):
    
    class mode:
        raw = 0
        channels = 1
    
    def __init__(self, path = None, mode = mode.channels):
        
        super(CSVObject, self).__init__()
        self.__data = []        
        if path == None:
            self.__init__noPath()
            return

        #Heuristic for determining the deliminiter
        with open(path, 'rb') as csvfile:
            strCSVFile = csvfile.read()
            Chars = [';', '\t']
            #numChars = []
            maxNumChars = 0
            idxMaxNumChars = 0
            for i,char in enumerate(Chars):
                count = strCSVFile.count(char)
                if maxNumChars > count:
                    idxMaxNumChars = i
                    maxNumChars = count 
            delimiter = Chars[idxMaxNumChars]
        
        # Read data.
        with open(path, 'rb') as csvfile:    
            spamreader = csv.reader(csvfile, delimiter='\t', quotechar='"')
            for row in spamreader:
                for j, cell in enumerate(row):
                    if j >= len(self.__data):
                        self.__data.append([])
                    self.__data[j].append(cell)
        
        # postprocessing if channel mode is selected
        if mode == CSVObject.mode.channels:
            
            # detecting preface
            def getIdxFirstNumber(col):
                numRowType = -1
                for i in range(len(col)):
                    try:
                        float((col[i + 2]).replace(',','.'))
                        bFloat = True
                    except:
                        bFloat = False
                    if bFloat: 
                        numRowType = i
                        break
                return numRowType

            
            # eliminate preface
            for i, col in enumerate(self.__data):
                idx = getIdxFirstNumber(col)
                if idx <= 1:
                    break
                self.__data[i] = self.__data[i][idx-1:]
                
            signalsDict = {}
            
            for col in self.__data:
                label =col[0]
                unit = col[2]
                _type = col[1]
                signalsDict[label] = {u"ylabel": label + " [" + unit + "]", \
                                      u"values": [val.replace(',','.') for val in col[3:]], \
                                      u"title":  label,
                                      u"label":  label,
                                      u"unit":   unit,
                                      u"type":   _type}
            
            master = None
            for key in signalsDict:
                if key in (u"time", u"Time", u"TIME"):
                    master = key
                    break
            
            if master == None:
                raise Exception("CSVObject.__init__: No master signal found!")
            
            for key in signalsDict:
                if key == master:
                    signalsDict[key][u"masterType"] = 1
                else:
                    signalsDict[key][u"masterType"] = 0
            
            time = signalsDict[master][u"values"]
            
            for key in signalsDict:
                signalsDict[key][u"xlabel"] = master
                signalsDict[key][u"time"]   = time
                    
            self.__data = signalsDict
            
    def __init__noPath(self):
        self.__data = {}
        
    def addChannel(self,channelDict):
        if u"label" in channelDict:
            label = channelDict["label"]
            dictToWrite = {}
            self.__data[label] = dictToWrite
        else:
            raise Exception(u"PX_CSVObject.addChannel: lable information missing!")
        
        for key, element in channelDict.iteritems():
            if key in (u"values", u"label", u"unit", u"type"):
                self.__data[label][key] = element
          
          
    def write(self, path, header = None):
        with open(path, 'wb') as csvfile:
            csvwriter = csv.writer(csvfile, 
                                   delimiter='\t',
                                   quotechar='"', 
                                   quoting=csv.QUOTE_MINIMAL)
            len_data = len(self.__data)
            signalFinished = [1] * len_data
            signalValues = [self.__data[key][u"values"] for key in self.__data]
            lenSignals = [len(values) for values in signalValues]
            
            if header != None:
                csvwriter.writerow(header)
            row = [u"sampleCount", max(lenSignals)]
            csvwriter.writerow(row)            
            row = [self.__data[label][u"label"] for label in self.__data]
            csvwriter.writerow(row)
            row = [self.__data[label][u"unit"] for label in self.__data]
            csvwriter.writerow(row)
            row = [self.__data[label][u"type"] for label in self.__data]
            csvwriter.writerow(row)
                       
            j = 0
            while 1:
                row = []
                for i in range(len_data):
                    if signalFinished[i] == 1:
                        if lenSignals[i] <= j:
                            signalFinished[i] = 0
                    if signalFinished[i] == 1:
                        row.append(str(signalValues[i][j]))
                    else:
                        row.append('')
                j += 1    
                if sum(signalFinished) == 0:
                    break
                csvwriter.writerow(row)
                
    def data(self):
        return self.__data

                
if __name__ == '__main__':
    csvfile = CSVObject(path = 'D:/Projekte/PyLinX/Measure_5.ascii')
    csvfile.write('D:/Projekte/PyLinX/Measure_5_v2.ascii', ["PyLinXItemFile", "record", "CrLf", "Tab"])    