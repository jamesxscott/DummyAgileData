from random import *
import datetime
import os

numStories=15
numDevs=5
lengthDevDays=120
CumuFlow=[[0 for j in range(numStories)] for i in range(8)] #IssueID,ReadyHrs,InProgressHrs,InReviewHrs,Created,ReadyCmp,InProgressCmp,ReviewCmp
DevTime=[[0 for j in range(lengthDevDays)] for i in range(numDevs+5)] # + Date, CountGrooming,CountWIP,CountReview,CountDone
startDate=datetime.datetime(2017,12,1)
InProgress_From=8
InProgress_To=80
Review_From=2
Review_To=8

def printCumuFlow():
    print "IssueID,ReadyHrs,InProgressHrs,InReviewHrs,Created,ReadyCmp,InProgressCmp,ReviewCmp"
    for j in range(len(CumuFlow[0])):
      print "%s,%s,%s,%s,%s,%s,%s,%s"  %(CumuFlow[0][j],CumuFlow[1][j],CumuFlow[2][j],CumuFlow[3][j],CumuFlow[4][j],CumuFlow[5][j],CumuFlow[6][j],CumuFlow[7][j])

def printDevTime():  
    print "Date, Dev#1,Dev#2,Dev#3,Dev#4,Dev#5,CountGrooming,CountWIP,CountReview,CountDone"
    for j in range(lengthDevDays):
      print "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s"  %(DevTime[0][j],DevTime[6][j],DevTime[7][j],DevTime[8][j],DevTime[9][j],DevTime[1][j],DevTime[2][j],DevTime[3][j],DevTime[4][j],DevTime[5][j])

def workOnStories(theDate, phase, devID):
    indexCurrentDate=DevTime[0].index(theDate)

    if phase == "Review":
        phaseWorkColumn=3
        phaseCompletedColumn=7
    elif phase == "InProgress":
        phaseWorkColumn=2
        phaseCompletedColumn=6
    elif phase == "Groom":
        phaseWorkColumn=1
        phaseCompletedColumn=5
    else:
        return
        
    while DevTime[devID][indexCurrentDate]>0 and max(CumuFlow[phaseWorkColumn])>0:
      indexMaxWorkToDo=CumuFlow[phaseWorkColumn].index(max(CumuFlow[phaseWorkColumn]))

      #subtract devtime from cumuflow
      CumuFlow[phaseWorkColumn][indexMaxWorkToDo]=CumuFlow[phaseWorkColumn][indexMaxWorkToDo]-DevTime[i+1][indexCurrentDate]

      #if cumuflow is >= 0 then DevTime is 0 else DevTime=abs(CumuFlow);CumuFlow=0
      if CumuFlow[phaseWorkColumn][indexMaxWorkToDo]>=0:
        DevTime[i+1][indexCurrentDate]=0
      else:
        DevTime[i+1][indexCurrentDate]=abs(CumuFlow[phaseWorkColumn][indexMaxWorkToDo])
        CumuFlow[phaseWorkColumn][indexMaxWorkToDo]=0
      if CumuFlow[phaseWorkColumn][indexMaxWorkToDo]==0: #phase complete
        CumuFlow[phaseCompletedColumn][indexMaxWorkToDo]=DevTime[0][indexCurrentDate] #note date complete
        if phase=="InProgress":
            CumuFlow[phaseWorkColumn+1][indexMaxWorkToDo]=randint(Review_From,Review_To) #generate Review randomized value
        elif phase=="Groom":
            CumuFlow[phaseWorkColumn+1][indexMaxWorkToDo]=randint(InProgress_From,InProgress_To) #generate Work In Progress randomized value
        elif phase=="Review": #issue completed
            if randint(1,10)<=3: #chance of bug being found
                #print "#create new bug"
                CumuFlow[0].append("Bug for " + CumuFlow[0][indexMaxWorkToDo])
                CumuFlow[1].append(randint(8,32)) #amount of work for the bug
                CumuFlow[2].append(0)
                CumuFlow[3].append(0)
                CumuFlow[4].append(theDate) #bug creation date
                CumuFlow[5].append(0)
                CumuFlow[6].append(0)
                CumuFlow[7].append(0)
      
def initialiseCumuFlow():      
    # set up randomized values for initial stories in CumuFlow
    for i in range(len(CumuFlow[0])):
      CumuFlow[0][i]="Story ID"+str(i+1)                #assign issue ID's for initial stories
      CumuFlow[1][i]=randint(4,16)                      #assign Ready times (hours) for initial stories, between 4 and 16 hours
      CumuFlow[4][i]=startDate                          #set created date for initial stories

def initialiseDevTime():
    # set up randomized values for developer capacity in DevTime
    absenceLength=0
    currentDate=startDate
    for dayloop in range(0,lengthDevDays):
      for devloop in range(1,len(DevTime)-4): #for each developer
        if absenceLength==0 and randint(1,100) < 20: #chance of developer absence (if not already absent)
          absenceLength=randint(1,4) #length of developer absence (days)

        DevTime[0][dayloop]=currentDate
        
        if absenceLength > 0:
          DevTime[devloop][dayloop]=0
          absenceLength=absenceLength-1
        else:
          DevTime[devloop][dayloop]=randint(2,6) #assign capacity (hours) for the developer on that day
      currentDate=currentDate + datetime.timedelta(days=1)
      if currentDate.strftime("%A")=="Saturday":
        currentDate=currentDate + datetime.timedelta(days=2)
    
  
#----------------------------------------------------------------------------------------------------------------------
# MAIN
#----------------------------------------------------------------------------------------------------------------------

initialiseCumuFlow()
initialiseDevTime()

#print initial state
printCumuFlow()
printDevTime()

#for each date - for each developer - work on story to complete phase
currentDate=startDate
while max(CumuFlow[1])+max(CumuFlow[2])+max(CumuFlow[3])>0: #work remaining
  indexCurrentDate=DevTime[0].index(currentDate)

  for i in range(0,numDevs): #for each developer on given day
      workOnStories(theDate = currentDate, phase = "Review", devID = i+1)
      workOnStories(theDate = currentDate, phase = "InProgress", devID = i+1)
      workOnStories(theDate = currentDate, phase = "Groom", devID = i+1)

  #track numbers in each phase for each day
  DevTime[6][indexCurrentDate]=sum([1 for x in CumuFlow[1] if x > 0]) #CountGrooming
  DevTime[7][indexCurrentDate]=sum([1 for x in CumuFlow[2] if x > 0]) #CountWIP
  DevTime[8][indexCurrentDate]=sum([1 for x in CumuFlow[3] if x > 0]) #CountReview
  DevTime[9][indexCurrentDate]=sum([1 for x in CumuFlow[7] if x <>0]) #CountDone
   
  currentDate=currentDate + datetime.timedelta(days=1)
  if currentDate.strftime("%A")=="Saturday":
    currentDate=currentDate + datetime.timedelta(days=2)
    
  if currentDate not in DevTime[0]:
    break
      
printCumuFlow()
printDevTime()
if max(CumuFlow[1])+max(CumuFlow[2])+max(CumuFlow[3])==0:
    print "Project completed on %s" %(CumuFlow[7][CumuFlow[7].index(max(CumuFlow[7]))]).strftime("%d/%m/%Y")
else:
        print "Project ran out of time"
