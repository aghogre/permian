

import time
from bs4 import BeautifulSoup
import requests
import logging
from datetime import datetime, timedelta
import hashlib
import json
from mongoDBConnection import bulk_mongo_update, initialize_mongo, bulk_mongo_insert



def texassite_scrapper(obj):
    
    texas_site_data = []
    City = ["odessa","midland"]
    i = 0
    while i < len(City):
        if i>0:
            time.sleep(5400)
            
        for count in range(0, 500, 25):
            time.sleep(45)
            url = 'http://www.texasbacktowork.com/Jobs/jobs-in-' + City[i] + '-tx?countryId=3&startindex=' + str(
                count) + '&radius=40'
            # print url
            response = requests.get(url)
            soup = BeautifulSoup(response.content)
            data = soup.findAll('div', {'class': 'Job-container'})
            try:
                for d in data:
                    json_object = {}
                    url = d.find('a', href=True)
                    link = url['href']
                    company = d.find("span", {"class": "Company-name"}).text
                    location = d.find("span", {"class": "Location"}).text
    
                    if d.find("span", {"class": "Normal-date"}) == None:
                        posted_date1 = "0"
                    else:
                        posted_ndays_ago = d.find("span", {"class": "Normal-date"}).text.strip()
                        posted_date1 = posted_ndays_ago.replace("DAYS AGO", "").strip()
                        
                    if not posted_date1.isdigit():
                        posted_date1 = "32"
                    posted_date = datetime.today() - timedelta(int(posted_date1))
    
                    json_object["Job Title"] = d.find("span",
                                                      {"class": "Pos-title col-xs-12 No-padding Ellipsis-title "}).text
                    json_object["Job Type"] = d.find("span", {
                        "class": "Engage-type Ellipsis-text visible-sm-inline visible-md-inline visible-lg-inline"}).text
                    #json_object["Posted Date"] = posted_date.strftime('%d-%m-%Y')
                    json_object["Company"] = company.strip()
                    json_object["location"] = location.strip()
                    
                    logging.info('Scraping url')
                    if obj is not None:
                        if posted_date.date()>datetime.strptime(obj['Posted'], '%Y-%m-%d').date():
                            json_object['Posted'] = str(posted_date.date())
                            
                            #Applying Checksum for unique identification of each Data in mongo
                            checksum = hashlib.md5(json.dumps(json_object, sort_keys=True)).hexdigest()
                            json_object['checksum'] = checksum
                            texas_site_data.append(json_object.copy())
                            
      
                            
                    else:
                        json_object['Posted'] = str(posted_date.date())
                        #Applying Checksum for unique identification of each Data in mongo
                        checksum = hashlib.md5(json.dumps(json_object, sort_keys=True)).hexdigest()
                        json_object['checksum'] = checksum
                        texas_site_data.append(json_object.copy())
                        
                            
                    
            except:
                logging.warn("Issue while Souping URL")
        i+=1
        
    return  texas_site_data



def mongo_insert(mongo_colln, texas_site_data):
    if(len(texas_site_data) > 0):
          # Inserting to mongo in first execution.  
          if mongo_colln.count() == 0:
              bulk_mongo_insert(mongo_colln, texas_site_data)
              logging.info("Inserting to mongo")
                            
          else:
              #updating to mongo with new data only
              bulk_mongo_update(mongo_colln, texas_site_data)
              logging.info("Updating to mongo")
                            
    else:
        logging.info("Empty data from website")
        

def execution_texas():
    
    # Initializing Mongo With Collection Name
    mongo_colln = initialize_mongo('mrtTexas')
    
    try:
        #Checking for latest date for data in Mongo
        if mongo_colln.find().sort("Posted", -1).limit(1).count()>0:
            for obj in mongo_colln.find().sort("Posted", -1).limit(1):
                #Scrapping all pages of Monster.com range 1 to 50.
                texas_site_data = texassite_scrapper(obj)
                
                mongo_insert(mongo_colln, texas_site_data)
 
                
        elif mongo_colln.find().sort("Posted", -1).limit(1).count() == 0:
            obj = None
            texas_site_data = texassite_scrapper(obj)
            mongo_insert(mongo_colln, texas_site_data)
                
            
        else:
            pass
     
    except:
        raise