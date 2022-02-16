from bs4 import BeautifulSoup as soup
import csv
import requests
import time

from functions import *


##### Function to scrape reddit for new saved posts from login account
def check_new_saved(file_path, username, password):

    # Open the file with read permissions and check what the last saved post was
    # This will be the post that the scraper stops at
    try:
        with open(file_path, 'r') as f:
            csv_reader = csv.reader(f, delimiter=",")

            for row in csv_reader:
                pass
            last_saved_title = row[2]
            last_saved_num = row[0]
            print(last_saved_num, last_saved_title)
    except FileNotFoundError:
        last_saved_title = "fillertitle"
        last_saved_num = "0"


    ##### Open HTTP Session with requests and log in
    s = requests.Session()
    send_signin_post(s, username, password)


    ##### Initialize necessary counter and variables
    i = 1
    page_counter = 1
    post_data_list = []

    post_attrs = {'class': 'thing'} # Attribues for finding posts in page
    url_start = f"https://old.reddit.com/user/{username}/saved"
    url_current = ''.join(url_start)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}


    ##### Start page-turning loop
    running = True
    while running:

        # Get page with HTTP GET request
        page = s.get(url_current, headers=headers)

        # Check response status code, proceed if HTTP Success code is returned
        if page.status_code == 200:


            # Increment page counter and parse the page into indexable format
            print(f"Page {page_counter}")
            soupage = soup(page.text, 'html.parser')


            # Find all posts in page using given attributes above, iterate over all posts in object
            for post in soupage.find_all('div', post_attrs):

                # Get domain (v.reddit, i.reddit, outbound, etc.)
                # Domain has no return if the post is actually a saved comment. Set domain to "Comment".
                try:
                    domain = post.attrs['data-domain']
                    # process post domain
                    if domain[:5] == "self.":
                        domain = "text"
                    elif domain == "i.redd.it":
                        domain = "image"
                    elif domain == "v.redd.it":
                        domain == "video"
                except KeyError:
                    domain = "comment"


                # Get post title, remove all commas to prevent unwanted CSV breaks
                title = " ".join(post.find('a', class_='title').text.split())
                title = " ".join(title.split(","))
                title = remove_non_ascii(title)
                print(i, title) # Print post number processed total, and title

                # Get post subreddit
                sub = post.find('a', class_='subreddit')
                if sub: # If sub doesn't exist for some reason, set "none" instead of throwing error
                    sub = sub.text
                    if sub[:2] == "r/":
                        sub = sub[2:]
                else:
                    sub = "None"

                # Get complete comments block (link and text)
                comments_block = post.find('a', class_='comments')
                # Double check that it *exists* (dunno why it wouldn't, but just in case)
                if comments_block:
                    comments_link = comments_block['href']
                else:
                    comments_link = "None"


                # Check if the processed title matches the last saved title
                if title == last_saved_title:
                    running = False
                    break
                else:
                    # If title matches, do not save. If title does not match, save and continue
                    post_data = [i, sub, title, domain, comments_link]
                    post_data_list.append(post_data)
                    i = 1 + i


            # After iterating over all posts on page, find next page button and save to url variable for next loop
            next_button = soupage.find("span", class_="next-button")
            if next_button:
                url_current = next_button.find("a").attrs['href']
                page_counter = page_counter + 1
            else:
                # If there is no more next button, break the while loop
                break

            # Can't overload the server - wait a few seconds inbetween page requests
            time.sleep(3)

        else:
            # If page status code is anything other than HTTP Success, print code and break loop
            print(f"HTTP Code {page.status_code}")
            break


    ##### Iterate through saved data and write to csv
    with open(file_path, 'a+', newline="\n") as f:
        csv_writer = csv.writer(f, delimiter=",", quoting=csv.QUOTE_MINIMAL, quotechar='"')
        for j in range(len(post_data_list)-1, -1, -1):
            line = post_data_list[j]
            line[0] = i - int(line[0]) + int(last_saved_num) # Make first col (counter) proper
            csv_writer.writerow(line)

    ##### Return number of posts processed
    return i



# The two most important lines of code
if __name__ == "__main__":
    from login_info import username, password
    file_path = 'testfile.csv'
    check_new_saved(file_path, username, password)
