# REELiveDownloader
Simple Python3 program to download charted data from REE's (Red Electrica Española) website.

This simple software package lets the user automatically download data which can be obtained at https://demanda.ree.es/visiona/ website, containing the latest information available about the Spanish Electrical Grid (and open for use).

This python3 package depends on the following libraries:

- json
- datetime
- sys

## Usage

python3 REELiveDownloader.py <region> <begin time> <optional: end time>
	
		Only 2 or 3 arguments must be provided in the stated order.
		Both <begin time> and <end time> should be given in YYYY-MM-DD format.
		End time argument is optional, if no end time is provided, the current time will be used as end time.
		The resulting data is collected in a file named REE<region>_<begin time>_to_<end time>.csv
	
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
