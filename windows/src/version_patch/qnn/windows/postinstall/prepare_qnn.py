import os
import platform
import sys
import shutil
import requests
import zipfile
import tempfile
from pathlib import Path
from urllib.parse import urlparse
from tqdm import tqdm

QNN_SDK_VERSION = "2.32.0.250228"
QNN_SDK_DL_URL = f"https://apigwx-aws.qualcomm.com/qsc/public/v1/api/download/software/sdks/Qualcomm_AI_Runtime_Community/All/{QNN_SDK_VERSION}/v{QNN_SDK_VERSION}.zip"
QNN_SDK_ROOT = os.environ.get("QNN_SDK_ROOT", None)
KUWA_ROOT = (
    Path(os.environ.get("KUWA_ROOT", "C:\\kuwa\\kuwa-aios\\windows\\root")) / "../../"
).resolve()


def search_file(search_paths, files):
    result = []
    for file in files:
        found = False
        for dir in search_paths:
            path = Path(dir) / file
            if path.is_file():
                result.append(path)
                found = True
                break
            
        if not found:
            raise RuntimeError(f"file {file} not found in the search path {str(search_paths)}")
        
    return result


def get_sys_arch():
    machine = platform.machine()
    sysinfo = sys.version

    arch = "ARM64"

    if machine == "AMD64" or "AMD64" in sysinfo:
        arch = "ARM64EC"

    if machine == "aarch64":
        arch = "aarch64"

    return arch


def download_and_extract_zip(zip_url: str, extract_to_dir: str = "."):
    """
    Downloads a zip file from a URL and extracts its contents to a specified directory,
    displaying a progress bar during download.

    Args:
        zip_url (str): The URL of the zip file.
        extract_to_dir (str, optional): The directory to extract the contents to. Defaults to the current directory (".")
    """

    try:
        filename = os.path.basename(urlparse(zip_url).path)
        temp_filename = Path(tempfile.gettempdir()) / Path(filename).with_suffix(
            ".zip.tmp"
        )
        with open(temp_filename, "ab") as f:
            pos = f.tell()
            headers = {"Range": f"bytes={pos}-"}
            response = requests.get(zip_url, headers=headers, stream=True)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            total_size_in_bytes = pos + int(response.headers.get("content-length", 0))
            block_size = 1024  # 1 Kibibyte
            progress_bar = tqdm(
                desc=f"Downloading QNN SDK ({filename})",
                total=total_size_in_bytes,
                initial=pos,
                unit="iB",
                unit_scale=True,
            )

            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                f.write(data)

        progress_bar.close()

        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            print("ERROR, something went wrong with download")

        with zipfile.ZipFile(temp_filename) as zip_ref:
            zip_ref.extractall(extract_to_dir)
        print(
            f"Successfully downloaded and extracted '{zip_url}' to '{extract_to_dir}'"
        )
        os.remove(temp_filename)

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
    except zipfile.BadZipFile as e:
        print(f"Error: Invalid zip file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def copy_qnn_dependencies(qnn_sdk_root: Path, kuwa_root: Path):
    print(f"QNN_SDK_ROOT={qnn_sdk_root}")
    print(f"KUWA_ROOT={kuwa_root}")

    dst_dir = kuwa_root / "windows/packages/qnn-binaries/"

    lib_search_path = []
    bin_search_path = []
    arch = get_sys_arch()
    print("Arch: " + arch)
    if arch == "ARM64EC":
        lib_search_path.append(qnn_sdk_root / "lib/arm64x-windows-msvc")
        lib_search_path.append(qnn_sdk_root / "lib/x86_64-windows-msvc")
        bin_search_path.append(qnn_sdk_root / "bin/arm64x-windows-msvc")
        bin_search_path.append(qnn_sdk_root / "bin/x86_64-windows-msvc")
    else:
        lib_search_path.append(qnn_sdk_root / "lib/aarch64-windows-msvc")
        bin_search_path.append(qnn_sdk_root / "bin/aarch64-windows-msvc")
    lib_search_path.append(qnn_sdk_root / "lib/hexagon-v73/unsigned")
    qnn_sdk_deps = search_file(
        lib_search_path,
        [
            "Genie.dll",
            "QnnHtp.dll",
            "QnnSystem.dll",
            "QnnHtpPrepare.dll",
            "QnnHtpNetRunExtensions.dll",
            "QnnHtpV73Stub.dll",
            "libqnnhtpv73.cat",
            # "libQnnHtpV73.so",
            "libQnnHtpV73Skel.so",
        ],
    )
    qnn_sdk_deps += search_file(
        bin_search_path, ["genie-t2t-run.exe", "qnn-net-run.exe"]
    )
    print("Dependencies:\n" + "\n".join([str(p) for p in qnn_sdk_deps]))

    os.makedirs(dst_dir, exist_ok=True)
    for dep in qnn_sdk_deps:
        shutil.copy(dep, dst_dir)

    with open(Path(dst_dir) / "VERSION.txt", "w") as f:
        f.write(f"QNN_SDK_VERSION={QNN_SDK_VERSION}")
    
    print(f"Copied dependencies to {dst_dir} successfully.")


if __name__ == "__main__":
    if QNN_SDK_ROOT is None:
        QNN_SDK_ROOT = f"C:\\qairt\\{QNN_SDK_VERSION}"
        if not Path(QNN_SDK_ROOT).is_dir():
            download_and_extract_zip(zip_url=QNN_SDK_DL_URL, extract_to_dir="C:\\")

    copy_qnn_dependencies(qnn_sdk_root=Path(QNN_SDK_ROOT), kuwa_root=Path(KUWA_ROOT))
