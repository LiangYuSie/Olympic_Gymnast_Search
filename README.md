# Olympic Gymnast Search

Olympic Gymnast Search is an application that allows user to filter results by year, gender and event and see results of the game. It displays the results accompanying by a stacked bar chart that shows a country's medal count or percentage in that event and the Olympic game.

## Required Packages

pandas
requests
BeautifulSoup
numpy
tkinter
matplotlib

```python
import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np
import tkinter as tk
from tkinter import *
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.font_manager
```


## API Requirements

There is no specific requirement or API key to access the data.
Please see final_list.json file to access the data.


## Data Structure

The project use tree structure to store the data.
Please see tree.json file to access tree structure data.

{
    "2000": {
        "Men": {
            "artistic_individual_all-around": [
                {
                    "Rank": 1,
                    "Gymnast": "Alexei Nemov",
                    "Nation": "Russia"
                },
                {
                    "Rank": 2,
                    "Gymnast": "Yang Wei",
                    "Nation": "China"
                }...]
		}
	}
}



## Interaction

After executing the python file, an interface will pop up and allow user to filter data using a drop dwon lists.
There are three filters for user to interact with, they are year, gender and event.
There are four options to display results.
1. Display the game result with a stacked bar chart of medal count of the country.
2. Display the game result with a stacked bar chart of medal percentage of the country.
3. Display champions of certain year.
4. Display champions of certain event.

