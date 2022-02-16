# Reddit Save Scrape (ReSaS)

ReSaS is a small custom GUI for managing, updating, and searching saved links from Reddit.

The GUI is able to:
- Process saved data from "saved_posts.csv" downloaded directly from Reddit.
- Log in and scrape 1000 most recent saved posts.
- Log in and scrape /user/saved to check for newly saved posts without having to re-update full file.
- Store and search posts by subreddit and keywords.
- Count and display all subreddits saved alongside number of saved posts in that sub.

## Dependencies
- BeautifulSoup4 (bs4)

## Usage

![update tab image](/img/img_update_tab.png)

The Update tab contains two functions:
- `Process Download` reads links from "Input File" and scrapes more information about them to save for searching.
  - Required Fields:
    - `Input File` ("saved_posts.csv" file downloaded from Information Request from Reddit.com, autofilled)
    - `Output File` (Overwritten .csv file to store link data, autofilled)
    - `Username` (Login necessary to easily maintain cookies)
    - `Password`
- `Scrape Update` reads information from user's /user/saved page directly on Reddit.com.
  - Appends any new saved posts to end of `Output File`
  - If `Output File` does not exist, it is created and the last 1000 saved posts are populated.
  - Required Fields
    - `Output File` (File to add new saved posts to, autofilled)
    - `Username`
    - `Password`

![search tab image](/img/img_search_tab.png)

The Search tab contains two functions:
- `List Subreddits` opens a table listing top subreddits and how many saved links each has.
  - Required Fields:
    - `Input File` (The same file created by the Update tab, autofilled)
- `Search` looks through all saved posts for those in any subreddit input with all keyword inputs. Opens HTML file with compiled table for ease of browsing.
  - Required Fields:
    - `Input File` (The same file created by the Update tab, autofilled)
    - 'Output File' (HTML file for search display, autofilled)
  - Optional Fields:
    - `Subreddits` (Separated by comma or space. Any post in these subreddits will be considered.)
    - `Title Keywords` (separated by comma or space. Only posts containing ALL keywords will be considered.)