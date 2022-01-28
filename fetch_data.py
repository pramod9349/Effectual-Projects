from requests_html import HTMLSession
import wget
def fetchZipFile():
    session  =HTMLSession()
    url = 'https://bulkdata.uspto.gov/data/trademark/dailyxml/applications/'
    html = session.get(url)
    html = html.html
    text = html.text.split('\n')
    try:
        index = text.index('United States Patent and Trademark Office - An Agency of the Department of Commerce')
        file = text[index-3]
        print(file)
        fileUrl = url+'/'+file
        #wget.download(fileUrl)
    except:
        return 'Can\'t Fetch File'
if __name__ == '__main__':
    fetchZipFile()
