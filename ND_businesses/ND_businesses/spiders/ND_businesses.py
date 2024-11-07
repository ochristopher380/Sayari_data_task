import scrapy
from scrapy import Request
import json

class NDBusinesses(scrapy.Spider):
    name = 'ND_businesses'
    
    def start_requests(self):

      url = 'https://firststop.sos.nd.gov/api/Records/businesssearch'

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
            #filter json response with list comprehension
            records = [i for i in data['rows'].keys() if data['rows'][i]['TITLE'][0].startswith('X')]

            for row in records:
                r_url = f'https://firststop.sos.nd.gov/api/FilingDetail/business/{row}/false'

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
        
    