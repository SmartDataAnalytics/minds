#!/usr/bin/env python

# -----------------------------------------------------------------------------
#
# tile: Math2SPARQL
# brief: Provide a simple interface which allows users to translate
#        mathematical formulae into SPARQL binding sequences.
# author: Damien Graux
# license: Apache License v2.0
# date: 2018
#
# -----------------------------------------------------------------------------

import ply.lex as lex
import ply.yacc as yacc
import os
import math             # For the factorial function.
import readline         # To have interactive input-line.

from colorama import init, Fore
init()

precision = 2
seriesdev = 3
subresult = 1

class Parser:
    """
    Base class for a lexer/parser that has the rules defined as methods
    """
    tokens = ()
    precedence = ()

    def __init__(self, **kw):
        self.debug = kw.get('debug', 0)
        self.names = {}
        try:
            modname = os.path.split(os.path.splitext(__file__)[0])[
                1] + "_" + self.__class__.__name__
        except:
            modname = "parser" + "_" + self.__class__.__name__
        self.debugfile = modname + ".dbg"
        self.tabmodule = modname + "_" + "parsetab"
        # print self.debugfile, self.tabmodule

        # Build the lexer and parser
        lex.lex(module=self, debug=self.debug)
        yacc.yacc(module=self,
                  debug=self.debug,
                  debugfile=self.debugfile,
                  tabmodule=self.tabmodule)

    def run(self):
        global subresult
        print(
            """
            +---------------------+
            |Math To SPARQL (v0.1)|
            +---------------------+
            """
        )
        while 1:
            try:
                subresult = 1 # Reset the subresult counter.
                s = raw_input(Fore.BLUE+'math2sparql > '+Fore.RESET)
            except EOFError:
                break
            if not s:
                continue
            if s.lower()=='exit' or s.lower()=='quit':
                break            
            yacc.parse(s)


class Calc(Parser):

    tokens = (
        'NAME', 'NUMBER', 'VAR',
        'PLUS', 'MINUS', 'POW', 'TIMES', 'DIVIDE',
        'EQUALS',
        'EXP', 'LN', 'SQRT',
        'SIN', 'COS', 'TAN',
        'LPAREN', 'RPAREN',
        'HELP', 'PRECISION', 'TERM',
    )

    # Tokens

    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_POW = r'\*\*'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_EQUALS = r'='
    t_EXP = r'[Ee][Xx][Pp]'
    t_LN = r'[Ll][Nn]'
    t_SQRT = r'[Ss][Qq][Rr][Tt]'
    t_SIN = r'[Ss][Ii][Nn]'
    t_COS = r'[Cc][Oo][Ss]'
    t_TAN = r'[Tt][Aa][Nn]'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_HELP = r'[Hh][Ee][Ll][Pp]'
    t_PRECISION = r'[Pp][Rr][Ee][Cc][Ii][Ss][Ii][Oo][Nn]'
    t_TERM = r'[Tt][Ee][Rr][Mm]'
    t_NAME = r'[Vv][Aa][Rr][a-zA-Z0-9_]*'
    t_VAR = r'\?[a-zA-Z0-9_]*'

    def t_NUMBER(self, t):
        r'\d+'
        try:
            t.value = int(t.value)
        except ValueError:
            print("Integer value too large %s" % t.value)
            t.value = 0
        return t

    t_ignore = " \t"

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Parsing rules

    precedence = (
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
        ('left', 'POW'),
        ('right', 'EXP', 'LN', 'SQRT'),
        ('right', 'SIN', 'COS', 'TAN'),
        ('right', 'UMINUS'),
    )

    def p_statement_help(self, p):
        'statement : HELP'
        print(
            """
Several operators are handle yet according the following table:

            +\n\t-\n\t*\n\t/\n\t**\n\tsin\n\tcos\n\ttan\n\texp\n\tln\n\tsqrt\n\tTODO: log, cotan, ...
            """)

    def p_statement_assign(self, p):
        'statement : NAME EQUALS expression'
        self.names[p[1]] = p[3]

    def p_statement_assign_precision(self, p):
        'statement : PRECISION EQUALS NUMBER'
        global precision
        if p[3]>=0 and p[3]<=10:
            print("New "+Fore.GREEN+"precision "+Fore.RESET+"is: " + str(p[3]))
            precision = p[3]
        else:
            print("The precision parameter should be in [0,10].")

    def p_statement_assign_term(self, p):
        'statement : TERM EQUALS NUMBER'
        global seriesdev
        if p[3]>=0 and p[3]<=15:
            print("New "+Fore.GREEN+"series term "+Fore.RESET+"is: " + str(p[3]))
            seriesdev = p[3]
        else:
            print("The number of terms for the series should be in [0,15].")

    def p_statement_expr(self, p):
        'statement : expression'
        # Finish by keeping only the needed precision.
        threshold = 10**precision
        print("BIND ( ( FLOOR(("+str(p[1])+")*"+str(threshold)+")/"+str(threshold)+" ) AS ?result )\n")
        
    def p_expression_binop(self, p):
        """
        expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression POW NUMBER
        """
        # print [repr(p[i]) for i in range(0,4)]
        if p[2] == '+':
            p[0] = str(p[1]) + "+" + str(p[3])
        elif p[2] == '-':
            p[0] = str(p[1]) + "-" + str(p[3])
        elif p[2] == '*':
            p[0] = str(p[1]) + "*" + str(p[3])
        elif p[2] == '/':
            p[0] = str(p[1]) + "/" + str(p[3])
        elif p[2] == '**':
            powstr = "1"
            for i in range(0,int(p[3])):
                powstr = powstr + "*" + str(p[1])
            p[0] = " ("+powstr+") "

    def p_expression_uminus(self, p):
        'expression : MINUS expression %prec UMINUS'
        p[0] = "-"+str(p[2])

    def p_expression_exp(self, p):
        'expression : EXP expression %prec EXP'
        global subresult
        expseries= "0"
        for n in range(0,seriesdev):
            x = "1"
            for i in range(0,n):
                x = x + "*" + str(p[2])
            x = "("+x+")"
            expseries = expseries + "+" + x + "/" + str(math.factorial(n))+".0" + "\n"
        print("BIND ((" + expseries + ")AS ?sub"+str(subresult)+")\n")
        p[0] = "?sub"+str(subresult)
        subresult += 1

    def p_expression_ln(self, p):
        'expression : LN expression %prec LN'
        global subresult
        lnseries= "0"
        for n in range(0,seriesdev):
            x = "1"
            for i in range(0,2*n+1):
                x = x + "*" + "(("+str(p[2])+"-1)/("+str(p[2])+"+1))"
            x = "("+x+")"
            lnseries = lnseries + "+" + x + "/" + str(2*n+1)+".0" + "\n"
        print("BIND (( 2*(" + lnseries + "))AS ?sub"+str(subresult)+")\n")
        p[0] = "?sub"+str(subresult)
        subresult += 1

    def p_expression_sqrt(self, p):
        'expression : SQRT expression %prec SQRT'
        global subresult
        lnseries= "0"
        expseries= "0"
        for n in range(0,seriesdev):
            x = "1"
            for i in range(0,2*n+1):
                x = x + "*" + "(("+str(p[2])+"-1)/("+str(p[2])+"+1))"
            x = "("+x+")"
            lnseries = lnseries + "+" + x + "/" + str(2*n+1)+".0" + "\n"
        print("BIND ((" + lnseries + ")AS ?sub"+str(subresult)+")\n") # Remove the '2*' of the ln series here !!!!
        for n in range(0,seriesdev):
            x = "1"
            for i in range(0,n):
                x = x + "*" + "?sub"+str(subresult)
            x = "("+x+")"
            expseries = expseries + "+" + x + "/" + str(math.factorial(n))+".0" + "\n"
        print("BIND ((" + expseries + ")AS ?sub"+str(subresult+1)+")\n")        
        p[0] = "?sub"+str(subresult+1)
        subresult +=2 
        
    def p_expression_sin(self, p):
        'expression : SIN expression %prec SIN'
        global subresult
        sinseries= "0"
        for n in range(0,seriesdev):
            x = "1"
            for i in range(0,2*n+1):
                x = x + "*" + " (" + str(p[2]) + "-6.28318530718*FLOOR("+str(p[2])+"/6.28318530718) )"
            x = "("+x+")"
            sinseries = sinseries + "+" + str((-1)**n) + "*" + x + "/" + str(math.factorial(2*n+1))+".0" + "\n"
        print("BIND ((" + sinseries + ")AS ?sub"+str(subresult)+")\n")
        p[0] = "?sub"+str(subresult)
        subresult += 1
        #p[0] = sinseries

    def p_expression_cos(self, p):
        'expression : COS expression %prec COS'
        global subresult
        cosseries= "0"
        for n in range(0,seriesdev):
            x = "1"
            for i in range(0,2*n):
                x = x + "*" + " (" + str(p[2]) + "-6.28318530718*FLOOR("+str(p[2])+"/6.28318530718) )"
            x = "("+x+")"
            cosseries = cosseries + "+" + str((-1)**n) + "*" + x + "/" + str(math.factorial(2*n))+".0" + "\n"
        #p[0] = cosseries
        print("BIND ((" + cosseries + ")AS ?sub"+str(subresult)+")\n")
        p[0] = "?sub"+str(subresult)
        subresult += 1

    def p_expression_tan(self, p):
        'expression : TAN expression %prec TAN'
        # Using the fact that tan(x)=sin(x)/cos(x) when x is not 0.
        global subresult
        sinseries= "0"
        cosseries= "0"
        for n in range(0,seriesdev):
            x = "1"
            for i in range(0,2*n+1):
                x = x + "*" + " (" + str(p[2]) + "-6.28318530718*FLOOR("+str(p[2])+"/6.28318530718) )"
            x = "("+x+")"
            sinseries = sinseries + "+" + str((-1)**n) + "*" + x + "/" + str(math.factorial(2*n+1))+".0" + "\n"
        for n in range(0,seriesdev):
            x = "1"
            for i in range(0,2*n):
                x = x + "*" + " (" + str(p[2]) + "-6.28318530718*FLOOR("+str(p[2])+"/6.28318530718) )"
            x = "("+x+")"
            cosseries = cosseries + "+" + str((-1)**n) + "*" + x + "/" + str(math.factorial(2*n))+".0" + "\n"
        print("BIND ((" + sinseries + ")AS ?sub"+str(subresult)+")\n")
        print("BIND ((" + cosseries + ")AS ?sub"+str(subresult+1)+")\n")
        p[0] = "?sub"+str(subresult)+"/?sub"+str(subresult+1)
        subresult += 2
        
    def p_expression_group(self, p):
        'expression : LPAREN expression RPAREN'
        p[0] = "("+str(p[2])+")"

    def p_expression_number(self, p):
        'expression : NUMBER'
        p[0] = str(p[1])
        
    def p_expression_var(self, p):
        'expression : VAR'
        p[0] = "xsd:double("+str(p[1])+")"

    def p_expression_name(self, p):
        'expression : NAME'
        try:
            p[0] = self.names[p[1]]
        except LookupError:
            print("Undefined name '%s'" % p[1])
            p[0] = 0

    def p_error(self, p):
        if p:
            print("Syntax error at '%s'" % p.value)
        else:
            print("Syntax error at EOF")

if __name__ == '__main__':
    calc = Calc()
    calc.run()
