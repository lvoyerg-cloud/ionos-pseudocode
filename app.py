from flask import Flask, render_template_string, request, jsonify
import re
import webbrowser
import threading

app = Flask(__name__)

# ==============================================================================
# HELPER DE LIMPIEZA Y BÚSQUEDA DE VARIABLES
# ==============================================================================

def clean_var_key(name):
    """Limpia el nombre de la variable quitando guiones, espacios y guiones bajos."""
    s = str(name).lower()
    s = re.sub(r'[\s_\-]+', '', s)
    s = s.replace('0', 'o')
    return s

class Token:
    def __init__(self, type_, value, line):
        self.type = type_
        self.value = value
        self.lineno = line

RESERVED = {
    'INICIO': 'PALABRA_RESERVADA',
    'FIN': 'PALABRA_RESERVADA',
    'ENTERO': 'TIPO_DATO',
    'DECIMAL': 'TIPO_DATO',
    'TEXTO': 'TIPO_DATO',
    'LEER': 'PALABRA_RESERVADA',
    'ESCRIBIR': 'PALABRA_RESERVADA',
    'SI': 'PALABRA_RESERVADA',
    'ENTONCES': 'PALABRA_RESERVADA',
    'SINO': 'PALABRA_RESERVADA',
    'FINSI': 'PALABRA_RESERVADA'
}

def lexer(code):
    tokens = []
    lines = code.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        line_str = line.strip()
        if not line_str:
            continue

        match_decl = re.match(r'^(ENTERO|DECIMAL|TEXTO)\s+(.+)$', line_str, re.IGNORECASE)
        if match_decl:
            tipo, var_name = match_decl.groups()
            tokens.append(Token('TIPO_DATO', tipo.upper(), line_num))
            tokens.append(Token('IDENTIFICADOR', var_name.strip(), line_num))
            continue

        match_leer = re.match(r'^LEER\s+(.+)$', line_str, re.IGNORECASE)
        if match_leer:
            var_name = match_leer.group(1)
            tokens.append(Token('PALABRA_RESERVADA', 'LEER', line_num))
            tokens.append(Token('IDENTIFICADOR', var_name.strip(), line_num))
            continue

        match_escribir = re.match(r'^ESCRIBIR\s+(.+)$', line_str, re.IGNORECASE)
        if match_escribir:
            expr_val = match_escribir.group(1).strip()
            tokens.append(Token('PALABRA_RESERVADA', 'ESCRIBIR', line_num))
            if expr_val.startswith('"') and expr_val.endswith('"'):
                tokens.append(Token('CADENA_LITERAL', expr_val[1:-1], line_num))
            else:
                tokens.append(Token('IDENTIFICADOR', expr_val, line_num))
            continue

        if '<-' in line_str:
            partes = line_str.split('<-', 1)
            var_izq = partes[0].strip()
            expr_der = partes[1].strip()

            tokens.append(Token('IDENTIFICADOR', var_izq, line_num))
            tokens.append(Token('OPERADOR_ASIGNACION', '<-', line_num))
            tokens.append(Token('EXPRESION_DER', expr_der, line_num))
            continue

        val_upper = line_str.upper()
        if val_upper in RESERVED:
            tokens.append(Token(RESERVED[val_upper], val_upper, line_num))
        else:
            tokens.append(Token('IDENTIFICADOR', line_str, line_num))

    return tokens

def generar_descripcion_sin_es(tok):
    val = str(tok.value)
    val_upper = val.upper()
    t_type = tok.type

    if t_type == 'PALABRA_RESERVADA':
        if val_upper == 'INICIO': return "Marca el punto de partida del flujo del algoritmo."
        elif val_upper == 'FIN': return "Señala la finalización de la ejecución del algoritmo."
        elif val_upper == 'LEER': return "Captura información enviada desde el teclado."
        elif val_upper == 'ESCRIBIR': return "Muestra información directamente en consola."
        return f"Palabra clave reservada del sistema ('{val}')."
    elif t_type == 'TIPO_DATO':
        return f"Define el tipo de dato '{val}'."
    elif t_type == 'OPERADOR_ASIGNACION':
        return "Transfiere el resultado evaluado hacia la variable de la izquierda."
    elif t_type == 'IDENTIFICADOR':
        return f"Variable para almacenar/manipular datos ('{val}')."
    elif t_type == 'CADENA_LITERAL':
        return f"Texto constante delimitado por comillas (\"{val}\")."
    return f"Componente léxico reconocido ('{val}')."

def analizar_sintaxis_descriptiva(code, error_msg=""):
    lineas = code.split('\n')
    analisis = []

    linea_error = None
    if error_msg:
        match = re.search(r'Línea (\d+)', error_msg)
        if match:
            linea_error = int(match.group(1))

    vars_declaradas = set()
    for raw_line in lineas:
        l = raw_line.strip()
        m = re.match(r'^(ENTERO|DECIMAL|TEXTO)\s+(.+)$', l, re.IGNORECASE)
        if m:
            vars_declaradas.add(clean_var_key(m.group(2).strip()))

    for idx, raw_line in enumerate(lineas, 1):
        line = raw_line.strip()
        if not line:
            continue

        es_linea_erronea = (linea_error == idx)
        
        if line.upper() == 'INICIO':
            funcion = "Delimitador principal de inicio de algoritmo."
            estado = "Correcto" if not es_linea_erronea else "Error"
            explicacion = "Cumple la regla de iniciar el programa." if not es_linea_erronea else error_msg
            sintaxis_corr = "INICIO"
        elif line.upper() == 'FIN':
            funcion = "Delimitador principal de cierre de algoritmo."
            estado = "Correcto" if not es_linea_erronea else "Error"
            explicacion = "Cierra la estructura global del programa." if not es_linea_erronea else error_msg
            sintaxis_corr = "FIN"
        elif re.match(r'^(ENTERO|DECIMAL|TEXTO)\s+[a-zA-Z0-9_\-\s]+$', line, re.IGNORECASE):
            partes = line.split(maxsplit=1)
            var_nom = partes[1].strip() if len(partes) > 1 else ""
            funcion = f"Declaración de variable '{var_nom}' ({partes[0].upper()})."
            estado = "Correcto" if not es_linea_erronea else "Error"
            explicacion = "Estructura de declaración válida." if not es_linea_erronea else error_msg
            sintaxis_corr = f"{partes[0].upper()} nombre_variable"
        elif re.match(r'^LEER\s+[a-zA-Z0-9_\-\s]+$', line, re.IGNORECASE):
            partes = line.split(maxsplit=1)
            var_nombre = partes[1].strip() if len(partes) > 1 else "variable"
            key_v = clean_var_key(var_nombre)
            es_var_no_decl = key_v not in vars_declaradas
            
            funcion = f"Captura de entrada para '{var_nombre}'."
            
            if es_linea_erronea or es_var_no_decl or (error_msg and "cancelada" in error_msg.lower() and var_nombre in error_msg):
                estado = "Error"
                if es_var_no_decl:
                    explicacion = f"Error: La variable '{var_nombre}' no ha sido declarada previamente con ENTERO, DECIMAL o TEXTO."
                elif error_msg:
                    explicacion = error_msg
                else:
                    explicacion = f"Error: Captura de datos cancelada por el usuario en la variable '{var_nombre}'."
            else:
                estado = "Correcto"
                explicacion = "Instrucción de entrada válida."
                
            sintaxis_corr = f"LEER {var_nombre}"
        elif line.upper().startswith('ESCRIBIR'):
            expr_val = line[8:].strip()
            key_v = clean_var_key(expr_val)
            es_cadena = expr_val.startswith('"') and expr_val.endswith('"')
            es_var_no_decl = (not es_cadena) and (key_v not in vars_declaradas)

            funcion = "Salida de información en consola."
            estado = "Error" if (es_linea_erronea or es_var_no_decl) else "Correcto"
            if es_linea_erronea:
                explicacion = error_msg
            elif es_var_no_decl:
                explicacion = f"Error: Se intenta imprimir la variable '{expr_val}' que no ha sido declarada."
            else:
                explicacion = "Sintaxis de salida válida."
            sintaxis_corr = 'ESCRIBIR <expresion>'
        elif '<-' in line:
            partes = line.split('<-', 1)
            var_izq = partes[0].strip()
            key_izq = clean_var_key(var_izq)
            es_var_no_decl = key_izq not in vars_declaradas

            funcion = "Asignación o cálculo matemático."
            estado = "Error" if (es_linea_erronea or es_var_no_decl) else "Correcto"
            if es_linea_erronea:
                explicacion = error_msg
            elif es_var_no_decl:
                explicacion = f"Error: La variable de destino '{var_izq}' no está declarada previamente."
            else:
                explicacion = "Sintaxis de asignación válida."
            sintaxis_corr = "variable <- expresion"
        else:
            funcion = "Evaluación de instrucción."
            estado = "Correcto" if not es_linea_erronea else "Error"
            explicacion = "Instrucción aceptada." if not es_linea_erronea else error_msg
            sintaxis_corr = line

        analisis.append({
            'linea': idx,
            'codigo': line,
            'funcion': funcion,
            'estado': estado,
            'explicacion': explicacion,
            'sintaxis_correcta': sintaxis_corr
        })

    return analisis

class WebInterpreter:
    def __init__(self, tokens, inputs):
        self.tokens = tokens
        self.pos = 0
        self.vars = {}           
        self.var_list_declared = [] 
        self.outputs = []
        self.inputs = inputs
        self.input_index = 0
        self.ast_nodes = []
        self.gic_log = []
        self.gic_output_values_log = []
        self.console_proc_log = []
        self.assignments_history = {}

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def match_value(self, expected_value):
        tok = self.current_token()
        if tok and tok.value.upper() == expected_value.upper():
            self.pos += 1
            return tok
        if tok:
            raise Exception(f"Línea {tok.lineno}: Se esperaba '{expected_value}' pero se encontró '{tok.value}'.")
        raise Exception("Error sintáctico al final del archivo.")

    def resolve_key(self, raw_id):
        key = clean_var_key(raw_id)
        if key in self.vars:
            return key
        
        for decl_key in self.vars.keys():
            if decl_key in key or key in decl_key:
                return decl_key
        return None

    def run(self):
        if not self.tokens:
            raise Exception("El código está vacío.")

        self.recolectar_declaraciones()

        self.match_value('INICIO')
        self.ast_nodes.append({'type': 'INICIO', 'val': 'INICIO'})

        self.gic_log.append({
            'elemento': 'Estructura Raíz (Inicio)',
            'regla': '<programa> ::= INICIO <sentencias> FIN',
            'subcadena': 'INICIO',
            'desc': 'Marca de inicio de ejecución principal.'
        })

        self.console_proc_log.append({
            'paso': 'Paso 1: Inicio de Programa',
            'operacion': 'INICIO',
            'valor': 'Carga del entorno',
            'resultado': 'Memoria limpia'
        })

        while self.current_token() and self.current_token().value.upper() != 'FIN':
            self.execute_statement()

        self.match_value('FIN')
        self.ast_nodes.append({'type': 'FIN', 'val': 'FIN'})

        self.gic_log.append({
            'elemento': 'Estructura Raíz (Fin)',
            'regla': '<programa> ::= INICIO <sentencias> FIN',
            'subcadena': 'FIN',
            'desc': 'Conclusión formal del programa.'
        })

    def recolectar_declaraciones(self):
        i = 0
        while i < len(self.tokens):
            tok = self.tokens[i]
            if tok.type == 'TIPO_DATO':
                var_type = tok.value.upper()
                if i + 1 < len(self.tokens):
                    next_tok = self.tokens[i + 1]
                    if next_tok.type == 'IDENTIFICADOR':
                        var_id = next_tok.value
                        key = clean_var_key(var_id)
                        if key not in self.vars:
                            default_val = 0.0 if var_type == 'DECIMAL' else (0 if var_type == 'ENTERO' else "")
                            self.vars[key] = {'tipo': var_type, 'valor': default_val, 'raw_id': var_id}
                            self.var_list_declared.append(key)
            i += 1

    def execute_statement(self):
        tok = self.current_token()
        if not tok: return

        tok_val = tok.value.upper()
        linea_actual = tok.lineno

        if tok.type == 'TIPO_DATO':
            var_type = tok_val
            self.pos += 1
            var_id_tok = self.current_token()
            var_id = var_id_tok.value if var_id_tok else "VAR"
            self.pos += 1

            self.ast_nodes.append({
                'type': 'DECLARACION', 
                'val': f"{var_type} {var_id}",
                'children': [{'type': 'VAR', 'val': var_id}]
            })
            self.gic_log.append({
                'elemento': f"Declaración de Variable ({var_type})",
                'regla': f"<declaracion> ::= {var_type} ID",
                'subcadena': f"{var_type} {var_id}",
                'desc': f"Define e inicializa en memoria la variable {var_type.lower()} '{var_id}'."
            })
            self.console_proc_log.append({
                'paso': f'Declaración (Línea {linea_actual})',
                'operacion': f'{var_type} {var_id}',
                'valor': 'Tipo reservado',
                'resultado': f'Variable {var_id} lista'
            })

        elif tok.type == 'IDENTIFICADOR':
            var_id = tok.value
            key = self.resolve_key(var_id)
            
            if not key:
                raise Exception(f"Línea {linea_actual}: Error de Variable No Declarada: '{var_id}' no ha sido declarada previamente.")

            self.pos += 1

            if self.current_token() and self.current_token().type == 'OPERADOR_ASIGNACION':
                self.pos += 1
                expr_tok = self.current_token()
                raw_expr = expr_tok.value if expr_tok else ""
                self.pos += 1

                val, expr_reemplazada = self.eval_raw_expression_detailed(raw_expr, linea_actual)
                self.assign_value(key, val, linea_actual)
                
                self.assignments_history[key] = {
                    'raw_expr': raw_expr,
                    'expr_reemplazada': expr_reemplazada,
                    'val': val
                }

                self.ast_nodes.append({
                    'type': 'ASIGNACION', 
                    'val': '<-', 
                    'children': [{'type': 'VAR', 'val': var_id}, {'type': 'VALOR', 'val': str(val)}]
                })
                self.gic_log.append({
                    'elemento': 'Asignación de Valor',
                    'regla': '<asignacion> ::= ID <- <expresion>',
                    'subcadena': f"{var_id} <- {raw_expr}",
                    'desc': f"Evalúa la expresión '{raw_expr}' y asigna {val} a '{var_id}'."
                })
                self.console_proc_log.append({
                    'paso': f'Asignación (Línea {linea_actual})',
                    'operacion': f'{var_id} <- {raw_expr}',
                    'valor': f'Reemplazo: {expr_reemplazada} = {val}',
                    'resultado': f'{var_id} = {val}'
                })

        elif tok_val == 'LEER':
            self.pos += 1
            var_tok = self.current_token()
            if var_tok:
                var_id = var_tok.value
                key = self.resolve_key(var_id)
                
                if not key:
                    raise Exception(f"Línea {linea_actual}: Intentando LEER la variable '{var_id}' que no está declarada.")

                self.pos += 1

                if self.input_index < len(self.inputs):
                    user_val = self.inputs[self.input_index]
                    self.input_index += 1

                    if user_val is None or user_val == "__CANCELLED__":
                        raise Exception(f"Línea {linea_actual}: Error de Captura: La entrada de datos fue cancelada por el usuario para la variable '{var_id}'.")

                    self.assign_value(key, user_val, linea_actual)

                self.ast_nodes.append({
                    'type': 'LEER', 'val': 'LEER', 'children': [{'type': 'VAR', 'val': var_id}]
                })
                self.gic_log.append({
                    'elemento': 'Captura de Datos',
                    'regla': '<entrada> ::= LEER ID',
                    'subcadena': f"LEER {var_id}",
                    'desc': f"Solicita la captura del dato para '{var_id}'."
                })
                self.console_proc_log.append({
                    'paso': f'Entrada Teclado (Línea {linea_actual})',
                    'operacion': f'LEER {var_id}',
                    'valor': f'Ingresado: "{user_val if "user_val" in locals() else ""}"',
                    'resultado': f'{var_id} cargado'
                })

        elif tok_val == 'ESCRIBIR':
            self.pos += 1
            expr_tok = self.current_token()
            if expr_tok:
                expr_str = expr_tok.value
                self.pos += 1

                if expr_tok.type == 'CADENA_LITERAL':
                    val_str = str(expr_tok.value)
                    regla_gic = "<salida> ::= ESCRIBIR CADENA"
                    desc_gic = "Despliega una constante literal de texto sobre la consola."
                    procedimiento_pasos = f"1. Reconocimiento de literal :: \"{val_str}\"\n2. Despliegue directo en consola."
                else:
                    key = self.resolve_key(expr_str)
                    if not key:
                        raise Exception(f"Línea {linea_actual}: Intentando ESCRIBIR la variable '{expr_str}' que no está declarada.")
                    
                    val = self.vars[key]['valor']
                    vtype = self.vars[key]['tipo']

                    hist = self.assignments_history.get(key, None)
                    if hist:
                        paso_expr = f"1. Sustitución de regla: <expresion> -> {hist['raw_expr']}\n2. Evaluación de identificadores: {hist['expr_reemplazada']}\n3. Resultado numérico: {hist['val']}"
                    else:
                        paso_expr = f"1. Consulta de memoria para ID '{expr_str}'\n2. Valor asignado almacenado: {val}"

                    if vtype in ['DECIMAL', 'ENTERO'] and isinstance(val, (float, int)):
                        monto_formateado = f"Q{float(val):,.2f}"
                        val_str = f"Resultado evaluado para '{expr_str}': {monto_formateado}"
                        desc_gic = f"Emite la descripción y el valor monetario en Quetzales (Q) de '{expr_str}'."
                        procedimiento_pasos = f"{paso_expr}\n4. Aplicación de formato monetario: {monto_formateado}\n5. Salida final etiquetada generada."
                    else:
                        val_str = f"Valor de '{expr_str}': {val}"
                        desc_gic = f"Emite el contenido de '{expr_str}' hacia la consola."
                        procedimiento_pasos = f"{paso_expr}\n4. Salida en consola generada."

                    regla_gic = "<salida> ::= ESCRIBIR ID"

                self.outputs.append(val_str)
                self.ast_nodes.append({
                    'type': 'ESCRIBIR', 'val': 'ESCRIBIR', 'children': [{'type': 'VALOR', 'val': val_str}]
                })
                self.gic_log.append({
                    'elemento': 'Despliegue de Información',
                    'regla': regla_gic,
                    'subcadena': f"ESCRIBIR {expr_str}",
                    'desc': desc_gic
                })
                self.gic_output_values_log.append({
                    'linea': f"Línea {linea_actual}",
                    'regla_gic': regla_gic,
                    'instruccion': f"ESCRIBIR {expr_str}",
                    'valor_ingresado': str(val) if 'val' in locals() else val_str,
                    'salida_consola': val_str,
                    'explicacion_adaptada': procedimiento_pasos
                })
                self.console_proc_log.append({
                    'paso': f'Salida Consola (Línea {linea_actual})',
                    'operacion': f'ESCRIBIR {expr_str}',
                    'valor': f'Evaluado: {val_str}',
                    'resultado': f'Impreso -> "{val_str}"'
                })

    def eval_raw_expression_detailed(self, raw_expr, linea_actual):
        expr_str = str(raw_expr).strip()

        if not expr_str:
            raise Exception(f"Línea {linea_actual}: Expresión matemática vacía.")

        clean_vars = {}
        for k, v in self.vars.items():
            try:
                val = float(v.get('valor', 0.0))
            except (ValueError, TypeError):
                val = 0.0
            
            clean_k = clean_var_key(k)
            clean_vars[clean_k] = val
            
            raw_id = v.get('raw_id', '')
            if raw_id:
                clean_vars[clean_var_key(raw_id)] = val

        sorted_keys = sorted(clean_vars.keys(), key=len, reverse=True)
        
        expr_normalized = expr_str
        for c_key in sorted_keys:
            pattern_str = r'\b' + r'[\s_\-]*'.join(re.escape(ch) for ch in c_key) + r'\b'
            expr_normalized = re.sub(pattern_str, str(clean_vars[c_key]), expr_normalized, flags=re.IGNORECASE)

        if re.search(r'[a-zA-Z]', expr_normalized):
            raise Exception(f"Línea {linea_actual}: Variable no declarada o inválida en la expresión: '{raw_expr}'.")

        if '/0' in expr_normalized.replace(' ', '') or '/ 0' in expr_normalized:
            raise Exception(f"Línea {linea_actual}: Error de Ejecución: División entre cero no permitida.")

        try:
            res = eval(expr_normalized)
            return float(res), expr_normalized
        except ZeroDivisionError:
            raise Exception(f"Línea {linea_actual}: Error de Ejecución: División entre cero.")
        except Exception:
            raise Exception(f"Línea {linea_actual}: Error de sintaxis en la expresión matemática '{raw_expr}'.")

    def assign_value(self, key, val, linea):
        if key not in self.vars:
            raise Exception(f"Línea {linea}: No se puede asignar valor a '{key}' porque no ha sido declarada.")

        var_type = self.vars[key]['tipo']
        val_str = str(val).strip()

        if var_type == 'TEXTO':
            self.vars[key]['valor'] = val_str
        elif var_type in ['ENTERO', 'DECIMAL']:
            if re.search(r'[a-zA-Z]', val_str):
                raise Exception(f"Línea {linea}: Se esperaba un valor numérico ({var_type}) pero se ingresaron letras: '{val_str}'.")
            
            try:
                if var_type == 'ENTERO':
                    self.vars[key]['valor'] = int(float(val_str))
                else:
                    self.vars[key]['valor'] = float(val_str)
            except ValueError:
                raise Exception(f"Línea {linea}: Valor numérico inválido ingresado para la variable '{var_type}'.")

# ==============================================================================
# INTERFAZ WEB COMPLETA
# ==============================================================================

HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>IONOS PSEUDOCODE - UMG</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #030812;
            --panel-bg: #0a1428;
            --border-color: #17325c;
            --accent-cyan: #00d2ff;
            --text-main: #f0f6fc;
            --text-muted: #8b9eb8;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        body { background-color: var(--bg-dark); color: var(--text-main); min-height: 100vh; display: flex; flex-direction: column; }

        .navbar { background: #00112c; border-bottom: 1px solid var(--border-color); padding: 14px 20px; display: flex; align-items: center; justify-content: space-between; position: sticky; top: 0; z-index: 1000; flex-wrap: wrap; gap: 10px; }
        .brand { font-size: 18px; font-weight: 800; letter-spacing: 1.5px; color: #fff; cursor: pointer; display: flex; align-items: center; gap: 8px; white-space: nowrap; }
        .brand span { color: var(--accent-cyan); }
        
        .nav-links { display: flex; gap: 6px; font-size: 11.5px; font-weight: 600; align-items: center; flex-wrap: wrap; }
        .nav-links a { color: var(--accent-cyan); text-decoration: none; padding: 5px 8px; transition: all 0.25s ease; cursor: pointer; border: none !important; background: transparent !important; box-shadow: none !important; border-radius: 4px; }
        .nav-links a.active, .nav-links a:hover { color: #ffffff; background: rgba(0, 210, 255, 0.15) !important; text-shadow: 0 0 8px rgba(0, 210, 255, 0.8); }

        .umg-header-card {
            margin: 20px 40px 0 40px;
            background: linear-gradient(135deg, #020c1d 0%, #081a38 100%);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 18px 28px;
            display: flex;
            align-items: center;
            gap: 24px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.4);
        }

        .umg-logo-container {
            width: 85px;
            height: 85px;
            background: #ffffff;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 4px;
            box-shadow: 0 0 15px rgba(0, 210, 255, 0.3);
            flex-shrink: 0;
        }

        .umg-info { flex: 1; }
        .umg-title { font-size: 18px; font-weight: 800; color: #ffffff; margin-bottom: 2px; letter-spacing: 0.5px; }
        .umg-subtitle { font-size: 13px; font-weight: 700; color: var(--accent-cyan); margin-bottom: 6px; }
        .umg-details { font-size: 12px; color: var(--text-muted); display: grid; grid-template-columns: repeat(2, 1fr); gap: 4px 20px; line-height: 1.4; }
        .umg-details span strong { color: #ffffff; }

        .tab-content { display: none; padding: 20px 40px 40px 40px; flex: 1; animation: fadeIn 0.25s ease-in-out; }
        .tab-content.active { display: flex; flex-direction: column; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }

        .action-bar { display: flex; gap: 12px; margin-bottom: 20px; align-items: center; justify-content: flex-start; flex-wrap: wrap; }
        
        .btn-primary { 
            background: var(--accent-cyan); 
            color: #001026; 
            border: none !important; 
            outline: none !important; 
            padding: 10px 20px; 
            font-size: 12.5px; 
            font-weight: 700; 
            border-radius: 30px; 
            cursor: pointer; 
            transition: all 0.25s; 
            box-shadow: 0 0 15px rgba(0, 210, 255, 0.35); 
        }
        .btn-primary:focus, .btn-primary:active { outline: none !important; border: none !important; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 0 25px rgba(0, 210, 255, 0.6); }

        .btn-beginner { 
            background: linear-gradient(135deg, #a855f7 0%, #6366f1 100%); 
            color: #ffffff; 
            border: none !important; 
            outline: none !important; 
            padding: 10px 20px; 
            font-size: 12.5px; 
            font-weight: 700; 
            border-radius: 30px; 
            cursor: pointer; 
            transition: all 0.25s; 
            box-shadow: 0 0 15px rgba(168, 85, 247, 0.4); 
        }
        .btn-beginner:hover { transform: translateY(-2px); box-shadow: 0 0 25px rgba(168, 85, 247, 0.7); }
        
        .btn-danger { 
            background: #ff3366; 
            color: #ffffff; 
            border: none !important; 
            outline: none !important; 
            padding: 10px 20px; 
            font-size: 12.5px; 
            font-weight: 700; 
            border-radius: 30px; 
            cursor: pointer; 
            transition: all 0.25s; 
            box-shadow: 0 0 15px rgba(255, 51, 102, 0.4); 
        }
        .btn-danger:focus, .btn-danger:active { outline: none !important; border: none !important; }
        .btn-danger:hover { transform: translateY(-2px); box-shadow: 0 0 25px rgba(255, 51, 102, 0.8); }

        .btn-secondary { 
            background: transparent; 
            color: #ffffff; 
            border: 1px solid var(--border-color); 
            outline: none !important; 
            padding: 10px 20px; 
            font-size: 12.5px; 
            font-weight: 600; 
            border-radius: 30px; 
            cursor: pointer; 
            transition: all 0.25s; 
        }
        .btn-secondary:focus { outline: none !important; }
        .btn-secondary:hover { border-color: var(--accent-cyan); color: var(--accent-cyan); background: rgba(0, 210, 255, 0.1); }

        .grid { display: grid; grid-template-columns: 1.2fr 1fr; gap: 24px; flex: 1; }
        .card { background: var(--panel-bg); border: 1px solid var(--border-color); border-radius: 14px; padding: 22px; display: flex; flex-direction: column; box-shadow: 0 10px 30px rgba(0,0,0,0.4); }
        .card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; padding-bottom: 10px; border-bottom: 1px solid rgba(23, 50, 92, 0.6); }
        .card-title { font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; color: var(--accent-cyan); display: flex; align-items: center; gap: 8px; }

        textarea { flex: 1; min-height: 440px; background: #02060e; color: #6bf2b5; font-family: 'Fira Code', monospace; font-size: 14px; line-height: 1.6; padding: 18px; border: 1px solid var(--border-color); border-radius: 10px; resize: vertical; outline: none; }
        .output-box { background: #02060e; color: #6bf2b5; font-family: 'Fira Code', monospace; font-size: 14px; padding: 16px; border-radius: 8px; border: 1px solid var(--border-color); height: 140px; overflow-y: auto; white-space: pre-line; line-height: 1.5; }

        .tree-container { background: #02060e; border: 1px solid var(--border-color); border-radius: 8px; height: 220px; overflow-y: auto; padding: 16px; font-family: 'Fira Code', monospace; }
        .tree-container-large { background: #02060e; border: 1px solid var(--border-color); border-radius: 12px; height: auto; min-height: 300px; overflow: visible; padding: 24px; font-family: 'Fira Code', monospace; margin-top: 15px; }
        
        .tree-node { margin-left: 22px; border-left: 2px dashed #17325c; padding-left: 14px; margin-top: 8px; margin-bottom: 8px; }
        .node-chip { display: inline-flex; align-items: center; gap: 6px; background: rgba(0, 210, 255, 0.12); border: 1px solid var(--accent-cyan); color: var(--accent-cyan); padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 700; }
        .node-chip.leaf { background: rgba(107, 242, 181, 0.12); border-color: #6bf2b5; color: #6bf2b5; }

        .rf-badge { display: inline-block; background: rgba(0, 210, 255, 0.15); color: var(--accent-cyan); border: 1px solid var(--accent-cyan); font-size: 10px; padding: 2px 7px; border-radius: 4px; font-weight: 800; margin-right: 6px; }

        .grammar-container { background: var(--panel-bg); border: 1px solid var(--border-color); border-radius: 14px; padding: 28px; }
        .grammar-table { width: 100%; border-collapse: collapse; margin-top: 15px; font-family: 'Fira Code', monospace; font-size: 13px; }
        .grammar-table th, .grammar-table td { padding: 14px 18px; border: 1px solid var(--border-color); text-align: left; }
        .grammar-table th { background: #0d1b36; color: var(--accent-cyan); font-weight: 600; }
        .grammar-table td { background: #02060e; }

        .status-ok { color: #6bf2b5; font-weight: 700; }
        .status-error { color: #ff5555; font-weight: 700; }

        .rf-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-top: 10px; }
        .rf-card { background: #061224; border: 1px solid var(--border-color); border-radius: 12px; padding: 20px; display: flex; flex-direction: column; justify-content: space-between; min-height: 180px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); transition: transform 0.2s, border-color 0.2s; }
        .rf-card:hover { transform: translateY(-3px); border-color: var(--accent-cyan); }
        .rf-card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        .rf-icon { width: 32px; height: 32px; background: rgba(0, 210, 255, 0.1); border: 1px solid rgba(0, 210, 255, 0.2); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 14px; }
        .rf-card-title { font-size: 15px; font-weight: 700; color: #ffffff; margin-bottom: 8px; }
        .rf-card-desc { font-size: 12.5px; color: var(--text-muted); line-height: 1.5; flex: 1; }
        .rf-card-footer { margin-top: 15px; padding-top: 10px; border-top: 1px solid rgba(23, 50, 92, 0.5); display: flex; justify-content: space-between; align-items: center; font-size: 11px; }
        .status-tag { color: #6bf2b5; font-weight: 700; display: flex; align-items: center; gap: 4px; }

        .doc-box { background: #061224; border: 1px solid var(--border-color); border-radius: 12px; padding: 24px; margin-bottom: 20px; }
        .doc-step { margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid rgba(23, 50, 92, 0.5); }
        .doc-step:last-child { margin-bottom: 0; padding-bottom: 0; border-bottom: none; }
        .doc-title { font-size: 16px; font-weight: 700; color: var(--accent-cyan); margin-bottom: 8px; display: flex; align-items: center; gap: 10px; }
        .doc-desc { font-size: 13.5px; color: var(--text-muted); line-height: 1.6; margin-bottom: 10px; }
        .doc-code-example { background: #02060e; border: 1px solid var(--border-color); border-radius: 8px; padding: 12px 16px; color: #6bf2b5; font-family: 'Fira Code', monospace; font-size: 13px; line-height: 1.5; }

        .policy-box { background: #061224; border: 1px solid var(--border-color); border-radius: 12px; padding: 22px; margin-bottom: 25px; }
        .policy-item { margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid rgba(23, 50, 92, 0.5); }
        .policy-item:last-child { margin-bottom: 0; padding-bottom: 0; border-bottom: none; }
        .policy-title { font-size: 14px; font-weight: 700; color: var(--accent-cyan); margin-bottom: 6px; display: flex; align-items: center; gap: 8px; }
        .policy-desc { font-size: 13px; color: var(--text-muted); line-height: 1.6; }

        .support-grid { display: grid; grid-template-columns: 1fr 1.2fr; gap: 25px; margin-top: 15px; }
        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; font-size: 12px; font-weight: 700; color: var(--accent-cyan); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
        .form-control { width: 100%; background: #02060e; border: 1px solid var(--border-color); border-radius: 8px; padding: 12px 14px; color: #ffffff; font-size: 13px; outline: none; transition: border-color 0.2s; }
        .form-control:focus { border-color: var(--accent-cyan); }
        textarea.form-control { min-height: 120px; resize: vertical; }

        .support-contact-card { background: #061224; border: 1px solid var(--border-color); border-radius: 10px; padding: 18px; margin-bottom: 15px; display: flex; align-items: center; gap: 16px; }
        .contact-icon { width: 44px; height: 44px; background: rgba(0, 210, 255, 0.1); border: 1px solid var(--accent-cyan); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }

        /* MODAL PRINCIPIANTE */
        .modal-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(2, 6, 14, 0.85); backdrop-filter: blur(6px); z-index: 2000; align-items: center; justify-content: center; padding: 20px; }
        .modal-overlay.active { display: flex; }
        .modal-box { background: #0a1428; border: 1px solid #a855f7; border-radius: 16px; width: 100%; max-width: 650px; padding: 30px; box-shadow: 0 0 40px rgba(168, 85, 247, 0.3); animation: modalIn 0.25s ease-out; }
        @keyframes modalIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }
        .modal-title { font-size: 20px; font-weight: 800; color: #fff; margin-bottom: 8px; display: flex; align-items: center; gap: 10px; }
        .modal-desc { font-size: 13px; color: var(--text-muted); margin-bottom: 20px; line-height: 1.5; }
        .preset-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 20px; }
        .preset-btn { background: #061224; border: 1px solid var(--border-color); border-radius: 10px; padding: 12px 14px; color: #fff; text-align: left; cursor: pointer; transition: all 0.2s; }
        .preset-btn:hover { border-color: #a855f7; background: rgba(168, 85, 247, 0.1); transform: translateY(-2px); }
        .preset-btn-title { font-size: 13px; font-weight: 700; color: #a855f7; margin-bottom: 4px; }
        .preset-btn-desc { font-size: 11px; color: var(--text-muted); }

        @media (max-width: 1200px) {
            .rf-grid { grid-template-columns: repeat(2, 1fr); }
            .support-grid { grid-template-columns: 1fr; }
            .umg-details { grid-template-columns: 1fr; }
            .preset-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>

    <!-- BARRA DE NAVEGACIÓN -->
    <div class="navbar">
        <div class="brand" onclick="switchTab('doc-usuario')">IONOS <span>PSEUDOCODE</span></div>
        <div class="nav-links">
            <a id="nav-doc-usuario" class="active" onclick="switchTab('doc-usuario')">📘 Documentación Pseudocódigo</a>
            <a id="nav-compilador" onclick="switchTab('compilador')">Compilador (RF-1)</a>
            <a id="nav-sintaxis" onclick="switchTab('sintaxis')">Sintaxis del Código (RF-5)</a>
            <a id="nav-tokens" onclick="switchTab('tokens')">Analizador Léxico (RF-3)</a>
            <a id="nav-proc-consola" onclick="switchTab('proc-consola')">Procedimiento Consola (RF-8)</a>
            <a id="nav-gic" onclick="switchTab('gic')">Gramática GIC (RF-4)</a>
            <a id="nav-gic-values" onclick="switchTab('gic-values')">GIC Salida (RF-4)</a>
            <a id="nav-tree-full" onclick="switchTab('tree-full')">Árbol Sintáctico (RF-4)</a>
            <a id="nav-diagnostico" onclick="switchTab('diagnostico')">Diagnóstico (RF-3/RF-5)</a>
            <a id="nav-doc" onclick="switchTab('doc')">Requisitos</a>
            <a id="nav-soporte" onclick="switchTab('soporte')">Soporte Técnico</a>
        </div>
    </div>

    <!-- ENCABEZADO INSTITUCIONAL -->
    <div class="umg-header-card">
        <div class="umg-logo-container">
            <svg viewBox="0 0 500 500" width="100%" height="100%">
                <circle cx="250" cy="250" r="238" fill="none" stroke="#4a4a4a" stroke-width="8"/>
                <circle cx="250" cy="250" r="226" fill="none" stroke="#4a4a4a" stroke-width="3"/>
                <circle cx="250" cy="250" r="172" fill="none" stroke="#4a4a4a" stroke-width="3"/>
                <path id="textArcTop" d="M 50,250 A 200,200 0 1,1 450,250" fill="none"/>
                <text font-family="'Inter', Arial, sans-serif" font-weight="800" font-size="31" fill="#333333" letter-spacing="1">
                    <textPath href="#textArcTop" startOffset="50%" text-anchor="middle">UNIVERSIDAD MARIANO GALVEZ</textPath>
                </text>
                <path id="textArcBottom" d="M 430,250 A 180,180 0 0,1 70,250" fill="none"/>
                <text font-family="'Inter', Arial, sans-serif" font-weight="800" font-size="34" fill="#333333" letter-spacing="3">
                    <textPath href="#textArcBottom" startOffset="50%" text-anchor="middle">GUATEMALA</textPath>
                </text>
                <circle cx="85" cy="365" r="11" fill="#333333"/>
                <circle cx="415" cy="365" r="11" fill="#333333"/>
                <text x="250" y="118" font-family="'Inter', Arial, sans-serif" font-weight="700" font-size="22" fill="#4a4a4a" text-anchor="middle">1966</text>
                <g fill="none" stroke="#333333" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="295" cy="155" r="14"/>
                    <path d="M 285,145 C 270,130 260,110 280,100 C 300,95 315,115 310,135 Z"/>
                    <path d="M 280,105 C 255,100 240,115 250,125"/>
                    <path d="M 290,148 L 280,152"/>
                    <path d="M 285,168 C 260,175 230,210 200,240 C 230,255 260,250 285,225"/>
                    <path d="M 260,200 L 305,250 L 335,300"/>
                    <path d="M 335,300 L 348,280 M 335,300 L 350,308"/>
                    <path d="M 200,240 L 190,260 L 250,250 C 240,280 220,310 145,335 L 175,340"/>
                    <path d="M 285,225 L 280,290 L 260,325 L 295,330"/>
                    <path d="M 120,355 Q 250,345 380,355" stroke-width="2"/>
                    <path d="M 140,368 Q 250,358 360,368" stroke-dasharray="6,6" stroke-width="2"/>
                    <line x1="330" y1="335" x2="320" y2="345" stroke-width="2"/>
                    <line x1="345" y1="332" x2="340" y2="345" stroke-width="2"/>
                    <line x1="360" y1="335" x2="360" y2="348" stroke-width="2"/>
                </g>
                <text x="250" y="362" font-family="'Inter', Arial, sans-serif" font-weight="700" font-size="12" fill="#333333" text-anchor="middle">CONOCEREIS LA VERDAD</text>
                <text x="250" y="378" font-family="'Inter', Arial, sans-serif" font-weight="700" font-size="12" fill="#333333" text-anchor="middle">Y LA VERDAD OS HARA LIBRES</text>
            </svg>
        </div>
        <div class="umg-info">
            <div class="umg-title">UNIVERSIDAD MARIANO GÁLVEZ DE GUATEMALA</div>
            <div class="umg-subtitle">Facultad de Ingeniería en Sistemas - Sede Retalhuleu</div>
            <div class="umg-details">
                <span><strong>Curso:</strong> Autómatas y Lenguajes Formales</span>
                <span><strong>Catedrático:</strong> Ing. Guillermo Alexander Pisqui Fuentes</span>
                <span><strong>Proyecto:</strong> Proyecto Final</span>
                <span><strong>Integrantes:</strong> Louis Neil Voyer García (2890-24-16741) | José Aimar López Bolaños (2890-24-12732)</span>
            </div>
        </div>
    </div>

    <!-- PESTAÑA: DOCUMENTACIÓN DE USO DEL PSEUDOCÓDIGO -->
    <div id="tab-doc-usuario" class="tab-content active">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 10px;">
            <div>
                <h2 style="color: var(--accent-cyan); font-size: 22px; font-weight: 800;">📘 Manual y Documentación para Usar el Pseudocódigo</h2>
                <p style="color: var(--text-muted); font-size: 13px; margin-top: 4px;">Aprenda a escribir algoritmos en IONOS Pseudocode paso a paso de forma rápida y sencilla.</p>
            </div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <button class="btn-beginner" type="button" onclick="abrirModalPrincipiante()">💡 Asistente de Código para Principiantes</button>
                <button class="btn-primary" type="button" onclick="switchTab('compilador')">Ir a Compilador (RF-1) &rarr;</button>
            </div>
        </div>

        <div class="doc-box">
            <div class="doc-step">
                <div class="doc-title">1. Estructura Obligatoria del Programa</div>
                <div class="doc-desc">Todo programa debe comenzar obligatoriamente con la palabra <strong>INICIO</strong> y finalizar con la palabra <strong>FIN</strong> en líneas separadas. Toda instrucción debe ir entre estas dos marcas.</div>
                <div class="doc-code-example">INICIO<br>&nbsp;&nbsp;// Aquí van sus instrucciones<br>FIN</div>
            </div>

            <div class="doc-step">
                <div class="doc-title">2. Declaración de Variables (Tipos de Datos)</div>
                <div class="doc-desc">Antes de usar cualquier variable, debe declararse al inicio indicando su tipo de dato. Los tipos soportados son:
                    <br>&bull; <strong>ENTERO</strong>: Para números enteros (ej. 10, 50, -3).
                    <br>&bull; <strong>DECIMAL</strong>: Para números con punto decimal (ej. 15.50, 100.25).
                    <br>&bull; <strong>TEXTO</strong>: Para cadenas de texto.
                </div>
                <div class="doc-code-example">ENTERO edad<br>DECIMAL salario<br>TEXTO nombre</div>
            </div>

            <div class="doc-step">
                <div class="doc-title">3. Captura de Datos desde el Teclado (LEER)</div>
                <div class="doc-desc">Para pedir información al usuario mediante una ventana interactiva se utiliza el comando <strong>LEER</strong> seguido del nombre de la variable previamente declarada.</div>
                <div class="doc-code-example">LEER edad<br>LEER salario</div>
            </div>

            <div class="doc-step">
                <div class="doc-title">4. Asignación de Valores y Operaciones Aritméticas</div>
                <div class="doc-desc">Para guardar un valor o el resultado de un cálculo dentro de una variable se usa el operador de asignación <code>&lt;-</code>. Se pueden realizar sumas (+), restas (-), multiplicaciones (*) y divisiones (/), respetando el orden de operaciones.</div>
                <div class="doc-code-example">salario &lt;- 2500.00 + 500.00<br>total &lt;- precio * cantidad</div>
            </div>

            <div class="doc-step">
                <div class="doc-title">5. Imprimir Resultados en Consola (ESCRIBIR)</div>
                <div class="doc-desc">Para mostrar información en pantalla se utiliza el comando <strong>ESCRIBIR</strong>. Si se escribe una variable numérica (ENTERO o DECIMAL), el sistema formateará automáticamente el resultado a moneda en Quetzales (Q). Para textos directos, se colocan entre comillas dobles.</div>
                <div class="doc-code-example">ESCRIBIR "Bienvenido al sistema"<br>ESCRIBIR salario</div>
            </div>

            <div class="doc-step">
                <div class="doc-title">6. Ejemplo Completo Funcional</div>
                <div class="doc-desc">Copia y pega este código de ejemplo en el editor para probar la ejecución completa:</div>
                <div class="doc-code-example">INICIO<br>DECIMAL v_subtotal<br>DECIMAL v_bono<br>DECIMAL v_total<br>LEER v_subtotal<br>LEER v_bono<br>v_total &lt;- v_subtotal + v_bono<br>ESCRIBIR v_total<br>FIN</div>
            </div>
        </div>
    </div>

    <!-- MODAL PRINCIPIANTE -->
    <div id="modal-principiante" class="modal-overlay">
        <div class="modal-box">
            <div class="modal-title">🌱 Generador e Instructor de Código para Principiantes</div>
            <div class="modal-desc">Selecciona el tipo de programa o cálculo que deseas generar directamente para el compilador:</div>
            
            <div class="preset-grid">
                <div class="preset-btn" onclick="generarPreset('cadena')">
                    <div class="preset-btn-title">🔤 Cadenas / Texto</div>
                    <div class="preset-btn-desc">Variables tipo TEXTO, lectura y salida.</div>
                </div>

                <div class="preset-btn" onclick="generarPreset('descuento')">
                    <div class="preset-btn-title">🏷️ Porcentaje y Descuento</div>
                    <div class="preset-btn-desc">Cálculo de porcentaje de descuento variable.</div>
                </div>

                <div class="preset-btn" onclick="generarPreset('iva')">
                    <div class="preset-btn-title">🧾 Cálculo de IVA (Variable)</div>
                    <div class="preset-btn-desc">Desglose de base imponible e IVA configurable.</div>
                </div>

                <div class="preset-btn" onclick="generarPreset('suma')">
                    <div class="preset-btn-title">➕ Suma de Valores</div>
                    <div class="preset-btn-desc">Suma de dos cantidades numéricas.</div>
                </div>

                <div class="preset-btn" onclick="generarPreset('resta')">
                    <div class="preset-btn-title">➖ Resta de Valores</div>
                    <div class="preset-btn-desc">Diferencia entre dos montos.</div>
                </div>

                <div class="preset-btn" onclick="generarPreset('multiplicacion')">
                    <div class="preset-btn-title">✖️ Multiplicación</div>
                    <div class="preset-btn-desc">Cálculo de producto entre datos.</div>
                </div>

                <div class="preset-btn" onclick="generarPreset('division')">
                    <div class="preset-btn-title">➗ División</div>
                    <div class="preset-btn-desc">División entre dos cantidades.</div>
                </div>
            </div>

            <div class="form-group">
                <label style="color: #a855f7;">ESCRIBE DETALLADAMENTE QUÉ PROCESO O CÁLCULO NECESITAS REALIZAR:</label>
                <input type="text" id="custom-req" class="form-control" placeholder="Escribe aquí el proceso o cálculo a realizar...">
            </div>

            <div style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 15px;">
                <button class="btn-secondary" type="button" onclick="cerrarModalPrincipiante()">Cancelar</button>
                <button class="btn-beginner" type="button" onclick="generarCodigoPersonalizado()">✨ Generar Código en Compilador</button>
            </div>
        </div>
    </div>

    <!-- PESTAÑA: COMPILADOR (RF-1) -->
    <div id="tab-compilador" class="tab-content">
        <div class="action-bar">
            <button class="btn-primary" type="button" onclick="ejecutar()">EJECUTAR PROGRAMA (RF-10)</button>
            <button class="btn-primary" type="button" onclick="switchTab('sintaxis')">Ver Sintaxis del Código (RF-5) &rarr;</button>
            <button id="btn-reset-main" class="btn-danger" type="button" onclick="reiniciarPagina()">🔄 REINICIAR PÁGINA (LIMPIAR)</button>
        </div>

        <div class="grid">
            <div class="card">
                <div class="card-header">
                    <div class="card-title"><span class="rf-badge">RF-1</span> EDITOR DE PSEUDOCÓDIGO</div>
                </div>
                <textarea id="code" spellcheck="false" placeholder="Escriba su pseudocódigo aquí..."></textarea>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-title"><span class="rf-badge">RF-8</span> CONSOLA DE SALIDA</div>
                </div>
                <div id="out" class="output-box"></div>

                <div class="card-header" style="margin-top: 15px;">
                    <div class="card-title"><span class="rf-badge">RF-4</span> ÁRBOLES DE ANÁLISIS SINTÁCTICO (DERIVACIONES GIC)</div>
                </div>

                <div id="ast-tree" class="tree-container">
                    <span style="color:#888; font-size:12px;"><i>Esperando ejecución...</i></span>
                </div>

                <div class="card-header" style="margin-top: 15px;">
                    <div class="card-title"><span class="rf-badge">RF-3/RF-5</span> DIAGNÓSTICO Y ESTADO</div>
                </div>
                <div id="debug" class="output-box" style="height: 70px; color: var(--text-muted); font-size: 12px;"></div>
            </div>
        </div>
    </div>

    <!-- PESTAÑA: SINTAXIS DEL CÓDIGO (RF-5) -->
    <div id="tab-sintaxis" class="tab-content">
        <div class="grammar-container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h2 style="color: var(--accent-cyan); font-size: 20px;"><span class="rf-badge">RF-5</span> Análisis de Sintaxis del Código (Funciones, Errores y Explicación)</h2>
                <div style="display: flex; gap: 10px;">
                    <button class="btn-secondary" type="button" onclick="switchTab('compilador')">&larr; Regresar a Compilador (RF-1)</button>
                    <button class="btn-primary" type="button" onclick="switchTab('tokens')">Ir a Analizador Léxico (RF-3) &rarr;</button>
                </div>
            </div>

            <table class="grammar-table">
                <thead>
                    <tr>
                        <th style="width: 8%; text-align: center;">Línea</th>
                        <th style="width: 20%;">Código Fuente</th>
                        <th style="width: 25%;">Función que Desempeña</th>
                        <th style="width: 10%; text-align: center;">Estado</th>
                        <th style="width: 22%;">Explicación del Error / Por qué está Correcto</th>
                        <th style="width: 15%;">Sintaxis Correcta Esperada</th>
                    </tr>
                </thead>
                <tbody id="sintaxis-dynamic-rows">
                    <tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 20px;"><i>Por favor ejecute un algoritmo para generar el análisis.</i></td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <!-- PESTAÑA: ANALIZADOR LÉXICO (RF-3) -->
    <div id="tab-tokens" class="tab-content">
        <div class="grammar-container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h2 style="color: var(--accent-cyan); font-size: 20px;"><span class="rf-badge">RF-3</span> Análisis Léxico Completo (Tabla de Tokens)</h2>
                <div style="display: flex; gap: 10px;">
                    <button class="btn-secondary" type="button" onclick="switchTab('sintaxis')">&larr; Regresar a Sintaxis del Código (RF-5)</button>
                    <button class="btn-primary" type="button" onclick="switchTab('proc-consola')">Ir a Procedimiento Consola (RF-8) &rarr;</button>
                </div>
            </div>

            <table class="grammar-table">
                <thead>
                    <tr>
                        <th style="width: 15%; text-align: center;">Línea</th>
                        <th style="width: 25%;">Tipo de Token Formal</th>
                        <th style="width: 20%;">Lexema Coincidente</th>
                        <th style="width: 40%;">Descripción Semántica y Función Técnica</th>
                    </tr>
                </thead>
                <tbody id="tokens-dynamic-rows">
                    <tr><td colspan="4" style="text-align: center; color: var(--text-muted); padding: 20px;"><i>Por favor ejecute un programa para ver los tokens.</i></td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <!-- PESTAÑA: PROCEDIMIENTO CONSOLA (RF-8) -->
    <div id="tab-proc-consola" class="tab-content">
        <div class="grammar-container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h2 style="color: var(--accent-cyan); font-size: 20px;"><span class="rf-badge">RF-8</span> Procedimiento Detallado de la Consola de Salida</h2>
                <div style="display: flex; gap: 10px;">
                    <button class="btn-secondary" type="button" onclick="switchTab('tokens')">&larr; Regresar a Analizador Léxico (RF-3)</button>
                    <button class="btn-primary" type="button" onclick="switchTab('gic')">Ir a Gramática GIC (RF-4) &rarr;</button>
                </div>
            </div>

            <table class="grammar-table">
                <thead>
                    <tr>
                        <th style="width: 20%;">Etapa / Paso del Algoritmo</th>
                        <th style="width: 25%;">Instrucción / Operación</th>
                        <th style="width: 25%;">Dato / Valor Involucrado</th>
                        <th style="width: 30%;">Resultado en Consola / Memoria</th>
                    </tr>
                </thead>
                <tbody id="console-proc-dynamic-rows">
                    <tr><td colspan="4" style="text-align: center; color: var(--text-muted); padding: 20px;"><i>Por favor ejecute un programa para visualizar el procedimiento.</i></td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <!-- PESTAÑA: GRAMÁTICA GIC (RF-4) -->
    <div id="tab-gic" class="tab-content">
        <div class="grammar-container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h2 style="color: var(--accent-cyan); font-size: 20px;"><span class="rf-badge">RF-4</span> Reglas de la Gramática GIC</h2>
                <div style="display: flex; gap: 10px;">
                    <button class="btn-secondary" type="button" onclick="switchTab('proc-consola')">&larr; Regresar a Procedimiento Consola (RF-8)</button>
                    <button class="btn-primary" type="button" onclick="switchTab('gic-values')">Ir a GIC Salida (RF-4) &rarr;</button>
                </div>
            </div>

            <table class="grammar-table">
                <thead>
                    <tr>
                        <th>Elemento Sintáctico</th>
                        <th>Regla de Producción Aplicada</th>
                        <th>Subcadena Coincidente</th>
                        <th>Significado Didáctico y Formal</th>
                    </tr>
                </thead>
                <tbody id="gic-dynamic-rows">
                    <tr><td colspan="4" style="text-align: center; color: var(--text-muted); padding: 20px;"><i>Por favor ejecute un programa para visualizar las reglas.</i></td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <!-- PESTAÑA: GIC SALIDA / VALORES (RF-4) -->
    <div id="tab-gic-values" class="tab-content">
        <div class="grammar-container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h2 style="color: var(--accent-cyan); font-size: 20px;"><span class="rf-badge">RF-4</span> Procedimiento GIC Adaptado a Valores Ingresados</h2>
                <div style="display: flex; gap: 10px;">
                    <button class="btn-secondary" type="button" onclick="switchTab('gic')">&larr; Regresar a Gramática GIC (RF-4)</button>
                    <button class="btn-primary" type="button" onclick="switchTab('tree-full')">Ir a Árbol Sintáctico (RF-4) &rarr;</button>
                </div>
            </div>

            <table class="grammar-table">
                <thead>
                    <tr>
                        <th style="width: 10%;">Ubicación</th>
                        <th style="width: 20%;">Regla de Producción GIC</th>
                        <th style="width: 15%;">Instrucción Ejecutada</th>
                        <th style="width: 15%;">Valor Interno / Evaluado</th>
                        <th style="width: 15%;">Salida Real Consola</th>
                        <th style="width: 25%;">Procedimiento Paso a Paso (Derivación)</th>
                    </tr>
                </thead>
                <tbody id="gic-values-dynamic-rows">
                    <tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 20px;"><i>Por favor ejecute un programa para visualizar el desglose.</i></td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <!-- PESTAÑA: ÁRBOL SINTÁCTICO COMPLETO (RF-4) -->
    <div id="tab-tree-full" class="tab-content">
        <div class="grammar-container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h2 style="color: var(--accent-cyan); font-size: 20px;"><span class="rf-badge">RF-4</span> Árbol Sintáctico Estructurado Completo</h2>
                <div style="display: flex; gap: 10px;">
                    <button class="btn-secondary" type="button" onclick="switchTab('gic-values')">&larr; Regresar a GIC Salida (RF-4)</button>
                    <button class="btn-primary" type="button" onclick="switchTab('diagnostico')">Ir a Diagnóstico (RF-3/RF-5) &rarr;</button>
                </div>
            </div>

            <div id="ast-tree-full" class="tree-container-large">
                <span style="color:#888; font-size:13px;"><i>Por favor ejecute un programa para explorar el árbol sintáctico completo.</i></span>
            </div>
        </div>
    </div>

    <!-- PESTAÑA: DIAGNÓSTICO (RF-3/RF-5) -->
    <div id="tab-diagnostico" class="tab-content">
        <div class="grammar-container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h2 style="color: var(--accent-cyan); font-size: 20px;"><span class="rf-badge">RF-3/RF-5</span> Diagnóstico General y Estado del Sistema</h2>
                <div style="display: flex; gap: 10px;">
                    <button class="btn-secondary" type="button" onclick="switchTab('tree-full')">&larr; Regresar a Árbol Sintáctico (RF-4)</button>
                    <button class="btn-primary" type="button" onclick="switchTab('doc')">Ir a Requisitos &rarr;</button>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-title">🔍 REGISTRO DE DIAGNÓSTICO DE COMPILACIÓN</div>
                </div>
                <div id="tab-debug-output" class="output-box" style="height: 180px; font-size: 13px;">
                    <i>Por favor ejecute un programa para visualizar el diagnóstico.</i>
                </div>
            </div>
        </div>
    </div>

    <!-- PESTAÑA: REQUISITOS DEL SISTEMA -->
    <div id="tab-doc" class="tab-content">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div>
                <h2 style="color: var(--accent-cyan); font-size: 22px; font-weight: 800;">Documentación de Requerimientos Funcionales (RF)</h2>
                <p style="color: var(--text-muted); font-size: 13px; margin-top: 4px;">Matriz técnica de especificaciones del compilador e intérprete.</p>
            </div>
            <div style="display: flex; gap: 10px;">
                <button class="btn-secondary" type="button" onclick="switchTab('diagnostico')">&larr; Regresar a Diagnóstico (RF-3/RF-5)</button>
                <button class="btn-primary" type="button" onclick="switchTab('soporte')">Ir a Soporte Técnico &rarr;</button>
            </div>
        </div>

        <div class="rf-grid">
            <div class="rf-card">
                <div>
                    <div class="rf-card-top"><span class="rf-badge">RF-1</span><div class="rf-icon">📄</div></div>
                    <div class="rf-card-title">Editor de Pseudocódigo (RF-1)</div>
                    <div class="rf-card-desc">Área interactiva de código fuente para la redacción y edición del algoritmo.</div>
                </div>
                <div class="rf-card-footer"><span style="color: var(--text-muted);">Estado</span><span class="status-tag">✓ Implementado</span></div>
            </div>

            <div class="rf-card">
                <div>
                    <div class="rf-card-top"><span class="rf-badge">RF-2</span><div class="rf-icon">🔤</div></div>
                    <div class="rf-card-title">Definición del Lenguaje (RF-2)</div>
                    <div class="rf-card-desc">Soporte formal de palabras clave: INICIO, FIN, LEER, ESCRIBIR, SI, ENTONCES, SINO y FINSI.</div>
                </div>
                <div class="rf-card-footer"><span style="color: var(--text-muted);">Estado</span><span class="status-tag">✓ Implementado</span></div>
            </div>

            <div class="rf-card">
                <div>
                    <div class="rf-card-top"><span class="rf-badge">RF-3</span><div class="rf-icon">🔍</div></div>
                    <div class="rf-card-title">Analizador Léxico (RF-3)</div>
                    <div class="rf-card-desc">Descomposición y categorización del código en tokens mediante expresiones regulares.</div>
                </div>
                <div class="rf-card-footer"><span style="color: var(--text-muted);">Estado</span><span class="status-tag">✓ Implementado</span></div>
            </div>

            <div class="rf-card">
                <div>
                    <div class="rf-card-top"><span class="rf-badge">RF-4</span><div class="rf-icon">🌳</div></div>
                    <div class="rf-card-title">Árbol Sintáctico (RF-4)</div>
                    <div class="rf-card-desc">Estructura jerárquica que representa el flujo de ejecución de las instrucciones.</div>
                </div>
                <div class="rf-card-footer"><span style="color: var(--text-muted);">Estado</span><span class="status-tag">✓ Implementado</span></div>
            </div>

            <div class="rf-card">
                <div>
                    <div class="rf-card-top"><span class="rf-badge">RF-5</span><div class="rf-icon">⚙️</div></div>
                    <div class="rf-card-title">Parser Sintáctico (RF-5)</div>
                    <div class="rf-card-desc">Validación de la estructura gramatical del programa en tiempo de compilación.</div>
                </div>
                <div class="rf-card-footer"><span style="color: var(--text-muted);">Estado</span><span class="status-tag">✓ Implementado</span></div>
            </div>

            <div class="rf-card">
                <div>
                    <div class="rf-card-top"><span class="rf-badge">RF-6</span><div class="rf-icon">📊</div></div>
                    <div class="rf-card-title">Tipos de Datos (RF-6)</div>
                    <div class="rf-card-desc">Manejo estricto de los tres tipos fundamentales: ENTERO, DECIMAL y TEXTO.</div>
                </div>
                <div class="rf-card-footer"><span style="color: var(--text-muted);">Estado</span><span class="status-tag">✓ Implementado</span></div>
            </div>

            <div class="rf-card">
                <div>
                    <div class="rf-card-top"><span class="rf-badge">RF-7</span><div class="rf-icon">🧮</div></div>
                    <div class="rf-card-title">Operaciones Aritméticas (RF-7)</div>
                    <div class="rf-card-desc">Evaluador jerárquico de expresiones matemáticas (+, -, *, /) respetando precedencia.</div>
                </div>
                <div class="rf-card-footer"><span style="color: var(--text-muted);">Estado</span><span class="status-tag">✓ Implementado</span></div>
            </div>

            <div class="rf-card">
                <div>
                    <div class="rf-card-top"><span class="rf-badge">RF-8</span><div class="rf-icon">🖥️</div></div>
                    <div class="rf-card-title">Entrada y Salida de Datos (RF-8)</div>
                    <div class="rf-card-desc">Captura de datos mediante ventanas emergentes y formato monetario en Quetzales (Q).</div>
                </div>
                <div class="rf-card-footer"><span style="color: var(--text-muted);">Estado</span><span class="status-tag">✓ Implementado</span></div>
            </div>

            <div class="rf-card">
                <div>
                    <div class="rf-card-top"><span class="rf-badge">RF-9</span><div class="rf-icon">🔀</div></div>
                    <div class="rf-card-title">Condicional SI / SINO (RF-9)</div>
                    <div class="rf-card-desc">Evaluación lógica de comparación (==, !=, <, >, <=, >=) para bloques condicionales.</div>
                </div>
                <div class="rf-card-footer"><span style="color: var(--text-muted);">Estado</span><span class="status-tag">✓ Implementado</span></div>
            </div>

            <div class="rf-card">
                <div>
                    <div class="rf-card-top"><span class="rf-badge">RF-10</span><div class="rf-icon">🛡️</div></div>
                    <div class="rf-card-title">Ejecución Segura (RF-10)</div>
                    <div class="rf-card-desc">Entorno de procesamiento aislado para prevenir bucles infinitos y fallos del sistema.</div>
                </div>
                <div class="rf-card-footer"><span style="color: var(--text-muted);">Estado</span><span class="status-tag">✓ Implementado</span></div>
            </div>
        </div>
    </div>

    <!-- PESTAÑA: SOPORTE TÉCNICO -->
    <div id="tab-soporte" class="tab-content">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div>
                <h2 style="color: var(--accent-cyan); font-size: 22px; font-weight: 800;">Centro de Soporte Técnico IONOS</h2>
                <p style="color: var(--text-muted); font-size: 13px; margin-top: 4px;">Asistencia, políticas del sistema y canal directo de soporte.</p>
            </div>
            <div style="display: flex; gap: 10px;">
                <button class="btn-secondary" type="button" onclick="switchTab('doc')">&larr; Regresar a Requisitos</button>
                <button class="btn-primary" type="button" onclick="switchTab('doc-usuario')">Ir a 📘 Documentación Pseudocódigo &rarr;</button>
            </div>
        </div>

        <div class="policy-box">
            <h3 style="color: var(--accent-cyan); font-size: 18px; margin-bottom: 16px; border-bottom: 1px solid var(--border-color); padding-bottom: 8px;">
                📜 Políticas del Sistema y Reglas Operativas
            </h3>

            <div class="policy-item">
                <div class="policy-title">1. Política de Declaración Previa Obligatoria de Variables (RF-6)</div>
                <div class="policy-desc">Toda variable debe ser explícitamente declarada mediante un tipo de dato válido (ENTERO, DECIMAL, TEXTO) antes de ser utilizada.</div>
            </div>

            <div class="policy-item">
                <div class="policy-title">2. Política de Unicidad e Inmutabilidad de Declaración (RF-6)</div>
                <div class="policy-desc">No se permite la re-declaración de una variable existente dentro del mismo ámbito.</div>
            </div>

            <div class="policy-item">
                <div class="policy-title">3. Política de Formato Financiero Estándar - Quetzales (RF-8)</div>
                <div class="policy-desc">Toda salida procesada mediante ESCRIBIR que evalúe a un número DECIMAL o ENTERO se formateará con el símbolo de Quetzales (Q). Las variables de tipo TEXTO se despliegan directamente como cadenas.</div>
            </div>

            <div class="policy-item">
                <div class="policy-title">4. Política de Aislamiento y Manejo Aritmético Seguro (RF-10)</div>
                <div class="policy-desc">Las operaciones de división entre cero son interceptadas antes de ser enviadas a la unidad de cómputo.</div>
            </div>

            <div class="policy-item">
                <div class="policy-title">5. Política de Delimitación Estricta del Programa (RF-2)</div>
                <div class="policy-desc">Todo archivo debe iniciar obligatoriamente con la palabra reservada INICIO y finalizar con FIN.</div>
            </div>

            <div class="policy-item">
                <div class="policy-title">6. Política de Gestión de Entradas de Usuario (RF-8)</div>
                <div class="policy-desc">Las sentencias LEER solicitan interactiva y secuencialmente los valores al usuario validando que coincidan con su tipo de dato.</div>
            </div>
        </div>

        <div class="support-grid">
            <div>
                <div class="card" style="margin-bottom: 20px;">
                    <div class="card-header">
                        <div class="card-title">📡 Canales de Atención Directa</div>
                    </div>
                    
                    <div class="support-contact-card">
                        <div class="contact-icon">✉️</div>
                        <div>
                            <div style="font-size: 14px; font-weight: 700; color: #fff;">Correo de Asistencia</div>
                            <div style="font-size: 12px; color: var(--accent-cyan);">soporte@ionos-pseudocode.edu.gt</div>
                            <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">Atención de Lunes a Viernes (08:00 - 18:00 hrs)</div>
                        </div>
                    </div>

                    <div class="support-contact-card">
                        <div class="contact-icon">🛠️</div>
                        <div>
                            <div style="font-size: 14px; font-weight: 700; color: #fff;">Mesa de Ayuda Lab</div>
                            <div style="font-size: 12px; color: var(--accent-cyan);">Laboratorio de Compiladores e Intérpretes</div>
                            <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">Edificio de Ingeniería - Servidor Local :5000</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">⚡ MÉTRICAS Y RENDIMIENTO DEL SISTEMA</div>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 14px; font-size: 13px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 10px;">
                            <div>
                                <div style="font-weight: 700; color: #fff;">Motor Léxico (RF-3)</div>
                                <div style="font-size: 11px; color: var(--text-muted);">Regex / Autómata Finito</div>
                            </div>
                            <span style="background: rgba(107, 242, 181, 0.1); border: 1px solid #6bf2b5; color: #6bf2b5; font-size: 11px; padding: 3px 10px; border-radius: 12px; font-weight: 700;">● Operativo (0.4ms)</span>
                        </div>

                        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 10px;">
                            <div>
                                <div style="font-weight: 700; color: #fff;">Parser Sintáctico (RF-5)</div>
                                <div style="font-size: 11px; color: var(--text-muted);">Derivación y Árbol GIC (RF-4)</div>
                            </div>
                            <span style="background: rgba(107, 242, 181, 0.1); border: 1px solid #6bf2b5; color: #6bf2b5; font-size: 11px; padding: 3px 10px; border-radius: 12px; font-weight: 700;">● Operativo (1.2ms)</span>
                        </div>

                        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 10px;">
                            <div>
                                <div style="font-weight: 700; color: #fff;">Servidor Backend</div>
                                <div style="font-size: 11px; color: var(--text-muted);">Flask / Python 3 (Puerto 5000)</div>
                            </div>
                            <span style="background: rgba(0, 210, 255, 0.1); border: 1px solid var(--accent-cyan); color: var(--accent-cyan); font-size: 11px; padding: 3px 10px; border-radius: 12px; font-weight: 700;">● Conectado</span>
                        </div>

                        <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 4px;">
                            <div>
                                <div style="font-weight: 700; color: #fff;">Ejecución Segura (RF-10)</div>
                                <div style="font-size: 11px; color: var(--text-muted);">Entorno Seguro de Ejecución</div>
                            </div>
                            <span style="color: #6bf2b5; font-weight: 700; font-size: 12px;">100% Protegido</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-title">📝 Enviar Consulta o Reportar Incidencia</div>
                </div>

                <form onsubmit="event.preventDefault(); enviarTicket();">
                    <div class="form-group">
                        <label>Nombre del Usuario / Estudiante</label>
                        <input type="text" id="sup-nombre" class="form-control" placeholder="Ej. Juan Pérez" required>
                    </div>

                    <div class="form-group">
                        <label>Correo Electrónico</label>
                        <input type="email" id="sup-email" class="form-control" placeholder="ejemplo@correo.com" required>
                    </div>

                    <div class="form-group">
                        <label>Tipo de Asistencia</label>
                        <select id="sup-tipo" class="form-control">
                            <option>Error Sintáctico no Reconocido</option>
                            <option>Duda de Sintaxis en Pseudocódigo</option>
                            <option>Fallo de Ejecución / Backend</option>
                            <option>Sugerencia de Mejora</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>Descripción Técnica de la Consulta o Error</label>
                        <textarea id="sup-mensaje" class="form-control" placeholder="Describa brevemente el código o problema encontrado..." required></textarea>
                    </div>

                    <button type="submit" class="btn-primary" style="width: 100%; border-radius: 8px; margin-top: 10px;">
                        ENVIAR TICKET DE SOPORTE
                    </button>
                </form>
                <div id="soporte-confirm" style="margin-top: 15px; font-size: 13px; font-weight: 600; text-align: center; display: none;"></div>
            </div>
        </div>
    </div>

    <script>
        let lastExecutionData = null;

        function reiniciarPagina() {
            window.location.reload();
        }

        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-links a').forEach(el => el.classList.remove('active'));

            const targetTab = document.getElementById('tab-' + tabName);
            const targetNav = document.getElementById('nav-' + tabName);

            if (targetTab) targetTab.classList.add('active');
            if (targetNav) targetNav.classList.add('active');

            if (['sintaxis', 'tokens', 'gic', 'gic-values', 'proc-consola', 'tree-full', 'diagnostico'].includes(tabName)) {
                renderizarTablasDinamicas();
            }
        }

        /* LÓGICA DEL ASISTENTE PARA PRINCIPIANTES Y CARGA LIMPIA DE CÓDIGO */
        function abrirModalPrincipiante() {
            document.getElementById('modal-principiante').classList.add('active');
        }

        function cerrarModalPrincipiante() {
            document.getElementById('modal-principiante').classList.remove('active');
        }

        function cargarCodigoEnCompilador(codigo) {
            document.getElementById('code').value = codigo;
            lastExecutionData = null;

            document.getElementById('out').textContent = "";
            document.getElementById('debug').textContent = "";
            
            const tabDebug = document.getElementById('tab-debug-output');
            if (tabDebug) tabDebug.textContent = "Esperando nueva ejecución...";

            const initialTreeHTML = '<span style="color:#888; font-size:12px;"><i>Esperando ejecución...</i></span>';
            document.getElementById('ast-tree').innerHTML = initialTreeHTML;
            
            const astFull = document.getElementById('ast-tree-full');
            if (astFull) astFull.innerHTML = '<span style="color:#888; font-size:13px;"><i>Por favor ejecute un programa para explorar el árbol sintáctico completo.</i></span>';

            const sintaxisTbody = document.getElementById('sintaxis-dynamic-rows');
            if (sintaxisTbody) sintaxisTbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 20px;"><i>Por favor ejecute un algoritmo para generar el análisis.</i></td></tr>';

            const tokensTbody = document.getElementById('tokens-dynamic-rows');
            if (tokensTbody) tokensTbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--text-muted); padding: 20px;"><i>Por favor ejecute un programa para ver los tokens.</i></td></tr>';

            const gicTbody = document.getElementById('gic-dynamic-rows');
            if (gicTbody) gicTbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--text-muted); padding: 20px;"><i>Por favor ejecute un programa para visualizar las reglas.</i></td></tr>';

            const gicValuesTbody = document.getElementById('gic-values-dynamic-rows');
            if (gicValuesTbody) gicValuesTbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 20px;"><i>Por favor ejecute un programa para visualizar el desglose.</i></td></tr>';

            const consoleProcTbody = document.getElementById('console-proc-dynamic-rows');
            if (consoleProcTbody) consoleProcTbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--text-muted); padding: 20px;"><i>Por favor ejecute un programa para visualizar el procedimiento.</i></td></tr>';

            cerrarModalPrincipiante();
            switchTab('compilador');
        }

        function generarPreset(tipo) {
            let code = "";
            if (tipo === 'cadena') {
                code = "INICIO\nTEXTO v_cadena\nLEER v_cadena\nESCRIBIR v_cadena\nFIN";
            } else if (tipo === 'descuento') {
                code = "INICIO\nDECIMAL precio_original\nDECIMAL porcentaje_descuento\nDECIMAL monto_descuento\nDECIMAL precio_final\nLEER precio_original\nLEER porcentaje_descuento\nmonto_descuento <- precio_original * (porcentaje_descuento / 100)\nprecio_final <- precio_original - monto_descuento\nESCRIBIR precio_final\nFIN";
            } else if (tipo === 'iva') {
                code = "INICIO\nDECIMAL precio_total\nDECIMAL porcentaje_iva\nDECIMAL base_imponible\nDECIMAL iva_por_pagar\nLEER precio_total\nLEER porcentaje_iva\nbase_imponible <- precio_total / (1 + (porcentaje_iva / 100))\niva_por_pagar <- precio_total - base_imponible\nESCRIBIR iva_por_pagar\nFIN";
            } else if (tipo === 'suma') {
                code = "INICIO\nDECIMAL num1\nDECIMAL num2\nDECIMAL resultado\nLEER num1\nLEER num2\nresultado <- num1 + num2\nESCRIBIR resultado\nFIN";
            } else if (tipo === 'resta') {
                code = "INICIO\nDECIMAL num1\nDECIMAL num2\nDECIMAL resultado\nLEER num1\nLEER num2\nresultado <- num1 - num2\nESCRIBIR resultado\nFIN";
            } else if (tipo === 'multiplicacion') {
                code = "INICIO\nDECIMAL num1\nDECIMAL num2\nDECIMAL resultado\nLEER num1\nLEER num2\nresultado <- num1 * num2\nESCRIBIR resultado\nFIN";
            } else if (tipo === 'division') {
                code = "INICIO\nDECIMAL num1\nDECIMAL num2\nDECIMAL resultado\nLEER num1\nLEER num2\nresultado <- num1 / num2\nESCRIBIR resultado\nFIN";
            }
            cargarCodigoEnCompilador(code);
        }

        function generarCodigoPersonalizado() {
            const req = document.getElementById('custom-req').value.trim().toLowerCase();
            if (!req) {
                alert("Por favor especifica qué proceso, texto u operación necesitas realizar.");
                return;
            }

            // Mapa para interpretar números escritos en palabras o dígitos
            const numMap = {
                'un': 1, 'uno': 1, 'una': 1, '1': 1,
                'dos': 2, '2': 2,
                'tres': 3, '3': 3,
                'cuatro': 4, '4': 4,
                'cinco': 5, '5': 5,
                'seis': 6, '6': 6,
                'siete': 7, '7': 7,
                'ocho': 8, '8': 8,
                'nueve': 9, '9': 9,
                'diez': 10, '10': 10
            };

            // Palabras clave numéricas
            const palabrasEnteros = ['edad', 'edades', 'año', 'años', 'cantidad', 'cantidades', 'alumnos', 'estudiantes', 'personas', 'numero', 'numeros', 'número', 'números'];
            const palabrasDecimales = ['precio', 'precios', 'monto', 'montos', 'sueldo', 'sueldos', 'salario', 'salarios', 'nota', 'notas', 'promedio', 'total', 'totales'];

            // 1. DETECCIÓN DE OPERACIONES ARITMÉTICAS EXPLÍCITAS (+, -, *, /)
            const opTokens = [
                { keys: ['resta', 'restas', 'restar', 'menos', '-'], type: 'resta' },
                { keys: ['suma', 'sumas', 'sumar', 'mas', '+'], type: 'suma' },
                { keys: ['multiplicacion', 'multiplicaciones', 'multiplicación', 'multiplicar', 'por', '*'], type: 'mult' },
                { keys: ['division', 'divisiones', 'división', 'dividir', 'entre', '/'], type: 'div' },
                { keys: ['porcentaje', 'porcentajes', 'descuento', 'descuentos', '%'], type: 'porcentaje' },
                { keys: ['iva', 'ivas', 'impuesto', 'impuestos'], type: 'iva' }
            ];

            const words = req.split(/\s+/);
            const opsList = [];
            let tieneIva = false;

            for (let i = 0; i < words.length; i++) {
                const w = words[i].normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9%+]/g, '');
                const foundOp = opTokens.find(item => item.keys.includes(w));

                if (foundOp) {
                    if (foundOp.type === 'iva') {
                        tieneIva = true;
                    } else {
                        let count = 1;
                        if (i > 0) {
                            const prev = words[i - 1].normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]/g, '');
                            if (numMap[prev] !== undefined) count = numMap[prev];
                            else if (!isNaN(parseInt(prev))) count = parseInt(prev);
                        }
                        for (let c = 0; c < count; c++) opsList.push(foundOp.type);
                    }
                }
            }

            // Si hay cálculos matemáticos explícitos
            if (opsList.length > 0 || tieneIva) {
                const decls = [];
                const leers = [];
                const totalVariables = Math.max(opsList.length + 1, 2);

                for (let i = 1; i <= totalVariables; i++) {
                    decls.push(`DECIMAL num${i}`);
                    leers.push(`LEER num${i}`);
                }

                let currentExpr = "num1";
                for (let i = 0; i < opsList.length; i++) {
                    const op = opsList[i];
                    const nextVar = `num${i + 2}`;
                    if (op === 'resta') currentExpr += ` - ${nextVar}`;
                    else if (op === 'suma') currentExpr += ` + ${nextVar}`;
                    else if (op === 'mult') currentExpr += ` * ${nextVar}`;
                    else if (op === 'div') currentExpr += ` / ${nextVar}`;
                    else if (op === 'porcentaje') currentExpr += ` * (${nextVar} / 100)`;
                }

                if (tieneIva) {
                    decls.push("DECIMAL porcentaje_iva");
                    leers.push("LEER porcentaje_iva");
                    currentExpr = `(${currentExpr}) * (porcentaje_iva / 100)`;
                }

                decls.push("DECIMAL resultado");

                const codigoAritmetico = [
                    "INICIO",
                    ...decls,
                    ...leers,
                    `resultado <- ${currentExpr}`,
                    "ESCRIBIR resultado",
                    "FIN"
                ].join("\n");

                cargarCodigoEnCompilador(codigoAritmetico);
                return;
            }

            // 2. DETECTOR UNIVERSAL SEGURO DE VARIABLES
            let cantidad = 1;

            // Detectar la cantidad solicitada
            const matchNum = req.match(/(\d+|un|uno|una|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez)/i);
            if (matchNum) {
                const keyNum = matchNum[1].toLowerCase();
                cantidad = numMap[keyNum] || parseInt(keyNum) || 1;
            }

            // Determinar tipo de dato
            let tipoDato = "TEXTO";
            if (palabrasEnteros.some(p => req.includes(p))) {
                tipoDato = "ENTERO";
            } else if (palabrasDecimales.some(p => req.includes(p))) {
                tipoDato = "DECIMAL";
            }

            // Filtrar palabras comunes y aislar términos alfabéticos limpios
            const stopwords = ['leer', 'una', 'un', 'unos', 'unas', 'cadena', 'de', 'letras', 'letra', 'el', 'la', 'los', 'las', 'pedir', 'ingresar', 'solicitar', 'realizar', 'proceso', 'calculo', 'cálculo', 'que', 'necesitas'];
            
            let palabrasLimpias = [];
            words.forEach(w => {
                // Dejar únicamente letras a-z
                let clean = w.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z]/g, '');
                
                // Validar que sea un nombre seguro (no vacío, no stopword, no número)
                if (clean.length > 0 && !stopwords.includes(clean) && numMap[clean] === undefined) {
                    clean = clean.replace(/(es|s)$/i, ''); // quitar plural
                    if (clean.length > 0) {
                        palabrasLimpias.push(clean);
                    }
                }
            });

            // Asignar un nombre válido garantizado que empiece con letra
            let nombreEntidad = "dato";
            if (palabrasLimpias.length > 0) {
                nombreEntidad = palabrasLimpias[0];
            } else if (tipoDato === "ENTERO") {
                nombreEntidad = "edad";
            } else if (tipoDato === "DECIMAL") {
                nombreEntidad = "monto";
            } else {
                nombreEntidad = "cadena";
            }

            const decls = [];
            const leers = [];
            const escribirs = [];

            for (let i = 1; i <= cantidad; i++) {
                const varName = cantidad === 1 ? nombreEntidad : `${nombreEntidad}${i}`;
                decls.push(`${tipoDato} ${varName}`);
                leers.push(`LEER ${varName}`);
                escribirs.push(`ESCRIBIR ${varName}`);
            }

            const codigoGenerado = [
                "INICIO",
                ...decls,
                ...leers,
                ...escribirs,
                "FIN"
            ].join("\n");

            cargarCodigoEnCompilador(codigoGenerado);
        }

        function renderASTTreeHTML(nodes) {
            if (!nodes || nodes.length === 0) return "<i>Sin estructura de Árbol Sintáctico</i>";
            let html = "";
            nodes.forEach(node => {
                html += `<div class="tree-node">`;
                html += `<div class="node-chip">${node.val}</div>`;
                if (node.children && node.children.length > 0) {
                    node.children.forEach(child => {
                        html += `<div class="tree-node"><div class="node-chip leaf">${child.val}</div></div>`;
                    });
                }
                html += `</div>`;
            });
            return html;
        }

        async function ejecutar() {
            const outDiv = document.getElementById('out');
            const debugDiv = document.getElementById('debug');
            const tabDebugDiv = document.getElementById('tab-debug-output');
            const astTreeDiv = document.getElementById('ast-tree');
            const astTreeFullDiv = document.getElementById('ast-tree-full');

            outDiv.textContent = "";
            debugDiv.textContent = "";
            if (tabDebugDiv) tabDebugDiv.textContent = "";
            astTreeDiv.innerHTML = '<span style="color:#888; font-size:12px;"><i>Iniciando análisis...</i></span>';
            if (astTreeFullDiv) astTreeFullDiv.innerHTML = '<span style="color:#888; font-size:13px;"><i>Iniciando análisis...</i></span>';

            outDiv.style.color = '#00d2ff';
            outDiv.textContent = "🔄 Procesando ejecución...";

            const code = document.getElementById('code').value;
            const inputs = [];

            const lineas = code.split('\n');
            for (let line of lineas) {
                let trimmed = line.trim();
                let match = trimmed.match(/^LEER\s+(.+)$/i);
                if (match) {
                    let varName = match[1].trim();
                    let userVal = prompt(`Ingrese el valor para la variable '${varName}':`);
                    
                    if (userVal === null) {
                        inputs.push("__CANCELLED__");
                        break;
                    } else {
                        inputs.push(userVal);
                    }
                }
            }

            try {
                const res = await fetch('/run', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ code: code, inputs: inputs })
                });

                const data = await res.json();
                lastExecutionData = data;

                if (data.status === 'ok') {
                    outDiv.style.color = '#6bf2b5';
                    outDiv.textContent = data.outputs.join('\n');

                    const renderedTree = renderASTTreeHTML(data.ast_nodes);
                    astTreeDiv.innerHTML = renderedTree;
                    if (astTreeFullDiv) astTreeFullDiv.innerHTML = renderedTree;

                    const debugText = "✅ Análisis Léxico/Sintáctico superado sin errores.\n✅ Árbol sintáctico estructurado generado exitosamente.";
                    debugDiv.style.color = '#6bf2b5';
                    debugDiv.textContent = debugText;
                    if (tabDebugDiv) {
                        tabDebugDiv.style.color = '#6bf2b5';
                        tabDebugDiv.textContent = debugText + "\n✅ Estado: Ejecución completada.";
                    }
                } else {
                    const errMsg = "❌ " + data.error;
                    outDiv.style.color = '#ff5555';
                    outDiv.textContent = errMsg;
                    debugDiv.style.color = '#ff5555';
                    debugDiv.textContent = errMsg;
                    
                    if (tabDebugDiv) {
                        tabDebugDiv.style.color = '#ff5555';
                        tabDebugDiv.textContent = errMsg;
                    }

                    const errTreeHTML = `<span style="color:#ff5555; font-size:13px; font-weight:700;">❌ Ejecución abortada por error sintáctico/semántico. No se generó el árbol completo.</span>`;
                    astTreeDiv.innerHTML = errTreeHTML;
                    if (astTreeFullDiv) astTreeFullDiv.innerHTML = errTreeHTML;

                    renderizarTablasDinamicas();
                }
            } catch (err) {
                lastExecutionData = null;
                outDiv.style.color = '#ff5555';
                outDiv.textContent = "Error de comunicación con el servidor.";
            }
        }

        function renderizarTablasDinamicas() {
            const sintaxisTbody = document.getElementById('sintaxis-dynamic-rows');
            const tokensTbody = document.getElementById('tokens-dynamic-rows');
            const gicTbody = document.getElementById('gic-dynamic-rows');
            const gicValuesTbody = document.getElementById('gic-values-dynamic-rows');
            const consoleProcTbody = document.getElementById('console-proc-dynamic-rows');

            if (lastExecutionData) {
                if (lastExecutionData.sintaxis_descriptiva && sintaxisTbody) {
                    let html = "";
                    lastExecutionData.sintaxis_descriptiva.forEach(stx => {
                        html += `<tr>
                            <td style="color: var(--accent-cyan); font-weight: 700; text-align: center;">Línea ${stx.linea}</td>
                            <td style="color: #6bf2b5;"><code>${stx.codigo}</code></td>
                            <td>${stx.funcion}</td>
                            <td class="${stx.estado === 'Correcto' ? 'status-ok' : 'status-error'}" style="text-align: center;">${stx.estado}</td>
                            <td style="${stx.estado === 'Error' ? 'color:#ff5555; font-weight:bold;' : ''}">${stx.explicacion}</td>
                            <td style="color: var(--accent-cyan);"><code>${stx.sintaxis_correcta}</code></td>
                        </tr>`;
                    });
                    sintaxisTbody.innerHTML = html;
                }

                if (tokensTbody) {
                    let html = "";
                    if (lastExecutionData.status === 'error' && (!lastExecutionData.tokens || lastExecutionData.tokens.length === 0)) {
                        html = `<tr><td colspan="4" style="text-align: center; color: #ff5555; padding: 20px; font-weight: 700;"><i>❌ Ejecución abortada por error. No se generó la tabla de tokens.</i></td></tr>`;
                    } else {
                        lastExecutionData.tokens.forEach(tok => {
                            html += `<tr>
                                <td style="color: var(--accent-cyan); text-align: center;">Línea ${tok.line}</td>
                                <td style="color: var(--accent-cyan); font-weight: 600;">${tok.type}</td>
                                <td style="color: #6bf2b5;"><code>${tok.value}</code></td>
                                <td>${tok.tech_desc}</td>
                            </tr>`;
                        });
                    }
                    tokensTbody.innerHTML = html;
                }

                if (gicTbody) {
                    let html = "";
                    if (lastExecutionData.status === 'error' && (!lastExecutionData.gic || lastExecutionData.gic.length === 0)) {
                        html = `<tr><td colspan="4" style="text-align: center; color: #ff5555; padding: 20px; font-weight: 700;"><i>❌ Ejecución abortada por error sintáctico/ejecución.</i></td></tr>`;
                    } else {
                        lastExecutionData.gic.forEach(item => {
                            html += `<tr>
                                <td style="color: var(--accent-cyan); font-weight: 700;">${item.elemento}</td>
                                <td style="color: #00d2ff;"><code>${item.regla}</code></td>
                                <td style="color: #6bf2b5;"><code>${item.subcadena}</code></td>
                                <td>${item.desc}</td>
                            </tr>`;
                        });
                    }
                    gicTbody.innerHTML = html;
                }

                if (gicValuesTbody) {
                    let html = "";
                    if (lastExecutionData.status === 'error' && (!lastExecutionData.gic_values || lastExecutionData.gic_values.length === 0)) {
                        html = `<tr><td colspan="6" style="text-align: center; color: #ff5555; padding: 20px; font-weight: 700;"><i>❌ Ejecución abortada por error sintáctico/ejecución.</i></td></tr>`;
                    } else {
                        lastExecutionData.gic_values.forEach(v => {
                            let procedimientoHtml = v.explicacion_adaptada.replace(/\n/g, '<br>');
                            html += `<tr>
                                <td style="color: var(--accent-cyan);">${v.linea}</td>
                                <td style="color: #00d2ff;"><code>${v.regla_gic}</code></td>
                                <td><code>${v.instruccion}</code></td>
                                <td style="color: #6bf2b5;"><code>${v.valor_ingresado}</code></td>
                                <td style="color: #6bf2b5; font-weight: 700;"><code>${v.salida_consola}</code></td>
                                <td style="font-family: 'Fira Code', monospace; font-size: 11px; line-height: 1.4;">${procedimientoHtml}</td>
                            </tr>`;
                        });
                    }
                    gicValuesTbody.innerHTML = html;
                }

                if (consoleProcTbody) {
                    let html = "";
                    if (lastExecutionData.status === 'error' && (!lastExecutionData.console_proc || lastExecutionData.console_proc.length === 0)) {
                        html = `<tr><td colspan="4" style="text-align: center; color: #ff5555; padding: 20px; font-weight: 700;"><i>❌ Ejecución abortada por error.</i></td></tr>`;
                    } else {
                        lastExecutionData.console_proc.forEach(p => {
                            html += `<tr>
                                <td style="color: var(--accent-cyan); font-weight: 700;">${p.paso}</td>
                                <td style="color: #00d2ff;"><code>${p.operacion}</code></td>
                                <td style="color: #6bf2b5;"><code>${p.valor}</code></td>
                                <td>${p.resultado}</td>
                            </tr>`;
                        });
                    }
                    consoleProcTbody.innerHTML = html;
                }
            }
        }

        function enviarTicket() {
            const confirmBox = document.getElementById('soporte-confirm');
            confirmBox.style.display = 'block';
            confirmBox.style.color = '#6bf2b5';
            confirmBox.innerHTML = '✔ Ticket enviado con éxito. El equipo de soporte se pondrá en contacto pronto.';
            document.getElementById('sup-nombre').value = '';
            document.getElementById('sup-email').value = '';
            document.getElementById('sup-mensaje').value = '';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/run', methods=['POST'])
def run():
    data = request.json
    code = data.get('code', '')
    inputs = data.get('inputs', [])

    try:
        tokens = lexer(code)
        tokens_data = [
            {
                'type': t.type, 
                'value': str(t.value), 
                'line': t.lineno,
                'tech_desc': generar_descripcion_sin_es(t)
            } for t in tokens
        ]

        interpreter = WebInterpreter(tokens, inputs)
        interpreter.run()

        sintaxis_data = analizar_sintaxis_descriptiva(code)

        return jsonify({
            'status': 'ok',
            'outputs': interpreter.outputs,
            'ast_nodes': interpreter.ast_nodes,
            'tokens': tokens_data,
            'sintaxis_descriptiva': sintaxis_data,
            'gic': interpreter.gic_log,
            'gic_values': interpreter.gic_output_values_log,
            'console_proc': interpreter.console_proc_log
        })
    except Exception as e:
        error_msg = str(e)
        is_lexical = "Error Léxico" in error_msg

        return jsonify({
            'status': 'error',
            'error': error_msg,
            'is_lexical_error': is_lexical,
            'tokens': [],
            'sintaxis_descriptiva': analizar_sintaxis_descriptiva(code, error_msg),
            'ast_nodes': [],
            'gic': [],
            'gic_values': [],
            'console_proc': []
        })

if __name__ == '__main__':
    threading.Timer(1.2, lambda: webbrowser.open_new('http://127.0.0.1:5000/')).start()
    app.run(debug=False, port=5000)