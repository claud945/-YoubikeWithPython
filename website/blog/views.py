# coding=UTF-8
from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
from django.http import HttpResponse




"""
This Python code is based on Java code by Lee Jacobson found in an article
entitled "Applying a genetic algorithm to the travelling salesman problem"
that can be found at: http://goo.gl/cJEY1
"""
import json, requests
import math
import random

#來自OpenData的新北市YOUBIKE的資料 是JSON檔,
#檔案匯入區
url = 'http://data.ntpc.gov.tw/api/v1/rest/datastore/382000000A-000352-001'
resp = requests.get(url=url)
data = json.loads(resp.text.encode('utf-8'))

RouteArray=[];
del RouteArray[:]


#建立City類別
class City:
   def __init__(self, x=None, y=None,z=None,x1=None):
      self.x = None
      self.y = None
      self.z = None
      if x is not None:
         self.x = x
      else:
         self.x = int(random.random() * 200)
      if y is not None:
         self.y = y
      else:
         self.y = int(random.random() * 200)
      if z is not None:
         self.z = z
      else:
         self.z = "no place name"
      if x1 is not None:
           self.x1=x1
      else:
           self.x1=0


   def getX(self):
      return self.x

   def getY(self):
      return self.y

   def getCityName(self):
   	  return self.z

   def getCityHowMany(self):
       return self.x1

   def distanceTo(self, city):
      xDistance = abs(self.getX() - city.getX())
      yDistance = abs(self.getY() - city.getY())
      distance = math.sqrt( (xDistance*xDistance) + (yDistance*yDistance) )
      return distance

   def __repr__(self):
      RouteArray.append([str(self.getCityName().encode('utf-8')),str(self.getX()),str(self.getY()),str(self.getCityHowMany())])
      return  str( str(self.getX())  + str(self.getY())+"   " + str(self.getCityHowMany())).encode('utf-8') + "\n"



#建立TourManager類別
class TourManager:
   def __init__(self):
   	  self.destinationCities=[]
   def addCity(self, city):
      self.destinationCities.append(city)

   def getCity(self, index):
      return self.destinationCities[index]

   def numberOfCities(self):
      return len(self.destinationCities)

#建立Tour類別
class Tour:
   def __init__(self, tourmanager, tour=None):
      self.tourmanager = tourmanager
      self.tour = []
      del self.tour[:]
      self.fitness = 0.0
      self.distance = 0
      if tour is not None:
         self.tour = tour
      else:
         for i in range(0, self.tourmanager.numberOfCities()):
            self.tour.append(None)

   def __len__(self):
      return len(self.tour)

   def __getitem__(self, index):
      return self.tour[index]

   def __setitem__(self, key, value):
      self.tour[key] = value

   def __repr__(self):
      geneString = "|"
      for i in range(0, self.tourSize()):
         geneString += str(self.getCity(i)) + "|"
      return geneString

   def generateIndividual(self):
      for cityIndex in range(0, self.tourmanager.numberOfCities()):
         self.setCity(cityIndex, self.tourmanager.getCity(cityIndex))
      random.shuffle(self.tour)

   def getCity(self, tourPosition):
      return self.tour[tourPosition]

   def setCity(self, tourPosition, city):
      self.tour[tourPosition] = city
      self.fitness = 0.0
      self.distance = 0

   def getFitness(self):
      if self.fitness == 0:
         spaceWeight = 0.6
         self.fitness = (float(self.getCity(1).getCityHowMany())
                        *spaceWeight ) * (1/float(self.getDistance()))
      return self.fitness

   def getDistance(self):
      if self.distance == 0:
         tourDistance = 0
         for cityIndex in range(0, self.tourSize()):
            fromCity = self.getCity(cityIndex)
            destinationCity = None
            if cityIndex+1 < self.tourSize():
               destinationCity = self.getCity(cityIndex+1)
            else:
               destinationCity = self.getCity(0)
            tourDistance += fromCity.distanceTo(destinationCity)
         self.distance = tourDistance
      return self.distance

   def tourSize(self):
      return len(self.tour)

   def containsCity(self, city):
      return city in self.tour

#建立Population類別
class Population:
   def __init__(self, tourmanager, populationSize, initialise):
      self.tours = []
      for i in range(0, populationSize):
         self.tours.append(None)

      if initialise:
         for i in range(0, populationSize):
            newTour = Tour(tourmanager)
            newTour.generateIndividual()
            self.saveTour(i, newTour)

   def __setitem__(self, key, value):
      self.tours[key] = value

   def __getitem__(self, index):
      return self.tours[index]

   def saveTour(self, index, tour):
      self.tours[index] = tour

   def getTour(self, index):
      return self.tours[index]

   def getFittest(self):
      fittest = self.tours[0]
      for i in range(0, self.populationSize()):
         if fittest.getFitness()<= self.getTour(i).getFitness():
            fittest = self.getTour(i)
      return fittest

   def populationSize(self):
      return len(self.tours)

#建立GA類別
class GA:
   def __init__(self, tourmanager):
      self.tourmanager = tourmanager
      '''參數調整區域'''
      #變異度
      self.mutationRate = 0.015
      #設定競爭的大小，約大速度越慢
      self.tournamentSize = 50
      #設定是否存在菁英主義
      self.elitism = True

   def evolvePopulation(self, pop):
      newPopulation = Population(self.tourmanager, pop.populationSize(), False)
      elitismOffset = 0
      if self.elitism:
         newPopulation.saveTour(0, pop.getFittest())
         elitismOffset = 1

      for i in range(elitismOffset, newPopulation.populationSize()):
         parent1 = self.tournamentSelection(pop)
         parent2 = self.tournamentSelection(pop)
         child = self.crossover(parent1, parent2)
         newPopulation.saveTour(i, child)

      for i in range(elitismOffset, newPopulation.populationSize()):
         self.mutate(newPopulation.getTour(i))

      return newPopulation

   #交配
   def crossover(self, parent1, parent2):
      child = Tour(self.tourmanager)
      #選擇開始的位置
      startPos = int(random.random() * parent1.tourSize())
      #選擇結束的位置
      endPos = int(random.random() * parent1.tourSize())

      #從0開始對於child的tourSize進行迴圈
      for i in range(0, child.tourSize()):
      	#如果開始的位置小於結束的位置 並且 i大於開始的位置 並且 i小於結束的位置
      	#    startPos <     i    < endPos
         if startPos < endPos and i > startPos and i < endPos:
         	#複製parent1的city「i」給孩子
            child.setCity(i, parent1.getCity(i))
        #假設開始的位置大於結束的位置
         elif startPos > endPos:
         	#並且 i 沒有 小於 startPos 並且 i沒有大於endPos
         	#  i<endPos<		<startPos<i
            if not (i < startPos and i > endPos):
               child.setCity(i, parent1.getCity(i))

      for i in range(0, parent2.tourSize()):
      	#找到parent2還沒有放如child的city
         if not child.containsCity(parent2.getCity(i)):
            for ii in range(0, child.tourSize()):
            	#如果當child的city還是空的時候，就把parent2的city補上去
               if child.getCity(ii) == None:
                  child.setCity(ii, parent2.getCity(i))
                  break

      return child
   #突變
   def mutate(self, tour):
      for tourPos1 in range(0, tour.tourSize()):
         if random.random() < self.mutationRate:
            tourPos2 = int(tour.tourSize() * random.random())

            city1 = tour.getCity(tourPos1)
            city2 = tour.getCity(tourPos2)

            tour.setCity(tourPos2, city1)
            tour.setCity(tourPos1, city2)
   #競爭法
   def tournamentSelection(self, pop):
      tournament = Population(self.tourmanager, self.tournamentSize, False)
      for i in range(0, self.tournamentSize):
         randomId = int(random.random() * pop.populationSize())
         tournament.saveTour(i, pop.getTour(randomId))
      fittest = tournament.getFittest()
      return fittest



def youbikeGo(PopulationArgumet=50,Itenery=50):

   tourmanager = TourManager()

   # 增加DATA至程式中  Create and add our data
   for x in range(len(data['result']['records'])):
   	city = City(float(data['result']['records'][x]['lat']), float(data['result']['records'][x]['lng']),data['result']['records'][x]['sna'],data['result']['records'][x]['sbi'])
   	tourmanager.addCity(city)
   	pass


   # 初始化母體參數Initialize population
   pop = Population(tourmanager, PopulationArgumet, True);
   #print(str(pop.getFittest()))

   # Evolve population for 50 generations
   ga = GA(tourmanager)
   pop = ga.evolvePopulation(pop)
   #firstTime = pop.getFittest().getDistance();
   for i in range(0, Itenery):
      pop = ga.evolvePopulation(pop)
      #儲存第一次使用的變數

   print(pop.getFittest())
   print("finish")
   return(RouteArray)

def youbike(request):
   del RouteArray[:]
   print("Doing no params")
   return JsonResponse({'data':youbikeGo()})
   #return HttpResponse("helloworld")
def testParemeter(request,params1,params2):
	print("Paremiter WebServiceON")
	print("Population: "+params1)
	print("Itenery: " + params2)
	del RouteArray[:]
	return JsonResponse({'data':youbikeGo(int(params1),int(params2))})
  