import json
import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np
import tkinter as tk
from tkinter import *
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image,ImageTk
import matplotlib.pyplot as plt
import matplotlib.font_manager
from IPython.core.display import HTML


def wikiurl(year_list, gender, event_list):
    '''
    Create a list of urls that the program try to extract data from.
    
    Parameters
    ----------
    year_list : list of integer
        A list of year of the year of Olympic games.
    gender : str
        A gender variable of the gymnastic event
    event_list : list of string
        Events of olympic gymnastic games.
    '''
    for year in year_list:
        for event in event_list:
            wikiurl = "https://en.wikipedia.org/wiki/Gymnastics_at_the_{}_Summer_Olympics_%E2%80%93_{}%27s_{}".format(str(year), gender, event)
            url.append(wikiurl)

def country(url):
    '''
    Create a dict to look up country code and country name
    
    Parameters
    ----------
    url : str
        A url that could extract data about country code and country name reference.
    
    Returns
    -------
    country_dict
        A dictionay that the key is the country code and the value is country name.
    '''
    global country_dict
    response=requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    indiatable=soup.find_all('table', {"class": "wikitable"})
    table = indiatable[-1]
    df=pd.read_html(str(table))
    df=pd.DataFrame(df[0])
    mask = df.iloc[:, 0] == 'POSITION_T'
    df = df[~mask]
    df.columns = df.loc[mask.idxmax].values
    df = df.apply(pd.to_numeric, errors='ignore')
    df = df.rename(columns={ df.columns[0]: "Nation" })
    df = df.rename(columns={ df.columns[4]: "Code" })
    df = df[['Nation','Code']]
    country_dict = dict(zip(df.Code, df.Nation))
    return country_dict

def scrape_olympics(url):
    '''
    Scrape url's table content which contains rank, gymnast, nation, event, year variable.
    Cleanse the data, for example, change country code to country name and unify the country name.
    Combine all years and events data together as a list.
    
    Parameters
    ----------
    url : list of str
        A url list wiht all urls that the program is going to scrape
    
    Returns
    -------
    final_list
        A list of dictionary that contains each record of gymnast results.
    '''
    global final_list
    final_list = []
    for wikiurl in url:
        response=requests.get(wikiurl)
        soup = BeautifulSoup(response.text, 'html.parser')
        indiatable=soup.find_all('table', {"class": "wikitable"})
        table = indiatable[-1]
        df=pd.read_html(str(table))
        df=pd.DataFrame(df[0])
        if "Gymnast" not in df:
            table = indiatable[-2]
            df=pd.read_html(str(table))
            df=pd.DataFrame(df[0])
        if "Gymnast" not in df:
            df = df.rename(columns={"Name": "Gymnast"})
        if "Rank" not in df:
            df = df.rename(columns={"Position": "Rank"})
        if "Nation" in df or "Country" in df:
            df = df.rename(columns={"Country": "Nation"})
            df = df[['Rank', 'Gymnast', 'Nation']]
        else:
            new = df.iloc[:,1].str.split("(", n = 1, expand = True)
            df["Gymnast"]= new[0]
            df["Nation"]= new[1]
            df['Nation'] = df['Nation'].str.replace(')' ,'')
            df = df[['Rank', 'Gymnast', 'Nation']]
        mask = df.iloc[:, 0] == 'POSITION_T'
        df = df[~mask]
        df.columns = df.loc[mask.idxmax].values
        df = df.apply(pd.to_numeric, errors='ignore')
        df = df.rename(columns={ df.columns[0]: "Rank" })
        df = df.rename(columns={ df.columns[1]: "Gymnast" })
        df = df.rename(columns={ df.columns[2]: "Nation" })
        df['Gymnast'] = df['Gymnast'].str.replace('\xa0' ,'')
        df['Year'] = wikiurl[48:52]
        df['Gender'] = wikiurl[79: wikiurl.find('%27s_')]
        df['Event'] = wikiurl[wikiurl.find('%27s_')+5:]
        df['Nation'] = df['Nation'].str.replace('SUI','Switzerland')
        df['Nation'] = df['Nation'].str.replace('TPE','Chinese Taipei')
        df['Nation'] = df['Nation'].str.replace('GER','Germany')
        df['Nation'] = df['Nation'].str.replace('GRE','Greece')
        df['Nation'] = df['Nation'].str.replace('PHI','Philippines')
        df['Nation'] = df['Nation'].str.replace('NED','Netherlands')
        df['Nation'] = df['Nation'].str.replace('LAT','Latvia')
        df['Nation'] = df['Nation'].str.replace('GUA','Guatemala')
        df['Nation'] = df['Nation'].str.replace('CRO','Croatia')
        df['Nation'] = df['Nation'].str.replace('BUL','Bulgaria')
        df['Nation'] = df['Nation'].str.replace('ROC','Russia')
        clean_country_dict = {'Korea (the Republic of)\u200a[p]':'North Korea',
                              "Korea (the Democratic People's Republic of)\u200a[o]":'South Korea',
                             'Australia\u200a[b]':'Australia',
                             'Türkiye [ab]':'Turkey',
                             'United Kingdom of Great Britain and Northern Ireland (the)':'Great Britain',
                              'Czechia\u200a[i]':'Czech Republic',
                              'Russian Federation (the)\u200a[v]':'Russia',
                              'France\u200a[l]':'France',
                              'Venezuela (Bolivarian Republic of)':'Venezuela',
                              'United States of America ':'United States',
                             'United States of America (the)':'United States'}
        name = df.to_dict('records')
        for i in name:
            if i.get('Nation') in country_dict:
                i['Nation'] = country_dict[i.get('Nation')]
            for key in clean_country_dict.keys():
                if i.get('Nation') == key:
                    i['Nation'] = i['Nation'].replace(key, clean_country_dict[key])
                
        name[0]['Rank'] = 1
        name[1]['Rank'] = 2
        name[2]['Rank'] = 3
        final_list = final_list + name
    return final_list
          
def fetch_data(*, update = False, json_cache, url):
    '''
    Fetch data of olympic scraping results
    
    Parameters
    ----------
    update : bool
        Whether to update the scraping results or not.
    json_cache : str
        The file that save the cache of data.
    url : list
        The list of url that the program will scrape content from.

    Returns
    -------
    json_data
        Data of the cache or scraping results
    '''
    if update:
        json_data = None
    else:
        try:
            with open(json_cache, 'r') as file:
                json_data = json.load(file)
        except(FileNotFoundError, json.JSONDecodeError) as e:
            json_data = None
    if not json_data:
        scrape_olympics(url)
        json_data = final_list
    with open(json_cache, 'w') as file:
        json.dump(json_data, file)
    
    return json_data



def olympic_medal(year_list):
    '''
    Scrape the table content of each year's olympic medal count by country
    
    Parameters
    ----------
    year_list : list of integer
        A list of year of the year of Olympic games.

    Returns
    -------
    medal_list
        A list of dictionary that contains each year and each country's medal count.
    '''
    global medal_list
    medal_list = []
    for year in year_list:
        wikiurl = "https://en.wikipedia.org/wiki/{}_Summer_Olympics_medal_table".format(str(year))
        response=requests.get(wikiurl)
        soup = BeautifulSoup(response.text, 'html.parser')
        indiatable=soup.find_all('table', {"class": "wikitable sortable plainrowheaders jquery-tablesorter"})
        table = indiatable[0]
        df=pd.read_html(str(table))
        df=pd.DataFrame(df[0])
        mask = df.iloc[:, 0] == 'POSITION_T'
        df = df[~mask]
        df.columns = df.loc[mask.idxmax].values
        df = df.apply(pd.to_numeric, errors='ignore')
        df = df.rename(columns={ df.columns[1]: "Nation" })
        df = df.rename(columns={ df.columns[5]: "Total" })
        df['Nation'] = df['Nation'].str.replace('ROC','Russia')
        df['Nation'] = df['Nation'].str.replace('*','')
        df = df[['Nation','Total']]
        df['Year'] = year
        df.drop(df.tail(1).index,inplace=True)
        medal = df.to_dict('records')
        medal_list = medal_list + medal
    return medal_list


def tree_structure(list):
    '''
    Transform the list of dictionary to a tree strucure dictionary
    
    Parameters
    ----------
    list : list of dictionay
        A list of dictionary that contains each record of gymnast results.

    Returns
    -------
    tree_2
        A dictionary that the data is in a tree structure
    '''
    global tree, tree_1, tree_2
    tree = {}
    for i in list:
        year = i.get('Year')
        if year not in tree:
            year_child = []
            i.pop('Year')
            year_child.append(i)
            tree[year] = year_child
        else:
            year_child = tree.get(year)
            i.pop('Year')
            year_child.append(i)
            tree[year] = year_child
    tree_1 = {}
    for year in tree:
        tree_1[year] = {}
        for i in tree[year]:
            gender = i.get('Gender')
            if gender not in tree_1[year]:
                gender_child = []
                i.pop('Gender')
                gender_child.append(i)
                tree_1[year][gender] = gender_child
            else:
                gender_child = tree_1[year].get(gender)
                i.pop('Gender')
                gender_child.append(i)
                tree_1[year][gender] = gender_child
    tree_2 = {}
    for year in tree_1:
        tree_2[year]={}
        for gender in tree_1[year]:
            tree_2[year][gender] = {}
            for i in tree_1[year][gender]:
                event = i.get('Event')
                if event not in tree_2[year][gender]:
                    event_child = []
                    i.pop('Event')
                    event_child.append(i)
                    tree_2[year][gender][event] = event_child

                else:
                    event_child = tree_2[year][gender].get(event)
                    i.pop('Event')
                    event_child.append(i)
                    tree_2[year][gender][event] = event_child
    return tree_2


def page1(window):
    '''
    Create a GUI page that displays dropdown lists and buttons for users to interact with.
    
    Parameters
    ----------
    window : 
        A GUI widgets
    '''
    global data, year_variable, gender_variable, event_variable, optionmenu_c
    window.geometry("%dx%d+%d+%d" % (900, 400, 200, 150))
    window.title("Olympic Gymnast Search")

    data = {'Men':["artistic_individual_all-around","pommel_horse", "floor",
                   "rings", "vault", "parallel_bars", "horizontal_bar"],
            'Women':["artistic_individual_all-around","uneven_bars",
                     "balance_beam", "floor", "vault"]}
    L1 = Label(window,  text='Year', width=600 )  
    L1.pack(side = TOP, pady=10) 
    
    year_variable = StringVar(window)
    year_variable.set("Select Year")
    optionmenu_a = OptionMenu(window, year_variable, "2000","2004", "2008", "2012", "2016", "2020")
    optionmenu_a.pack() 

    
    L2 = Label(window,  text='Event', width=600 )  
    L2.pack(side = TOP, pady=10) 
    
    gender_variable = StringVar(window)
    event_variable = StringVar(window)

    gender_variable.trace('w', update_options)
    optionmenu_b = OptionMenu(window, gender_variable, *data.keys())
    optionmenu_c = OptionMenu(window, event_variable, "")

    gender_variable.set('Men')
    optionmenu_b.pack()
    event_variable.set('floor')
    optionmenu_c.pack()
    
    display = Label(window)
    display.pack()
    
    btnShow1 = Button(window, text="Show Results with Number of Medalists of the Country", command = show)
    btnShow1.pack()
    btnShow2 = Button(window, text="Show Results with Percentage of Medalists of the Country", command = percentage)
    btnShow2.pack()
    btnShow3 = Button(window, text="Show Champions of the Year", command = year)
    btnShow3.pack()
    btnShow4 = Button(window, text="Show Champions of the Event", command = event)
    btnShow4.pack()


def update_options(*args):
    '''Update event dropdown list based on gender selection'''
    global event_variable, optionmenu_c, menu
    gender = data[gender_variable.get()]
    event_variable.set(gender[0])
    menu = optionmenu_c['menu']
    menu.delete(0, 'end')
    for g in gender:
        menu.add_command(label=g, command=lambda nation = g: event_variable.set(nation))

        
        
def show():
    '''
    Create a dictionary of data based on users' selection and switch to the page that displays stacked bar chart.
    This function connects with the first two buttons that display event results of a game.
    '''
    global tree, tree_1, tree_2, year_variable, gender_variable, event_variable, result_dict, pagenum
    year_variable = year_variable.get()
    gender_variable = gender_variable.get()
    event_variable = event_variable.get()
    results = tree_2[year_variable][gender_variable][event_variable]
    result_dict = {}
    for i in results[:9]:
        a = []
        rank = int(i.get('Rank'))
        gymnast = i.get('Gymnast')
        gymnast = gymnast.ljust(20, " ")
        nation = i.get('Nation')
        nation_width = nation.rjust(15, " ")
        display =  "{}. {} - {}".format(str(rank), gymnast, nation_width) 
        event_count = 0
        if str(int(i.get('Rank'))).isnumeric():
            if int(i.get('Rank')) <= 3:
                count = -1
                event_count += 1
                a.append(event_count)                
            else:
                for i in results[:9]:
                    if i.get('Nation') == nation and int(i.get('Rank')) <= 3:
                        count = -1
                        event_count += 1
                a.append(event_count)
        for i in tree[year_variable]:
            if str(i.get('Rank')).isnumeric():
                if i.get('Nation') == nation and int(i.get('Rank')) <= 3:
                    count += 1
        a.append(count)
        for i in medal_list:
            if i.get('Nation') == nation and i.get('Year') == int(year_variable):
                total_count = i.get('Total')
        a.append(total_count)
        total_count = total_count - count
        result_dict[display] = a
    
    if percentage_show == False:
        for widget in window.winfo_children():
            widget.destroy()
        if pagenum == 1:
            page2(window)
            pagenum = 2


def year():
    '''
    Create a dataframe based on users' selection and switch to the page that displays the dataframe.
    This function connects with the third buttons that display champions of that year.
    '''
    global df, cols, pagenum, year_variable
    year_variable = year_variable.get()
    results = tree_2[year_variable]
    year_dict = {}
    gender = []
    event = []
    rank = []
    gymnast = []
    nation = []
    for k, v in results.items():
        for k1, v1 in v.items():
            for i in v1:
                if i.get('Rank') in [1]:
                    nation.append(i.get('Nation')) 
                    year_dict['Nation'] = nation
                    gender.append(k) 
                    year_dict['Gender'] = gender
                    event.append(k1) 
                    year_dict['Event'] = event
                    gymnast.append(i.get('Gymnast')) 
                    year_dict['Gymnast'] = gymnast

    df = pd.DataFrame(year_dict)
    df = df.set_index('Gymnast')
    cols = list(df.columns)
    for widget in window.winfo_children():
        widget.destroy()
    if pagenum == 1:
        page3(window)
        pagenum = 3

def event():
    '''
    Create a dataframe based on users' selection and switch to the page that displays the dataframe.
    This function connects with the fourth buttons that display champions of that event.
    '''
    global df, cols, pagenum, event_variable
    event_variable = event_variable.get()
    event_dict = {}
    gender = []
    year = []
    gymnast = []
    nation = []
    for k, v in tree_2.items():
        for k1, v1 in v.items():
            for k2, v2 in v1.items():
                if k2 == event_variable:
                    for i in v2:
                        if i.get('Rank') in [1]:
                            nation.append(i.get('Nation')) 
                            event_dict['Nation'] = nation
                            gender.append(k1) 
                            event_dict['Gender'] = gender
                            year.append(k) 
                            event_dict['Year'] = year
                            gymnast.append(i.get('Gymnast')) 
                            event_dict['Gymnast'] = gymnast
    df = pd.DataFrame(event_dict)
    df = df.set_index('Gymnast')
    cols = list(df.columns)
    
    for widget in window.winfo_children():
        widget.destroy()
    if pagenum == 1:
        page3(window)
        pagenum = 3


def make_html(fontname):
    return "<p>{font}: <span style='font-family:{font}; font-size: 24px;'>{font}</p>".format(font=fontname)


def chart(results, category_names):
    global fig, ax
    """
    Parameters
    ----------
    results : dict
        A dictionary of data based on the show function
    category_names : list of str
        The category labels.

    Returns
    -------
    fig
        The canvas for plotting.
    ax
        Axes of the plot.
    """
    font_color = 'black'
    csfont = {'fontname':'Courier New'} # title font
    hfont = {'fontname':'Courier New'} # main font
    labels = list(results.keys())
    data = np.array(list(results.values()))
    data_cum = data.cumsum(axis=1)
    category_colors = ['#f47e7a', '#b71f5c', '#621237']

    fig, ax = plt.subplots(figsize=(9.2, 5))
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())
    title = plt.title('Medals of the Country', pad=60, fontsize=18, color=font_color, **csfont)
    title.set_position([.5, 1.02])
    
    
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontsize(15)
    plt.xticks(color=font_color, **hfont)
    plt.yticks(color=font_color, **hfont)
    

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        rects = ax.barh(labels, widths, left=starts, height=0.5,
                        label=colname, color=color)

        text_color ='white'
        ax.bar_label(rects, label_type='center', color=text_color)
    ax.legend(ncol=len(category_names), bbox_to_anchor=(0, 1),
              loc='lower left', fontsize='small')
    
    
    plt.tight_layout()
    

    return fig, ax

def percentage():
    '''
    Use the results of the show function to create a dictionary that converts the data from number to percentage.
    '''
    global perc_result_dict, pagenum, percentage_show
    percentage_show = True
    show()
    perc_result_dict = {}
    for k, v in result_dict.items():
        total = 0
        perc_list = []
        for i in v:
            total += i
        for i in v:
            p = i*100/total
            perc_list.append(round(p))
        perc_result_dict[k] = perc_list
        if sum(perc_list) == 101:
            perc_list[-1] = perc_list[-1] - 1
        if sum(perc_list) == 99:
            perc_list[-1] = perc_list[-1] + 1
    for widget in window.winfo_children():
        widget.destroy()
    if pagenum == 1:
        page2(window)
        pagenum = 2
    
def page2(window):
    '''
    Create a GUI page that displays the chart results.
    
    Parameters
    ----------
    window : 
        A GUI widgets
    '''
    window.geometry("%dx%d+%d+%d" % (900, 400, 200, 150))
    category_names = ['Event', 'Gymnastic','Olympic']
    if percentage_show:
        chart(perc_result_dict, category_names)
    else:
         chart(result_dict, category_names)
    
    
    bar1 = FigureCanvasTkAgg(fig, window)
    bar1.get_tk_widget().pack()
    
def page3(window):
    '''
    Create a GUI page that displays the dataframe results.
    
    Parameters
    ----------
    window : 
        A GUI widgets
    '''
    window.geometry("%dx%d+%d+%d" % (900, 400, 200, 150))

    treeview = ttk.Treeview(window)
    treeview.pack()
    treeview["columns"] = cols
    for i in cols:
        treeview.column(i, anchor="w")
        treeview.heading(i, text=i, anchor='w')

    for index, row in df.iterrows():
        treeview.insert("",0,text=index,values=list(row))

url = []
year_list = [year for year in range(2000, 2024, 4)]
men_event = ["artistic_individual_all-around","pommel_horse", "floor", "rings", "vault", "parallel_bars", "horizontal_bar"]
women_event = ["artistic_individual_all-around","uneven_bars","balance_beam", "floor", "vault"]
country('https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes')
wikiurl(year_list, 'Men', men_event)
wikiurl(year_list, 'Women', women_event)
url.remove("https://en.wikipedia.org/wiki/Gymnastics_at_the_2012_Summer_Olympics_%E2%80%93_Women%27s_vault") #Due to the source code error, this page needs to be removed.

final_list = fetch_data(update = False, json_cache = 'final_list.json' , url = url)
tree_structure(final_list)
with open("tree.json", "w") as outfile:
    json.dump(tree_2, outfile, indent =4)

code = "\n".join([make_html(font) for font in sorted(set([f.name for f in matplotlib.font_manager.fontManager.ttflist]))])
HTML("<div style='column-count: 2;'>{}</div>".format(code))

olympic_medal(year_list)
percentage_show = False
pagenum = 1
window = Tk()
page1(window)
window.mainloop()