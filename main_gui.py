import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import askyesno

import re
import os
from webbrowser import open as openweb

from lib.process_downloaded_saved import *
from lib.check_new_saved import *
from lib.functions import *


def main():

# ============================================================================================
# Function to read data from file and check matching with sub and keywords strings
# ============================================================================================

    def search_results():

        ##### Grab values from input fields for subreddit search
        sub_string = sub_entry.get().lower() # lowercase everything so its easier to match
        subreddits = re.split(',| ', sub_string) # Split by all punctuation into word lists
        for i in range(len(subreddits)-1, -1, -1): # Iterate backwards and remove all empty strings
            if not subreddits[i]:
                subreddits.pop(i)

        ##### Grab values from input fields for keyword search
        key_string = key_entry.get().lower()
        keywords = re.split(',| |_|-|!', key_string)
        for i in range(len(keywords)-1, -1, -1):
            if not keywords[i]:
                keywords.pop(i)


        ##### Grab values from input fields for input and output files
        input_file = file_in_entry.get()
        output_file = file_out_entry.get()


        ##### Read through all entries in the save file and determine if they match criteria
        output_lines = []
        with open(input_file, "r") as f:
            csv_reader = csv.reader(f, delimiter=",")
            for row in csv_reader:

                ##### Check if subreddit search terms exist. if they match, set sub_match to true
                if subreddits:
                    if row[1].lower() in subreddits:
                        sub_match = True
                    else:
                        sub_match = False
                else:
                    sub_match = True

                ##### Check if keyword search terms exist. If all keywords are in title, set key_match to true
                if keywords:
                    if all(elem in re.split(',|_|-|!| ', row[2].lower()) for elem in keywords):
                        key_match = True
                    else:
                        key_match = False
                else:
                    key_match = True

                ##### If keywords and subreddits match, add line to output list
                if key_match and sub_match:
                    temp = row[1:]
                    temp[3] = f'<a href="{temp[3]}">{temp[3]}</a>' # Turn link string into HTML clickable URL
                    output_lines.append(temp)

        ##### Open output HTML file and write data
        with open(output_file, "w+") as f:

            ##### Open setup HTML file and copy in the framework saved there
            with open("lib\html_setup.txt", "r") as setup:
                setup_lines = setup.readlines()
                for line in setup_lines:
                    f.write(line)

            ##### Append each line matching the criteria to a table in the HTML file
            for result in output_lines:
                html_append = f"<tr> <td>{result[0]}</td> <td>{result[1]}</td> <td>{result[2]}</td> <td>{result[3]}</td> </tr>"
                f.write(html_append)

            ##### Close out HTML tags
            f.write("</tbody></table>")

        ##### Open page in web browser for easy access
        openweb('file://' + os.path.realpath(output_file), new=2)


# ============================================================================================
# Function to open new window with list of saved subreddits and saved count from each
# ============================================================================================

    def get_subreddits():

        ##### Create secondary window for list of saved subreddits
        win_subs = tk.Tk()
        win_subs.title("Saved Subreddits")

        ##### Create table to hold and display variables, push to top
        table_subs = tk.Frame(win_subs)
        table_subs.pack(side=tk.TOP)

        ##### Create scroll bars
        scroll_x = tk.Scrollbar(table_subs, orient=tk.HORIZONTAL)
        scroll_y = tk.Scrollbar(table_subs, orient=tk.VERTICAL)

        ##### Create linked tree for data storage and configure
        tree_subs = ttk.Treeview(table_subs, columns=("Subreddit","Saved Posts"), selectmode="extended", yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        tree_subs.heading('Subreddit', text="Subreddit", anchor=tk.W)
        tree_subs.heading('Saved Posts', text="Number Saved", anchor=tk.W)
        tree_subs.column("#0", width=0)  # OR tree_subs['show'] = 'headings'

        ##### Configure scrollbars to link with tree and table
        scroll_x.config(command=tree_subs.xview)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        scroll_y.config(command=tree_subs.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        ##### Show the tree on the window
        tree_subs.pack()

        ##### Get subreddits and counts, sort, and append to table
        input_file = file_in_entry.get()
        subreddits_list = subreddit_breakdown(input_file)
        subreddits_list = {k: v for k, v in sorted(subreddits_list.items(), key=lambda item: item[1])}
        for sub in subreddits_list:
            #print(sub, subreddits_list[sub])
            tree_subs.insert("", 0, values=(sub, subreddits_list[sub]))


# ============================================================================================
# Function to process csv of data downloaded directly from reddit
# ============================================================================================
    def process_download():
        answer = askyesno(title="Confirmation", message="This will overwrite your current save file. Continue?")

        if answer:
            file_input = file_in_update_entry.get()
            file_output = file_out_update_entry.get()
            username = username_entry.get()
            password = password_entry.get()
            process_num = pnum_entry.get()
            if not process_num:
                process_num = 0
            else:
                process_num = int(process_num)

            process_downloaded_saved(file_input, file_output, username, password, startnum=process_num)



# ============================================================================================
# Function to scrape new saved files from reddit by logging in with bs4
# ============================================================================================
    def scrape_update():
        answer = askyesno(title="Confirmation", message="This function takes input and output from the \"Output File\" field. Is the entered information correct?")

        if answer:
            file_output = file_out_update_entry.get()
            username = username_entry.get()
            password = password_entry.get()

            num_processed = check_new_saved(file_output, username, password)
            print(f"\nRetrieved {num_processed-1} new entries.\n")




# ============================================================================================
# Main tkinter setup
# ============================================================================================

    ##### Open main tkinter window for search term input
    window = tk.Tk()
    window.title("Reddit Saved Search")
    # tk.Label(window, text="Enter Subreddit and Title Keywords").grid(row=0, column=0, sticky=W, pady=2)

    ##### Create tabs for search and update
    tab_controller = ttk.Notebook(window)
    tab_search = ttk.Frame(tab_controller)
    tab_update = ttk.Frame(tab_controller)
    tab_controller.add(tab_search, text="Search")
    tab_controller.add(tab_update, text="Update")
    tab_controller.pack(expand=1, fill="both")

# ============================================================================================
# Search Tab Setup
# ============================================================================================

    ##### Add input file input field
    tk.Label(tab_search, text="Input File: ").grid(row=0, column=0, pady=2, sticky=tk.W)
    file_in_entry = tk.Entry(tab_search)
    file_in_entry.insert(0, "cleaned_output.csv")
    file_in_entry.grid(row=0, column=1, pady=2, sticky=tk.W)

    ##### Add output file input field
    tk.Label(tab_search, text="Output File: ").grid(row=1, column=0, pady=2, sticky=tk.W)
    file_out_entry = tk.Entry(tab_search)
    file_out_entry.insert(0, "temp.html")
    file_out_entry.grid(row=1, column=1, pady=2, sticky=tk.W)

    ##### Add subreddit search terms input field
    tk.Label(tab_search, text="Subreddits: ").grid(row=2, column=0, pady=2, sticky=tk.W)
    sub_entry = tk.Entry(tab_search)
    sub_entry.grid(row=2, column=1, pady=2, sticky=tk.W)

    ##### Add title keyword search input field
    tk.Label(tab_search, text="Title Keywords: ").grid(row=3, column=0, pady=2, sticky=tk.W)
    key_entry = tk.Entry(tab_search)
    key_entry.grid(row=3, column=1, pady=2, sticky=tk.W)

    ##### Add button to grab entry field variables and perform search
    button_submit = tk.Button(tab_search, text="Search", width=12, command=search_results)
    button_submit.grid(row=2, column=2, pady=2, padx=4)

    ##### Add button to analyze subreddits and save counts
    button_submit = tk.Button(tab_search, text="List Subreddits", width=12, command=get_subreddits)
    button_submit.grid(row=1, column=2, pady=2, padx=4)


# ============================================================================================
# Update Tab Setup
# ============================================================================================

    ##### Add input file input field
    tk.Label(tab_update, text="Input File: ").grid(row=0, column=0, pady=2, sticky=tk.W)
    file_in_update_entry = tk.Entry(tab_update)
    file_in_update_entry.insert(0, "saved_posts.csv")
    file_in_update_entry.grid(row=0, column=1, pady=2, sticky=tk.W)

    ##### Add output file input field
    tk.Label(tab_update, text="Output File: ").grid(row=1, column=0, pady=2, sticky=tk.W)
    file_out_update_entry = tk.Entry(tab_update)
    file_out_update_entry.insert(0, "cleaned_output.csv")
    file_out_update_entry.grid(row=1, column=1, pady=2, sticky=tk.W)

    ##### Add username input field
    tk.Label(tab_update, text="Username: ").grid(row=2, column=0, pady=2, sticky=tk.W)
    username_entry = tk.Entry(tab_update)
    username_entry.grid(row=2, column=1, pady=2, sticky=tk.W)

    ##### Add password input field
    tk.Label(tab_update, text="Password: ").grid(row=3, column=0, pady=2, sticky=tk.W)
    password_entry = tk.Entry(tab_update)
    password_entry.grid(row=3, column=1, pady=2, sticky=tk.W)

    ##### Add process num input field for force quit and resume
    tk.Label(tab_update, text="Process Num: ").grid(row=4, column=0, pady=2, sticky=tk.W)
    pnum_entry = tk.Entry(tab_update)
    pnum_entry.grid(row=4, column=1, pady=2, sticky=tk.W)

    ##### Add button to analyze subreddits and save counts
    button_submit = tk.Button(tab_update, text="Scrape Update", width=15, command=scrape_update)
    button_submit.grid(row=1, column=2, pady=2, padx=4)

    ##### Add button to analyze subreddits and save counts
    button_submit = tk.Button(tab_update, text="Process Download", width=15, command=process_download)
    button_submit.grid(row=2, column=2, pady=2, padx=4)



# ============================================================================================
# Run Tkinter
# ============================================================================================
    tk.mainloop()



if __name__ == "__main__":
    main()