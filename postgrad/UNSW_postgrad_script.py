"""Description:
    * author: Magdy Abdelkader
    * company: Fresh Futures/Seeka Technology
    * position: IT Intern
    * date: 03-11-20
    * description:This script extracts the corresponding postgraduate courses details and tabulate it.
"""

import csv
import re
import time
from pathlib import Path
from selenium import webdriver
import bs4 as bs4
from selenium.webdriver.support.ui import Select
import os
import copy
from CustomMethods import TemplateData
from CustomMethods import DurationConverter as dura

option = webdriver.ChromeOptions()
option.add_argument(" - incognito")
option.add_argument("headless")
exec_path = Path(os.getcwd().replace('\\', '/'))
exec_path = exec_path.parent.__str__() + '/Libraries/Google/v86/chromedriver.exe'
browser = webdriver.Chrome(executable_path=exec_path, options=option)

# read the url from each file into a list
course_links_file_path = Path(os.getcwd().replace('\\', '/'))
course_links_file_path = course_links_file_path.__str__() + '/UNSW_postgrad_links.txt'
course_links_file = open(course_links_file_path, 'r')

# the csv file we'll be saving the courses to
csv_file_path = Path(os.getcwd().replace('\\', '/'))
csv_file = csv_file_path.__str__() + '/UNSW_postgrad.csv'

course_data = {'Level_Code': '', 'University': 'University of New South Wales', 'City': '', 'Country': 'Australia',
               'Course': '', 'Int_Fees': '', 'Local_Fees': '', 'Currency': 'AUD', 'Currency_Time': 'year',
               'Duration': '', 'Duration_Time': '', 'Full_Time': '', 'Part_Time': '', 'Prerequisite_1': 'IELTS',
               'Prerequisite_2': '', 'Prerequisite_3': '', 'Prerequisite_1_grade': '6.5',
               'Prerequisite_2_grade': '',
               'Prerequisite_3_grade': '', 'Website': '', 'Course_Lang': '', 'Availability': '', 'Description': '',
               'Career_Outcomes': '', 'Online': '', 'Offline': '', 'Distance': '', 'Face_to_Face': '',
               'Blended': '', 'Remarks': ''}

possible_cities = {'rockhampton': 'Rockhampton', 'cairns': 'Cairns', 'bundaberg': 'Bundaberg',
                   'townsville': 'Townsville', 'canberra': 'Canberra', 'paddington': 'Paddington',
                   'online': 'Online', 'gladstone': 'Gladstone', 'mackay': 'Mackay', 'mixed': 'Online',
                   'yeppoon': 'Yeppoon', 'brisbane': 'Brisbane', 'sydney': 'Sydney', 'queensland': 'Queensland',
                   'melbourne': 'Melbourne', 'albany': 'Albany', 'perth': 'Perth', 'adelaide': 'Adelaide',
                   'noosa': 'Noosa', 'emerald': 'Emerald', 'hawthorn': 'Hawthorn', 'wantirna': 'Wantirna',
                   'prahran': 'Prahran', 'kensington': 'Kensington'}

possible_languages = {'Japanese': 'Japanese', 'French': 'French', 'Italian': 'Italian', 'Korean': 'Korean',
                      'Indonesian': 'Indonesian', 'Chinese': 'Chinese', 'Spanish': 'Spanish'}

course_data_all = []
level_key = TemplateData.level_key  # dictionary of course levels
faculty_key = TemplateData.faculty_key  # dictionary of course levels

# GET EACH COURSE LINK
for each_url in course_links_file:
    actual_cities = []
    remarks_list = []
    browser.get(each_url)
    pure_url = each_url.strip()
    each_url = browser.page_source

    soup = bs4.BeautifulSoup(each_url, 'lxml')
    time.sleep(1)

    # SAVE COURSE URL
    course_data['Website'] = pure_url

    # SAVE COURSE TITLE
    course_tag = soup.find('dt', class_='metadata-list__title body2', text=re.compile('Award', re.IGNORECASE))
    if course_tag:
        course_container = course_tag.find_parent('div', class_='metadata-list__item')
        if course_container:
            course_dd = course_container.find('dd', class_='metadata-list__description display2')
            if course_dd:
                course_div = course_dd.find('div')
                if course_div:
                    course_title = course_div.find('p')
                    if course_title:
                        course = course_title.get_text().strip()
                        course_data['Course'] = course
                        print('COURSE TITLE: ', course_data['Course'])

    # DECIDE THE LEVEL CODE
    for i in level_key:
        for j in level_key[i]:
            if j in course_data['Course']:
                course_data['Level_Code'] = i
    print('COURSE LEVEL CODE: ', course_data['Level_Code'])

    # DECIDE THE FACULTY
    for i in faculty_key:
        for j in faculty_key[i]:
            if j.lower() in course_data['Course'].lower():
                course_data['Faculty'] = i
    print('COURSE FACULTY: ', course_data['Faculty'])

    # COURSE DESCRIPTION
    desc_header = soup.find('h1', class_='content-section__title display3', text=re.compile('Overview', re.IGNORECASE))
    if desc_header:
        desc_list = []
        desc_div = desc_header.find_next_sibling('div', class_='content-section__column')
        if desc_div:
            desc_div_1 = desc_div.find('div', class_='text')
            if desc_div_1:
                desc_p_list = desc_div_1.find_all('p')
                if desc_p_list:
                    for p in desc_p_list:
                        desc_list.append(p.get_text().strip())
                    desc_list = ' '.join(desc_list)
                    course_data['Description'] = desc_list
                    print('COURSE DESCRIPTION: ', desc_list)

    # COURSE LANGUAGE
    for language in possible_languages:
        if language in course_data['Course']:
            course_data['Course_Lang'] = language
        else:
            course_data['Course_Lang'] = 'English'
    print('COURSE LANGUAGE: ', course_data['Course_Lang'])

    # DURATION & DURATION_TIME / PART-TIME & FULL-TIME
    duration_tag = soup.find('dt', class_='metadata-list__title body2', text=re.compile('Duration', re.IGNORECASE))
    if duration_tag:
        duration_container = duration_tag.find_parent('div', class_='metadata-list__item')
        if duration_container:
            duration_dd = duration_container.find('dd', class_='metadata-list__description display2')
            if duration_dd:
                duration_div = duration_dd.find('div')
                if duration_div:
                    duration_ = duration_div.find('p')
                    if duration_:
                        duration = duration_.get_text().strip()
                        if 'full-time' in duration.lower():
                            course_data['Full_Time'] = 'yes'
                        else:
                            course_data['Full_Time'] = 'no'
                        if 'part-time' in duration.lower():
                            course_data['Part_Time'] = 'yes'
                        else:
                            course_data['Part_Time'] = 'no'
                        converted_duration = dura.convert_duration(duration)
                        if converted_duration is not None:
                            duration_list = list(converted_duration)
                            if duration_list[0] == 1 and 'Years' in duration_list[1]:
                                duration_list[1] = 'Year'
                            if duration_list[0] == 1 and 'Months' in duration_list[1]:
                                duration_list[1] = 'Month'
                            course_data['Duration'] = duration_list[0]
                            course_data['Duration_Time'] = duration_list[1]
                            print('COURSE DURATION: ', str(duration_list[0]) + ' / ' + duration_list[1])
                        print('FULL-TIME/PART-TIME: ', course_data['Full_Time'] + ' / ' + course_data['Part_Time'])

    # DELIVERY
    deli_tag = soup.find('dt', class_='metadata-list__title body2', text=re.compile('Delivery Mode', re.IGNORECASE))
    if deli_tag:
        deli_container = deli_tag.find_parent('div', class_='metadata-list__item')
        if deli_container:
            deli_dd = deli_container.find('dd', class_='metadata-list__description display2')
            if deli_dd:
                deli_div = deli_dd.find('div')
                if deli_div:
                    deli_ = deli_div.find('p')
                    if deli_:
                        delivery = deli_.get_text().strip().lower()
                        if 'on campus' in delivery:
                            course_data['Face_to_Face'] = 'yes'
                            course_data['Offline'] = 'yes'
                        else:
                            course_data['Face_to_Face'] = 'no'
                            course_data['Offline'] = 'no'
                        if 'online' in delivery:
                            course_data['Online'] = 'yes'
                            course_data['Distance'] = 'yes'
                            actual_cities.append('online')
                        else:
                            course_data['Online'] = 'no'
                            course_data['Distance'] = 'no'
                        if 'on campus' in delivery and 'online' in delivery:
                            course_data['Blended'] = 'yes'
                        else:
                            course_data['Blended'] = 'no'
    print('DELIVERY: online: ' + course_data['Online'] + ' offline: ' + course_data['Offline'] + ' face to face: ' +
          course_data['Face_to_Face'] + ' blended: ' + course_data['Blended'] + ' distance: ' + course_data['Distance'])

    # AVAILABILITY
    student_type = soup.find('select', class_='display2')
    if student_type:
        avi_list = []
        student_option = student_type.find_all('option')
        if student_option:
            for option in student_option:
                option = option.get_text().lower().strip()
                avi_list.append(option)
            if 'domestic student' in avi_list:
                course_data['Availability'] = 'D'
            if 'international student' in avi_list:
                course_data['Availability'] = 'I'
            if 'international student' in avi_list and 'domestic student' in avi_list:
                course_data['Availability'] = 'A'
    else:
        course_data['Availability'] = 'D'
    print('AVAILABILITY: ' + course_data['Availability'])

    # CAREER OUTCOMES
    career_title = soup.find('h2', class_='display2', text=re.compile('Career Opportunities', re.IGNORECASE))
    if career_title:
        career_list = []
        list_tag = career_title.find_next('div', class_='text')
        if list_tag:
            ul_ = list_tag.find('ul')
            if ul_:
                li_ = ul_.find_all('li')
                if li_:
                    for li in li_:
                        career = li.get_text().strip()
                        career_list.append(career)
                    career_list = ', '.join(career_list)
                    course_data['Career_Outcomes'] = career_list
                    print('CAREER OUTCOMES: ', course_data['Career_Outcomes'])

    # CITY
    location_container = soup.find_all('div', class_='content-definition-list__item')
    if location_container:
        cities = []
        for element in location_container:
            location_dd = element.find('dd', class_='content-definition-list__description display3')
            if location_dd:
                location_div = location_dd.find('div')
                if location_div:
                    location_ = location_div.find('p')
                    if location_:
                        location = location_.get_text().strip().lower()
                        cities.append(location)
        for city in cities:
            if 'kensington' in city:
                actual_cities.append('kensington')
            if 'canberra' in city:
                actual_cities.append('canberra')
            if 'paddington' in city:
                actual_cities.append('paddington')
        print('COURSE LOCATION: ', actual_cities)

    course_data['Local_Fees'] = ''
    course_data['Int_Fees'] = ''
    # FEES
    # for local
    fee_section_loc = soup.find('section', id='fees')
    if fee_section_loc:
        fee_loc = fee_section_loc.find('dd', class_='content-definition-list__description display3')
        if fee_loc:
            fee_loc_n = fee_loc.get_text().replace('$', '').replace('*', '')
            course_data['Local_Fees'] = fee_loc_n
        else:
            course_data['Local_Fees'] = 'Not Available'
    else:
        course_data['Local_Fees'] = 'Not Available'
    # for international
    # navigate to international section
    student_type_ = soup.find('select', class_='display2')
    if student_type_:
        select = Select(browser.find_element_by_name('student-type'))
        select.select_by_value('international')
        time.sleep(1)
        # grab the data
        fee_section_int = soup.find('section', id='fees')
        if fee_section_int:
            fee_int = fee_section_int.find('dd', class_='content-definition-list__description display3')
            if fee_int:
                fee_int_n = fee_int.get_text().replace('$', '').replace('*', '').replace('^', '')
                course_data['Int_Fees'] = fee_int_n
            else:
                course_data['Int_Fees'] = 'Not Available'
        else:
            course_data['Int_Fees'] = 'Not Available'
    print('LOCAL FEE: ', course_data['Local_Fees'])
    print('INTERNATIONAL FEE: ', course_data['Int_Fees'])

    # duplicating entries with multiple cities for each city
    for i in actual_cities:
        course_data['City'] = possible_cities[i]
        course_data_all.append(copy.deepcopy(course_data))
    del actual_cities

    # TABULATE THE DATA
    desired_order_list = ['Level_Code', 'University', 'City', 'Course', 'Faculty', 'Int_Fees', 'Local_Fees',
                          'Currency', 'Currency_Time', 'Duration', 'Duration_Time', 'Full_Time', 'Part_Time',
                          'Prerequisite_1', 'Prerequisite_2', 'Prerequisite_3', 'Prerequisite_1_grade',
                          'Prerequisite_2_grade', 'Prerequisite_3_grade', 'Website', 'Course_Lang', 'Availability',
                          'Description', 'Career_Outcomes', 'Country', 'Online', 'Offline', 'Distance', 'Face_to_Face',
                          'Blended', 'Remarks']

    course_dict_keys = set().union(*(d.keys() for d in course_data_all))

    with open(csv_file, 'w', encoding='utf-8', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, course_dict_keys)
        dict_writer.writeheader()
        dict_writer.writerows(course_data_all)

    with open(csv_file, 'r', encoding='utf-8') as infile, open('UNSW_postgrad_ordered.csv', 'w', encoding='utf-8',
                                                               newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=desired_order_list)
        # reorder the header first
        writer.writeheader()
        for row in csv.DictReader(infile):
            # writes the reordered rows to the new file
            writer.writerow(row)
