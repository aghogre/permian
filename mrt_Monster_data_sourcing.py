from bs4 import BeautifulSoup
import requests
import logging
from datetime import datetime, timedelta
import hashlib
import json
from mongoDBConnection import bulk_mongo_update, initialize_mongo, bulk_mongo_insert
import logging.handlers
import time


def mrt_monster_scrapper(obj, start, end):
    feed_object = []
    City = ["Midland__2C-TX","Odessa__2C-TX"]
    i=0

    while i<len(City):
        for page in range(1, 50):

            midland_url = "https://jobs.local-jobs.monster.com/search/?where="+City[i]+"&rad=40&page="+str(page)
            midland_url_data =  requests.get(midland_url)
            soup = BeautifulSoup(midland_url_data.content)
            div_data = soup.find('section', {'id': 'resultsWrapper'})
            data = div_data.findAll('div', {'class': ['js_result_container clearfix','js_result_container js_job-bold clearfix']})
            try:
                for url in data:
                    json_object = {}
                    URL = url.find('a', href=True)
                    url_data = requests.get(URL['href'])
                    url_data_soup = BeautifulSoup(url_data.content)
                    jobDetail = url_data_soup.find('div', {'id':'JobViewHeader'})
                    jd = jobDetail.find('div', {'class': 'heading'})
                    job = jd.find('h1', {'class': 'title'}).text
                    # Striping Job Title and Company Name from a string using at and from.
                    if job.find(" at ") != -1:
                        company = job.split(" at ")[1]
                        jobTitle = job.split(" at ")[0]
                        json_object['Company'] = company.rstrip()
                        json_object['Job Title'] = jobTitle.rstrip()
                    elif job.find(" from ") != -1:
                        company = job.split(" from ")[1]
                        jobTitle = job.split(" from ")[0]
                        json_object['Company'] = company.rstrip()
                        json_object['Job Title'] = jobTitle.rstrip()
                    else:
                        pass
                    jobDetail2 =  url_data_soup.find('div', {'class':'mux-job-summary'})  
                    listdata = jobDetail2.findAll('dl', {'class': 'header'})
                    for summary in listdata:
                            key = summary.find('dt', {'class': 'key'})
                            value = summary.find('dd', {'class': 'value'})
                            json_object[key.text] = value.text.rstrip()
                 
                    # Coverting into date format
                    if '30+' in json_object['Posted'].split(" ")[0]:
                        posted_date = datetime.today() - timedelta(days=30)
                    elif 'Today' in json_object['Posted'].split(" ")[0]:
                        posted_date = datetime.today()
                    else:
                        posted_date = datetime.today() - timedelta(days=int(json_object['Posted'].split(" ")[0]))

                    #Applying condition to check for only latest data from Monster using latest date from mongo data. 
                    logging.info('Scraping url')
                    if obj is not None:
                        if posted_date.date()>datetime.strptime(obj['Posted'], '%Y-%m-%d').date():
                            json_object['Posted'] = str(posted_date.date())
                            
                            #Applying Checksum for unique identification of each Data in mongo
                            checksum = hashlib.md5(json.dumps(json_object, sort_keys=True)).hexdigest()
                            json_object['checksum'] = checksum
                            feed_object.append(json_object.copy())
                            
      
                            
                    else:
                        json_object['Posted'] = str(posted_date.date())
                        #Applying Checksum for unique identification of each Data in mongo
                        checksum = hashlib.md5(json.dumps(json_object, sort_keys=True)).hexdigest()
                        json_object['checksum'] = checksum
                        feed_object.append(json_object.copy())
                time.sleep(60)
                        
                            
                    
            except:
                logging.warn("Issue while Souping URL")
                print URL['href']
        i+=1
        time.sleep(120)
    time.sleep(1800)

        
    return  feed_object

def mongo_insert(mongo_colln, feed_object):
    if(len(feed_object) > 0):
          # Inserting to mongo in first execution.  
          if mongo_colln.count() == 0:
              bulk_mongo_insert(mongo_colln, feed_object)
              logging.info("Inserting to mongo")
                            
          else:
              #updating to mongo with new data only
              bulk_mongo_update(mongo_colln, feed_object)
              logging.info("Updating to mongo")
                            
    else:
        logging.info("Empty data from website")
        

def execution_monster():
    
    # Initializing Mongo With Collection Name
    mongo_colln = initialize_mongo('MRT_Monster')
    
    try:
        #Checking for latest date for data in Mongo
        if mongo_colln.find().sort("Posted", -1).limit(1).count()>0:
            for obj in mongo_colln.find().sort("Posted", -1).limit(1):
                #Scrapping all pages of Monster.com range 1 to 50.
                feed_object = mrt_monster_scrapper(obj)
                
                mongo_insert(mongo_colln, feed_object)
 
                
        elif mongo_colln.find().sort("Posted", -1).limit(1).count() == 0:
            obj = None
            feed_object = mrt_monster_scrapper(obj)
            mongo_insert(mongo_colln, feed_object)
                
            
        else:
            pass
     
    except:
        raise
                     
    
        

    
    """with open('listfile.json', 'w') as filehandle:  
        for listitem in feed_object:
            filehandle.write('%s\n' % listitem)"""
    