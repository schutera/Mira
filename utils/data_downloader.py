import os
import requests
from bs4 import BeautifulSoup

def list_csv_files_from_huggingface(repo="collective-intelligence-project/Global-AI-Dialogues", subdir="Global%20AI%20Dialogues%20Data%20-%20September%202024"):
    """
    Scrape the Hugging Face dataset repo for CSV file names.
    """
    base_url = f"https://huggingface.co/datasets/{repo}/tree/main/{subdir}"
    response = requests.get(base_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    csv_files = []
    for link in soup.find_all("a"):
        href = link.get("href", "")
        if href.endswith(".csv"):
            csv_files.append(href.split("/")[-1])
    return list(set(csv_files))

def download_csv_files_from_huggingface(repo="collective-intelligence-project/Global-AI-Dialogues", 
                                        subdir="Global%20AI%20Dialogues%20Data%20-%20September%202024", 
                                        save_dir="datasets"):
    """
    Downloads all CSV files from the Hugging Face dataset repo and saves them locally.
    Returns a list of local file paths.
    """
    csv_files = list_csv_files_from_huggingface(repo, subdir)
    base_url = f"https://huggingface.co/datasets/{repo}/resolve/main/{subdir}/"
    os.makedirs(save_dir, exist_ok=True)
    local_paths = []
    for filename in csv_files:
        url = base_url + filename
        response = requests.get(url)
        response.raise_for_status()
        local_path = os.path.join(save_dir, filename)
        with open(local_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded and saved {filename} to {local_path}")
        local_paths.append(local_path)
    return local_paths

if __name__ == "__main__":
    repo = "collective-intelligence-project/Global-AI-Dialogues"
    subdir = "Global%20AI%20Dialogues%20Data%20-%20September%202024"
    print("Downloading CSV files from the Hugging Face dataset repo...")
    local_csv_paths = download_csv_files_from_huggingface(repo, subdir)
    print(f"Downloaded CSV files: {local_csv_paths}")

