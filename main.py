from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.schema import SystemMessage
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
import config
from langchain.document_loaders import GitLoader
from langchain.agents import Tool
from langchain.agents import AgentType
from langchain.memory import ConversationBufferMemory
from langchain import OpenAI
from langchain.utilities import SerpAPIWrapper
from langchain.agents import initialize_agent
from langchain.document_loaders import WebBaseLoader
from git import Repo
from msrest.authentication import BasicAuthentication
from azure.devops.connection import Connection
from msrestazure.azure_active_directory import AADTokenCredentials
from azure.devops.connection import Connection
from azure.devops.exceptions import AzureDevOpsServiceError
import os
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
import json
import config
import git


def copy_file_to_txt(input_file, output_file):
    with open(input_file, 'r') as file:
        content = file.read()

    with open(output_file, 'w') as output:
        output.write(content)

    print(f"El archivo {input_file} se ha copiado en {output_file} correctamente.")

def obtener_contenido_archivo(nombre_archivo):
    with open(nombre_archivo, 'r') as archivo:
        contenido = archivo.read()
    return contenido







api = config.OPENAI_API_KEY 
project_name= config.project_name
pipeline_id = config.pipeline_id
# Fill in with your personal access token and org URL
personal_access_token = config.PAT
organization_url = config.organization_url

logBuild= config.logBuild
logTest= config.logTest


 # Create a connection to the org
credentials = BasicAuthentication('', personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)









'''
#TENGO EL REPO
loader = GitLoader(
    clone_url="https://dev.azure.com/Tailspin0523388/_git/terraform",
    repo_path="./REPOSITORIO/",
    branch="master",
     #file_filter=lambda file_path: file_path.endswith("Product.cs"),
)

data = loader.load()

'''


## CLONAMOS EL REPO

repository_url = 'https://Tailspin0523388@dev.azure.com/Tailspin0523388/terraform/_git/terraform'

# Ruta local donde se clonará el repositorio
local_repo_path = 'REPOSITORIO'

# Verifica si el repositorio ya está clonado
if os.path.exists(local_repo_path):
    repo = git.Repo(local_repo_path)
    print("Repositorio existente encontrado.")
else:
    # Clona el repositorio utilizando el token de acceso personal
    repo = git.Repo.clone_from(repository_url, local_repo_path, branch="terraform", env={
        "GIT_ASKPASS": "echo",
        "VSS_NUGET_EXTERNAL_FEED_ENDPOINTS": '{"endpointCredentials":[{"endpoint":"https://pkgs.dev.azure.com/Tailspin0523388/_packaging/tu-feed/nuget/v3/index.json","username":"laura.plaza@babelgroup.com","password":"'+personal_access_token+'"}]}'})
    print("Repositorio clonado.")






#PASO A TXT EL ARCHIVO QUE QUIERO

input_file = 'REPOSITORIO/src/PartsUnlimited.Models/Product.cs'  # Reemplaza 'tu_archivo.txt' por la ruta del archivo que deseas copiar.
output_file = 'codigo.txt'
copy_file_to_txt(input_file, output_file)





# GUARDO EN UN STRING EL TXT
nombre_archivo = 'codigo.txt'  # Reemplaza 'archivo.txt' con el nombre del archivo que deseas leer.
codigo = obtener_contenido_archivo(nombre_archivo)
print(codigo)



prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="Eres una IA hablando con un programador, la respuesta dada debe ser únicamente código modificado, no  pongas nada de texto ni comentarios"), # The persistent system prompt
    MessagesPlaceholder(variable_name="chat_history"), # Where the memory will be stored.
    HumanMessagePromptTemplate.from_template("{human_input}"), # Where the human input will injectd
])
    
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

llm = ChatOpenAI(model_name="gpt-3.5-turbo",temperature=.7,openai_api_key=api)

chat_llm_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=True,
    memory=memory,
)

#print(chat_llm_chain.run(human_input=tarea + "Este es el código:" + "\n---\n" + codigo + "\n---\n"))




contador = 0
correcto = False

tarea= "Añademe varios comentario indicandome que crees que significa cada variable del código.:"
#while contador <=3 and correcto == False :
respuesta= chat_llm_chain.run(human_input=tarea + "Este es el código:" + "\n---\n" + codigo + "\n---\n")
print(respuesta)

#Iteramos mientras la respuesta no sea válida o mientras el contador sea menor que 3 para que no itere en un bucle infinito
while correcto == False or contador < 3 :
    # pasar respuesta a input file 
    with open (input_file,"w") as archivo :
        archivo.write(respuesta)


    # se sube al repositorio los cambios y se hace un commit y push   
    repo.git.add('.')
    commit_message = "Cambios automáticos"
    commit = repo.index.commit(commit_message)
    #guardamos el hash
    hash_full = commit.hexsha 
    repo.git.push('origin', "terraform")
    print("Hash completo del commit: " + hash_full)


    #esperamos a que se ejecute el pipeline al completo 6 minutos
    time.sleep(config.tiempoEspera)



    #OBTENEMOS LOS BUILDS
    core_client = connection.clients.get_core_client()
    # Get a list of builds (executions) for the pipeline
    builds = pipelines_client.get_builds(project=project_name, definitions=[pipeline_id])


#  iteramos por los builds hasta que encontremos el nuestro (coinciden los hash de los commit)
# si si el estado es suceeded, ha sido exitosos y salimos del bucle y fin del flujo
# en otro caso, 
    #si  hay un error en el build se le pasa a chatgpt con su respectivo mensaje y volvemos a iterar
    # si hay un  error en el test se le pasa a chatgpt con su respectivo mensaje y volvemos a iterar
    encontrado = False
    i = 0 
    while encontrado == False : 
        build = builds[i]
        if build.source_version ==  hash_full :
            if build.result == "succeeded" :
                correcto = True
                print("CODIGO MODIFICADO CON ÉXITO")
            else : 
                urlLogBuild = getattr(pipelines_client.get_build_logs(build_id=build.id, project=project_name)[logBuild-1],"url")
                urlLogTest = getattr(pipelines_client.get_build_logs(build_id=build.id, project="terraform")[logTest-1],"url")
                tarea = "El código que nos has dado tiene un error en uno de los siguientes codigos  : . Corrígelo : " +  urlLogBuild + " " + urlLogTest
                respuesta= chat_llm_chain.run(human_input=tarea  + "\n---\n")
                print(respuesta)
            encontrado = True
        i = i +1

    contador = contador + 1




    ## hacer un commit del pipeline
    ## por tanto se lanza el pipeline
    ##  tener log del pipeline
    ## if ha pasado todas las pruebas:
        # correcto= true
    #else:  
        # if error compilacion :
            # tarea= "El código que me has dado : " + respuesta + " tiene errores de compilación. solucionalo"
        #else error pruebas:
            # tarea= "El código que me has dado : " + respuesta + " no ha pasado las pruebas"

        #contador = contador +1





'''
# Create a connection to the org
credentials = BasicAuthentication('', personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)
# Get a client (the "core" client provides access to projects, teams, etc)
core_client = connection.clients.get_core_client()


# Get a list of builds (executions) for the pipeline
builds = pipelines_client.get_builds(project=project_name, definitions=[pipeline_id])
'''

