from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
import json

# Fill in with your personal access token and org URL
personal_access_token = 'evzh4lc3o5x3cjx7gbsyvk2uezkx5op7d6inkhx545z6zfq2h4iq'
organization_url = 'https://dev.azure.com/Tailspin0523388'

# Create a connection to the org
credentials = BasicAuthentication('', personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)

# Get a client (the "core" client provides access to projects, teams, etc)
core_client = connection.clients.get_core_client()

# Get information about a specific project by its name
project_name = "terraform"
project = core_client.get_project(project_name)

print("Project Name:", project.name)
print("Description:", project.description)
print("Visibility:", project.visibility)
print("Default Team:", project.default_team.name)
# ... You can access other properties of the project as needed

# Get a client (the "pipelines" client provides access to pipelines, build definitions, etc)
pipelines_client = connection.clients.get_build_client()

# Get information about a specific pipeline by its ID
pipeline_id = 37  # Replace this with the actual ID of your pipeline
pipeline = pipelines_client.get_definition(project=project_name, definition_id=pipeline_id)

print("Pipeline Name:", pipeline.name)
print("Repository URL:", pipeline.repository.url)
print("Default Branch:", pipeline.repository.default_branch)
print("Build Definition ID:", pipeline.id)
# ... You can access other properties of the pipeline as needed

# Get a list of builds (executions) for the pipeline
builds = pipelines_client.get_builds(project=project_name, definitions=[pipeline_id])

# Print the information of each build
print("Builds:")
for build in builds:
    print(build)
    print("Build ID:", build.id)
    print("Build Number:", build.build_number)
    print("Status:", build.result)
    print("Started On:", build.start_time)
    print("Finished On:", build.finish_time)
    print("Source Branch:", build.source_branch)
    # ... You can access other properties of the build as needed
    print("---")

    # Get the logs for the build with ID 377
print(pipelines_client.get_build_logs(build_id=377, project="terraform"))




for o in pipelines_client.get_build_logs(build_id=377, project="terraform") : 
    print(o)
    print("Log  : ")
    print(getattr(o,"url"))


#https://dev.azure.com/Tailspin0523388/terraform/_apis/build/builds/377/logs?api-version=7.0



#recorrer cada log y si alguno contiene la cadena 'Error' entonces está mal, se sale del bucle y vuelve a preguntarle a chatgpt

#logs= 
#while !error :



#git rev-parse HEAD
#source_version DEL BUILD