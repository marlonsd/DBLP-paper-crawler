# Author: Marlon Dias
# coding: utf-8

import math, sys
import requests
from xml.dom import minidom

from collections import defaultdict

# Name of the authors
professors = {'W. Bruce Croft', 'Jamie Callan' ,'Ben Carterette'}

# Get DBLP's key
def get_urlpt(name):
    url = 'http://dblp.uni-trier.de/search/author?xauthor='+name
    response = requests.get(url)
    
    xmldoc = minidom.parseString(response.content)
    item = xmldoc.getElementsByTagName('author')[0]
    
    if item.hasAttribute("urlpt"):
        return item.attributes['urlpt'].value
    
    return None

def list_of_papers(pure_name):
    name = get_urlpt(pure_name)
    
    # In case no URLPT was found
    if name is None:
        return None
    
    url = 'http://dblp.uni-trier.de/pers/xk/'+name+'.xml'
    response = requests.get(url)
    
    xmldoc = minidom.parseString(response.content)
    itemlist = xmldoc.getElementsByTagName('dblpkey')

    papers = []

    for item in itemlist:
        if item.hasAttribute("type"):
            if item.attributes['type'].value == 'person record':
                continue
        rc = []
        for node in item.childNodes:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        papers.append(''.join(rc))
    
    return papers

def get_paper_info(paper):
    url = 'http://dblp.uni-trier.de/rec/xml/'+paper+'.xml'
    response = requests.get(url)
    
    xmldoc = minidom.parseString(response.content)
    
    publication_type = paper.split('/')[0]
    
    data = None
    
    if publication_type == 'journals':
        aux = xmldoc.getElementsByTagName('article')
        if len(aux):
            data = treating_journal(xmldoc.getElementsByTagName('article'))
    else:
        if publication_type == 'conf':
            aux = xmldoc.getElementsByTagName('inproceedings')
            if len(aux):
                data = treating_conf(xmldoc.getElementsByTagName('inproceedings'))
            
    return data

# # Extracting info
def treating_conf(itemlist):
    paper_info = defaultdict(lambda:[])
    
    for item in itemlist:
        for author in item.getElementsByTagName('author'):
            paper_info['author'].append(author.firstChild.data)
    
        if item.getElementsByTagName('title'):
            paper_info['title'] = item.getElementsByTagName('title')[0].firstChild.data
            
        if item.getElementsByTagName('pages'):
            paper_info['pages'] = item.getElementsByTagName('pages')[0].firstChild.data
        
        paper_info['year'] = '0'
        if item.getElementsByTagName('year'):
            paper_info['year'] = item.getElementsByTagName('year')[0].firstChild.data
        
        if item.getElementsByTagName('booktitle'):
            paper_info['booktitle'] = item.getElementsByTagName('booktitle')[0].firstChild.data
            
        paper_info['doi'] = ''
        if item.getElementsByTagName('ee'):
            paper_info['doi'] = item.getElementsByTagName('ee')[0].firstChild.data
    
    
    return paper_info

def treating_journal(itemlist):
    paper_info = defaultdict(lambda:[])
    
    for item in itemlist:
        for author in item.getElementsByTagName('author'):
            paper_info['author'].append(author.firstChild.data)
    
        if item.getElementsByTagName('title'):
            paper_info['title'] = item.getElementsByTagName('title')[0].firstChild.data
            
        if item.getElementsByTagName('pages'):
            paper_info['pages'] = item.getElementsByTagName('pages')[0].firstChild.data
        
        paper_info['year'] = '0'
        if item.getElementsByTagName('year'):
            paper_info['year'] = item.getElementsByTagName('year')[0].firstChild.data
        
        if item.getElementsByTagName('journal'):
            paper_info['journal'] = item.getElementsByTagName('journal')[0].firstChild.data
            
        if item.getElementsByTagName('volume'):
            paper_info['volume'] = item.getElementsByTagName('volume')[0].firstChild.data
            
        if item.getElementsByTagName('number'):
            paper_info['number'] = item.getElementsByTagName('number')[0].firstChild.data
            
        paper_info['doi'] = ''
        if item.getElementsByTagName('ee'):
            paper_info['doi'] = item.getElementsByTagName('ee')[0].firstChild.data
    
    
    return paper_info

def print_html_paper(paper):
    for author in paper['author']:
        print author+',',
    
    print '<a style="color: black;" href=\''+paper['doi']+'\'><strong>'+paper['title']+'</strong></a>',
        
    if paper['booktitle']:
        print '<em>'+paper['booktitle']+'</em>,',
    else:
        if paper['journal']:
            print '<em>'+paper['journal']+'</em>',
            if paper['number']:
                print paper['volume']+'('+str(paper['number'])+')'+',',
            else:
                print paper['volume']+',',
    if paper['pages']:
        print paper['pages']+',',
    print paper['year']+'.<br><br>'

# # Collecting info

# List all papers of all professores
# A set is used in order to avoid replicates
papers = set()
for professor in professors:
    paper_list = list_of_papers(professor)
    
    if paper_list is not None:
        papers.update(list_of_papers(professor))
    else:
        print professor, 'error'

# Papers are sorted according their years of publication
papers_info = defaultdict(lambda:[])
for paper in papers:
    aux = get_paper_info(paper)
    if aux is not None:
        papers_info[int(aux['year'])].append(aux)

# Print papers sorted by year (in decreasing order)
for year in sorted(papers_info.keys())[::-1]:
    papers = papers_info[year]
    print '<h3><strong>'+str(year)+'</strong></h3><hr />'
    for paper in papers:
        print '<p>'
        print_html_paper(paper)
        print '</p><br><br>'
    print
