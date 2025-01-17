from difflib import SequenceMatcher
from tabulate import tabulate
import numpy as np
import pandas as pd
import itertools
import jellyfish
import logging
import yaml
import json
import sys
import os
import re

# ===========================================================================================
# ======================================= Begin Class =======================================
# ===========================================================================================

class TableMapping:
    # * ----------------------------------------------------------------- Variables
    def __init__(self):
        # * ------------------- public vars
        self.prjWorkDir                 = str()
        self.sramTableDir               = str()
        self.tcamTableConfigsFilePath   = str()
        self.tcamTableConfigsFileName   = str()
        self.tcamTableXlsxFilePath      = str()
        self.tcamTableXlsxFileName      = str()
        self.sramTableXlsxFilePath      = str()
        self.sramTableXlsxFileName      = str()
        self.sramTableHtmlFilePath      = str()
        self.sramTableHtmlFileName      = str()
        self.sramTableJsonFilePath      = str()
        self.sramTableJsonFileName      = str()
        self.sramTableTxtFilePath       = str()
        self.sramTableTxtFileName       = str()
        # * ------------------- protected vars
        self._tcamTableConfigs  = dict()
        self._queryStrAddrTable = pd.DataFrame
        self._tcamTable         = pd.DataFrame
        self._sramTable         = pd.DataFrame
        # * ------------------- private vars
        self.__tcamQueryStrLen  = int()
        self.__tcamSubStrLen    = int()
        self.__tcamTotalSubStr  = int()
        self.__tcamPotMatchAddr = int()
        self.__sramTableRows    = int()
        self.__sramTableCols    = int()
        self.__tcamRows         = list()
        self.__tcamCols         = list()
        self.__tcamColVec       = list()
        self.__sramRows         = list()
        self.__sramRowVec       = list()
        self.__sramCols         = list()
        # * logging config
        logging.basicConfig(level=logging.DEBUG, filename='./logs/tableMapping.log',
                            format='%(asctime)s | %(filename)s | %(funcName)s | %(levelname)s | %(lineno)d | %(message)s')
    
    
    # * ----------------------------------------------------------------- Functions
    def getPrjDir(self,verbose):
        """
        what does this func do ?
        input args:
        return val:
        """
        self.prjWorkDir=os.getcwd()
        logging.info('Project working dir: {:<s}'.format(self.prjWorkDir))
        printVerbose(verbose,'Project working dir: {:<s}'.format(self.prjWorkDir))
        return self.prjWorkDir
    
    
    def getYAMLFilePath(self,verbose):
        """
        what does this func do ?
        input args:
        return val:
        """
        # * get tcamTables config file path
        tempPath = os.path.join(self.prjWorkDir,'compiler/configs/tcamTables.yaml')
        if os.path.isfile(tempPath) is True:
            self.tcamTableConfigsFilePath = tempPath
            self.tcamTableConfigsFileName = os.path.basename(tempPath)
            logging.info('"FOUND": TCAM table config file path: {:<s}'.format(self.tcamTableConfigsFilePath))
            printVerbose(verbose,'"FOUND": TCAM table config file path: {:<s}'.format(self.tcamTableConfigsFilePath))
            return self.tcamTableConfigsFilePath
        else:
            logging.error('"NOT FOUND": TCAM table config file path: {:<s}'.format(self.tcamTableConfigsFilePath))
            sys.exit('"NOT FOUND": TCAM table config file path: {:<s}'.format(self.tcamTableConfigsFilePath))
    
    
    def readYAML(self,filePath,verbose):
        """
        what does this func do ?
        input args:
        return val:
        """
        with open(filePath) as file:
            self._tcamTableConfigs=yaml.full_load(file)
        # print(json.dumps(self._tcamTableConfigs,indent=4))
        # print(yaml.dump(self._tcamTableConfigs,sort_keys=False,default_flow_style=False))
        logging.info('Read TCAM table config file: {:<s}'.format(self.tcamTableConfigsFilePath))
        printVerbose(verbose,'Read TCAM table config file: {:<s}'.format(self.tcamTableConfigsFilePath))
        return self._tcamTableConfigs
    
    
    def printYAML(self,debug):
        """
        what does this func do ?
        input args:
        return val:
        """
        printDebug(debug,'Printing TCAM table configs')
        print(json.dumps(self._tcamTableConfigs,indent=4))
        # print(yaml.dump(self._tcamTableConfigs,sort_keys=False,default_flow_style=False))
        logging.info('Printed TCAM table configs')
    
    
    def getTCAMConfig(self,tcamConfig):
        """
        what does this func do ?
        input args:
        return val:
        """
        # * look for specific tcam config in compiler/configs/tcamTables.yaml
        if tcamConfig in self._tcamTableConfigs.keys():
            tempConfig = self._tcamTableConfigs[tcamConfig]
            # * save tcam config vars
            self.__tcamQueryStrLen  = tempConfig['queryStrLen']
            self.__tcamSubStrLen    = tempConfig['subStrLen']
            self.__tcamTotalSubStr  = tempConfig['totalSubStr']
            self.__tcamPotMatchAddr = tempConfig['potMatchAddr']
            # * print specific tcam config
            # print(tempConfig)
            logging.info('"FOUND" Required TCAM Config [{:<s}]'.format(tcamConfig))
            print('"FOUND" Required TCAM Config [{:<s}]'.format(tcamConfig))
            logging.info('TCAM Config Data [{:<s}] = {}'.format(tcamConfig,tempConfig))
            return tempConfig
        else:
            logging.error('"NOT FOUND": TCAM Config [{:<s}]'.format(tcamConfig))
            sys.exit('"NOT FOUND": Required TCAM table config [{:<s}]'.format(tcamConfig))
    
    
    def getTCAMTableFilePath(self,tcamConfig,verbose):
        """
        what does this func do ?
        input args:
        return val:
        """
        # * find the specific tcam table map in compiler/lib/
        tempPath = os.path.join(self.prjWorkDir,'compiler/lib/'+tcamConfig+'.xlsx')
        if os.path.isfile(tempPath) is True:
            self.tcamTableXlsxFilePath = tempPath
            self.tcamTableXlsxFileName = os.path.basename(tempPath)
            logging.info('"FOUND" TCAM table map XLSX file path: {:<s}'.format(self.tcamTableXlsxFilePath))
            printVerbose(verbose,'"FOUND" TCAM table map XLSX file path: {:<s}'.format(self.tcamTableXlsxFilePath))
            return self.tcamTableXlsxFilePath
        else:
            logging.error('"NOT FOUND": TCAM table map XLSX file path: {:<s}'.format(self.tcamTableXlsxFilePath))
            sys.exit('"NOT FOUND": TCAM table map XLSX file path {:<s}'.format(self.tcamTableXlsxFilePath))
    
    
    def printDF(self,dataFrame,heading):
        """
        what does this func do ?
        input args:
        return val:
        """
        print('\n')
        print('Printing dataframe: ' + str(heading))
        print(tabulate(dataFrame,headers='keys', showindex=True, disable_numparse=True, tablefmt='github'),'\n')
        logging.info('Printing dataframe: ' + str(heading))
    
    
    def readTCAMTable(self,verbose):
        """
        what does this func do ?
        input args:
        return val:
        """
        # * store tcam table in dataframe
        self._tcamTable = pd.read_excel(self.tcamTableXlsxFilePath, skiprows=2, index_col=None, engine='openpyxl')
        # * get num of rows and col from tcam table
        tcamTableRows = self._tcamTable.shape[0]
        tcamTableCols = self._tcamTable.shape[1]
        # * compare row/col of tcam table with respective yaml config
        if (tcamTableRows == self.__tcamPotMatchAddr and
            tcamTableCols - 1 == self.__tcamQueryStrLen):
            logging.info('"MATCH FOUND": TCAM table map rows == TCAM table YAML config potMatchAddr')
            printVerbose(verbose,'"MATCH FOUND": TCAM table map rows == TCAM table YAML config potMatchAddr')
            logging.info('"MATCH FOUND": TCAM table map cols == TCAM table YAML config queryStrLen')
            printVerbose(verbose,'"MATCH FOUND": TCAM table map cols == TCAM table YAML config queryStrLen')
            return [tcamTableRows, tcamTableCols];
        else:
            logging.info('"MATCH NOT FOUND": TCAM table map rows != TCAM table YAML config potMatchAddr')
            logging.info('"MATCH NOT FOUND": TCAM table map cols != TCAM table YAML config queryStrLen')
            sys.exit('"MATCH NOT FOUND": MISMATCH in TCAM table map and YAML config rows/cols')
    
    
    def getSRAMTableDim(self,verbose):
        """
        what does this func do ?
        input args:
        return val:
        """
        self.__sramTableRows = self.__tcamTotalSubStr * pow(2,self.__tcamSubStrLen)
        self.__sramTableCols = self.__tcamPotMatchAddr
        logging.info('SRAM table rows [{:>4d}] cols [{:>4d}]'.format(self.__sramTableRows,self.__sramTableCols))
        printVerbose(verbose,'SRAM table rows [{:>4d}] cols [{:>4d}]'.format(self.__sramTableRows,self.__sramTableCols))
        return [self.__sramTableRows, self.__sramTableCols]
    
    
    def genSRAMTable(self,verbose):
        """
        what does this func do ?
        input args:
        return val:
        """
        # * create temp vars
        sramTableAddrList = list()
        sramColHeadings = list()
        # * create row address
        for i in range(self.__tcamTotalSubStr):
            for j in range(2**self.__tcamSubStrLen):
                padding = '0'+str(self.__tcamSubStrLen)+'b'
                # sramTableAddrList.append(format(j, '#012b'))  # with 0b prefix
                sramTableAddrList.append(format(j, padding))    # without 0b prefix
            logging.info('Created [{:>4d}] SRAM addresses from search query [{:>4d}]'.format(j+1,i))
            printVerbose(verbose,'Created [{:>4d}] SRAM addresses from search query [{:>4d}]'.format(j+1,i))
        # * create col headings
        for k in reversed(range(self.__tcamPotMatchAddr)):
            heading = 'D'+str(k)
            sramColHeadings.append(heading)
        logging.info('Created [{:>4d}] data fields from potential match addresses'.format(k+1))
        printVerbose(verbose,'Created [{:>4d}] data fields from potential match addresses'.format(k+1))
        # * gen empty m*n sram table
        self._sramTable = pd.DataFrame(index=np.arange(self.__sramTableRows), columns=np.arange(self.__sramTableCols))
        # * rename column headings
        self._sramTable.columns = sramColHeadings
        # * insert addr col at position 0
        self._sramTable.insert(0,'Addresses',sramTableAddrList,allow_duplicates=True)
        logging.info('Created empty [{:d} x {:d}] SRAM table'.format(self._sramTable.shape[0],self._sramTable.shape[1]))
        printVerbose(verbose,'Created empty [{:d} x {:d}] SRAM table'.format(self._sramTable.shape[0],self._sramTable.shape[1]))
    
    
    def createSRAMTableDir(self,verbose):
        """
        what does this func do ?
        input args:
        return val:
        """
        # * create sramTables dir if it doesnt exist
        self.sramTableDir = os.path.join(self.prjWorkDir,'sramTables')
        if os.path.exists(self.sramTableDir) is False:
            os.makedirs('sramTables')
            logging.info('Created sramTables dir: {:<s}'.format(self.sramTableDir))
            printVerbose(verbose,'Created sramTables dir: {:<s}'.format(self.sramTableDir))
        return self.sramTableDir
    
    
    def splitRowsAndCols(self,debug):
        """
        what does this func do ?
        input args:
        return val:
        """        
        # * store tcam and sram table in temp vars
        tcamDF = self._tcamTable
        sramDF = self._sramTable
        logging.info('TCAM table (r*c): {0}'.format(tcamDF.shape))
        logging.info('SRAM table (r*c): {0}'.format(sramDF.shape))
        # * create tcamRows vector
        self.__tcamRows = np.arange(0,self.__tcamPotMatchAddr,1).tolist()
        logging.info('TCAM table row vector: {0}'.format(self.__tcamRows))
        printDebug(debug,'TCAM table row vector: {0}'.format(self.__tcamRows))
        # * create tcamCols vector
        self.__tcamCols = np.arange(1,self.__tcamQueryStrLen+1,1).tolist()
        logging.info('TCAM table col vector: {0}'.format(self.__tcamCols))
        printDebug(debug,'TCAM table col vector: {0}'.format(self.__tcamCols))
        # * create tcamColVec vector and split in equal pieces
        self.__tcamColVec = np.array_split(self.__tcamCols,self.__tcamTotalSubStr)
        for i in range(len(self.__tcamColVec)):
            self.__tcamColVec[i] = self.__tcamColVec[i].tolist()
            logging.info('TCAM table col split vector [{0}]: {1}'.format(i,self.__tcamColVec[i]))
            printDebug(debug,'TCAM table col split vector [{0}]: {1}'.format(i,self.__tcamColVec[i]))
        # * create sramRows vector
        self.__sramRows = np.arange(0,self.__tcamTotalSubStr * 2**self.__tcamSubStrLen,1).tolist()
        logging.info('SRAM table row vector: {0}'.format(self.__sramRows))
        printDebug(debug,'SRAM table row vector: {0}'.format(self.__sramRows))
        # * create sramRowVec vector and split in equal pieces
        self.__sramRowVec = np.array_split(self.__sramRows,self.__tcamTotalSubStr)
        for i in range(len(self.__sramRowVec)):
            self.__sramRowVec[i] = self.__sramRowVec[i].tolist()
            logging.info('SRAM table row split vector [{0}]: {1}'.format(i,self.__sramRowVec[i]))
            printDebug(debug,'SRAM table row split vector [{0}]: {1}'.format(i,self.__sramRowVec[i]))
        # * create sramCols vector
        self.__sramCols = np.arange(0,self.__tcamPotMatchAddr+1,1).tolist()
        logging.info('SRAM table col vector: {0}'.format(self.__sramCols))
        printDebug(debug,'SRAM table col vector: {0}'.format(self.__sramCols))
        return [self.__tcamRows, self.__tcamColVec, self.__sramRowVec, self.__sramCols]
    
    
    def generateSRAMSubStr(self,verbose,debug):
        """
        what does this func do ?
        input args:
        return val:
        """
        tcamDF = self._tcamTable
        count1 = 0
        count2 = 0
        tempQSAddrTable = pd.DataFrame(columns=['Query Str Addr','QS col','PMA'])
        self._queryStrAddrTable = pd.DataFrame(columns=['Query Str Addr','QS col','PMA'])
        
        # * ----- add all original search queries in dataframe
        # * iterate through tcam table rows
        for row in range(len(tcamDF)):
            # * iterate through tcam table cols
            for col in range(len(self.__tcamColVec)):
                # * search and concat search query string address in tcam table
                tempAddr = [str(c) for c in list(tcamDF.iloc[row,self.__tcamColVec[col]])]
                tempAddr = ''.join(tempAddr)
                # * append row in sqSubStrAddrDf data frame
                tempRow = [tempAddr, col, row]
                tempQSAddrTable.loc[count1] = tempRow
                count1 += 1
                logging.info('Address Mapping to SRAM | Addr: {:>s} | Sub String Col: {:>5d} | TCAM Row: {:>5d} |'.format(tempAddr,col,row))
                printDebug(debug,'Address Mapping to SRAM | Addr: {:>s} | Sub String Col: {:>3d} | TCAM Row: {:>3d} |'.format(tempAddr,col,row))
        if verbose:
            self.printDF(tempQSAddrTable,'Original Search Query Address Table')
        
        # * ----- find all possible alternatives for X based addr
        # * create array of N bit bin addresses
        queryStrBinAddrList = np.arange(2**self.__tcamSubStrLen).tolist()
        padding = '0'+str(self.__tcamSubStrLen)+'b'
        for item in queryStrBinAddrList:
            dec2Bin = format(item,padding)
            queryStrBinAddrList = queryStrBinAddrList[:item]+[dec2Bin]+queryStrBinAddrList[item+1:]
        logging.info('N bit bin addr list: {0}'.format(queryStrBinAddrList))
        logging.info('N bit bin addr list len: {0}'.format(len(queryStrBinAddrList)))
        if verbose or debug:
            print('N bit bin addr list: {0}'.format(queryStrBinAddrList))
            print('N bit bin addr list len: {0}'.format(len(queryStrBinAddrList)))
        
        # * get origSQ addr
        tempQSAddrList = tempQSAddrTable['Query Str Addr'].to_list()
        printDebug(debug,'Search Query addr list: {0}'.format(tempQSAddrList))
        printDebug(debug,'Search Query addr list len: {0}\n'.format(len(tempQSAddrList)))
        # * map the 'bX in search queries to 0 and 1
        for orig in tempQSAddrList:
            # * if 'bX in search query them find alternatives and add in table
            if 'x' in orig:
                for new in queryStrBinAddrList:
                    matching = jellyfish.damerau_levenshtein_distance(orig, new)
                    if matching == len(re.findall('x',orig)):
                        printVerbose(verbose,'orig Search Query = {} | new Search Query = {} | matching ratio = {} |'.format(orig, new, matching))
                        logging.info('orig Search Query = {} | new Search Query = {} | matching ratio = {} |'.format(orig, new, matching))
                        origRowData = tempQSAddrTable.loc[tempQSAddrTable['Query Str Addr'] == orig].values.flatten().tolist()
                        # origRowIndex = tempQSAddrTable.index[tempQSAddrTable['Query Str Addr'] == orig].tolist()
                        i = origRowData.index(orig)
                        origRowData = origRowData[:i]+[new]+origRowData[i+1:]
                        self._queryStrAddrTable.loc[count2] = origRowData
                        count2 += 1
            # * else simply add search query in table as is
            else:
                printVerbose(verbose,'orig Search Query = {} | new Search Query = {} | matching ratio = {} |'.format(orig, orig, 0))
                logging.info('orig Search Query = {} | new Search Query = {} | matching ratio = {} |'.format(orig, orig, 0))
                origRowData = tempQSAddrTable.iloc[count2].to_list()
                self._queryStrAddrTable.loc[count2] = origRowData
                count2 += 1
    
    
    def mapTCAMtoSRAM(self,verbose,debug):
        """
        what does this func do ?
        input args:
        return val:
        """
        sramDF = self._sramTable
        sramAddrList = self._queryStrAddrTable['Query Str Addr'].to_list()
        tcamRowList = self._queryStrAddrTable['PMA'].to_list()
        sramColList = self._queryStrAddrTable['QS col'].to_list()
        
        if len(tcamRowList) == len(sramColList):
            for tempSQ, a,b in itertools.zip_longest(sramAddrList, tcamRowList, sramColList):
                # * create sram table subsections based on query str
                tempSRAMTable = sramDF.iloc[self.__sramRowVec[b],self.__sramCols]
                logging.info('Search Query mapping portion: {:d}'.format(b))
                printDebug(debug,'Search Query mapping portion: {:d}'.format(b))
                # print(tabulate(tempSRAMTable,headers='keys',tablefmt='github'),'\n')
                # * find specific mapping cell in sram table
                rowIndx = tempSRAMTable.index[tempSRAMTable['Addresses']==tempSQ].to_list()[0]
                colIndx = len(self.__sramCols) - a - 1
                # print('sram rowIndx: ',rowIndx,type(rowIndx))
                # print('sram colIndx: ',colIndx,type(colIndx))
                # * find specific entry
                tempData = sramDF.iloc[rowIndx,colIndx]
                # print(sramDF.iloc[rowIndx,colIndx])
                logging.info('SRAM table cell [{:d}, {:d}] | Old Value = {}'.format(rowIndx,colIndx,tempData))
                printDebug(debug,'SRAM table cell [{:d}, {:d}] | Old Value = {}'.format(rowIndx,colIndx,tempData))
                # * replace specific entry
                sramDF.iat[rowIndx,colIndx] = 1
                # print(sramDF.iat[rowIndx, colIndx])
                logging.info('SRAM table cell [{:d}, {:d}] | New Value = {}'.format(rowIndx,colIndx,sramDF.iloc[rowIndx,colIndx]))
                if verbose or debug:
                    print('SRAM table cell [{:d}, {:d}] | New Value = {}'.format(rowIndx,colIndx,sramDF.iloc[rowIndx,colIndx]))
            # * add zeros in empty cells
            sramDF = sramDF.fillna(0)
            self._sramTable = sramDF
        else:
            logging.info('"MATCH NOT FOUND": TCAM table rows != SRAM table cols config potMatchAddr')
            sys.exit('"MATCH NOT FOUND": MISMATCH in TCAM table map and YAML config rows/cols')
    
    
    def writeSRAMtoXlsx(self):
        """
        what does this func do ?
        input args:
        return val:
        """
        # * create sram table file path and name
        self.sramTableXlsxFileName = os.path.basename(self.tcamTableXlsxFileName.replace('tcam','sram'))
        self.sramTableXlsxFilePath = os.path.join(self.sramTableDir,self.sramTableXlsxFileName)
        # * create excel file in dir sramTables
        writer = pd.ExcelWriter(self.sramTableXlsxFilePath,engine='xlsxwriter')
        writer.save()
        self._sramTable.to_excel(excel_writer=self.sramTableXlsxFilePath, sheet_name=self.sramTableXlsxFileName,
                                    na_rep='', header=True, index=True, engine='xlsxwriter')
        logging.info('Created SRAM table XLSX file: {:<s}'.format(self.sramTableXlsxFilePath))
        print('Created SRAM table XLSX file: {:<s}'.format(self.sramTableXlsxFilePath))
        return self.sramTableXlsxFilePath
    
    
    def writeSRAMtoHtml(self):
        """
        what does this func do ?
        input args:
        return val:
        """
        # * create sram table file path and name
        self.sramTableHtmlFileName = os.path.basename(self.tcamTableXlsxFileName.replace('tcam','sram').replace('.xlsx','.html'))
        self.sramTableHtmlFilePath = os.path.join(self.sramTableDir,self.sramTableHtmlFileName)
        # * create html file in dir sramTables
        self._sramTable.to_html(self.sramTableHtmlFilePath,index=True,header=True,justify='center',classes='table table-stripped')
        logging.info('Created SRAM table HTML file: {:<s}'.format(self.sramTableHtmlFilePath))
        print('Created SRAM table HTML file: {:<s}'.format(self.sramTableHtmlFilePath))
        return self.sramTableHtmlFilePath
    
    
    def writeSRAMtoJson(self):
        """
        what does this func do ?
        input args:
        return val:
        """
        # * create sram table file path and name
        self.sramTableJsonFileName = os.path.basename(self.tcamTableXlsxFileName.replace('tcam','sram').replace('.xlsx','.json'))
        self.sramTableJsonFilePath = os.path.join(self.sramTableDir,self.sramTableJsonFileName)
        # * create json file in dir sramTables
        self._sramTable.to_json(self.sramTableJsonFilePath,orient='index',indent=4)
        logging.info('Created SRAM table JSON file: {:<s}'.format(self.sramTableJsonFilePath))
        print('Created SRAM table JSON file: {:<s}'.format(self.sramTableJsonFilePath))
        return self.sramTableJsonFilePath
    
    
    def writeSRAMtoTxt(self):
        """
        what does this func do ?
        input args:
        return val:
        """
        # * create sram table file path and name
        self.sramTableTxtFileName = os.path.basename(self.tcamTableXlsxFileName.replace('tcam','sram').replace('.xlsx','.txt'))
        self.sramTableTxtFilePath = os.path.join(self.sramTableDir,self.sramTableTxtFileName)
        # * create txt file in dir sramTables
        myTable = tabulate(self._sramTable,headers='keys', showindex=True, disable_numparse=True, tablefmt='github')
        with open(self.sramTableTxtFilePath,'w') as f:
            f.write(myTable)
        logging.info('Created SRAM table Txt file:  {:<s}'.format(self.sramTableTxtFilePath))
        print('Created SRAM table Txt file:  {:<s}'.format(self.sramTableTxtFilePath))
        return self.sramTableTxtFilePath


# ===========================================================================================
# ======================================== End Class ========================================
# ===========================================================================================

def printVerbose(verbose,msg):
    if verbose:
        print(str(msg))

def printDebug(debug,msg):
    if debug:
        print(str(msg))
