%{
#include "parser.tab.h"
%}

WHITESPACE  [ \t\n]

%%

{WHITESPACE}                                                    {/* Ignorar espacios */}                                       
([A-Z][a-z]+([ ]?[A-Z][a-z]+)*),[ \t\n\r]*([A-Z]\.)             { yylval.str = strdup(yytext); return NAME;}
\([0-9]{4}\)\.([^\.]+)\.                                        { yylval.str = strdup(yytext); return TITLE;}
[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}                  { yylval.str = strdup(yytext); return EMAIL;}
https?:\/\/(www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(\/\S*)?         { yylval.str = strdup(yytext); return URL;}
[0-9]{2}\/[0-9]{2}\/[0-9]{4}                                    { yylval.str = strdup(yytext); return DATE;}
[0-9]{4}-[0-9]{2}-[0-9]{2}                                      { yylval.str = strdup(yytext); return DATE_YEAR;}
.                                                               { }

%%
int yywrap() {
    return 1;
}