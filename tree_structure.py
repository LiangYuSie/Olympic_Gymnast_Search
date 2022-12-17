import json
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

f = open('final_list.json')
final_list = json.load(f)
tree_structure(final_list)
with open("tree.json", "w") as outfile:
    json.dump(tree_2, outfile, indent =4)
f = open('tree.json')
data = json.load(f)