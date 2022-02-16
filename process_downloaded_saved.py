# Reddit saved posts are limited to ~1000 viewable
# Complete history can be obtained as a CSV of links
# This script is to process these links into a searchable format

# Every link is to the comments page of the post
# From each link, must pull:
#   Sub
#   Title
#   Domain ("image", "video", or "text" if reddit hosted. domain if not.)
#   Link


# Library imports
import csv
import requests
import time
from bs4 import BeautifulSoup as soup

from functions import *


##### Function to process the saved data downloaded directly from reddit into searchable CSV
def process_downloaded_saved(read_file_path, write_file_path, username, password, request_delay_time=1, startnum=0):

    # Initialize Variables
    url_list = []

    ##### Open file for reading and process input
    with open(read_file_path, 'r', newline='', encoding="utf-8") as read_file:

        # Iterate over reading file and save all URLs to a list
        line_counter = 0
        csv_reader = csv.reader(read_file, delimiter=",")

        for row in csv_reader:
            # Skip first row of file (headers)
            if line_counter != 0 and line_counter >= startnum:
                # Go to old.reddit instead because it is easier to scrape
                url_list.append(row[1].replace("www", "old"))
            else:
                line_counter = line_counter + 1



    ##### Open requests session and log in
    s = requests.Session()
    send_signin_post(s, username, password)

    time.sleep(3)



    ##### Open file for writing and configure for CSV
    if startnum == 0:
        rw = "w+"
    else:
        rw = "a+"
    with open(write_file_path, rw) as write_file:
        # Create CSV writer
        csv_writer = csv.writer(write_file, delimiter=",", quoting=csv.QUOTE_MINIMAL, quotechar='"', lineterminator='\n')

        # Check for non-zero starting numer (if non-zero, start at number and append instead of overwrite)
        stopnum = startnum
        for post_url in url_list:

            # Try loop prevents crashing due to processing problems (can be improved to handle processing later)
            try:
                stopnum = stopnum + 1
                print(post_url)
                code_delay_time = 5

                # Get the same page until a desired status code is obtained
                while True:
                    page_raw = s.get(post_url, headers=headers)
                    if page_raw.status_code in [200, 404, 403]:
                        break
                    else:
                        print("______________________________________________")
                        print(f"Error: HTTP Code {page_raw.status_code}")
                        print(f"Trying again in {code_delay_time} seconds...")
                        time.sleep(code_delay_time)
                        code_delay_time = 2 * code_delay_time


                ##### Process with a 200 status code. Skip with 404, 403 and retry with anything else
                if page_raw.status_code == 200:
                    # Get beautifulSoup page
                    page_soup = soup(page_raw.text, 'html.parser')

                    # process subreddit name
                    post_sub = post_url.split("/")[4]

                    # Process post domain
                    post_domain = page_soup.find('span', class_="domain").text[1:-1]
                    if post_domain == "self." + post_sub:
                        post_domain = "text"
                    elif post_domain == "i.redd.it":
                        post_domain = "image"
                    elif post_domain == "v.redd.it":
                        post_domain == "video"
                    elif post_domain == "This video is being processed.":
                        # If media doesn't exist, skip post
                        raise ValueError

                    # Change title location if self post is text vs. any media
                    if post_domain in ["text"]:
                        post_title = remove_non_ascii(page_soup.find('a', class_="title may-blank loggedin").text)
                    else:
                        post_title = remove_non_ascii(page_soup.find('a', class_="title may-blank loggedin outbound").text)

                    ##### print and save output
                    print(stopnum, post_sub, post_title, post_domain)
                    csv_writer.writerow([stopnum, post_sub, post_title, post_domain, post_url])
                    time.sleep(request_delay_time)

                else:
                    print("BANNED. SKIPPED.")

            except (UnicodeEncodeError, ValueError):
                print("Big Error. Stopped.")



if __name__ == "__main__":
    from login_info import username, password
    process_downloaded_saved("saved_posts.csv", "complete_output.csv", username, password)