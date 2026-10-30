# ⚡ IONOS PSEUDOCODE - UMG

> **Compilador, Intérprete y Entorno de Pseudocódigo Interactivo**  
> Proyecto desarrollado para la cátedra de *Autómatas y Lenguajes Formales* de la Universidad Mariano Gálvez de Guatemala.

---

## 🎓 Información Académica

* **🏛️ Universidad:** Universidad Mariano Gálvez de Guatemala (UMG)
* **🏫 Facultad:** Ingeniería en Sistemas de Información y Ciencias de la Computación
* **📍 Sede:** Retalhuleu
* **📚 Curso:** Autómatas y Lenguajes Formales
* **👨‍🏫 Catedrático:** Ing. Guillermo Alexander Pisqui Fuentes
* **👥 Integrantes:**
  * 👨‍💻 **Louis Neil Voyer García** — *(Carné: 2890-24-16741)*
  * 👨‍💻 **José Aimar López Bolaños** — *(Carné: 2890-24-12732)*

---

## 🚀 Características Principales (Requerimientos Funcionales)

El sistema cuenta con una arquitectura modular completa dividida en las siguientes secciones e indicadores técnicos:

* 📄 **Editor de Pseudocódigo (`RF-1`):** Área interactiva para redacción de algoritmos en tiempo real.
* 🔤 **Definición del Lenguaje (`RF-2`):** Soporte formal de palabras reservadas (`INICIO`, `FIN`, `LEER`, `ESCRIBIR`, `SI`, `ENTONCES`, `SINO`, `FINSI`).
* 🔍 **Analizador Léxico (`RF-3`):** Escáner léxico mediante Expresiones Regulares (Regex) con generación dinámica de tabla de tokens.
* 🌳 **Árbol Sintáctico (`RF-4`):** Generación de árbol de derivación (AST) visual para analizar la jerarquía de las sentencias.
* ⚙️ **Parser Sintáctico (`RF-5`):** Validación detallada de reglas de producción y sintaxis con diagnósticos descriptivos por línea.
* 📊 **Tipos de Datos (`RF-6`):** Control e inicialización estricta de variables de tipo `ENTERO`, `DECIMAL` y `TEXTO`.
* 🧮 **Operaciones Aritméticas (`RF-7`):** Evaluador jerárquico de operaciones matemáticas (`+`, `-`, `*`, `/`) con manejo de precedencia.
* 🖥️ **Entrada y Salida (`RF-8`):** Captura interactiva mediante ventanas emergentes y formateo automático de salidas numéricas a moneda local (**Quetzales - Q**).
* 🛡️ **Ejecución Segura (`RF-10`):** Entorno protegido contra divisiones entre cero, referencias nulas y bucles infinitos.
* 🌱 **Asistente Inteligente para Principiantes:** Generador que convierte lenguaje natural en código formal garantizando identificadores de variable válidos.

---

## 🛠️ Tecnologías Utilizadas

* 🐍 **Backend:** Python 3 + Flask (Servidor Web y Motor de Compilación)
* 🌐 **Frontend:** HTML5, CSS3 (Variables CSS, Modern Dark Theme), JavaScript ES6+
* ⚙️ **Motor Léxico / Sintáctico:** Módulo `re` (Regex) y Árboles de Análisis Sintáctico

---

## 💻 Instalación y Ejecución Local

### Prerrequisitos
Asegúrate de tener instalado **Python 3.8+** y **Git** en tu sistema.

### Pasos para Ejecutar

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/lvoyerg-cloud/ionos-pseudocode.git](https://github.com/lvoyerg-cloud/ionos-pseudocode.git)
   cd ionos-pseudocode
