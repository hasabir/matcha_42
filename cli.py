#!/usr/bin/env python3
"""
Matcha Docker CLI - Manage your Docker containers easily
Usage: python3 cli.py <command>
"""

import subprocess
import sys


def build():
    """Build and start all Docker containers (frontend, backend, db, redis, pgadmin)"""
    subprocess.run(["docker-compose", "up", "--build"])


def up():
    """Start all Docker containers in detached mode"""
    subprocess.run(["docker-compose", "up", "-d"])


def down():
    """Stop and remove all Docker containers"""
    subprocess.run(["docker-compose", "down"])


def restart():
    """Restart all Docker containers"""
    subprocess.run(["docker-compose", "restart"])


def logs(service=None):
    """View logs for all services or a specific service"""
    cmd = ["docker-compose", "logs", "-f"]
    if service:
        cmd.append(service)
    subprocess.run(cmd)


def ps():
    """Show status of all containers"""
    subprocess.run(["docker-compose", "ps"])


def restart_backend():
    """Restart only the backend container"""
    subprocess.run(["docker-compose", "restart", "backend"])


def restart_frontend():
    """Restart only the frontend container"""
    subprocess.run(["docker-compose", "restart", "frontend"])


def rebuild_backend():
    """Rebuild and restart the backend container"""
    subprocess.run(["docker-compose", "up", "-d", "--build", "backend"])


def rebuild_frontend():
    """Rebuild and restart the frontend container"""
    subprocess.run(["docker-compose", "up", "-d", "--build", "frontend"])


def clean():
    """Remove all Docker images and containers"""
    subprocess.run("docker rmi -f $(docker images -q)", shell=True)
    subprocess.run("docker rm -f $(docker ps -qa)", shell=True)


def clean_cache():
    """Clean up unused Docker resources"""
    subprocess.run(["docker", "system", "prune", "--all"])


def clean_volumes():
    """Remove all Docker volumes (WARNING: This deletes all data!)"""
    response = input("⚠️  This will delete all database data. Continue? (y/N): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return
    subprocess.run(["docker-compose", "down", "-v"])


def reset():
    """Stop containers and remove volumes for a fresh start"""
    response = input("⚠️  This will delete all data and reset everything. Continue? (y/N): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return
    subprocess.run(["docker-compose", "down", "-v"])
    print("✅ Containers stopped and volumes removed. Run 'python3 cli.py up' to start fresh.")


def help_cmd():
    """Show available commands"""
    print("\n🚀 Matcha Docker CLI - Available Commands\n")
    print("Basic Commands:")
    print("  build             - Build and start all containers (attached)")
    print("  up                - Start all containers in detached mode")
    print("  down              - Stop and remove all containers")
    print("  restart           - Restart all containers")
    print("  ps                - Show container status")
    print()
    print("Logs:")
    print("  logs              - View logs for all services")
    print("  logs-backend      - View backend logs only")
    print("  logs-frontend     - View frontend logs only")
    print()
    print("Service Management:")
    print("  restart-backend   - Restart only backend")
    print("  restart-frontend  - Restart only frontend")
    print("  rebuild-backend   - Rebuild and restart backend")
    print("  rebuild-frontend  - Rebuild and restart frontend")
    print()
    print("Cleanup:")
    print("  clean             - Remove all Docker images and containers")
    print("  clean-cache       - Clean up unused Docker resources")
    print("  clean-volumes     - Remove all volumes (deletes data)")
    print("  reset             - Full reset (stop + remove volumes)")
    print()
    print("Examples:")
    print("  python3 cli.py up")
    print("  python3 cli.py logs-backend")
    print("  python3 cli.py rebuild-frontend")
    print()


COMMANDS = {
    'build': build,
    'up': up,
    'down': down,
    'restart': restart,
    'logs': lambda: logs(),
    'logs-backend': lambda: logs('backend'),
    'logs-frontend': lambda: logs('frontend'),
    'logs-db': lambda: logs('db'),
    'ps': ps,
    'restart-backend': restart_backend,
    'restart-frontend': restart_frontend,
    'rebuild-backend': rebuild_backend,
    'rebuild-frontend': rebuild_frontend,
    'clean': clean,
    'clean-cache': clean_cache,
    'clean-volumes': clean_volumes,
    'reset': reset,
    'help': help_cmd,
}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        help_cmd()
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command in COMMANDS:
        COMMANDS[command]()
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python3 cli.py help' to see available commands")
        sys.exit(1)