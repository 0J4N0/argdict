import sys
import numpy as np 
import shlex

class Parser:
    blueprint = {}
    argv = []
    out = {}
    
    def __init__(self,blueprint:dict):
        """
        This Class is not intended to be initiated so the init exists just for the possibility
        of alternative syntax.
        """
        return Parser.set_blueprint(blueprint)

    @classmethod
    def set_argv(cls,argv)->None:
        """
        @argv: type str or list
        mainly intended for debugging and unittests  
        """
        cls.argv = argv.copy() if type(argv) == list() else shlex.split(argv)
    
    @classmethod
    def set_blueprint(cls,blueprint:dict)->None:
        cls.blueprint = blueprint
        cls.__clean_blueprint()
    
    @classmethod
    def __argv(cls)->list:
        cls.argv = sys.argv.copy() if not cls.argv else cls.argv

    @classmethod
    def argdict(cls,blueprint=False)->dict:
        if blueprint:
           cls.set_blueprint(blueprint) 
        cls.__argv()
        cls.__parse_loop()
        if cls.__validity_check(): return cls.out
    
    @classmethod
    def print_help(cls,prnt=False)->str:
        """
        @prnt: bool toggles whether or not the help info in printed
        """
        out = "################# Help #################\n"
        mandatory_flags = [flag for flag in cls.blueprint if cls.blueprint[flag]["mandatory"]]
        optional_flags = [flag for flag in cls.blueprint if not cls.blueprint[flag]["mandatory"]]

        if mandatory_flags: out += "\nMandatory flags:\n" + cls.__build_help_string(mandatory_flags)

        if optional_flags:
            out += "\nOptional flags:\n" + cls.__build_help_string(optional_flags)
        
        if prnt: print(out)
        return out 
    
    @classmethod
    def __build_help_string(cls,flags:list)->str:
        out = ""
        for flag in flags:
                out += f"\n{flag}"
                if "description" in cls.blueprint[flag]:
                    out += "\t"+cls.blueprint[flag]["description"] 
                out += "\n"
                flag_type = cls.blueprint[flag]["type"]
                out += f"\n\ttype: {flag_type.__name__}\n" if flag_type != list else f"\n\ttype: {flag_type.__name__} with elements of type {cls.blueprint[flag]['list_type'].__name__}\n"
                if cls.blueprint[flag]['type'] == bool:
                    out += "\n\tflags of type bool take no arguments\n"
                
                if cls.blueprint[flag]['type']==list:
                    lower,upper = list_bounds = cls.blueprint[flag]["list_bounds"]
                    if cls.blueprint[flag]["mandatory"]: lower = max(1,lower)
                    if lower > 0: out += f"\n\tthis flag needs at least {lower} arguments\n"
                    if upper != np.inf: out += f"\n\tthis flag accepts at most {max(0,upper)} arguments\n"

                if "in" in cls.blueprint[flag]:
                    words = []
                    for i in cls.blueprint[flag]["in"]:
                        word,_,_ = cls.__split_tripple(i)
                        words.append(word)
                    out += f"\n\targuments have to be among the following: {words}\n"
        return out
    
    
    @classmethod
    def __clean_blueprint(cls)->None:
        arg_options = []
        flags = cls.blueprint.keys()
        for flag in flags:
            if not cls.__flag_attribute(flag,"type"): cls.blueprint[flag]["type"] = list 
            if not cls.__flag_attribute(flag,"fuzzy"): cls.blueprint[flag]["fuzzy"] = 0
            cls.blueprint[flag]["case_sensitive"] = True if "case_sensitive" not in cls.blueprint[flag] else cls.blueprint[flag]["case_sensitive"]
            if not cls.__flag_attribute(flag, "mandatory"): cls.blueprint[flag]["mandatory"] = False

            if cls.blueprint[flag]["type"] == bool: cls.out[flag] = False
            if cls.blueprint[flag]["type"] == list:
                if not cls.__flag_attribute(flag, "list_bounds"): cls.blueprint[flag]["list_bounds"] = (0,np.inf)
                if not cls.__flag_attribute(flag, "list_type"): cls.blueprint[flag]["list_type"] = str
                if cls.__flag_attribute(flag,"in"): arg_options += cls.blueprint[flag]["in"]
            if cls.blueprint[flag]["type"] == str:
                if cls.__flag_attribute(flag,"in"): arg_options += cls.blueprint[flag]["in"]
        
        in_conflict = []
        for flag in flags:
            if cls.__word_to_list_distance(flag, arg_options): in_conflict.append(flag)
        
        tripple_flags = cls.__blueprint_keys()
        for i,flag in enumerate(tripple_flags):
            word,fuzz,case_sensitive = cls.__split_tripple(flag)
            if cls.__word_to_list_distance(word,tripple_flags[:i]+tripple_flags[i+1:]): in_conflict.append(flag)
        
        for arg_option in arg_options:
            word,fuzz,case_sensitive = cls.__split_tripple(arg_option)
            if cls.__word_to_list_distance(word,tripple_flags): in_conflict.append(arg_option)
        
        for flag in flags:
            args = cls.__flag_attribute(flag,"in")
            if args:
                for i,arg in enumerate(args):
                    word,fuzz,case_sensitive = cls.__split_tripple(arg)
                    if cls.__word_to_list_distance(word, args[:i]+args[i+1:]): in_conflict.append(word)

        if in_conflict:
            raise Exception(f"some flag names are to similar for fuzz: {in_conflict}")
    
    @classmethod
    def __blueprint_keys(cls)->list:
        out = []
        for k in cls.blueprint.keys():
            case_sensitive = cls.blueprint[k]["case_sensitive"]
            fuzzy = cls.blueprint[k]["fuzzy"]
            out.append((k,fuzzy,case_sensitive))
        return out 

    @classmethod
    def __split_tripple(cls,tripple):
        fuzz = 0
        case_sensitive = True
        if type(tripple) == str:
            return tripple,fuzz,case_sensitive

        for element in tripple:
            if type(element) == str: word = element
            if type(element) == int: fuzz = element
            if type(element) == bool: case_sensitive = element
        
        if word: return word,fuzz,case_sensitive
            
    @classmethod
    def __flag_attribute(cls,flag,attribute):
        if attribute in cls.blueprint[flag]: return cls.blueprint[flag][attribute]

    @classmethod
    def __parse_loop(cls)->None:
        used_flags = {}
        for i, flag in enumerate(cls.argv):
            f = cls.__word_to_list_distance(flag,cls.__blueprint_keys())
            if f: used_flags[f] = i
        
        flag_args = {}
        for flag in used_flags.keys():
            flag_args[flag] = []
            for i,arg in enumerate(cls.argv[used_flags[flag]+1:]):
                if (used_flags[flag] + i + 1) in used_flags.values(): break
                else: flag_args[flag].append(arg)

        for a in flag_args.keys():
            if cls.blueprint[a]["type"] == str: cls.__parse_str(a,flag_args[a])
            if cls.blueprint[a]["type"] == int: cls.__parse_int(a, flag_args[a])
            if cls.blueprint[a]["type"] == float: cls.__parse_float(a, flag_args[a])
            if cls.blueprint[a]["type"] == bool: cls.__parse_bool(a)
            if cls.blueprint[a]["type"] == list: cls.__parse_list(a, flag_args[a])

    @classmethod
    def __parse_str(cls,arg,args)->None:
        if "in" in cls.blueprint[arg]:
            for i in args:
                f = cls.__word_to_list_distance(i,cls.blueprint[arg]["in"])
                if f:
                    cls.out[arg] = f
                    break
        else:
            cls.out[arg] = args[0]

    @classmethod
    def __parse_int(cls,arg:str,args:list):
        clean = [i for i in args if i.replace(".","").isnumeric()]
        cls.out[arg] = int(float(clean[0]))
    
    @classmethod
    def __parse_float(cls,arg:str,args:list):
        clean = [i for i in args if i.replace(".","").isnumeric()]
        cls.out[arg] = float(clean[0])
    
    @classmethod
    def __parse_bool(cls,arg:str):
        cls.out[arg] = True
    
    @classmethod
    def __parse_list(cls,arg:str,args:list)->None:
        out = []
        upper_bound = cls.blueprint[arg]["list_bounds"][-1]
        add_argument = lambda a: out.append(a) if len(out) < upper_bound else None 
        list_type = cls.blueprint[arg]["list_type"]
        if list_type == str:
            if "in" in cls.blueprint[arg]:
                for i in args:
                    f = cls.__word_to_list_distance(i,cls.blueprint[arg]["in"])
                    if f: add_argument(f)
            else:
                for i in args:
                    add_argument(i)
        else:
            for i in args:
                if i.replace(".","").isnumeric():
                    if list_type == int: add_argument(int(float(i)))
                    if list_type == float: add_argument(float(i)) 
        
        if out: cls.out[arg] = out
    
    @classmethod
    def __word_to_list_distance(cls,arg,args)->str:
        """
        arg:str
        args:list like [(arg:str,fuzz:int,case_sensitivity:bool)]
        """
        arguments,fuzzes = [],[]
        for argument in args:
            word,fuzz,case_sensitive = cls.__split_tripple(argument)

            if case_sensitive: f = cls.__DL_distance(arg, word)
            else: f = cls.__DL_distance(arg.lower(), word.lower())

            if f <= max(fuzz,0):
                arguments.append(word)
                fuzzes.append(f)
            
            if arguments: return arguments[np.argmin(fuzzes)]

    @staticmethod
    def __DL_distance(word1:str, word2:str)->int:
        # https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance
        d = {}
        lenstr1,lenstr2 = len(word1),len(word2)
        for i in range(-1,lenstr1+1): d[(i,-1)] = i+1
        for j in range(-1,lenstr2+1): d[(-1,j)] = j+1
        for i in range(lenstr1):
            for j in range(lenstr2):
                if word1[i] == word2[j]: cost = 0
                else: cost = 1
                d[(i,j)] = min(d[(i-1,j)] + 1,d[(i,j-1)] + 1,d[(i-1,j-1)] + cost)
                if i and j and word1[i]==word2[j-1] and word1[i-1] == word2[j]: d[(i,j)] = min (d[(i,j)], d[i-2,j-2] + cost)
        
        return d[lenstr1-1,lenstr2-1]
    
    @classmethod
    def __validity_check(cls)->None:
        # check if all mandetory flags are used and of sufficient length: 
        mandetory_flags = [flag for flag in cls.blueprint.keys() if cls.blueprint[flag]["mandatory"]]
        difference = [flag for flag in mandetory_flags if flag not in cls.out.keys()]
        if difference: raise Exception(f"mandetory arguments missing: {' '.join(difference)}")
        
        if cls.out:
            list_flags = [flag for flag in list(cls.out.keys()) if cls.blueprint[flag]["type"] == list]
            list_to_short = [flag for flag in list_flags if cls.blueprint[flag]["list_bounds"][0] > len(cls.out[flag])]

        if list_to_short: raise Exception(f"not enough arguments for flags: {' '.join(list_to_short)}")
        return True
