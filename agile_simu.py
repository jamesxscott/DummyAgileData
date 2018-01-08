from random import *
import datetime
import os

numStories=20
numDevs=5
lengthDevTime=100
absenceLength=0
CumuFlow=[[0 for j in range(numStories)] for i in range(7)] #IssueID,ReadyHrs,InProgressHrs,InReviewHrs,ReadyCmp,InProgressCmp,ReviewCmp
DevTime=[[0 for j in range(lengthDevTime)] for i in range(numDevs+5)] # + Date, CountGrooming,CountWIP,CountReview,CountDone
startDate=datetime.datetime(2017,12,1)
InProgress_From=8
InProgress_To=80
Review_From=2
Review_To=8

def printCumuFlow():
    print "IssueID,ReadyHrs,InProgressHrs,InReviewHrs,ReadyCmp,InProgressCmp,ReviewCmp"
    for j in range(20):
      print "%s,%s,%s,%s,%s,%s,%s"  %(CumuFlow[0][j],CumuFlow[1][j],CumuFlow[2][j],CumuFlow[3][j],CumuFlow[4][j],CumuFlow[5][j],CumuFlow[6][j])

def printDevTime():  
    print "Date, Dev#1,Dev#2,Dev#3,Dev#4,Dev#5,CountGrooming,CountWIP,CountReview,CountDone"
    for j in range(lengthDevTime):
      print "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s"  %(DevTime[0][j],DevTime[6][j],DevTime[7][j],DevTime[8][j],DevTime[9][j],DevTime[1][j],DevTime[2][j],DevTime[3][j],DevTime[4][j],DevTime[5][j])

def workOnStories(currentDate, phase, devID):
    indexCurrentDate=DevTime[0].index(currentDate)
    if phase == "Review":
        phaseWorkColumn=3
        phaseCompletedColumn=6
    elif phase == "InProgress":
        phaseWorkColumn=2
        phaseCompletedColumn=5
    elif phase == "Groom":
        phaseWorkColumn=1
        phaseCompletedColumn=4
    else:
        return
        
    while DevTime[devID][indexCurrentDate]>0 and max(CumuFlow[phaseWorkColumn])>0:
      indexMaxWorkToDo=CumuFlow[phaseWorkColumn].index(max(CumuFlow[phaseWorkColumn]))

      #subtract devtime from cumuflow
      CumuFlow[phaseWorkColumn][indexMaxWorkToDo]=CumuFlow[phaseWorkColumn][indexMaxWorkToDo]-DevTime[i+1][j]

      #if cumuflow is >= 0 then DevTime is 0 else DevTime=abs(CumuFlow);CumuFlow=0
      if CumuFlow[phaseWorkColumn][indexMaxWorkToDo]>=0:
        DevTime[i+1][j]=0
      else:
        DevTime[i+1][j]=abs(CumuFlow[phaseWorkColumn][indexMaxWorkToDo])
        CumuFlow[phaseWorkColumn][indexMaxWorkToDo]=0
      if CumuFlow[phaseWorkColumn][indexMaxWorkToDo]==0: #phase complete
        CumuFlow[phaseCompletedColumn][indexMaxWorkToDo]=DevTime[0][j].strftime('%d/%m/%Y') #note date complete
        if phase=="InProgress":
            CumuFlow[phaseWorkColumn+1][indexMaxWorkToDo]=randint(Review_From,Review_To) #generate Review randomized value
        elif phase=="Groom":
            CumuFlow[phaseWorkColumn+1][indexMaxWorkToDo]=randint(InProgress_From,InProgress_To) #generate Work In Progress randomized value
      
      
# set up randomized values for initial stories in CumuFlow
for i in range(len(CumuFlow[0])):
  CumuFlow[0][i]="Story ID"+str(i+1) #assign issue ID's for initial stories
  CumuFlow[1][i]=randint(4,16) #assign Ready times (hours) for initial stories

 # set up randomized values for developer capacity in DevTime
for i in range(1,len(DevTime)-4):
  for j in range(len(DevTime[i])):
    if absenceLength==0 and randint(1,100) < 20: #chance of developer absence (if not already absent)
      absenceLength=randint(1,4) #length of developer absence (days)

    DevTime[0][j]=startDate + datetime.timedelta(days=j)
    
    if absenceLength > 0:
      DevTime[i][j]=0
      absenceLength=absenceLength-1
    else:
      DevTime[i][j]=randint(2,6) #assign capacity (hours) for the developer on that day 
  
#print initial state
printCumuFlow()
printDevTime()

#---------------------------------------------------------------------------------------  
#main loop - complete stories
#for each date - for each developer - work on story to complete phase
for j in range(0,len(DevTime[i])): #for each day
  #track numbers in each phase for each day
  DevTime[6][j]=sum([1 for x in CumuFlow[1] if x > 0]) #CountGrooming
  DevTime[7][j]=sum([1 for x in CumuFlow[2] if x > 0]) #CountWIP
  DevTime[8][j]=sum([1 for x in CumuFlow[3] if x > 0]) #CountReview
  DevTime[9][j]=sum([1 for x in CumuFlow[6] if x > 0]) #CountDone
  #if j==50:
  #  printDevTime()
  #  os.system('pause')
  
  #TODO add best/worst/guess framework and output results for each
  #TODO add blocker randomization
  #TODO add date created column and populate it
  #TODO add bug creation
  #TODO add new story creation
  #TODO add system testing and user acceptance
  #TODO add frequency bins columns
  #TODO after set threshold, calculate (daily) expected completion date using extrapolation of stories done rate
  #TODO after same threshold, calculate (daily) expected completion date using frequency bins
  #TODO add csv output
  #TODO add graph output
  
  for i in range(0,numDevs): #for each developer
      workOnStories(currentDate = DevTime[0][j], phase = "Review", devID = i+1)
      workOnStories(currentDate = DevTime[0][j], phase = "InProgress", devID = i+1)
      workOnStories(currentDate = DevTime[0][j], phase = "Groom", devID = i+1)
      
printCumuFlow()
printDevTime()
if max(CumuFlow[1])+max(CumuFlow[2])+max(CumuFlow[3])>0:
    print "Project ran out of time"
else:
    print "Project completed on %s" %(max(CumuFlow[6]))