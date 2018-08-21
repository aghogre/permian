# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 12:56:40 2017
@author: ANSHUL
"""


from azure.storage.blob import BlockBlobService
import logging
from config import argument_config
from py2neo import  Graph


    
def downloadToAzure(azure_account_name,azure_account_key,azure_container,block_blob_service):

    filename = "Consolidated_sheet_v2_neo4j.csv"
    block_blob_service.create_blob_from_text(
            azure_container,
            filename, filename)

    download_url = block_blob_service.make_blob_url(
        azure_container, filename)
    
    return download_url

def neo4jQueries(download_url, neo4j_host):
    
    url = download_url
    queries = ['LOAD CSV WITH HEADERS FROM "'+url+'" AS line MERGE(tsnvlocation:GeographyCity{Name:line.GeographyCity}) MERGE(tsnvcontact:TSnVContact{Name:line.TSnVContact}) MERGE(Need:Editedneed{Need:line.Editedneed,Priority:line.Priority,TimeFrame:line.TimeFrame}) MERGE(LeadCompany:LeadCompany{LeadCompany:line.LeadCompany}) MERGE(Companycontact:LeadCompanyContact{LeadContact:line.LeadCompanyContact}) MERGE(CompanyTechnology:LeadcompanyTechnology{TechnologyName:line.LeadcompanyTechnology}) CREATE UNIQUE (tsnvlocation)<-[:Location]-(tsnvcontact) CREATE UNIQUE (tsnvcontact)-[:Need]->(Need) CREATE UNIQUE (Need)-[:Lead_Company]->(LeadCompany) CREATE UNIQUE (LeadCompany)-[:Lead_Contact]->(Companycontact) CREATE UNIQUE (LeadCompany)-[:Lead_Technology]->(CompanyTechnology)']
    g = Graph(neo4j_host, bolt = True)
    g.begin(autocommit=True)
    g.delete_all()
    for q in queries:   
        g.run(q)
        
def main():

    
    # collecting the input arguments
    azure_account_name = argument_config.get('azure_account_name')
    azure_account_key = argument_config.get('azure_account_key')
    azure_container = argument_config.get('azure_container')
    neo4j_host = argument_config.get('neo4j_host')
    
    block_blob_service = BlockBlobService(
        account_name=azure_account_name,
        account_key=azure_account_key)
    if not block_blob_service.exists(azure_container):
        block_blob_service.create_container(azure_container)
    try:
        download_url = downloadToAzure(azure_account_name,azure_account_key,azure_container,block_blob_service)
        
        neo4jQueries(download_url, neo4j_host)
    except:
        raise
    
if __name__ == '__main__':
    main()
