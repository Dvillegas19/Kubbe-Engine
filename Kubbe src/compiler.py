# -*- coding: utf-8 -*-
import re
import os
import json
import sys
import io

class Tokenizer:
    def __init__(self, source_code):
        self.source = source_code
        self.tokens = []
        
    def tokenize(self):
        lines = self.source.splitlines()
        for line in lines:
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            
            regex_pattern = u"\u00b4([^\u00b4]*)\u00b4|'([^']*)'|([-+]?\\d*\\.?\\d+)|({|}|;)|!([^!]*)!|(BEGIN\\b|END\\b|ASSIGN\\b)|([a-z][a-z0-9~]*)"
            regex_tokens = re.findall(regex_pattern, line)
            
            for group in regex_tokens:
                if group[0]:
                    self.tokens.append(("String", group[0]))
                elif group[1]: 
                    self.tokens.append(("String", group[1]))
                elif group[2]:
                    if "." in group[2]:
                        self.tokens.append(("Number", float(group[2])))
                    else:
                        self.tokens.append(("Number", int(group[2])))
                elif group[3]:
                    self.tokens.append(("Operator", group[3]))
                elif group[4]:
                    self.tokens.append(("Action", group[4]))
                elif group[5]:
                    self.tokens.append(("Keyword", group[5]))
                elif group[6]:
                    self.tokens.append(("Identifier", group[6]))

        return self.tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_inx = 0
        self.symbol_table = {} 
    
    def parse(self):
        while self.current_token_inx < len(self.tokens):
            if self.peek_token() is None:
                break
            
            key_token = self.get_token()
            if key_token[0] != "Identifier":
                raise SyntaxError("Se esperaba un identificador, se encontro " + str(key_token))
            
            assign_token = self.get_token()
            if assign_token is None or assign_token[1] != "ASSIGN":
                got = str(assign_token) if assign_token else "Nada"
                raise SyntaxError("Se esperaba 'ASSIGN' despues de '" + str(key_token[1]) + "', se encontro: " + got)
            
            value = self.parse_value()
            self.symbol_table[key_token[1]] = value
        return self.symbol_table
            
    def get_token(self):
        if self.current_token_inx < len(self.tokens):
            token = self.tokens[self.current_token_inx]
            self.current_token_inx += 1
            return token
        return None
    
    def peek_token(self):
        if self.current_token_inx < len(self.tokens):
            return self.tokens[self.current_token_inx]  
        return None 
    
    def parse_value(self):
        token = self.peek_token()
        if token is None:
            raise SyntaxError("Se esperaba un valor despues de 'ASSIGN'")
        
        token_type, token_value = token 
        
        if token_type == "String" or token_type == "Number" or token_type == "Action": 
            self.current_token_inx += 1
            return token_value
        
        elif token_type == "Keyword" and token_value == "BEGIN":
            return self.parse_block()
        
        elif token_type == "Operator" and token_value == "{":
            return self.parse_list()
        
        raise SyntaxError("Error por valor inesperado encontrado: " + str(token_value))
        
    def parse_block(self): 
        self.get_token() 
        block_content = {}
        
        while self.peek_token() and self.peek_token()[1] != "END":
            key_token = self.get_token()
            if key_token[0] != "Identifier":
                raise SyntaxError("Error en bloque, se espera identificador, se encontro: " + str(key_token))
            
            assign_token = self.get_token()
            if assign_token is None or assign_token[1] != "ASSIGN":
                raise SyntaxError("Se esperaba 'ASSIGN', se encontro " + str(assign_token))
        
            value = self.parse_value() 
            block_content[key_token[1]] = value
            
        self.get_token() 
        return block_content
        
    def parse_list(self):
        self.get_token() 
        list_content = []
        while self.peek_token() and self.peek_token()[1] != "}":
            token_type, token_value = self.peek_token()
            
            if token_type == "Identifier":
                self.get_token()
                if token_value in self.symbol_table:
                     list_content.append(self.symbol_table[token_value])
                else:
                     list_content.append(token_value) 
            else:
                item = self.parse_value()
                list_content.append(item)
            
            if self.peek_token() and self.peek_token()[1] == ";":
                self.get_token()
        
        self.get_token() 
        return list_content

def load_file_content(filepath):
    if not os.path.exists(filepath):
        print "Error: El archivo " + filepath + " no se encontro."
        return None
    
    with io.open(filepath, "r", encoding="utf-8") as file:
        return file.read()
                
def save_ast_to_file(ast, filepath):
    try:
        json_str = json.dumps(ast, indent=4, ensure_ascii=False)
        
        if isinstance(json_str, str):
            json_str = json_str.decode('utf-8')
            
        with io.open(filepath, "w", encoding="utf-8") as file:
            file.write(json_str)
            
        print "Compilacion exitosa! Archivo de juego creado en " + filepath
    except Exception as e:
        print "Hubo un error al guardar el arbol: " + str(e)
     
if __name__ == "__main__":
    files_to_compile = ["games/snake.brick", "games/tetris.brick"]
    
    if len(sys.argv) > 1:
        files_to_compile = [sys.argv[1]]

    for file_path in files_to_compile:
        print "\n--- Procesando " + file_path + " ---"
        source_code = load_file_content(file_path)
        
        if source_code:
            try:
                tokenizer = Tokenizer(source_code)
                tokens = tokenizer.tokenize()
                parser = Parser(tokens)
                ast_and_table = parser.parse()
                
                output_path = file_path.replace(".brick", ".json")
                save_ast_to_file(ast_and_table, output_path)
                
            except Exception as e:
                print "!!! ERROR DE COMPILACION en " + file_path + " !!!"
                print str(e)