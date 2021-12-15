##############
# Your turn! #
##############
# Now you're ready for the next part, where you retrieve data from an API
# of your choice. Note that you may need to provide an authentication key
# for some APIs. For that, work another file, called hw5-application.py.
#
# You will need to copy a few of the import statements from the top of this
# file. You may copy any helpful functions, too, like pretty() or
# safe_get().
#
# See requirements in the README.
#
# Also note that when the sunrise sunset API we used is queried for a
# date that doesn't exist, it gives a 400 error. Some APIs that you may
# use will return JSON-formatted data saying that the requested item
# couldn't be found. You may have to check the contents of the data you 
# get back to see whether a query was successful. You don't have to do
# that with the sunrise sunset API.

import urllib.parse, urllib.request, urllib.error, json
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from flask import Flask, request, render_template
def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

def callREST(urlstr):
    # try block was catching a 403 error, so I make a Request object and add a header
    # Meena helped me with this
    # returns a dictionary of the response data
    req = urllib.request.Request(urlstr)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36')

    try:
        response = urllib.request.urlopen(req)
        apistr = response.read()
        return json.loads(apistr)
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            print("The server couldn't fulfill the request.")
            print("Error code: ", e.code)
        if hasattr(e,'reason'):
            print("We failed to reach a server")
            print("Reason: ", e.reason)
    
    return None

    
# Function that iterates through json results from the recipe search api function
# and builds out a web page with meal options and their links to the recipe source.
# params -
#    jsondata - dictionary of api search results
#    lonks - dictionary of recipe links in ['id'] : 'linkURL' format
def buildMealPage(jsondata):
    header = "<html><head> <title> Meal Ideas </title></head><body>"
    header = header + '<form><input type="button" value="< Back" onclick="history.back()"></form>'
    footer = '<form><input type="button" value="< Back" onclick="history.back()"></form>' + "</body></html>"
    content = ''
    
    if len(jsondata['results']) < 1:
        content = "<h1>None of our meals matched your search :(</h1>"

    for item in jsondata['results']:
        content = content + '<h1>'+item['title']+'</h1>'
        content = content + '<img src="'+item["image"]+'" alt=\"img\" max-width=\"600\">'
        content = content + "<br><a href="+item['sourceUrl']+' target="_blank">See the Recipe --></a>'
    
    ofile = open('output.html', 'w')
    ofile.write(header + content + footer)
    ofile.close()
    return header + content + footer
    
# Takes in a list of meal ids from the spoonacular api
# Iterates over that list and calls the recipe search function of the api with the meal ids
# returns a dictionary with ids as keys and their corresponding recipe urls as values
#TODO maybe remove if we don't need this
def createLinks(idlst):
    linkdict = {}
    for id in idlst:
        searchstr = 'https://api.spoonacular.com/recipes/' + str(id) + '/information?includeNutrition=false&apiKey=13c376e11f2642f88f73581396090379'
        retdata = callREST(searchstr)
        if retdata != None:
            linkdict[id] = retdata['sourceUrl']
    return linkdict

# Big function that uses the input from the html form to make api calls
# This is essentially main()
def generateMeals():
    #print("List of accepted intolerances here: https://spoonacular.com/food-api/docs#Intolerances")
    intolStr = ''
    intol=''
    if request.args.get("iDairy"):
        intolStr = intolStr + 'Dairy,'
    if request.args.get('iEgg'):
        intolStr = intolStr + 'Egg,'
    if request.args.get('iGluten'):
        intolStr = intolStr + 'Gluten,'
    if request.args.get('iGrain'):
        intolStr = intolStr + 'Grain,'
    if request.args.get('iPeanut'):
        intolStr = intolStr + 'Peanut,'
    if request.args.get('iSeafood'):
        intolStr = intolStr + 'Seafood,'
    if request.args.get('iSesame'):
        intolStr = intolStr + 'Sesame,'
    if request.args.get('iShellfish'):
        intolStr = intolStr + 'Shellfish,'
    if request.args.get('iSoy'):
        intolStr = intolStr + 'Soy,'
    if request.args.get('iSulfite'):
        intolStr = intolStr + 'Sulfite,'
    if request.args.get('iTreeNut'):
        intolStr = intolStr + 'Tree Nut,'
    if request.args.get('iWheat'):
        intolStr = intolStr + 'Wheat,'

    if intolStr:
        intol = intolStr[:-1]
    tags = request.args.get('ingredients')
    maxTime = request.args.get("maxTime")
    sortMethod = request.args.get('sortin')
    mealType = request.args.get('mealType')
    diet = request.args.get('diet')

    #headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
    baseurl = 'https://api.spoonacular.com/recipes/complexSearch'

    tdic = {"apiKey":'13c376e11f2642f88f73581396090379'}
    if intol:
        tdic['intolerances'] = intol
    if tags:
        tdic['includeIngredients'] = tags
    if maxTime:
        tdic['maxReadyTime'] = maxTime
    if sortMethod:
        tdic['sort'] = sortMethod
    if mealType:
        tdic['type'] = mealType
    if diet:
        tdic['diet'] = diet

    tdic['addRecipeInformation'] = 'true'

    paramstr = urllib.parse.urlencode(tdic)

    apirequest = baseurl + "?" + paramstr
    print("URL:")
    print(apirequest)
    apidata = callREST(apirequest)

    if apidata == None:
        print("API call went wrong, we have no response data!")
        exit()

    print(pretty(apidata))
    #print('Meal Ideas:')

    idlst = []
    for item in apidata['results']:
        #print("   " + item['title'])
        idlst.append(item['id'])

    #print("ID list: {}".format(idlst))
    #print('Getting Links...')
    #links = createLinks(idlst)
    #print("Links: {}".format(links))

    print('Writing HTML...')
    return buildMealPage(apidata)

app = Flask(__name__)
@app.route("/")
def hello():
    return render_template('form.html')

@app.route("/mealsresponse")
def mealResponseHandler():
    #print(request.args)
    return generateMeals()
if __name__ == "__main__":
# Used when running locally only.
# When deploying to Google AppEngine, a webserver process will
# serve your app.
    app.run(host="localhost", port=8080, debug=True)
