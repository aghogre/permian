# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 17:05:51 2018

@author: Rajesh
"""
from bs4 import BeautifulSoup
import requests
import logging
from datetime import datetime, timedelta
import hashlib
import json
from mongoDBConnection import bulk_mongo_update, initialize_mongo, bulk_mongo_insert
import re



def midlandgovtjobs_scraper(obj):
    
    govtjobs = []
    
    for j in range(1,9):
        url = "https://www.governmentjobs.com/jobs?page="+str(j)+"&location=Midland%2C%20TX&distance=40"
        response = requests.get(url)
        soup = BeautifulSoup(response.content)
        data = soup.findAll("li",{"class":"job-item"})
        try:
            for d in data:
                json_object = {}
                json_object["Job Title"] = d.find("h3").text.strip()
                json_object["location"] = d.find("div",{"class":"primaryInfo job-location"}).text.strip()
        
                json_object["Job Type"] = str(d.findAll("div",{"class":"primaryInfo"})[1].text.strip()).split(" - ")[0]
                json_object['Salary'] = str(d.findAll("div",{"class":"primaryInfo"})[1].text.strip()).split(" - ")[1]
                for date in d.findAll("div",{"class":"termInfo"}):
                    date1 = date.find("span").text
                    posteddate = datetime.today() - timedelta(int(re.findall(r'\d+',date1)[0]))
                posted_date = posteddate
                
                logging.info('Scraping url')
                if obj is not None:
                    if posted_date.date()>datetime.strptime(obj['Posted'], '%Y-%m-%d').date():
                        json_object['Posted'] = str(posted_date.date())
                        
                        #Applying Checksum for unique identification of each Data in mongo
                        checksum = hashlib.md5(json.dumps(json_object, sort_keys=True)).hexdigest()
                        json_object['checksum'] = checksum
                        govtjobs.append(json_object.copy())
                    
  
                    
                else:
                    json_object['Posted'] = str(posted_date.date())
                    #Applying Checksum for unique identification of each Data in mongo
                    checksum = hashlib.md5(json.dumps(json_object, sort_keys=True)).hexdigest()
                    json_object['checksum'] = checksum
                    govtjobs.append(json_object.copy())
                
                            
                    
        except:
            logging.warn("Issue while Souping URL")
            
    return govtjobs

def mongo_insert(mongo_colln, govtjobs):
    if(len(govtjobs) > 0):
          # Inserting to mongo in first execution.  
          if mongo_colln.count() == 0:
              bulk_mongo_insert(mongo_colln, govtjobs)
              logging.info("Inserting to mongo")
                            
          else:
              #updating to mongo with new data only
              bulk_mongo_update(mongo_colln, govtjobs)
              logging.info("Updating to mongo")
                            
    else:
        logging.info("Empty data from website")
        

def execution_govt():
    
    # Initializing Mongo With Collection Name
    mongo_colln = initialize_mongo('GovtJobs')
    
    try:
        #Checking for latest date for data in Mongo
        if mongo_colln.find().sort("Posted", -1).limit(1).count()>0:
            for obj in mongo_colln.find().sort("Posted", -1).limit(1):
                #Scrapping all pages of govtsite
                govtjobs = midlandgovtjobs_scraper(obj)
                
                mongo_insert(mongo_colln, govtjobs)
 
                
        elif mongo_colln.find().sort("Posted", -1).limit(1).count() == 0:
            obj = None
            govtjobs = midlandgovtjobs_scraper(obj)
            mongo_insert(mongo_colln, govtjobs)
                
            
        else:
            pass
     
    except:
        raise
 

       