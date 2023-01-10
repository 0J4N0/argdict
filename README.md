
This is a simple script to bring the [`sys.argv`](https://docs.python.org/3/library/sys.html#sys.argv "sys.argv") output in a more usable format.
if you need a tool that is more geared towards a command-line interface please take a look at [argparse](https://docs.python.org/3/library/argparse.html) 

How it works:

You define what flags you want to use by creating a blueprint dictionary like this:
```python
from argdict import Parser
blueprint = {
			 "-flag1":{},
			 "-flag2":{}
}
arg_dict = Parser.argdict(blueprint)
```
now if you call that script like this:
```bash
python3 test.py -flag1 arg_for_flag1 -flag2 arg_for_flag2
```
your arg_dict variable will get a dictionary like this:
```python
arg_dict = {
			"-flag1":["args_for_flag1"],
			"-flag2":["args_for_flag2"]
}
```
You can further specify in the blueprint what arguments you expect and how you want to get them.

## Bool:

```python
blueprint = {
			 "-bool_flag":{"type":bool}
}
```
In this case if your -bool_flag is among the parsed arguments you will get:
```python
{"-bool_flag":True}
```
if the -bool_flag is not among the arguments you will get: 
```python
{"-bool_flag":False}
```

## Int and  Float:

```python
blueprint = {
			 "-intflag":{"type":int},
			 "-floatflag":{"type":float}
}
```

in this case the first parsed numeric argument will be the value for the that flag 

lets say your arguments for your numeric flag are: 
```txt
test also_not_numeric 5.3 7
```
"test" and "also_not_numeric" will be ignored. 5.3 is the first number and will therefor be the key of your numeric flag in case the flag is of type int 5.3 will be rounded down to 5.

## String:

```python
blueprint = {
			 "-strflag":{
			 "type":str,
			 "in":[("str_test",1,False),("another",2),("RaNdOm",False),"normal"]
			 }
}
```

by default the value for a flag of type string will be the first word after that flag. If  a list  is provided as the value for "in" only words from that list are accepted as values.
the list can have strings and tuples as elements. every tuple will by default be translated into 
```python
("word",0,True)
```
The string is the word, the number specifies the accepted fuzz. for a example with fuzz = 1 we have
word == lord == wodr. This might introduce confusion if not used wisely but it might add comfort if you expect inconsequential typos.
the boolean specifies the case sensitivity.
Only a word of type string is needed, the rest will default to (0,True) if not specified.

## List:

```python
blueprint = {
			 "-listflag":{
			 "type":list,
			 "in":[("str_test",1,False),("another",2),("RaNdOm",False),"normal"],
			 "list_type":str,
			 "list_bounds":(1,3)
			 }
}
```

List does what you came to expect form the previous types but it adds the key "list_type"
if the list type is str then you can also use a "in" key/value pair.
bool is not supported.

list_bounds specifies how many elements are the minimum and how many elements are the maximum. (minimum_inclusive,maximum_inclusive)



# general keys:

### all keys are optional

```python
{"generic_flag":{
				 "fuzzy":0,
				 "case_sensitive":True,
				 "mandatory":False,
				 "description":"this does important stuff"
	}
}
```

### fuzzy
as explained in the string case: the value for fuzzy specifies by how many letters a string can differ from the expected to still be interpreted as the expected string.
and because I can not say this often enough: even tho some possible errors are handled by the script you should try to avoid this function if there is a chance arguments could be confused.
[further information about the used algorithm](https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance)

### mandatory:
if a flag is specified as mandatory but is not among the arguments an error will be thrown 

### description:
the descriptions for all flags with a description gets printed with the Parser.print_help() function among other information about the flags.


## Set Blueprint:

there are three options to set the blueprint. 
Option one is:
```python
Parser.argdict(blueprint)
```
this directly returns the resulting dictionary.
the second option is to initiate the parser class object with the blueprint:
```python
p = Parser(blueprint)
```
and the third option is:
```python
p = Parser
p.set_blueprint(blueprint)
```
in both the second and third case you can get the dictionary like this:
```python
p.argdict()
```

## Set Arg Values:
argument values are automatically set to sys.argv but
for debugging you might want to set the arguments to parse manually and this can be done like this:
```python
p = Parser(blueprint)
p.set_argv(argv)
```
argv can be of type list or of type string:
```python
option1 = ["test","helo world"]
option2 = "test 'hello world'"
```

## Print Help:

```python
p = Parser(blueprint)
p.print_help()
```
this will print all flags in the blueprint and some information about them




































