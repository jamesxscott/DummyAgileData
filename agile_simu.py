from random import *
from ruamel.yaml import YAML
import datetime
import os

def initialiseCumuFlow():    
    global TotalInitialWorkHrs 
    # set up randomized values for initial stories in CumuFlow
    for i in range(len(CumuFlow[0])):
      CumuFlow[0][i]="Story ID"+str(i+1)                #assign issue ID's for initial stories
      #assign Ready times (hours) for initial stories
      CumuFlow[1][i]=randint(config_data['randomisation'][1]['grooming_hours']['from'],config_data['randomisation'][1]['grooming_hours']['to'])
      CumuFlow[4][i]=startDate                          #set created date for initial stories
      TotalInitialWorkHrs=TotalInitialWorkHrs+CumuFlow[1][i]

def printCumuFlow():
    print "IssueID,ReadyHrs,InProgressHrs,InReviewHrs,Created,ReadyCmp,InProgressCmp,ReviewCmp"
    for j in range(len(CumuFlow[0])):
      print "%s,%s,%s,%s,%s,%s,%s,%s"  %(CumuFlow[0][j],CumuFlow[1][j],CumuFlow[2][j],CumuFlow[3][j],CumuFlow[4][j],CumuFlow[5][j],CumuFlow[6][j],CumuFlow[7][j])

def printDevTime():  
    print "Date, Dev#1,Dev#2,Dev#3,Dev#4,Dev#5,CountGrooming,CountWIP,CountReview,CountDone"
    for j in range(lengthDevDays):
      print "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s"  %(DevTime[0][j],DevTime[6][j],DevTime[7][j],DevTime[8][j],DevTime[9][j],DevTime[1][j],DevTime[2][j],DevTime[3][j],DevTime[4][j],DevTime[5][j],DevTime[10][j],DevTime[11][j])

def workOnStories(theDate, phase, devID):
    global TotalInitialWorkHrs, TotalBugsHrs
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
            TotalInitialWorkHrs=TotalInitialWorkHrs+CumuFlow[phaseWorkColumn+1][indexMaxWorkToDo]
        elif phase=="Groom":
            CumuFlow[phaseWorkColumn+1][indexMaxWorkToDo]=randint(InProgress_From,InProgress_To) #generate Work In Progress randomized value
            TotalInitialWorkHrs=TotalInitialWorkHrs+CumuFlow[phaseWorkColumn+1][indexMaxWorkToDo]
        elif phase=="Review": #issue completed
            if randint(1,100)<=config_data['randomisation'][6]['chance_of_bug_raised_percent']: #chance of bug being found
                #print "#create new bug"
                CumuFlow[0].append("Bug for " + CumuFlow[0][indexMaxWorkToDo])
                #amount of work for the bug:
                bug_work = randint(config_data['randomisation'][7]['work_to_resolve_bug_hours']['from'],config_data['randomisation'][7]['work_to_resolve_bug_hours']['to'])
                CumuFlow[1].append(bug_work) 
                TotalBugsHrs=TotalBugsHrs+bug_work
                CumuFlow[2].append(0)
                CumuFlow[3].append(0)
                CumuFlow[4].append(theDate) #bug creation date
                CumuFlow[5].append(0)
                CumuFlow[6].append(0)
                CumuFlow[7].append(0)
      
def initialiseDevTime():
    global AvgDevCapacity
    # set up randomized values for developer capacity in DevTime
    absenceLength=0
    currentDate=startDate
    for dayloop in range(0,lengthDevDays):
      for devloop in range(1,len(DevTime)-4): #for each developer
        if absenceLength==0 and randint(1,100) < config_data['randomisation'][8]['chance_of_developer_absence_percent']: 
          #if --- chance of developer absence (if not already absent) then --- length of developer absence (days)
          absenceLength=randint(config_data['randomisation'][9]['length_of_developer_absence_days']['from'],config_data['randomisation'][9]['length_of_developer_absence_days']['to']) 

        DevTime[0][dayloop]=currentDate
        
        if absenceLength > 0:
          DevTime[devloop][dayloop]=0
          absenceLength=absenceLength-1
        else:
          #assign capacity (hours) for the developer on that day
          DevTime[devloop][dayloop]=randint(config_data['randomisation'][5]['developer_capacity_per_day_hours']['from'],config_data['randomisation'][5]['developer_capacity_per_day_hours']['to']) 
          AvgDevCapacity=AvgDevCapacity+DevTime[devloop][dayloop]
      currentDate=currentDate + datetime.timedelta(days=1)
      if currentDate.strftime("%A")=="Saturday":
        currentDate=currentDate + datetime.timedelta(days=2)

def calcLinearExtrapolation(totalNumberOfStories,storiesCompletedSoFar,daysSinceProjectStart):
    #returns remaining number of days required on project to complete all remaining stories
    return (daysSinceProjectStart / storiesCompletedSoFar) * (totalNumberOfStories-storiesCompletedSoFar)
  
#----------------------------------------------------------------------------------------------------------------------
# MAIN
#----------------------------------------------------------------------------------------------------------------------

#read configuration file
yaml=YAML(typ='safe')
with open ("agile_simu_input.yaml", "r") as myfile:
    config_file=myfile.read()
    config_data = yaml.load(config_file)



#monte carlo loop - run simulation many times
print "ProjectCompleteDate,TotalInitialWorkHrs,NumDevs,AvgDevCapacity,TotalBugsHrs,TotalAddedStoriesHrs"
for mcloop in range(0,1000):
    numStories=config_data['randomisation'][0]['num_initial_stories']
    numDevs=config_data['randomisation'][4]['num_developers']
    lengthDevDays=450
    CumuFlow=[[0 for j in range(numStories)] for i in range(8)] #IssueID,ReadyHrs,InProgressHrs,InReviewHrs,Created,ReadyCmp,InProgressCmp,ReviewCmp
    DevTime=[[0 for j in range(lengthDevDays)] for i in range(numDevs+7)] # + Date, CountGrooming,CountWIP,CountReview,CountDone,Estimate1,Estimate2
    startDate=datetime.datetime.strptime(config_data['randomisation'][11]['start_date'], "%d/%m/%Y")
    InProgress_From=config_data['randomisation'][2]['inprogress_hours']['from']
    InProgress_To=config_data['randomisation'][2]['inprogress_hours']['to']
    Review_From=config_data['randomisation'][3]['review_hours']['from']
    Review_To=config_data['randomisation'][3]['review_hours']['to']
    AvgDevCapacity=0
    AvgGroomingHrs=0
    AvgInProgressHrs=0
    AvgReviewHrs=0
    TotalBugsHrs=0
    TotalAddedStoriesHrs=0
    TotalInitialWorkHrs=0
    
    initialiseCumuFlow()
    initialiseDevTime()

    #print initial state
    #printCumuFlow()
    #printDevTime()

    #for each date - for each developer - work on story to complete phase
    currentDate=startDate
    while max(CumuFlow[1])+max(CumuFlow[2])+max(CumuFlow[3])>0: #work remaining
      indexCurrentDate=DevTime[0].index(currentDate)

      for i in range(0,numDevs): #for each developer on given day
          workOnStories(theDate = currentDate, phase = "Review", devID = i+1)
          workOnStories(theDate = currentDate, phase = "InProgress", devID = i+1)
          workOnStories(theDate = currentDate, phase = "Groom", devID = i+1)
          
      #every four weeks (grooming meeting) add 0-2 new stories
      if currentDate.strftime("%A")=="Monday" and currentDate.isocalendar()[1] % 4 == 0: #Monday every fourth week
            numNewStories=randint(config_data['randomisation'][10]['num_stories_added_every_4_weeks']['from'],config_data['randomisation'][10]['num_stories_added_every_4_weeks']['to'])
            while numNewStories>0:
                CumuFlow[0].append("New Story " + str(len(CumuFlow[0])+1))
                #amount of work for the new story:
                newstory_work = randint(config_data['randomisation'][1]['grooming_hours']['from'],config_data['randomisation'][1]['grooming_hours']['to'])
                CumuFlow[1].append(newstory_work) 
                TotalAddedStoriesHrs=TotalAddedStoriesHrs+newstory_work
                CumuFlow[2].append(0)
                CumuFlow[3].append(0)
                CumuFlow[4].append(currentDate) #creation date
                CumuFlow[5].append(0)
                CumuFlow[6].append(0)
                CumuFlow[7].append(0)
                numNewStories=numNewStories-1

      #track numbers in each phase for each day
      DevTime[6][indexCurrentDate]=sum([1 for x in CumuFlow[1] if x > 0]) #CountGrooming
      DevTime[7][indexCurrentDate]=sum([1 for x in CumuFlow[2] if x > 0]) #CountWIP
      DevTime[8][indexCurrentDate]=sum([1 for x in CumuFlow[3] if x > 0]) #CountReview
      DevTime[9][indexCurrentDate]=sum([1 for x in CumuFlow[7] if x <>0]) #CountDone
      if DevTime[9][indexCurrentDate]>0: #wait until one story done before calculating estimate
        DevTime[10][indexCurrentDate]=currentDate + \
            datetime.timedelta(days=calcLinearExtrapolation(
                                                            totalNumberOfStories   = len(CumuFlow[0]),
                                                            storiesCompletedSoFar  = DevTime[9][indexCurrentDate],
                                                            daysSinceProjectStart  = (currentDate-startDate).days
                                                           ))
      if DevTime[9][indexCurrentDate]>5: #wait until six stories done before calculating rolling last five rate estimate  
        #check currentDate-1 until stories done<=5 less than currently
        referenceDate =currentDate
        indexReferenceDate=DevTime[0].index(referenceDate)
        while (DevTime[9][indexCurrentDate]) - (DevTime[9][indexReferenceDate]) < 5:
            referenceDate = referenceDate - datetime.timedelta(days=1)
            if referenceDate.strftime("%A")=="Sunday":
                referenceDate=referenceDate - datetime.timedelta(days=2)
            indexReferenceDate=DevTime[0].index(referenceDate)

        DevTime[11][indexCurrentDate]=currentDate + \
            datetime.timedelta(days=calcLinearExtrapolation(
                                                            totalNumberOfStories   = len(CumuFlow[0])-DevTime[9][indexReferenceDate],
                                                            storiesCompletedSoFar  = DevTime[9][indexCurrentDate]-DevTime[9][indexReferenceDate],
                                                            daysSinceProjectStart  = (currentDate-referenceDate).days
                                                           ))
                                                            
      currentDate=currentDate + datetime.timedelta(days=1)
      if currentDate.strftime("%A")=="Saturday":
        currentDate=currentDate + datetime.timedelta(days=2)
        
      if currentDate not in DevTime[0]:
        break
    
    #calculate Average Dev Capacity over whole project
    AvgDevCapacity=AvgDevCapacity-sum(DevTime[1])
    AvgDevCapacity=AvgDevCapacity-sum(DevTime[2])
    AvgDevCapacity=AvgDevCapacity-sum(DevTime[3])
    AvgDevCapacity=AvgDevCapacity-sum(DevTime[4])
    AvgDevCapacity=AvgDevCapacity-sum(DevTime[5])
    #remove remaining hours in DevTime and divide by number of developers
    AvgDevCapacity=AvgDevCapacity/5

    #printCumuFlow()
    #printDevTime()
    if max(CumuFlow[1])+max(CumuFlow[2])+max(CumuFlow[3])==0:
        print "%s,%s,%s,%s,%s,%s" %((CumuFlow[7][CumuFlow[7].index(max(CumuFlow[7]))]).strftime("%d/%m/%Y"),TotalInitialWorkHrs,numDevs,AvgDevCapacity,TotalBugsHrs,TotalAddedStoriesHrs)
    else:
        print "%s,%s,%s,%s,%s,%s" %("Project ran out of time",TotalInitialWorkHrs,numDevs,AvgDevCapacity,TotalBugsHrs,TotalAddedStoriesHrs)
print "Finished"