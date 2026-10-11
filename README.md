# PSS/E Dynamics Models - Control Block Editor

Una herramienta gráfica interactiva basada en **Python y PyQt5** para el diseño de diagramas de bloques de control y la generación automática de subrutinas **Fortran 77/90** para modelos de dinámica definidos por el usuario (User-Defined Dynamic Models) en el simulador de potencia **Siemens PSS/E**.

---

## 🚀 ¿Qué hace este proyecto?

En simulaciones de estabilidad transitoria con PSS/E, los controladores de generadores, excitadores (AVR), gobernadores (GOV), estabilizadores de sistemas de potencia (PSS) y parques eólicos/solares se programan habitualmente mediante subrutinas Fortran estructuradas por Modos de ejecución (`MODE 1` a `MODE 8`).

Esta herramienta permite:
1. **Diseñar visualmente diagramas de bloques de control**:
   - Agregar bloques de control típicos (Ganancias, Integradores, Filtros Lag de 1er orden, Washout, Lead-Lag, PI, PID, Sumadores).
   - Definir señales de entrada (`INPUT`) y salida (`OUTPUT`) vinculadas a variables y constantes de red/máquina de PSS/E (`VOLT`, `EFD`, `VREF`, `PELEC`, `CON`, `VAR`, etc.).
   - Conectar puertos gráficamente mediante curvas cúbicas con flechas indicadoras de flujo de señal.
   - Configurar límites (**Windup** y **Non-Windup**) con cotas mínimas y máximas en cada bloque.
2. **Resolver el orden topológico de cálculo**:
   - Aplica el algoritmo de Kahn sobre el grafo dirigido para ordenar la ejecución de las ecuaciones en la subrutina Fortran sin dependencias circulares no resueltas.
3. **Generar código Fortran estandarizado de PSS/E**:
   - `MODE 1`: Inicialización del modelo (propagación inversa desde las condiciones iniciales del flujo de carga).
   - `MODE 2`: Cálculo de derivadas de estado (`DSTATE`).
   - `MODE 3`: Cálculo de variables de salida algebraicas (`VAR`).
   - `MODE 4`: Reserva de espacio para variables de estado integradas (`NINTEG = MAX(NINTEG, K + n)`).
   - `MODE 8`: Descripción de parámetros en constantes (`CON_DSCRPT`).
4. **Inspeccionar y editar asignaciones PSS/E en tiempo real**:
   - Mapeo automático de arreglos estándar: `CON` (base $J$), `ICON` (base $M$), `STATE` (base $K$) y `VAR` (base $L$).
   - Vista previa con resaltado de sintaxis Fortran en tiempo real y exportación directa a archivos `.f` o `.f90`.

---

## 📂 Estructura del Proyecto

El código sigue una arquitectura **MVC (Modelo - Vista - Controlador)** modular y desacoplada:

```plaintext
PSSEDynamicsModels/
│
├── main.py                     # Punto de entrada de la aplicación GUI (Ventana principal y docks)
├── sexs.json                   # Ejemplo de modelo de excitación simplificado (SEXS) serializado
├── SEXS.f90                    # Código Fortran de referencia generado para SEXS
├── Q_CNTRL.f90                 # Ejemplo de controlador de reactivos en Fortran
├── docs/
│   └── ARRAYS.txt              # Documentación de arreglos y variables dinámicas de PSS/E
│
└── app/
    ├── codegen.py              # Motor de generación de código Fortran y orden topológico (Kahn)
    ├── TEMPLATE.f90            # Plantilla base Fortran para la subrutina PSS/E
    │
    ├── models/                 # Modelos de datos y estructuras de estado
    │   ├── __init__.py
    │   ├── core.py             # Elementos gráficos base (Port y Connection con curvas Bézier)
    │   └── diagram.py          # DiagramModel, BlockModel y ConnectionModel (serializables a JSON)
    │
    ├── views/                  # Componentes de interfaz gráfica (UI)
    │   ├── __init__.py
    │   ├── view.py             # GraphicsView interactivo (zoom, selección, conexiones)
    │   ├── code_preview.py     # Widget con resaltado de sintaxis Fortran y exportación
    │   └── allocation_table.py # Widget de asignación de variables (J+offset, K+offset, etc.)
    │
    ├── controllers/            # Lógica de negocio y orquestación
    │   ├── __init__.py
    │   └── diagram_controller.py # Controlador que gestiona DiagramModel, persistencia y estado
    │
    └── blocks/                 # Catálogo de bloques de control dinámicos
        ├── __init__.py
        ├── base.py             # BaseBlock: clase base gráfica, configuración y métodos estáticos de modo
        ├── signal_mixin.py     # Mixin para configuración de señales PSS/E (BUS, MACHINE, INDEX)
        ├── input.py            # Bloque de entrada (lectura de arreglos PSS/E o señales de máquina)
        ├── output.py           # Bloque de salida (escritura de arreglos o inyección de variables)
        ├── gain.py             # Bloque de ganancia proporcional (K)
        ├── sum.py              # Bloque sumador/restador multi-entrada
        ├── integrator.py       # Bloque integrador puro (1 / sTi)
        ├── lag.py              # Filtro de primer orden (Ki / (1 + sTi))
        ├── washout.py          # Filtro pasa-altos / Washout (Ki*sTi / (1 + sTi))
        ├── lead_lag.py         # Bloque adelanto-atraso (Ki * (1 + sT1) / (1 + sT2))
        ├── pi.py               # Controlador Proporcional-Integral (Kp + Ki / s)
        └── pid.py              # Controlador PID con filtro derivativo en Td
```

---

## 🛠️ Requisitos e Instalación

### Requisitos previos
- **Python 3.9+** (probado y compatible hasta Python 3.14).
- **PyQt5**.

### Instalación de dependencias
```bash
pip install PyQt5
```

---

## 💻 Uso de la Aplicación

### Ejecución
Para iniciar el editor:
```bash
python main.py
```

### Flujo de trabajo básico
1. **Configuración Global**:
   - En el panel de **Propiedades**, asigna el **Nombre de la Subrutina** (por ejemplo `SEXS`) y selecciona el **Tipo de Modelo PSS/E** (como `USRMDL`, `USRLOD`, etc.).
2. **Construir el Diagrama**:
   - Usa el menú **Bloques** para insertar bloques de control o bloques de señales (`INPUT`/`OUTPUT`).
   - Conecta un bloque arrastrando con el ratón desde el puerto de salida rojo hasta el puerto de entrada verde de otro bloque.
3. **Parametrizar Bloques**:
   - Haz doble clic sobre un bloque o selecciónalo para ajustar sus ganancias, constantes de tiempo y límites (*Windup* / *Non-Windup*).
4. **Guardar / Cargar**:
   - Guarda tu diseño en formato JSON desde **Archivo > Guardar Diagrama**. Puedes abrir ejemplos como `sexs.json`.
5. **Generar y Exportar Código**:
   - Selecciona **Archivo > Generar Código Fortran** (o activa la vista previa desde el menú **Ver > Vista Previa de Código Fortran**).
   - Podrás revisar el código generado, copiarlo al portapapeles o exportarlo como archivo `.f` / `.f90` listo para compilar con el entorno de PSS/E.
