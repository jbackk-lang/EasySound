import os
import zipfile
import hashlib
import tempfile
import shutil

def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def auto_compress_test(input_path):
    if not os.path.isfile(input_path):
        return "Plik nie istnieje."

    # hash oryginału
    original_hash = file_hash(input_path)

    # folder tymczasowy
    temp_dir = tempfile.mkdtemp()

    zip_path = os.path.join(temp_dir, "test.zip")
    out_path = os.path.join(temp_dir, "out")

    # kompresja
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(input_path, arcname="file")

    # dekompresja
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(out_path)

    extracted_file = os.path.join(out_path, "file")

    # hash po dekompresji
    new_hash = file_hash(extracted_file)

    # porównanie
    if original_hash == new_hash:
        result = "Plik jest IDENTYCZNY po kompresji/dekompresji."
    else:
        result = "Plik został ZMIENIONY przez kompresję."

    # sprzątanie
    shutil.rmtree(temp_dir)

    return result
