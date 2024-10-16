import requests
import urllib.parse
import json
import random
from datetime import datetime

directory_url = "http://newssites.pythonanywhere.com/api/directory/"
# default url for when running locally
api_url = 'http://127.0.0.1:8000'
session = requests.Session()


# user enters 'login <url>'
def login(args):
    
    # check for valid form
    if len(args) != 2:
        invalid()
        return
        
    # set api url for login
    global api_url 
    api_url = args[1]
    
    # request username and password
    username = input("Username: ")
    password = input("Password: ")
    
    # create payload and header
    payload = urllib.parse.urlencode({
        'username': username,
        'password': password
    })
    header = {
        'Content-Type' : 'application/x-www-form-urlencoded'
    }
    
    # make POST request
    try:
        response = session.post(api_url+'/api/login', data=payload, headers=header)
    except requests.exceptions.RequestException as e:
        print("Error: Unable to connect to url provided - " + api_url + "/api/login. Please try again.")
        return
        
    # check for success
    if response.status_code == 200:
        print(response.text)
    else:
        print("Error: " + response.text)


# user enters 'logout'
def logout(args):
    # check for valid form
    if len(args) != 1:
        invalid()
        return
    
    # make POST request
    try:
        response = session.post(api_url+'/api/logout')
    except requests.exceptions.RequestException as e:
        print("Error: Unable to connect to url provided - " +api_url + "/api/logout. Please try again.")
        return
    
    # check for success
    if response.status_code == 200:
        print(response.text)
    else:
        print("Error: " + response.text)


# user enters 'post'
def postStory(args):
    
    # check for valid form
    if len(args) != 1:
        invalid()
        return
    
    # request details and validate inputs
    print("Please give following information...")
    cats = ['pol', 'art', 'tech', 'trivia']
    regs = ['uk', 'eu', 'w']
    
    headline = input("Headline: \n>>")
    if len(headline) > 64:
        print("Your story's headline should be no more than 64 characters. This is " + str(len(headline)) + " characters.")
        return
    
    category = input("Category: \nChoices are: 'pol' (for politics), 'art' (for art), 'tech' (for technology) or 'trivia' (for trivial)\n>>")
    if category not in cats:
        print("Category should be: 'pol', 'art', 'tech' or 'trivia'.")
        return 
    
    region = input("Region: \nChoices are: 'uk' (for the uk), 'eu' (for europe) or 'w' (for world)\n>>")
    if region not in regs:
        print("Region should be: 'uk' (for the uk), 'eu' (for europe) or 'w' (for world)")
        return
    
    details = input("Details: \n>>")
    if len(details) > 64:
        print("Your story's details should be no more than 64 characters. This is " + str(len(details)) + " characters.")
        return
  
    # create payload and header
    payload = {
        'headline': headline,
        'category': category,
        'region' : region,
        'details' : details
    }
    header = {
        'Content-Type' : 'application/json'
    }
        
    # make POST request
    try:
        response = session.post(api_url+'/api/stories', json=payload, headers=header)
    except requests.exceptions.RequestException as e:
        print("Error: Unable to connect to the url provided - " +api_url + "/api/login. Please try again.")
        return
    
    # check for success
    if response.status_code == 201:
        print("Story has been posted succesfully.")
    else:
        print("Error: " + response.text + "\nPlease try again")
    

# user enters 'news [-id=] [-cat=] [-reg=] [-date=]'
def newsStory(args):
    
    # check for valid form
    if len(args) > 5 or len(args) == 0:
        invalid()
        return
    
    # set default values
    storyId = '*'
    storyCat = '*'
    storyReg = '*'
    storyDate = '*'

    # remove first arg: 'news'
    args.pop(0)
    
    # loop through arguments checking for validity and updating parameters
    for i in args:
        if i.startswith('-id='):
            storyId = i[5:-1]
        elif i.startswith('-cat='):         
            storyCat = i[6:-1]
        elif i.startswith('-reg='):
            storyReg = i[6:-1]
        elif i.startswith('-date='):
            storyDate = i[7:-1]
            # check date is in valid format:
            try:
                date = datetime.strptime(storyDate, '%d/%m/%Y')
                if storyDate != date.strftime('%d/%m/%Y'):
                    print("That is not a valid date. Please try again.")
                    return
            except ValueError:
                print("That is not a valid date. Please try again.")                
                return
        else:
            invalid()
            return
    
    # create payload
    payloadString = urllib.parse.urlencode({
        'story_cat': storyCat,
        'story_region': storyReg,
        'story_date' : storyDate
    })
    
    # get all news services from directory
    try:
        response = session.get(directory_url)
    except requests.exceptions.RequestException as e:
        print("Error: Unable to connect to url provided: " +api_url + "/api/login. Please try again.")
        return
    allAgencies = json.loads(response.text)
    selectedAgencies = []

    # if id is specified - limit to that one if possible
    if(storyId != '*'):
        for agency in allAgencies:
            # if found, select that agency
            if agency["agency_code"] == storyId:
                selectedAgencies.append(agency) 
    # pick 20 agencies if there are more than that
    elif len(allAgencies) > 20:
        selectedAgencies = random.sample(allAgencies, 20)
    else:
        selectedAgencies = allAgencies
    
    # if not found print error
    if len(selectedAgencies) == 0:
        print("No agencies found. Check that any id provided is a valid agency code.")
        return
    
    # loop through selected agencies
    for agency in selectedAgencies:
        # make GET requests to chosen services
        try:
            response = session.get(agency["url"]+'/api/stories?' + payloadString)
            print("\n\n-------------------------- From " + agency["agency_name"] + ": --------------------------" )
            # check for success
            if response.status_code == 200:
                # load stories and print them
                stories = json.loads(response.text)
                printStories(stories)
            elif response.status_code == 404: 
                print("No news stories were found at this agency.")
            else:
                print("Error: Could not get stories from this agency")
        except requests.exceptions.RequestException as e:
            print("Error collecting stories from url: " + e)


# user enters 'list'
def listServices(args):
    
    # check for valid form
    if len(args) != 1:
        invalid()
        return
    
    # send get request to directory
    try:
        response = session.get(directory_url)
    except requests.exceptions.RequestException as e:
        print("Error: Unable to connect to url provided: " +api_url + "/api/login. Please try again.")
        return
    
    # check for success
    if response.status_code == 200:
        printList(json.loads(response.text))
    else:
        print("Error: " + response.status_code + ", " + response.text)


# user enters 'delete <story_key>'
def deleteStory(args):
    
    # check for valid form
    if len(args) > 2:
        invalid()
        return
    if not args[1].isdigit():
        invalid()
        return
    
    # send delete request to logged in api
    try:
        response = session.delete(api_url+'/api/stories/' + args[1])
    except requests.exceptions.RequestException as e:
        print("Error: Unable to connect to url provided, or you are not logged in. Please try again.")
        return
    
    # check for success
    if response.status_code == 200:
        print("Story succesfully deleted.")
    else:
        print("Error: " + response.text)


# format stories
def printStories(stories):
    # use try statement to catch errors in keys returned by other services
    try:
        # get list of stories from dictionary pair
        storyList = stories["stories"]
        # print stories
        for story in storyList:
            print("\n" + story["headline"] + " (id: " + str(story["key"])+")")
            print("By: " + story["author"] + ", " + story["story_date"])
            print("Category: " + story["story_cat"] + ", Region: " + story["story_region"])
            print(story["story_details"])
    except KeyError:
        print("Error: This news agency hasn't returned the appropriate format.")
    except TypeError:
        print("Error: This news agency hasn't returned the appropriate format.")


# format list of services
def printList(services):
    for service in services:
        print("\nName: " + service["agency_name"])
        print("URL: " + service["url"])
        print("Code/ID: " + service["agency_code"])


# error message for an inavlid command
def invalid():
    print("That is not a valid command. Please try again.")


# print menu
def viewMenu():
    print("""\nAvailable commands:
          Login: 'login <url>'
          Logout: 'logout'
          Post a story: 'post'
          View stories: 'news [-id=] [-cat=] [-reg=] [-date=]'
          List services: 'list'
          Delete a story: 'delete <story_key>'\n
          See this menu again: 'menu'
          Exit this application: 'quit' or 'exit'\n""")


# function called only once (!) to register news service
def register():  
    
    # create payload and header
    payload = {
        'agency_name': "Hope Brooke News Agency",
        'url': "https://sc21hb.pythonanywhere.com",
        'agency_code' : "HMB02",
    }
    header = {
        'Content-Type' : 'application/json'
    }
        
    # make POST request
    try:
        response = session.post(directory_url, json=payload, headers=header)
    except requests.exceptions.RequestException as e:
        print("Error: Unable to connect to the url provided - " +directory_url + "/api/login. Please try again.")
        return
    
    # check for success
    if response.status_code == 201:
        print("Registered succesfully.")
    else:
        print("Error: " + response.text + "\nPlease try again")
    
    
    
def main():
    
    # register()    -- commented out after being ran once
    
    print("\nWelcome to this news aggregator!\n")
    viewMenu()
    
    # loop until exit
    while True:
    
        # take user input
        userInput = input("\n>> ")
        
        # check for exit
        if userInput.lower() == 'exit' or userInput.lower() == 'quit':
            break
        
        # parse the arguments
        args = userInput.split()
        
        # direct to appropriate function
        command = args[0].lower()
        if command == 'login':
            login(args)
        elif command == 'logout':
            logout(args)
        elif command == 'post':
            postStory(args)
        elif command == 'news':
            newsStory(args)
        elif command == 'list':
            listServices(args)
        elif command == 'delete':
            deleteStory(args)
        elif command == 'menu':
            viewMenu()
        else:
            invalid()


if __name__ == '__main__':
    main()
