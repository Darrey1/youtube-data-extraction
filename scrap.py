import os
import json
import csv
import time
import re
import unicodedata
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
def scrape_content(url, driver, content):
    try:
        
        # Search for the specified content within the page
      driver.get(url)
      driver.find_element(By.XPATH,"//*[contains(text(), '{}')]".format(content))
      driver.implicitly_wait(10) # seconds
      prev_h = 0
      while True:
          height = driver.execute_script("""function getActualHeight(){
           return Math.max(
           Math.max(document.body.scrollHeight),
           Math.max(document.body.offsetHeight),
           Math.max(document.body.offsetHeight,document.documentElement.clientHeight));
          }
          return getActualHeight()
          """)
          #driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
          driver.execute_script(f'window.scrollTo({prev_h}, {prev_h + 200})')
          time.sleep(1)
          prev_h += 200
          if prev_h >= height:
            
              break
          driver.implicitly_wait(10)
          
          content = driver.page_source
          soup = BeautifulSoup(content, 'lxml')
          #print(soup.contents)
          all=soup.find_all('ytd-watch-flexy', {'class':'style-scope ytd-page-manager hide-skeleton'})
          #print(all)
          for all_content in all:
              title =all_content.find('h1',{'class':'style-scope ytd-watch-metadata'})
              if title != None:
                 title = title.text.strip()
                 title = str(title).encode('ascii','ignore').decode('ascii')
              else:
                  title = 'error! No title detected'
              pattern = re.compile('(?<=shortDescription":").*(?=","isCrawlable)')
              decriptions_string = pattern.findall(str(soup))[0]
              if decriptions_string != None:
                  decriptions_string = str(decriptions_string).replace('\\n', ' ')
                  normalized_decriptions = unicodedata.normalize('NFKD', decriptions_string)
                  decriptions_str = normalized_decriptions.encode('ascii', 'ignore').decode('ascii')

                  # Remove any remaining control characters and other special characters
                  decriptions = ''.join(c for c in decriptions_str if unicodedata.category(c)[0] != 'C')
                      
              else:
                  decriptions = 'error! No decriptions text detected'
                  #total views of the movies
              total_views = all_content.find('span', {'class': 'bold style-scope yt-formatted-string'})
              if total_views != None:
                 total_views = total_views.text.replace('views', '')
                 total_views = total_views.replace(' ', '')
              else:
                  total_views = 'error! No total views detected'
              #total_likes = all_content.find('span', {'class':'yt-core-attributed-string yt-core-attributed-string--white-space-no-wrap'}).text.strip()
              total_likes_element = driver.find_element(By.XPATH,'.//*[@id="segmented-like-button"]/ytd-toggle-button-renderer/yt-button-shape/button/div[2]/span')
              if total_likes_element != None:
                 total_likes = total_likes_element.text
              else:
                  total_likes = 'error! No total likes detected'
              video_length_elem = all_content.find('span', {'class':'ytp-time-duration'})
              if video_length_elem != None:
                 video_length = video_length_elem and video_length_elem.text.strip()
              else:
                  video_length_elem = 'error! No video lenght duration detected'
              #print(video_length)
              subscriber_count_elem = all_content.find('yt-formatted-string', {'id':'owner-sub-count'})
              if subscriber_count_elem != None:
                 subscriber_count_elem = subscriber_count_elem.text.strip().replace('subscribers', '')
              else:
                  subscriber_count_elem = 'error! No subscriber found!'
              
              #print(subscriber_count_elem)
              video_link = url
              #print(url)
              channel_name_elem = soup.find('yt-formatted-string', {'class':'ytd-channel-name'})
              if channel_name_elem != None:
                 channel_name = channel_name_elem and channel_name_elem.text.strip()
              else:
                  channel_name = 'error! No channel name detected'
              total_comments = soup.find('yt-formatted-string', {'class':'count-text style-scope ytd-comments-header-renderer'})
              if total_comments != None:
                 total_comments = total_comments.text
                 if total_comments != '':
                  total_comments = total_comments.replace('Comments', '')
                  total_comments = total_comments.replace(' ', '')
                 else:
                  total_comments ='0'
              else:
                  total_comments = 'error! No total comments found!'
              comment_list = []
              comments_total  = driver.find_element(By.ID,'contents')#span',{'class':'yt-core-attributed-string yt-core-attributed-string--white-space-no-wrap'}).text.replace('replies', '')
              #comments = comments_total.find_elements(By.ID,'comment')
              comments =comments_total.find_elements(By.TAG_NAME, 'ytd-comment-thread-renderer')
              #replies = re.find_elements(By.ID,'main')
                  #number_of_replies = int(replies_total) #//*[@id="contents"]/ytd-comment-renderer[2]
                  #//*[@id="header-author"]/h3
              for comment in comments:
                  #//*[@id="author-text"]/span //*[@id="contents"]/ytd-comment-thread-renderer[1]
                  author = comment.find_element(By.XPATH,'.//*[@id="author-text"]/span')
                  if author != None:
                     author = author.text.strip().replace('\n','')
                     if author != '':
                         author = author.replace('@', '')
                         author = str(author).encode('ascii', 'ignore').decode('ascii')
                     else:
                         author = 'No name'
                  else:
                      author = 'No name'
                  comment_text = comment.find_element(By.ID,'content-text')
                  if comment_text != None:
                     comment_text = comment_text.text.strip().replace('\n', ' ')
                     comment_text = str(comment_text).encode('ascii', 'ignore').decode('ascii')
                  else:
                      comment_text = 'error! No comment text detected!'
                  comment_like = comment.find_element(By.ID,'vote-count-middle')
                  if comment_like != None:
                     comment_like = comment_like.text
                     if comment_like:
                         comment_like = comment_like
                     else:
                         comment_like = '0'
                  else:
                      comment_like = 'error! No like detected'
                  time_span = comment.find_element(By.CLASS_NAME,'yt-formatted-string')
                  if time_span != None:
                     time_span = time_span.text
                  else:
                      time_span ='error! No time span detected'
                  total_replies = comment.find_element(By.ID, "replies")
                  if total_replies != None:
                     total_replies = total_replies.text
                     total_replies = str(total_replies).encode('ascii', 'ignore').decode('ascii').replace('\n', '')
                     if total_replies != '':
                         if 'replies' in total_replies:
                             total_replies = total_replies.replace('replies', '')
                             total_replies =total_replies.replace(' ', '')
                         elif 'reply' in total_replies:
                             total_replies = total_replies.replace('reply', '')
                             total_replies = total_replies.replace(' ', '')
                         else:
                             pass
                             
                     else:
                         total_replies = '0'
                  else:
                      total_replies = 'error! No total replies detected'
                  wait = WebDriverWait(driver,15)
                  wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body"))).send_keys(Keys.END)
                  
                      ########################3
                  if not re.search(r'\u2620\ufe0f\u20ddlucifer\u20df\u0fd0\ufba9\ufba9\u0668\u0640\u0640\ufba9\u0640\u2764\ufe0f',author):
                      
                     comment_list.append({
                         'author': author,
                         'comment':comment_text,
                         'timestamp': time_span,
                         'likes': comment_like,
                         'total_replies':total_replies, 
                     })
                     
                     data = {
                         'url': video_link,
                         'title': title,
                         'description':decriptions,
                         'duration':video_length,
                         'channel_name':channel_name,
                         'views': total_views,
                         'total_likes':total_likes,
                         'subscribers': subscriber_count_elem,
                         'total_comments':total_comments,
                         'comments':comment_list
                     }
                     filename = re.sub('[^0-9a-zA-Z]+', '_', title)+ '.json'
                     with open(filename, 'w') as jsonfile:
                         json.dump(data, jsonfile)
    except TimeoutError:
        print('time out...bad network connection try again')
    except NoSuchElementException:
        content = driver.page_source
        soup = BeautifulSoup(content, 'lxml')
        message= soup.find('div', {'class':'promo-message style-scope ytd-background-promo-renderer'})
        if message != None:
            message =message.text
            message = message.replace('\n', '') #.encode('ascii', 'ignore').decode('ascii')
            #message = message.replace("NaN", '')
        else:
            message = soup.find('div',{'id':'reason'})
            if message != None:
                message = message.text.strip()
            else:
               message= "This video has been removed for violating YouTube's Community Guidelines!."
        filename = url[-4:]+ '.json'
        data ={
            'url':url,
            #'Error Message':"This particular video is no longer available or has been removed  on the youtube web page.It may due to the violating YouTube's Community Guidelines,copyright issues or restrictions through geographycal locations" +
           # " And also it may be due to poor or bad network connection."
           'Error message':message
        }
        with open(filename, 'w') as jsonfile:
            json.dump(data, jsonfile)
if __name__ == '__main__':
    urls = []
    content = "Welcome"
    path = r'C:\Users\Public\chromedriver\chromedriver.exe'
    option = webdriver.ChromeOptions()
    driver = webdriver.Chrome(path,service_log_path=os.devnull,options=option)
    driver.maximize_window()
    
    with open('my_file.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
           urls.append(row[0])
           driver.implicitly_wait(5)
    for url in urls:
       scrape_content(url,driver, content)
    driver.quit()
