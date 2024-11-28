%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern int yylex(void);
extern char *yytext;
extern FILE *yyin, *yyout;
void yyerror(char *s);
int yylex();
FILE *output;
FILE *input;

%}

%union {
    char* str;
    int num;
}

%token <str> NAME YEAR TITLE EMAIL URL DATE DATE_YEAR

%%

input:
    | input_list
    ;

input_list:
    input_item
    | input_list input_item
    ;

input_item:
    NAME                { fprintf(output, "NAME: %s ", $1); }
    | NAME TITLE        { fprintf(output, "NAME: %s TITLE: %s\n", $1, $2); }
    | EMAIL             { fprintf(output, "EMAIL: %s\n", $1); }
    | URL               { fprintf(output, "URL: %s\n", $1);}
    | DATE              { fprintf(output, "DATE: %s\n", $1);}
    | DATE_YEAR              { fprintf(output, "DATE_YEAR: %s\n", $1);}
    | error             { 
        printf("\n"); 
        yyerrok;      
        yyclearin;    
    }
    ;

%%

void yyerror(char *s) {
    fprintf(stderr, "Error: %s\n", s);
}

int main(int argc, char **argv) {
    if(argc != 3){
        fprintf(stderr, "%s", argv[0]);
        return 1;
    }

    input = fopen(argv[1], "r");
    if(!input){
        perror("No se pudo abrir el archivo");
        return 1;
    }

    output = fopen(argv[2], "w");
    if(!output){
        perror("No se pudo abrir el archivo");
        return 1;
    }

    yyin = input;
    yyparse();

    fclose(input);
    fclose(output);
    return 0;
}
