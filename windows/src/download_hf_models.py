import os
import argparse
import asyncio
import aiohttp
import tqdm
from huggingface_hub import snapshot_download


async def download_repo(repo_id: str, session: aiohttp.ClientSession, progress: tqdm.tqdm):
    """
    Asynchronously downloads a Hugging Face repository.

    Args:
        repo_id: The ID of the Hugging Face repository (e.g., "bert-base-uncased").
        session:  aiohttp Client Session
        progress: tqdm instance
    """
    try:
        snapshot_download(repo_id,  local_dir_use_symlinks=False)  # prevent symlink issue on some OS
        progress.update(1)  # Increment progress bar after successful download

    except Exception as e:
        print(f"Error downloading {repo_id}: {e}")

async def download_repos_concurrently(repo_ids: list[str]):
    """
    Downloads multiple Hugging Face repositories concurrently.

    Args:
        repo_ids: A list of Hugging Face repository IDs.
        dest_dir: The destination directory where the repositories will be downloaded.
    """

    # Create a progress bar.
    with tqdm.tqdm(total=len(repo_ids), desc="Downloading Repositories") as progress:

        async with aiohttp.ClientSession() as session:
            tasks = [download_repo(repo_id, session, progress) for repo_id in repo_ids]
            await asyncio.gather(*tasks)


def main():
    parser = argparse.ArgumentParser(
        description="Download multiple Hugging Face repositories concurrently."
    )
    parser.add_argument(
        "repo_list_file",
        help="Path to a file containing a list of Hugging Face repository IDs (one per line).",
    )

    args = parser.parse_args()

    # Read the repository IDs from the file.
    try:
        with open(args.repo_list_file, "r") as f:
            repo_ids = [line.strip() for line in f]  # remove \n
    except FileNotFoundError:
        print(f"Error: File not found: {args.repo_list_file}")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return


    # Download the repositories concurrently.
    asyncio.run(download_repos_concurrently(repo_ids))

    print("Download complete.")


if __name__ == "__main__":
    main()