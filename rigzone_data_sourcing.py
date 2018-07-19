# -*- coding: utf-8 -*-
"""
Created on Mon Jul 09 22:48:28 2018

@author: ADMIN
"""

from bs4 import BeautifulSoup
import requests
import logging
import hashlib
from datetime import datetime
import json
from mongoDBConnection import bulk_mongo_update, initialize_mongo, bulk_mongo_insert



def rigzone_scrapper(obj):
    sitemap_url = 'http://www.rigzone.com/GoogleSiteMapForJobs.asp'
    resp = requests.get(sitemap_url)
    soup = BeautifulSoup(resp.content)
    urls = soup.findAll('url')
    out = []
    for u in urls:
        Us_jobfiltr = "http://www.rigzone.com/oil/jobs/regional/north-america/us-united-states"
        loc = u.find('loc').string
        if Us_jobfiltr in loc:
            out.append(loc)
    
    rig_data = []
    for catagory_url in out[1:]:
        resp1 = requests.get(catagory_url)
        soup1 = BeautifulSoup(resp1.content)
        data = soup1.findAll("div",{"id":"content", "style":"margin-bottom:3px;width:100%"})
        
        for d in data:
            comp_txt = d.find("address")
            text = str(comp_txt.text.strip().replace(" ",""))
            if "Midland" in text or "Odessa" in text:
                data1 = d.findAll("div", {"class": "holder"})
                
                for a in data1:
                    url = a.findAll("a", href=True)
                    for u in url:
                        rig_json = {}
                        link = u['href']
                        resp2 = requests.get(link)
                        soup2 = BeautifulSoup(resp2.content)
                        data = soup2.findAll("article",{"class":"update-block current"})
                        try:
                            rig_json['jobtitle'] =  data[0].find("h1").string
                            rig_json['experience'] = data[0].find("span",{"class":"experience"}).text
                            rig_json['company'] = str(data[0].find("address").contents[0]).strip()
                            for loc in data[0].find("address").contents:
                                if "Midland" in loc or "Odessa" in loc:
                                    location = loc.strip()
                            rig_json['location'] =  location
                            pstd_date_oldformat = data[0].find("time").text.replace("Posted:","").strip()
                            posted_date = datetime.strptime(pstd_date_oldformat,'%b %d, %Y')
                            
                            logging.info('Scraping url')
                            if obj is not None:
                                if posted_date.date()>datetime.strptime(obj['Posted'], '%Y-%m-%d').date():
                                    rig_json['Posted'] = str(posted_date.date())
                                    
                                    #Applying Checksum for unique identification of each Data in mongo
                                    checksum = hashlib.md5(json.dumps(rig_json, sort_keys=True)).hexdigest()
                                    rig_json['checksum'] = checksum
                                    rig_data.append(rig_json.copy()) 
                                    
                            else:
                                rig_json['Posted'] = str(posted_date.date())
                                #Applying Checksum for unique identification of each Data in mongo
                                checksum = hashlib.md5(json.dumps(rig_json, sort_keys=True)).hexdigest()
                                rig_json['checksum'] = checksum
                                rig_data.append(rig_json.copy()) 
                            
                        except:
                            logging.warn("Issue while Souping last level URL")
                            
                       
    return  rig_data
                        

def mongo_insert(mongo_colln, rig_data):
    if(len(rig_data) > 0):
          # Inserting to mongo in first execution.  
          if mongo_colln.count() == 0:
              bulk_mongo_insert(mongo_colln, rig_data)
              logging.info("Inserting to mongo")
                            
          else:
              #updating to mongo with new data only
              bulk_mongo_update(mongo_colln, rig_data)
              logging.info("Updating to mongo")
                            
    else:
        logging.info("Empty data from website")
        

def execution_rigzone():
    
    # Initializing Mongo With Collection Name
    mongo_colln = initialize_mongo('RIGZONE')
    
    try:
        #Checking for latest date for data in Mongo
        if mongo_colln.find().sort("Posted", -1).limit(1).count()>0:
            for obj in mongo_colln.find().sort("Posted", -1).limit(1):
                #Scrapping all pages of Monster.com range 1 to 50.
                rig_data = rigzone_scrapper(obj)
                
                mongo_insert(mongo_colln, rig_data)
 
                
        elif mongo_colln.find().sort("Posted", -1).limit(1).count() == 0:
            obj = None
            rig_data = rigzone_scrapper(obj)
            mongo_insert(mongo_colln, rig_data)
                
            
        else:
            pass
     
    except:
        raise

    
    '''with open('listfile.json', 'w') as filehandle:  
        for listitem in rig_data:
            filehandle.write('%s\n' % listitem)'''

