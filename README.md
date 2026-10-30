# IONOS PSEUDOCODE - Compilador e Interprete Web

## Descripcion del Proyecto
IONOS PSEUDOCODE es una plataforma educativa web desarrollada como proyecto final para la asignatura de Autometas y Lenguajes Formales de la Universidad Mariano Galvez de Guatemala (Sede Retalhuleu).

## Datos Academicos
* **Institucion:** Universidad Mariano Galvez de Guatemala
* **Facultad:** Facultad de Ingenieria en Sistemas
* **Curso:** Automatas y Lenguajes Formales
* **Catedratico:** Ing. Guillermo Alexander Pisqui Fuentes
* **Integrantes:**
  * Louis Neil Voyer Garcia (Carne: 2890-24-16741)
  * Jose Aimar Lopez Bolanos (Carne: 2890-24-12732)

## Requerimientos Funcionales Implementados
* **RF-1 Editor de Pseudocodigo:** Entorno interactivo para redaccion del algoritmo fuente.
* **RF-2 Definicion del Lenguaje:** Palabras clave soportadas (INICIO, FIN, LEER, ESCRIBIR, SI, ENTONCES, SINO, FINSI).
* **RF-3 Analizador Lexico:** Tokenizacion mediante Expresiones Regulares.
* **RF-4 Arbol Sintactico y GIC:** Generacion de arbol AST estructurado y tabla GIC.
* **RF-5 Parser Sintactico:** Validacion de reglas gramaticales con diagnostico por linea.
* **RF-6 Tipos de Datos:** Control estricto de tipos (ENTERO, DECIMAL, TEXTO).
* **RF-7 Evaluador Aritmetico:** Procesamiento de expresiones matematicas (+, -, *, /).
* **RF-8 Entradas y Salidas:** Captura interactiva y formato monetario en Quetzales (Q).
* **RF-10 Ejecucion Segura:** Manejo aislado de excepciones e interceptacion de division entre cero.

## Tecnologias Utilizadas
* **Backend:** Python 3.8+ / Flask
* **Frontend:** HTML5, CSS3, JavaScript Vanilla

## Instrucciones de Ejecucion
1. Instalar dependencias: `pip install -r requirements.txt`
2. Ejecutar servidor: `python app.py`
