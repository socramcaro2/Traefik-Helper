import logging, time, json
from os import path, makedirs, walk, system, name
from sys import exit, executable
try:
    from rich.logging import RichHandler
    from rich import print
    from rich.console import Console
    from rich.table import Table
except ImportError:
    import subprocess
    subprocess.check_call([executable, "-m", "pip", "install", "rich"])
    from rich.logging import RichHandler
    from rich.console import Console
    from rich.table import Table
    from rich import print

console = Console()

DirConfYaml, DirStaticJson, DirVarJson, DirConfigJson = ' ', path.join(path.dirname(__file__), 'config_data', 'static.json'), path.join(path.dirname(__file__), 'config_data', 'variables.json'), path.join(path.dirname(__file__), 'config_data', 'config.json')
class NoConfigDir(Exception):
    pass

# Configuracion de Rich Handler con los parámetros correctos
handler = RichHandler(
    rich_tracebacks=False,      # Para combinar los mensajes que ocurren en el mismo segundo, por eso en false
    omit_repeated_times=False,  # Para no mostrar la hora si ocurre a la vez, por eso en false
    show_time=True,             # Mostrar la hora
    show_level=True,            # Mostrar el nivel (debug, info, etc)
    show_path=False,            # Mostrar la ruta del archivo donde se ejecuta la linea de codigo a la derecha, para debug solo
    markup=True                 # Habilitar marcado de Rich para colores
)

# Configuración básica de logging
logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%X]", 
    handlers=[handler]
)
log = logging.getLogger("rich")

#funcion para tener la hora como los logs para usarla con las barras de rich
def hora():
    return f"[{time.strftime('%H:%M:%S')}]"

#definir diccionarios y variables predefinidas para dumpear
def FileCheck():
    user_input_name, user_input_domain = '', ''
    DirConfYaml, DirStaticJson, DirVarJson, DirConfigJson = ' ', path.join(path.dirname(__file__), 'config_data', 'static.json'), path.join(path.dirname(__file__), 'config_data', 'variables.json'), path.join(path.dirname(__file__), 'config_data', 'config.json')
    class NoConfigDir(Exception):
        pass
    
    error_counter = 0

    config_dump = {
    }
    variables_dump = {
    }
    static_dump = {
        'DirConf.yaml' : DirConfYaml,
        'DirVar.json' : DirVarJson,
        'DirStatic.json' : DirStaticJson,
        'DirConfig.json' : DirConfigJson,
        
        'routers' : '''
    {user_input_name}:
      entryPoints:
        - "https"
      rule: "Host('{user_input_domain}')"
      middlewares:
        - default-headers
        - https-redirectscheme
      tls: {{}}
      service: {user_input_name}''', 
      
        'services' : '''
    {user_input_name}:
      loadBalancer:
        servers:
          - url: "{user_input_ip}"
        passHostHeader: true
        ''',
        
        'middlewares' : '''  middlewares:
        https-redirectscheme:
          redirectScheme:
            scheme: https
            permanent: true
        default-headers:
          headers:
            frameDeny: true
            browserXssFilter: true
            contentTypeNosniff: true
            forceSTSHeader: true
            stsIncludeSubdomains: true
            stsPreload: true
            stsSeconds: 15552000
            customFrameOptionsValue: SAMEORIGIN
            customRequestHeaders:
              X-Forwarded-Proto: https''',
              
        'whitelist' : '''    default-whitelist:
          ipAllowList:
            sourceRange:
            - "10.0.0.0/8"
            - "192.168.0.0/16"
            - "172.16.0.0/12"''',
            
            'secured' : '''    secured:
          chain:
            middlewares:
            - default-whitelist
            - default-headers'''

    }
    
    # chequeo de los archivos y directorios para la persistencia
    directory = path.dirname(__file__)
    ruta_subcarpeta = path.join(directory, 'config_data')

    try: # creo la carpeta de trabajo
        makedirs(ruta_subcarpeta)
        log.warning('[[bold yellow]CREATED[/ bold yellow]] Working directory ')
    except FileExistsError:
        log.info('[[bold green]OK[/ bold green]] Working directory ')
    except PermissionError:
        log.critical('[[bold RED]ERROR[/bold RED]] No permission to work here ')
        error_counter += 1


    try: #intenta conseguir el directorio guardado del config.yaml
        with open(path.join(ruta_subcarpeta, 'static.json'), 'r') as f:
            static = json.load(f)
            if 'config.yaml' in static['DirConf.yaml'] and path.exists(static['DirConf.yaml']):
                log.info(f'[[bold green]OK[/ bold green]] Found config.yaml')
            else:
                raise NoConfigDir()


    except (FileNotFoundError, json.decoder.JSONDecodeError, NoConfigDir):

        log.warning(f'[[bold yellow]ERROR[/bold yellow]] Could not import config.yaml directory, missing or corrupted file?')
        def buscar_archivo(nombre_archivo, directorio_base="/"): # buscar archivo indicado
            for directorio_actual, subcarpetas, ArchivosEnCarpeta in walk(directorio_base):
                if nombre_archivo in ArchivosEnCarpeta:
                    return directorio_actual  # Devuelve la ruta de la carpeta del archivo indicado
            return None  # Si no lo encuentra, devuelve None

        with console.status(f'[cyan][/cyan] searching config.yaml'):
            global ruta
            ruta = buscar_archivo('traefik.yaml')

    
        DirConfYaml = buscar_archivo('config.yaml', ruta)
        DirConfYaml = path.join(DirConfYaml, 'config.yaml')
        static_dump.update({'DirConf.yaml' : DirConfYaml})
        ruta_static_json = path.join(ruta_subcarpeta, 'static.json')
        with open(ruta_static_json, 'w') as f: # ya se que la primera vez que se ejecute el programa se ejecutara dos veces, no encuentro otra manera mas optima
            json.dump(static_dump, f, indent=4)
        log.info(f'[[bold green]OK[/bold green]] Config.yaml found and saved')
        log.warning(f'[[bold yellow]CREATED[/bold yellow]] static.json created or modified')

    ARCHIVOS_PARA_CHEQUEAR= {
        'config.json' : config_dump,
        'variables.json' : variables_dump
    }

    for archivo, dumping in ARCHIVOS_PARA_CHEQUEAR.items(): # se va alternando al mismo tiempo el archivo y su contenido predefinido para que al crear los archivos tenga lo correcto, solo cuando se crean por primera vez
        RutaArchivo = path.join(ruta_subcarpeta, archivo)
        if not path.exists(RutaArchivo):
            try:
                with open(RutaArchivo, 'w') as f:
                    log.warning(f'[[bold yellow]CREATED[/ bold yellow]] {archivo} has been created ')
                    json.dump(dumping, f, indent=4)
            except PermissionError:
                log.critical('[[bold RED]ERROR[/ bold RED]] No permission to work here ')
                error_counter += 1
        else:
            log.info(f'[[bold green]OK[/ bold green]] {archivo} ')




    if error_counter >= 1:
        log.critical('[[bold red]ERROR[/ bold red]] [cyan]File integrity check[/cyan] ')
        exit(500) 
    else:
        log.info('[[bold green]OK[/ bold green]] [cyan]File integrity check[/cyan] ') 
    
# fin del chequeo
FileCheck()
# importar configuraciones

JSONS_FILES_IMPORT = {
    'config' : 'config.json',
    'static' : 'static.json',
    'variables' : 'variables.json'
}

for name, name_json in JSONS_FILES_IMPORT.items(): # nombre en este caso tomaria los valores de la columna de la izquierda mientras que nombre_json los de la derecha, y luego se añadirian los config como una extension del diccionario
    ruta = path.join(path.join(path.dirname(__file__), 'config_data'), name_json)
    try:
        with open(ruta, 'r') as f:
            JSONS_FILES_IMPORT[name] = json.load(f)
            log.info(f'[[bold green]OK[/ bold green]] succesfully imported {name_json}')
    except json.decoder.JSONDecodeError:
        log.critical(f'[[bold RED]ERROR[/ bold RED]] Failed to import {name_json}, stopping...')
        exit(500)
        

with open(f'{JSONS_FILES_IMPORT['static']['DirVar.json']}.old', 'w') as f: # copia por si acaso de Variables.json
    json.dump(JSONS_FILES_IMPORT['static'], f, indent=4)
        

log.info('[[bold green]OK[/ bold green]][cyan] Succesfully imported all required files[/cyan]')

#nombrando las variables para hacerlo mas sencillo

config = JSONS_FILES_IMPORT['config']
static = JSONS_FILES_IMPORT['static']
variables = JSONS_FILES_IMPORT['variables']

# Fin del chequeo de todo

# menu seleccion de que hacer
table = Table(title="Traefik helper")

table.add_column("Option", style="yellow", no_wrap=True, justify="center")
table.add_column("What to do", style="purple", justify="center")
table.add_row("1", "Add a new service")
table.add_section()
table.add_row("2", "Delete an existing service")
table.add_section()
table.add_row("3", "Edit current services")
table.add_section()
table.add_row("4", "Change a workload name")
table.add_section()
table.add_row("5", "Check current services")
table.add_section()
table.add_row("6", "Save changes")
table.add_section()
table.add_row("7", "Save and exit")
table.add_section()
table.add_row("8", "Exit without saving")
    
# limpiar consola
def clear_screen():
    system("cls" if name == "nt" else "clear")

#pantalla de informacion de variables.json
def show_info():
    table = Table(title="Traefik helper")

    table.add_column("Option", style="yellow", no_wrap=True, justify="center")
    table.add_column("What to do", style="purple", justify="center")

    for x in variables:
        table.add_row('[bold cyan]workload[/bold cyan]', f'[bold cyan]{x}[/bold cyan]')
        for y, z in variables[x].items():
            table.add_row(y, z)
        table.add_section()
    
    console = Console()
    console.print(table)
    

def workload_edit(change): # para no repetir el mismo codigo he creado una variable que simplemente cambia las restricciones a la hora de seleccionar un workload
    select_workload = ' '
    
    if change == 'edit':
        while select_workload not in variables:
            select_workload = input('workload: ')
            if select_workload not in variables:
                log.warning('[[bold red]ERR[/bold red]] That workload doesnt exist')

    elif change == 'create': 
        select_workload = input('workload: ')
        if select_workload in variables:
            log.warning('[[bold red]ERR[/bold red]] That workload already exists')                   
            workload_edit('create')
        elif not select_workload.strip():
            log.warning('[[bold red]ERR[/bold red]] Cant create an empty workload')        
            workload_edit('create')
    
    else:
        log.debug('has introducido mal la variable')
    
    change_name = input('name: ')
    if not change_name.strip():
        change_name = variables[select_workload]['name']
    
    change_ip = input('ip: ')
    if not change_ip.strip():
        change_ip = variables[select_workload]['ip']
    
    
    change_url = input('url: ')
    if not change_url.strip():
        change_url = variables[select_workload]['domain']
    
    variables.update({
        select_workload : {
            'name' : change_name,
            'ip' : change_ip,
            'domain' : change_url
        }
    })
    
    with open(static['DirVar.json'], 'w') as f:         #  cambiar directorio a la info del diccionario de FileCheck.py
        json.dump(variables, f, indent=4)

def ChangeWorkloadName():
    Select_Workload = ' '
    while Select_Workload not in variables:
        Select_Workload = input('workload: ')
        if Select_Workload not in variables:
            print('Not a correct option')                       # CAMBIAR A UN LOG DE RICH, IMPORTANTE, CAMBIAR A LOG DE RICH, PUESTO ASI EN ARCHIVO DE TESTEO
    New_Name = input('New workload name: ')
    
    SaveDic = variables.pop(Select_Workload)
    variables[New_Name] = SaveDic
    print(variables)

    with open('C:\\proyectos git\\traefik helper\\config_data\\variables.json', 'w') as f:         #  cambiar directorio a la info del diccionario de FileCheck.py
        json.dump(variables, f, indent=4)

def delete_workload():
    Select_Workload = input('Select workload to delete: ')
    if Select_Workload not in variables:
        delete_workload()
    variables.pop(Select_Workload)
    
def Save_To_Yaml():
    user_inputs = []
    for workload in variables:
        for info in variables[workload]:
            user_inputs.append(variables[workload][info])
    
    for name, ip, domain in zip(*[iter(user_inputs)]*3): # aqui basicamente lo que estoy haciendo es ((1, 2, 3), (4, 5, 6), etc)
        config.update({name : {}})
        router_config = static['routers'].format(user_input_name=name, user_input_domain=domain)
        config[name].update({'routers': router_config})
        services_config = static['services'].format(user_input_name=name, user_input_ip=ip)
        config[name].update({'services': services_config})
        
    with open(static['DirConfig.json'], 'w') as f:
        json.dump(config, f, indent=4)
    
    
    
    with open(static['DirConf.yaml'], 'w') as f:
        f.write('http:\n  routers:')
    
    for workload_config in config:
        with open(static['DirConf.yaml'], 'a') as f:
            f.write(config[workload_config]['routers'])
            
    with open(static['DirConf.yaml'], 'a') as f:
        f.write('\n  services:')
    
    for workload_config in config: #tienen que estar separados y no intercalados, por eso uso 2 bucles for
        with open(static['DirConf.yaml'], 'a') as f:
            f.write(config[workload_config]['services'])
    
    with open(static['DirConf.yaml'], 'a') as f:
        f.write(f'{static['middlewares']}\n{static['whitelist']}\n{static['secured']}')
    
    
    
        
def menu_start():
    
    clear_screen()
    console.print(table)    
    
    MenuWhatToDo = input('What you want to do: ')
    clear_screen()
    show_info()
    if MenuWhatToDo == '1':
        workload_edit('create')
    if MenuWhatToDo == '2':
        delete_workload()
    if MenuWhatToDo == '3':
        workload_edit('edit')
    if MenuWhatToDo == '4':
        ChangeWorkloadName()
    if MenuWhatToDo == '5':
        input('Give any input to go back: ')
    if MenuWhatToDo == '6':
        Save_To_Yaml()
    if MenuWhatToDo == '7':
        Save_To_Yaml()
        clear_screen()
        print('[bold]Bye![/bold]')
        exit(1)
    if MenuWhatToDo == '8':
        i = 0
        clear_screen()
        you_sure = input('are you sure you dont want to save? y/n\n')
        while i != 1:
            if you_sure == 'y' or you_sure == 'yes':
                clear_screen()
                print('[bold]Bye![/bold]')
                exit(1)
            elif not you_sure.strip() or you_sure == 'n' or you_sure == 'no':
                i = 1
            else:
                clear_screen()
                print('[bold red]Not a valid option[/bold red], You want to exit without saving?')
                you_sure = input()
    menu_start()

menu_start()