import typer
import subprocess

app = typer.Typer()

@app.command()
def build():
    subprocess.run(["docker-compose", '-f', "build/docker/docker-compose.yml", "up", "--build"])
@app.command()
def down():
    subprocess.run(["docker-compose",'-f',"build/docker/docker-compose.yml", "down"]) #, "--rmi" ,"all"

@app.command()
def clean():
    subprocess.run("docker rmi -f $(docker images -q)", shell=True)
    subprocess.run("docker rm -f $(docker ps -qa)", shell=True)

@app.command()
def clean_cache():
    subprocess.run(["docker", "system", "prune", "--all"])

@app.command()
def clean_volumes():
    subprocess.run("docker volume rm $(docker volume ls -q)", shell=True)

@app.command()
def help():
    typer.echo("Available commands:")
    typer.echo("  build       - Build and start the Docker containers")
    typer.echo("  down        - Stop and remove the Docker containers")
    typer.echo("  clean       - Remove all Docker images and containers")
    typer.echo("  clean_cache - Clean up unused Docker resources")
    typer.echo("  clean_volumes - Remove all Docker volumes")

if __name__ == "__main__":
    app()