import scrapy
from scrapy import Request
import json

class NDBusinesses(scrapy.Spider):
    name = 'ND_businesses'
    
    def start_requests(self):

      url = 'https://firststop.sos.nd.gov/api/Records/businesssearch'
      #probably more headers than needed but better to have them to not get flagged as a bot
      headers = {
          "accept": "*/*",
          "accept-language": "en-US,en;q=0.9",
          "authorization": "undefined",
          "content-type": "application/json",
          "dnt": "1",
          "origin": "https://firststop.sos.nd.gov",
          "priority": "u=1, i",
          "referer": "https://firststop.sos.nd.gov/search/business",
          "sec-ch-ua": "\"Chromium\";v=\"130\", \"Microsoft Edge\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
          "sec-ch-ua-mobile": "?0",
          "sec-ch-ua-platform": "\"Windows\"",
          "sec-fetch-dest": "empty",
          "sec-fetch-mode": "cors",
          "sec-fetch-site": "same-origin",
          "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
      }
      #the web app search has bugs and will return businesses that do not start with X 
      #it may also fail to return some businesses starting with X which would require more requests to verify
      body = '{"SEARCH_VALUE":"X","STARTS_WITH_YN":"true","ACTIVE_ONLY_YN":true}'

      request = Request(
          url=url,
          method='POST',
          dont_filter=True,
          headers=headers,
          body=body,
          callback=self.parse)
      
      yield request

      
    def parse(self, response):
        try:
            data = json.loads(response.text)
            #filter json response with list comprehension to businesses that start with X
            records = [i for i in data['rows'].keys() if data['rows'][i]['TITLE'][0].startswith('X')]

            for row in records:
                #I also tried the ending /true for the link to see if it produced more data on a test and it did not
                #left as false since that is the apps normal behavior
                r_url = f'https://firststop.sos.nd.gov/api/FilingDetail/business/{row}/false'
                #probably more headers than needed but better to have them to not get flagged as a bot
                headers = {
                    "accept": "*/*",
                    "accept-language": "en-US,en;q=0.9",
                    "authorization": "undefined",
                    "dnt": "1",
                    "priority": "u=1, i",
                    "referer": "https://firststop.sos.nd.gov/search/business",
                    "sec-ch-ua": "\"Chromium\";v=\"130\", \"Microsoft Edge\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "\"Windows\"",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
                }

                record_request = Request(
                    url=r_url,
                    method='GET',
                    dont_filter=True,
                    headers=headers,
                    callback=self.parse_records, meta={'Company': data['rows'][row]['TITLE'][0]})
                    
                yield record_request
        except json.JSONDecodeError:
            self.logger.error('Error decoding JSON response')
    
    def parse_records(self, response):
        try:
            record_data = json.loads(response.text)

            record = {'Company': response.meta['Company']}
            for i in record_data['DRAWER_DETAIL_LIST']:
                record[i.get('LABEL')] = i.get('VALUE')
            yield record
        except json.JSONDecodeError:
            self.logger.error('Error decoding JSON response in parse_records')
        
    