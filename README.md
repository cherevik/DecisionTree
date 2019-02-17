# Decision Tree

Before you can use the script, you must install the following prerequisites: 

- Python 3: https://www.python.org/downloads/
- Graphviz: https://graphviz.gitlab.io/download/

Next, use your favorite GitHub client to clone the DecisionTree project on your machine. 
In a command window, change to the project directory, and execute the following commands:

Mac: 
```
> python3 -m pip install --user --upgrade pip
> python3 -m pip install --user virtualenv
> python3 -m virtualenv venv
> source venv/bin/activate
> pip install -r requirements.txt
```

Wndows: 
```
> py -m pip install --user virtualenv
> py -m virtualenv venv
> .\env\Scripts\activate
> pip install -r requirements.txt
```

Test your installation by running the following command.

Mac: 
```
> python decision_tree.py examples/simple.json
```

Windows: 
```
> py decision_tree.py examples\simple.json 
```

The command will process the simple tree definition saved in the 
“simple.json” file and display an image with the tree diagram. The 
corresponding Excel file will be saved in the file named “tree.xslx” 
in the “out” directory. 

You are now all set. You can begin by changing the simple tree 
definition the “simple.json” file and running the command to see the 
effects of your changes. 