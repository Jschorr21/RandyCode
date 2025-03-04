import subprocess

# List of scripts to execute
scripts = ["./data_ingestion/catalog_pipeline.py", "./data_ingestion/courses_pipeline.py"]
def run_scripts():
    # Execute each script
    for script in scripts:
        subprocess.run(["python3", script], check=True)

if __name__ == "__main__":
    run_scripts()