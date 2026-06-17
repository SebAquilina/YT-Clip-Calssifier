#!/usr/bin/env python3
"""build_deliverable.py <video_folder> [--title NAME]
Package a finished video into the SOP deliverable zip:

  <Title>_deliverable.zip
  ├── <Title>.mp4        (the final video found in the folder)
  ├── description.txt    (the .txt description found in the folder)
  ├── thumbnail.png      (the thumbnail PNG found in the folder)
  └── Source clips/      (all generated clips)

Prints the path to the zip. Host it and share the link (zips are large).
"""
import os, sys, shutil, glob, zipfile, tempfile

def find_one(folder, patterns):
    for p in patterns:
        hits=sorted(glob.glob(os.path.join(folder,p)))
        if hits: return hits[0]
    return None

def main():
    if len(sys.argv)<2:
        print("usage: build_deliverable.py <video_folder> [--title NAME]"); sys.exit(1)
    folder=sys.argv[1].rstrip("/")
    title=None
    if "--title" in sys.argv: title=sys.argv[sys.argv.index("--title")+1]
    mp4=find_one(folder, ["*.mp4"])
    desc=find_one(folder, ["*.txt"])
    thumb=find_one(folder, ["Thumbnail*.png","thumbnail*.png","*thumb*.png","*.png"])
    clips=os.path.join(folder,"Source clips")
    if not mp4: print("[error] no final .mp4 in",folder); sys.exit(1)
    if not title: title=os.path.splitext(os.path.basename(mp4))[0]

    staging=tempfile.mkdtemp()
    pkg=os.path.join(staging, title); os.makedirs(pkg)
    shutil.copy(mp4, os.path.join(pkg, title+".mp4"))
    if desc:  shutil.copy(desc, os.path.join(pkg,"description.txt"))
    else:     print("[warn] no description.txt found")
    if thumb: shutil.copy(thumb, os.path.join(pkg,"thumbnail.png"))
    else:     print("[warn] no thumbnail.png found")
    if os.path.isdir(clips): shutil.copytree(clips, os.path.join(pkg,"Source clips"))
    else: print("[warn] no 'Source clips/' found")

    out=os.path.join(folder, title+"_deliverable.zip")
    with zipfile.ZipFile(out,"w",zipfile.ZIP_STORED) as z:  # STORED: mp4 already compressed
        for root,_,files in os.walk(pkg):
            for f in files:
                fp=os.path.join(root,f)
                z.write(fp, os.path.relpath(fp, staging))
    shutil.rmtree(staging, ignore_errors=True)
    print("DELIVERABLE:", out, f"({os.path.getsize(out)//(1024*1024)} MB)")

    # --host: upload the zip (and the final mp4 + thumbnail) and print links.
    # Uses host_upload.py, which SANITIZES the filename first — uploading the
    # title-named file directly fails silently (curl -F chokes on spaces/commas).
    if "--host" in sys.argv:
        import subprocess
        hu=os.path.join(os.path.dirname(os.path.abspath(__file__)),"host_upload.py")
        targets=[out, mp4] + ([thumb] if thumb else [])
        print("== hosting deliverable (sanitized filenames) ==")
        subprocess.run(["python3",hu,*targets])

if __name__=="__main__": main()
