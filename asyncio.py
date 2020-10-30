# Write a command-line tool using the asyncio library that takes a file with a URL per line as input. The program should make GET requests to each URL, without blocking on a response. As output, it should print (in the order the requests are returned, as soon as they are returned) the time taken for each request and its HTTP status code. Finally, it should output the mean, median, and 90th percentile response times. Be sure to handle cases where some URLs are invalid or when the server doesn't respond.

# Write a command line tool using the asyncio library 

# Take a file with a URL per line as input

# The program should make GET requests to each URL, without blocking on a response

# As output, it should print (in order the requests are returned), the time taken for each request and it's HTTP status code. 

# It should output the mean, median, and the 90th percentile response times. 

# Be sure to handle cases where some URLS are invalid or when the server doesn't respond

import aiohttp
import asyncio
import time
from requests.exceptions import HTTPError
import re
import math
import sys
import logging

list_of_times = []
list_of_url = []

def read_file(file):
    """Reads a file on a line by line basis, validates the URL on every line and returns the valid URLs as a list

    Args:
        file ([string]): [path to file]

    Returns:
        [list]: [validated URLs]
    """

    valid_urls = []
    file1 = open(file, 'r') 
    lines = file1.readlines() 
    lines = [x[:-1] for x in lines]

    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    for urls in lines: 
        if (re.match(regex, urls) is not None): # True
            valid_urls.append(urls)

    return valid_urls

async def fetch(session, url):
    """[Coroutine to send HTTP request to URLs provided]

    Args:
        session ([aiohttp Client Session object]): [session object]
        url ([string]): [URL to query]

    Returns:
        [list]: [response url, status and time taken]
    """
    tic = time.perf_counter() # Start timer
    try:
        response = await session.request(method='GET', url=url, timeout=10)
        toc = time.perf_counter() # Stop timer
        time_taken  = toc - tic # Calculate time taken to get response
        response.raise_for_status()
        print("URL : ", url)
        print("HTTP Status : ", response.status)
        print(f"Time taken : {time_taken:4f} seconds")
        print()
        return str(response.url), response.status, time_taken
    
    except HTTPError as http_err:
        logging.error(http_err)
    except Exception as err:
        logging.error(err)
    

async def main():
    """[Main function to create tasks and call supporting functions]"""
    urls = read_file(sys.argv[1])
    tasks = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            for i in range(0, 10):
                tasks.append(fetch(session, url))
        htmls = await asyncio.gather(*tasks)
        
        print()
        for html in range(0, len(htmls)):
            # Create a set of urls
            # TODO : Figure out a better way of getting list of distinct URLs
            try:
                if (list_of_url.append(htmls[html][0]) is not None):
                    list_of_url.append(htmls[html][0])
            except Exception as err:
                logging.error(err)    
            
        for urls in set(list_of_url):
            for html in range(0,len(htmls)):
                if (htmls[html][0] == urls) and (htmls[html] is not None):
                    list_of_times.append(htmls[html][2])
                    
            print(urls)
            print(f"Mean : {get_mean(list_of_times):4f} seconds")
            print(f"Median : {get_median(list_of_times):4f} seconds")
            print(f"90th percentile: {percentile(list_of_times, 90):4f} seconds")
            list_of_times.clear()
            print()
                    
    
def get_mean(list_of_times):
    """[Calculates the mean value given a list of numbers]

    Args:
        list_of_times ([list]): [List of numbers]

    Returns:
        [float]: [Mean]
    """
    sum = 0
    for ele in list_of_times: 
        sum += ele 
    mean = sum / len(list_of_times) 
    return mean

def get_median(list_of_times):
    """[Calculates the median given a list of numbers]

    Args:
        list_of_times ([list]): [List of numbers]

    Returns:
        [float]: [Median]
    """
    list_of_times.sort()
    l = len(list_of_times)

    mid = (l-1)//2

    if(l%2==0):
        return (list_of_times[mid] + list_of_times[mid+1])/2
    else:
        return list_of_times[mid]
    
def percentile(list_of_times, percentile):
    """[Calculates nth percentile given a list of numbers]

    Args:
        list_of_times ([list]): [List of numbers]
        percentile ([int]): [Percentile to calculate]

    Returns:
        [float]: [Nth percentile]
    """
    size = len(list_of_times)
    return sorted(list_of_times)[int(math.ceil((size * percentile) / 100)) - 1]

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

