from random import *
import datetime

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
  
#main loop - complete stories
#for each date - for each developer - work on story to complete phase
for j in range(0,len(DevTime[i])): #for each day
  #track numbers in each phase for each day
  DevTime[6][j]=sum([1 for x in CumuFlow[1] if x > 0]) #CountGrooming
  DevTime[7][j]=sum([1 for x in CumuFlow[2] if x > 0]) #CountWIP
  DevTime[8][j]=sum([1 for x in CumuFlow[3] if x > 0]) #CountReview
  DevTime[9][j]=sum([1 for x in CumuFlow[6] if x > 0]) #CountDone
  for i in range(0,5): #for each developer
    #find max remaining work to be reviewed <= developer capacity
    if max(CumuFlow[3])>0: #there is some story to reviewed
      while DevTime[i+1][j]>0 and max(CumuFlow[3])>0:
        indexMaxWorkToDo=CumuFlow[3].index(max(CumuFlow[3]))
        #print "Dev%i - getting %s Ready with %i hours capacity on %s" %(i+1,CumuFlow[0][indexMaxWorkToDo],DevTime[i+1][j],DevTime[0][j])
        #subtract devtime from cumuflow
        CumuFlow[3][indexMaxWorkToDo]=CumuFlow[3][indexMaxWorkToDo]-DevTime[i+1][j]
        #if cumuflow is >= 0 then DevTime is 0 else DevTime=abs(CumuFlow);CumuFlow=0
        if CumuFlow[3][indexMaxWorkToDo]>=0:
          DevTime[i+1][j]=0
        else:
          DevTime[i+1][j]=abs(CumuFlow[3][indexMaxWorkToDo])
          CumuFlow[3][indexMaxWorkToDo]=0
        if CumuFlow[3][indexMaxWorkToDo]==0: #phase complete
          CumuFlow[6][indexMaxWorkToDo]=DevTime[0][j].strftime('%d/%m/%Y') #note date complete
    elif max(CumuFlow[2])>0: #there is some story in progress to work on
      while DevTime[i+1][j]>0 and max(CumuFlow[2])>0:
        indexMaxWorkToDo=CumuFlow[2].index(max(CumuFlow[2]))
        #print "Dev%i - getting %s Ready with %i hours capacity on %s" %(i+1,CumuFlow[0][indexMaxWorkToDo],DevTime[i+1][j],DevTime[0][j])
        #subtract devtime from cumuflow
        CumuFlow[2][indexMaxWorkToDo]=CumuFlow[2][indexMaxWorkToDo]-DevTime[i+1][j]
        #if cumuflow is >= 0 then DevTime is 0 else DevTime=abs(CumuFlow);CumuFlow=0
        if CumuFlow[2][indexMaxWorkToDo]>=0:
          DevTime[i+1][j]=0
        else:
          DevTime[i+1][j]=abs(CumuFlow[2][indexMaxWorkToDo])
          CumuFlow[2][indexMaxWorkToDo]=0
        if CumuFlow[2][indexMaxWorkToDo]==0: #phase complete
          CumuFlow[5][indexMaxWorkToDo]=DevTime[0][j].strftime('%d/%m/%Y') #note date complete
          CumuFlow[3][indexMaxWorkToDo]=randint(Review_From,Review_To) #generate Review randomized value
    elif max(CumuFlow[1])>0: #there are stories to get ready
      while DevTime[i+1][j]>0 and max(CumuFlow[1])>0:
        indexMaxWorkToDo=CumuFlow[1].index(max(CumuFlow[1]))
        #print "Dev%i - getting %s Ready with %i hours capacity on %s" %(i+1,CumuFlow[0][indexMaxWorkToDo],DevTime[i+1][j],DevTime[0][j])
        #subtract devtime from cumuflow
        CumuFlow[1][indexMaxWorkToDo]=CumuFlow[1][indexMaxWorkToDo]-DevTime[i+1][j]
        #if cumuflow is >= 0 then DevTime is 0 else DevTime=abs(CumuFlow);CumuFlow=0
        if CumuFlow[1][indexMaxWorkToDo]>=0:
          DevTime[i+1][j]=0
        else:
          DevTime[i+1][j]=abs(CumuFlow[1][indexMaxWorkToDo])
          CumuFlow[1][indexMaxWorkToDo]=0
        if CumuFlow[1][indexMaxWorkToDo]==0: #phase complete
          CumuFlow[4][indexMaxWorkToDo]=DevTime[0][j].strftime('%d/%m/%Y') #note date complete
          CumuFlow[2][indexMaxWorkToDo]=randint(InProgress_From,InProgress_To) #generate Work In Progress randomized value

printCumuFlow()
printDevTime()
if max(CumuFlow[1])+max(CumuFlow[2])+max(CumuFlow[3])>0:
    print "Project ran out of time"
else:
    print "Project completed on %s" %(max(CumuFlow[6]))