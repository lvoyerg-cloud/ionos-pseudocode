# IONOS Pseudocode

Aplicación web educativa para escribir, analizar y ejecutar pseudocódigo. El proyecto fue desarrollado con Python y Flask; la interfaz HTML, CSS y JavaScript está integrada en `app.py` mediante una plantilla HTML.

## Funcionalidades incluidas

- Editor web para escribir pseudocódigo.
- Análisis léxico y clasificación de tokens.
- Validación descriptiva de instrucciones y diagnóstico de errores.
- Ejecución de declaraciones de variables (`ENTERO`, `DECIMAL`, `TEXTO`).
- Captura de datos mediante `LEER`.
- Asignaciones y operaciones aritméticas con `<-`.
- Salida de información mediante `ESCRIBIR`.
- Registro de derivaciones de la Gramática Independiente del Contexto (GIC).
- Visualización del árbol sintáctico y del procedimiento de ejecución.
- Manual integrado y ejemplos para principiantes.

> Nota: el código fuente contiene palabras reservadas adicionales como `SI`, `ENTONCES` y `SINO`, pero la ejecución de estructuras condicionales no está implementada en el intérprete actual. La sintaxis admitida debe seguir el manual incluido en la aplicación.

## Tecnologías y herramientas

| Tecnología / herramienta | Uso |
|---|---|
| Python 3 | Lenguaje principal y lógica del intérprete. |
| Flask | Servidor web y rutas HTTP (`/` y `/run`). |
| HTML5 | Estructura de la interfaz. |
| CSS3 | Diseño visual y estilos. |
| JavaScript | Interacción del editor, envío de código y presentación de resultados. |
| Expresiones regulares (`re`) | Reconocimiento y clasificación de instrucciones y tokens. |
| Git y GitHub | Control de versiones y alojamiento del código fuente. |
| Visual Studio Code (opcional) | Editor recomendado para modificar el proyecto. |

La interfaz utiliza Google Fonts para cargar las fuentes Inter y Fira Code cuando hay conexión a Internet.

## Requisitos previos

- Python 3.10 o superior.
- `pip`, incluido normalmente con Python.
- Un navegador web actualizado.
- Conexión a Internet solo para cargar las fuentes externas; la aplicación puede funcionar sin ellas usando fuentes alternativas.

## Instalación e inicio

### Windows (PowerShell o CMD)

1. Descarga o clona este repositorio.
2. Abre una terminal dentro de la carpeta del proyecto.
3. Crea un entorno virtual:

   ```powershell
   python -m venv .venv
   ```

4. Activa el entorno virtual:

   **PowerShell**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   **CMD**
   ```cmd
   .venv\Scripts\activate.bat
   ```

5. Instala las dependencias:

   ```powershell
   pip install -r requirements.txt
   ```

6. Inicia la aplicación:

   ```powershell
   python app.py
   ```

7. La aplicación abrirá el navegador automáticamente. Si no sucede, visita:

   http://127.0.0.1:5000/

### Linux o macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Después, abre http://127.0.0.1:5000/ en el navegador.

Para detener el servidor, vuelve a la terminal y presiona `Ctrl + C`.

## Estructura del repositorio

```text
ionos-pseudocode/
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Ejemplo de pseudocódigo

```text
INICIO
DECIMAL subtotal
DECIMAL bono
DECIMAL total
LEER subtotal
LEER bono
total <- subtotal + bono
ESCRIBIR total
FIN
```

Al ejecutar este ejemplo, la aplicación solicita los valores de entrada y muestra el resultado en la consola de salida junto con los análisis disponibles.

## Publicar el proyecto en GitHub

1. Inicia sesión en https://github.com/ y crea un repositorio nuevo, por ejemplo `ionos-pseudocode`.
2. Coloca los archivos de esta carpeta en tu repositorio local.
3. Desde la terminal, ubicada en la carpeta del proyecto, ejecuta:

   ```bash
   git init
   git add .
   git commit -m "Primer commit: proyecto IONOS Pseudocode"
   git branch -M main
   git remote add origin https://github.com/TU-USUARIO/ionos-pseudocode.git
   git push -u origin main
   ```

4. Sustituye `TU-USUARIO` por tu nombre de usuario de GitHub y utiliza la URL real que GitHub muestra para tu repositorio.

## Consideraciones

- Esta es una aplicación local de uso educativo. El servidor se inicia en el puerto `5000`.
- No se debe publicar directamente en Internet sin revisar y reforzar la seguridad del intérprete y del servidor.
- El intérprete evalúa expresiones aritméticas mediante `eval()`; por ello, no debe utilizarse para ejecutar código no confiable ni exponerse como servicio público.
- El formulario de soporte de la interfaz muestra una confirmación visual; el código actual no integra un servicio externo para enviar tickets.
