import csv

##### Remove any non-ascii characters before writing to file
def remove_non_ascii(s):
    return "".join(c for c in s if ord(c)<128)


##### Sign in to reddit with HTTP POST request
def send_signin_post(session, user, passwd):
    url_signin = f"https://old.reddit.com/api/login"
    headers_login = {'referer': 'https://old.reddit.com/',
                     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
    data = {'op': 'login', 'user': user, 'passwd': passwd, 'rem': 'yes', 'over18': '1'}
    session.post(url_signin, data, headers=headers_login)


##### Function to read and keep count of all subreddits in saved file
def subreddit_breakdown(file_path):
    # Initialize Variables
    total_posts = 0
    post_counter = {}

    ##### Open the input file and read through
    with open(file_path, "r", newline="\n") as f:
        csv_reader = csv.reader(f, delimiter=",")
        for row in csv_reader:
            total_posts = total_posts + 1
            sub = row[1]

            # Increment value with sub name as key
            try:
                post_counter[sub] = post_counter[sub] + 1
            # If key doesn't exist, create
            except KeyError:
                post_counter[sub] = 1

    return post_counter