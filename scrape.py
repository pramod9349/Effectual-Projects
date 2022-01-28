from requests_html import HTMLSession


def find(text, element):
    try:
        index = text.index(element)
        return text[index+1]
    except:
        return ''


def scrape(irnis):
    session = HTMLSession()
    headers = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36 OPR/67.0.3575.137"}
    data = {}
    status_url = f'https://tsdr.uspto.gov/statusview/sn{irnis}'
    docs_url = f'https://tsdr.uspto.gov/docsview/sn{irnis}'
    # FETCHING STATUS RELEATED DETAILS
    html = session.get(status_url)
    html = html.html
    text = html.text.split('\n')
    # Finding Mark
    summarySection = html.find('div#sumary-section')

    # Finding Mark
    data['Mark'] = ''
    mark = summarySection[0].find('div.value.markText')
    if len(mark) > 0:
        data['Mark'] = mark[0].text
    else:
        data['Mark'] = ''
    # Finding Us Serial Number
    us_serial_number = summarySection[0].find('div.double.table')
    data['US Serial Number'] = ''
    data['Application Filing Date'] = ''
    if len(us_serial_number) > 0:
        element = us_serial_number[0].find('div.value')
        if len(element) > 0:
            data['US Serial Number'] = element[0].text
            data['Application Filing Date'] = element[1].text
        else:
            data['US Serial Number'] = ''
            data['Application Filing Date'] = ''
    # Finding Mark Type:
    mark_type = summarySection[0].find('div.row')
    data['Mark Type'] = ''
    for i in range(len(mark_type)):
        temp = mark_type[i].text.strip('\n')

        if temp.find('Mark Type:') != -1:
            temp = temp.split('\n')
            if len(temp) > 1:
                data['Mark Type'] = temp[1]
                break
    # Finding TM5
    data['TM5 Common Status Descriptor'] = ''
    Tm5 = summarySection[0].find('div.double.table')
    for i in Tm5:
        temp = i.text
        if temp.find('TM5 Common Status Descriptor') != -1:
            data['TM5 Common Status Descriptor'] = '\n'.join(
                i.text.split('\n')[1:])
            break

    # Finding Status Date :
    status_date = summarySection[0].find('div.row')
    data['Status Date'] = ''
    data['Publication Date'] = ''
    data['Date Abandoned'] = ''
    for i in range(len(status_date)):
        temp = status_date[i].text.strip('\n')
        if temp.find('Date') != -1 and temp.find('Application Filing Date:') == -1:
            temp = temp.split('\n')
            if len(temp) > 1:
                data[temp[0].replace(':', '')] = temp[1]

    # Mark Information Done:

    # Finding Goods and Service Details
    data['International Class(es)'] = ''
    try:
        temp = text.copy()
        temp.reverse()
        # Getting Last Occurance
        index = temp.index('International Class(es):')
        data['International Class(es)'] = temp[index-1]
    except:
        data['International Class(es)'] = ''
    # Owner Information
    ownerInfo = html.find('div#relatedProp-section')
    data['Owner Name'] = ''
    data['Legal Entity Type'] = ''
    data['Owner Address'] = ''

    elements = ownerInfo[0].find('div.single.table')
    for i in elements:
        temp = i.text
        if temp.find('Owner Name:') != -1:
            data['Owner Name'] = ' '.join(temp.split('\n')[1:])
            continue
        if temp.find('Owner Address:') != -1:
            data['Owner Address'] = '\n'.join(temp.split('\n')[1:])
            continue

    elements = ownerInfo[0].find('div.double.table')
    for i in elements:
        temp = i.text
        if temp.find('Legal Entity Type:') != -1:
            data['Legal Entity Type'] = temp.split('\n')[1]
            break
    # Finding Email and Phone Number:
    sections = html.find('div.expand_wrapper.default_hide')
    index = -1
    for i in range(len(sections)):
        if sections[i].text.find('Attorney/Correspondence Information') != -1:
            index = i
            break
    correspondence = sections[i]
    data['Correspondent Name/Address'] = ''
    data['Phone No'] = ''
    data['Email'] = ''
    info = correspondence.find('div.single.table')
    for i in info:
        temp = i.text
        if temp.find('Correspondent Name/Address:') != -1:
            data['Correspondent Name/Address'] = '\n'.join(
                temp.split('\n')[1:])
            break
    info = correspondence.find('div.double.table')
    for i in info:
        temp = i.text
        if temp.find('Phone:') != -1:
            data['Phone No'] = ''.join(temp.split('\n')[1])
        if temp.find('Correspondent e-mail:') != -1:
            data['Email'] = ''.join(temp.split('\n')[1])

    # END OF FETCHING STATUS RELATED DETAILS:

    # FETCHING DOCUMENTS RELATED DETAILS
    html = session.get(docs_url, headers=headers)
    html = html.html
    summary = html.find('div#docs_data_container')
    text = summary[0].text.split('\n')
    data['Document Date'] = ''
    data['Document Title'] = ''
    data['Office  Action Date '] = ''

    # Finding Office Action Date:
    sections = html.find('tr.doc_row.dataRowTR')
    docs = []
    # Finding First Document
    text = '\n'.join([i.text for i in sections]).split('\n')
    prevId = text[3]
    for i in range(len(text)):
        if text[i] == prevId:
            docs.append([text[i-3], text[i-2]])
    if len(docs) > 0:
        data['Document Date'] = docs[-1][0]
        data['Document Title'] = docs[-1][1]
    # Finding First Off Action Outgoing
    docs = []
    j = 0
    prev = []
    text = '\n'.join([i.text for i in sections]).split('\n')
    for i in range(len(text)):
        if text[i].find('Offc Action Outgoing') != -1:
            if j == 0:
                j += 1
                prev = [text[i-1], text[i], text[i+2]]
            docs.append([text[i-1], text[i], text[i+2]])

    sameDocs = [i for i in docs if i[0] == prev[0]]
    docId = -1

    if len(sameDocs) > 0:
        data['Office  Action Date '] = sameDocs[-1][0]
        docId = sameDocs[-1][-1]
    data['SUMMARY OF ISSUES'] = ''
    if docId != -1:
        url = f'https://tsdrsec.uspto.gov/ts/cd/casedoc/sn{irnis}/OOA{docId}/1/webcontent?scale=1'
        html = session.get(url)
        html = html.html
        elements = html.find('p.MsoNormal')
        for i in range(len(elements)):
            if elements[i].text.find('SUMMARY OF ISSUES') != -1:
                t = ''
                ol = html.find('ol', first=True)
                if ol is not None:
                    t = ol.text
                else:
                    ul = html.find('ul', first=True)
                    if ul is not None:
                        t = ul.text
                data['SUMMARY OF ISSUES'] = '\n'.join(t.split('\n'))
                break

    return data


if __name__ == '__main__':
    print(scrape('76709358'))
# 76709358
