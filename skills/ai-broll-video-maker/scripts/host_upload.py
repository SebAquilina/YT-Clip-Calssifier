#!/usr/bin/env python3
"""host_upload.py <file> [<file> ...]
Upload one or more files to litterbox and print public download links.

CRITICAL LESSON (do not remove): litterbox/catbox/gofile/0x0/etc. uploads are done
with `curl -F fileToUpload=@<path>`. curl's -F field parses `;`, `,` and other
characters specially and CHOKES on paths that contain spaces, commas or other
shell/`-F`-special characters — it fails with `curl (26) Failed to open/read local
data` and returns an EMPTY body, which looks exactly like a size/network limit.

Our deliverables are named for the video title (e.g.
"POOR SCENT THROW - Stop Adding More Fragrance, This Is The REAL Issue.mp4"), so a
naive upload of that path silently fails and you wrongly conclude the host rejected
a "too-large" file. THE FIX: copy to a sanitized temp filename (no spaces/commas)
before uploading. With a clean name, full 100-300MB files upload in seconds.

This helper always sanitizes first, so it works regardless of how the source file
is named. Prints `LINK: <name> -> <url>` per file. Verifies content-length matches.
"""
import sys, os, re, shutil, tempfile, subprocess

def sanitize(name):
    base=os.path.basename(name)
    stem,ext=os.path.splitext(base)
    stem=re.sub(r"[^A-Za-z0-9._-]+","_",stem).strip("_") or "file"
    return f"{stem}{ext.lower()}"

def upload(path, tries=5):
    if not os.path.exists(path):
        return None,f"missing: {path}"
    clean=sanitize(path)
    tmp=os.path.join(tempfile.gettempdir(), clean)
    if os.path.abspath(tmp)!=os.path.abspath(path):
        shutil.copy(path, tmp)          # copy to a curl-safe filename
    size=os.path.getsize(tmp)
    url=None
    for i in range(1,tries+1):
        r=subprocess.run(["curl","-sS","--max-time","1800","--connect-timeout","30",
            "-F","reqtype=fileupload","-F","time=72h",
            "-F",f"fileToUpload=@{tmp}",
            "https://litterbox.catbox.moe/resources/internals/api.php"],
            capture_output=True,text=True)
        out=r.stdout.strip()
        if out.startswith("http"): url=out; break
        # backoff; surface the real curl error (e.g. "(26) Failed to open")
        err=(r.stderr or out or "empty response").strip()[:120]
        sys.stderr.write(f"  attempt {i} failed: {err}\n")
        subprocess.run(["sleep",str(4*i)])
    if os.path.abspath(tmp)!=os.path.abspath(path):
        os.path.exists(tmp) and os.remove(tmp)
    if not url: return None,"upload failed"
    # verify content-length matches
    h=subprocess.run(["curl","-sI","-m","60",url],capture_output=True,text=True).stdout
    m=re.search(r"content-length:\s*(\d+)", h, re.I)
    ok = m and int(m.group(1))==size
    return url, ("verified" if ok else f"WARNING size mismatch (local {size}, host {m.group(1) if m else '?'})")

def main():
    if len(sys.argv)<2:
        print("usage: host_upload.py <file> [<file> ...]"); sys.exit(1)
    for p in sys.argv[1:]:
        url,note=upload(p)
        if url: print(f"LINK: {os.path.basename(p)} -> {url}  [{note}]")
        else:   print(f"FAIL: {os.path.basename(p)} ({note})")

if __name__=="__main__": main()
