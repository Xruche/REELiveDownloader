from urllib.request import urlopen
import json
import datetime
import sys

def ValidateRegionCode(code):
	RegionCodes = {
	"Peninsula":{"urlCode": "Peninsula", "curva":"DEMANDA", "name" : "Peninsula"},
	"Baleares":{"urlCode": "Baleares", "curva":"BALEARES", "name" : "Baleares"},
	"Mallorca":{"urlCode": "Baleares", "curva":"MALLORCA", "name" : "Mallorca"},
	"Menorca":{"urlCode": "Baleares", "curva":"MENORCA", "name" : "Menorca"},
	"Ibiza":{"urlCode": "Baleares", "curva":"IBIZA", "name" : "Ibiza"},
	"Formentera":{"urlCode": "Baleares", "curva":"FORMENTERA", "name" : "Formentera"},
	"Tenerife":{"urlCode": "Canarias", "curva":"TENERIFE", "name" : "Tenerife"},
	"ElHierro":{"urlCode": "Canarias", "curva":"EL_HIERRO", "name" : "ElHierro"},
	"GranCanaria":{"urlCode": "Canarias", "curva":"GCANARIA", "name" : "GranCanaria"},
	"LanzaroteFuerteventura":{"urlCode": "Canarias", "curva":"LZ_FV", "name" : "LanzaroteFuerteventura"},
	"LaGomera":{"urlCode": "Canarias", "curva":"LA_GOMERA", "name" : "LaGomera"},
	"Lanzarote":{"urlCode": "Canarias", "curva":"LANZAROT", "name" : "Lanzarote"},
	"LaPalma":{"urlCode": "Canarias", "curva":"LA_PALMA", "name" : "La Palma"},
	"Fuerteventura":{"urlCode": "Canarias", "curva":"FUERTEVE", "name" : "Fuerteventura"}
	}
	
	if (code in RegionCodes):
		return True, RegionCodes[code]
	else:
		return False, 0

def DisplayHelpPage():
	print("""REELiveDownloader usage:
	
	This software downloads data from demanda.ree.es into a csv file cotaining all the data displayed in the charts in a time-series csv format
	
	Usage :
	
	python3 REELiveDownloader.py <region> <begin time> <optional: end time>
	
		Only 2 or 3 arguments must be provided in the stated order.
		Both <begin time> and <end time> should be given in YYYY-MM-DD format.
		End time argument is optional, if no end time is provided, the current time will be used as end time.
		The resulting data is collected in a file named REE<region>_<begin time>_to_<end time>
	
		Available regions :
			Peninsula
			Baleares
			Mallorca
			Menorca
			Ibiza
			Formentera
			Tenerife
			ElHierro
			GranCanaria
			LanzaroteFuerteventura
			Fuerteventura
			LaGomera
			Lanzarote
			LaPalma
			
	usage example : 
		
		python3 REELiveDownloader.py Lanzarote 2020-9-30
		
		or
		
		python3 REELiveDownloader.py Lanzarote "2020-09-30" "2021-09-30"

	by Xavier Ruché : x.ruche (at) gmail.com
""")

def SaveDataToCSV (TotalDataList, TotalHeaderList,  filename):
	with open(filename+".csv", 'w') as f:
		line = ""
		for Header in TotalHeaderList:
			line += Header + ","
		line = line[:-1]+"\n"
		f.write(line)
		for Element in TotalDataList:
			line = ""
			for Header in TotalHeaderList:
				try:
					line += str(Element[Header]) + ","
				except:
					line = line+"-,"
			line = line[:-1]+"\n"
			f.write(line)

def GetTimeFromTimeStamp(timestamp):
	
	try:
		timeObj = datetime.datetime.fromisoformat(timestamp)
		valid = True;
		return timeObj, valid
	except ValueError:
		valid = False;
		return False, valid

def GetDate(dateTimeObj):
	##Get the iso representation of time (YYYY-MM-DD) of the given time stated as a dateTimeObj
	
	date = dateTimeObj.isoformat().split("T")
	return (date[0])

def GetTimestampsList (dataList, time):
	ISODayString = GetDate(time)
	TimestampsList = []
	for Element in dataList:
		if (ISODayString in Element["ts"]):
			TimestampsList.append(Element["ts"])
	return TimestampsList

def PreParseJSONs (dataList, time):
	ISODayString = GetDate(time)
	ReturnDictionary = {}
	for Element in dataList:
		if (ISODayString in Element["ts"]):
			ReturnDictionary[Element["ts"]] = Element
	return ReturnDictionary
		
def ParseData(Generation_Data, MinMax_Data, ForecastProgrammed_Data, C02_Data, time):

	EnergyCodesReference = {
    "total":"Total",
    "renovables":"Renewable",
    "norenovables":"Non renovables",
    
    "nuc":"Nuclear",
    "gf":"Fuel/gas",
    "car":"Coal",
    "cc":"Combined cycle",
    "el":"Wind",
    "hid":"Hydro",
    "aut":"Other special regime",
    "inter":"Int. exchanges",
    "sol":"Solar",
    "icb":"Balear link",
    "termRenov":"Thermal renewable",
    "cogenResto":"Cogeneration and waste",
    "otrRen":"Other renewables",

    "die":"Diesel engines",
    "gas":"Gas turbine",
    "cc":"Combined cycle",
    "cogen":"Cogeneration",
    "genAux":"Auxiliary generation",
    "resid":"Wastes",
    "cb":"Balearic-Peninsula link",
    "tnr":"Other special regime",
    "trn":"Thermal renewable",
    "eol":"Wind",
    "emm":"Mallorca-Menorca link",
    "fot":"Solar PV",
    "emi":"Mallorca-Ibiza link",
    "eif":"Ibiza-Formentera link",
    "solFot":"Solar PV",
    "solTer":"Solar thermal",


    "ele":"Electric",    
    "vap":"Vapor turbine",
    "solar_termica":"Solar thermal"
  }

	TimestampsList = GetTimestampsList(ForecastProgrammed_Data["valoresPrevistaProgramada"], time)
	
	PreParsedGeneration_data = PreParseJSONs (Generation_Data["valoresHorariosGeneracion"], time);
	PreParsedForecastProgrammed_data = PreParseJSONs (ForecastProgrammed_Data["valoresPrevistaProgramada"], time);
	
	ReturnDataList = []
	ReturnHeaderList = ["TimeStamp", "Year", "Month", "Day", "Hour", "Minute", "Programmed Power Demand", "Forecasted Power Demand", "Real Power Demand"]
	firstRun = True
	for TimeStamp in TimestampsList:
		if (TimeStamp in PreParsedGeneration_data):
			CurrentTimeObject, validTimeStamp = GetTimeFromTimeStamp(TimeStamp)
			if (validTimeStamp == True):
				TimestampData = {}
				TimestampData["TimeStamp"] = TimeStamp										##Timestamp of the data in YYYY-MM-DD HH:MM
				TimestampData["Year"] = CurrentTimeObject.year
				TimestampData["Month"] = CurrentTimeObject.month
				TimestampData["Day"] = CurrentTimeObject.day
				TimestampData["Hour"] = CurrentTimeObject.hour
				TimestampData["Minute"] = CurrentTimeObject.minute
				TimestampData["Programmed Power Demand"] = PreParsedForecastProgrammed_data[TimeStamp]["pro"]				##Programmed power extracted from Forecast_Programmed_Data in the given timestamp (DataElement["ts"])
				TimestampData["Forecasted Power Demand"] = PreParsedForecastProgrammed_data[TimeStamp]["pre"]				##Forecasted power extracted from Forecast_Programmed_Data in the given timestamp (DataElement["ts"])
				TimestampData["Real Power Demand"] = PreParsedGeneration_data[TimeStamp]["dem"]					##Forecasted power extracted from Forecast_Programmed_Data in the given timestamp (DataElement["ts"])
				
				for EnergyType in PreParsedGeneration_data[TimeStamp]:
					if (EnergyType in EnergyCodesReference):
						TimestampData[EnergyCodesReference[EnergyType]] = PreParsedGeneration_data[TimeStamp][EnergyType]
						if (firstRun):
							ReturnHeaderList.append(EnergyCodesReference[EnergyType])
				for EnergyType in PreParsedGeneration_data[TimeStamp]:
					if (EnergyType in EnergyCodesReference):
						if (firstRun):
							ReturnHeaderList.append(EnergyCodesReference[EnergyType]+ " Emissions")
						if (str("factorEmisionCO2_"+EnergyType) in C02_Data):
							TimestampData[EnergyCodesReference[EnergyType]+ " Emissions"] = PreParsedGeneration_data[TimeStamp][EnergyType] * C02_Data[str("factorEmisionCO2_"+EnergyType)]
						else:
							TimestampData[EnergyCodesReference[EnergyType]+ " Emissions"] = 0.0
				
				ReturnDataList.append(TimestampData)
				if (firstRun == True):
					firstRun = False
			else:
				print("Skipping 10 minutes due to bad-formatted timestamp!!!")
	
	return ReturnDataList, ReturnHeaderList

def QueryData(url):
	response = urlopen(url)
	datastring = response.read()
	datastring = datastring[5:-2]
	return (json.loads(datastring))

def GetREEData(time, RegionCode):
	##Obtain all the data from REE through queries returning JSON objects
	
	##Quey for the energy demand + generation data (MW for each generation method)
	url = "https://demanda.ree.es/WSvisionaMoviles"+RegionCode["urlCode"]+"Rest/resources/demandaGeneracion"+RegionCode["urlCode"]+"?curva="+RegionCode["curva"]+"&fecha="+GetDate(time)
	Generation_data = QueryData(url)
	
	
	##Query for Max and Min power production
	url = "https://demanda.ree.es/WSvisionaMoviles"+RegionCode["urlCode"]+"Rest/resources/maxMin"+RegionCode["urlCode"]+"?curva="+RegionCode["curva"]+"&fecha="+GetDate(time)
	MinMax_data = QueryData(url)

	##Query for Forecast and Programmed power production
	url = "https://demanda.ree.es/WSvisionaMoviles"+RegionCode["urlCode"]+"Rest/resources/prevProg"+RegionCode["urlCode"]+"?curva="+RegionCode["curva"]+"&fecha="+GetDate(time)
	ForecastProgrammed_data = QueryData(url)
	
	##Query for C02 emissions factor
	url = "https://demanda.ree.es/WSvisionaMoviles"+RegionCode["urlCode"]+"Rest/resources/coeficientesCO2?curva="+RegionCode["curva"]+"&mapId2="+RegionCode["urlCode"]+"&fecha="+GetDate(time)
	C02_data = QueryData(url)
	
	return (ParseData(Generation_data, MinMax_data, ForecastProgrammed_data, C02_data, time))



Allset = False;
regionCode = 0

if (len(sys.argv) == 1 ):
	DisplayHelpPage()

elif (len(sys.argv) > 4):
	print("Too many arguments provided! please refer to the manual page with \"python3 REELiveDownloader.py -help\"")
else:
	if (sys.argv[1] == "-help"):
		DisplayHelpPage()
	else:
		validRegion, regionCode = ValidateRegionCode(sys.argv[1])
		if validRegion:
			if (len(sys.argv) == 3):
				try:
					BeginTime = datetime.datetime.fromisoformat(sys.argv[2])
				except ValueError:
					print("Invalid begining date provided, check correct formatting (YYYY-MM-DD) and validity of the given date!")
					print(" ")
					exit()
				EndTime = datetime.datetime.now()
				Allset = True
			else:
				try:
					BeginTime = datetime.datetime.fromisoformat(sys.argv[2])
				except ValueError:
					print("Invalid begining date provided, check correct formatting (YYYY-MM-DD) and validity of the given date!")
					print(" ")
					exit()
				
				try:
					EndTime = datetime.datetime.fromisoformat(sys.argv[3])
				except ValueError:
					print("Invalid end date provided, check correct formatting (YYYY-MM-DD) and validity of the given date!")
					print(" ")
					exit()
				Allset = True
		else:
			Allset = False
			print("Bad Region Code, please refer to the -help page for correct usage :")
			print("")
			print("	python3 REELiveDownloader.py -help")
			exit()

if Allset:	
	chrono1 = datetime.datetime.now()
	currentTime = BeginTime
	TotalDataList = []
	TotalHeaderList = []
	if (EndTime > BeginTime):
		while (currentTime<=EndTime):
			print ("Starting download and parsing for data of :  " + str(currentTime))
			DataList, HeaderList = GetREEData(currentTime, regionCode)
			TotalDataList += DataList
			TotalHeaderList = HeaderList
			currentTime += datetime.timedelta(days=1) 
		SaveDataToCSV (TotalDataList, TotalHeaderList,  "REE"+regionCode["name"]+"_"+GetDate(BeginTime)+"_to_"+GetDate(EndTime))
	else:
		print("Please put the Beginning time and Ending Time in the correct order!")
	chrono2 = datetime.datetime.now()
	delta = (chrono2 -chrono1)
	print("")
	print("WOW!, that took "+str(delta.seconds//3600)+":"+str((delta.seconds//60)%60)+":"+str(delta.seconds%60)+" to download.")





