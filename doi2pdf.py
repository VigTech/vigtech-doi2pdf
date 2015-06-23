from flask import Flask
from flask import request
from flask import jsonify
import lxml.html, urllib2, urlparse, urllib, simplejson as json

def descargar_pdf(doi, path):
    # the url of the page you want to scrape
    base_url = 'http://dx.doi.org/'+doi
    try:
        res = urllib2.urlopen(base_url)
    except urllib2.URLError as e:
        return {'downloaded': 'false', 'metadata': {}}


    base_url = res.geturl()

    # parse the response into an xml tree
    tree = lxml.html.fromstring(res.read())

    # construct a namespace dictionary to pass to the xpath() call
    # this lets us use regular expressions in the xpath
    ns = {'re': 'http://exslt.org/regular-expressions'}

    # iterate over all <a> tags whose href ends in ".pdf" (case-insensitive)
    for node in tree.xpath('//a[re:test(@href, "\.pdf$", "i")]', namespaces=ns):

        # print the href, joining it to the base_url
        pdf_url = urlparse.urljoin(base_url, node.attrib['href'])
        response = urllib2.urlopen("http://api.crossref.org/works/"+doi)
        j =  json.loads(response.read())
        try :
            pdf_name = j['message']['title'][0]+'.pdf'
        except IndexError as e:
            pdf_name = doi
        f = urllib2.urlopen(pdf_url)
        data = f.read()
        if data:
            with open("/home/vigtech/shared/repository/"+path+"/"+pdf_name, "wb") as code:
                code.write(data)
            return {'downloaded': 'true', 'metadata': j['message']}
        else:
            return {'downloaded': 'false', 'metadata': j['message']}

app = Flask(__name__)

@app.route('/download', methods=['GET'])
def download():
    dois = request.args.get('dois', '')
    path = request.args.get('path', '')
    doiarray = dois.split(",")
    response = dict()
    
    for doi in doiarray:
        response[doi] = descargar_pdf(doi, path)
    
    return jsonify(**response)

if __name__ == '__main__':
    app.debug = True
    app.run()
