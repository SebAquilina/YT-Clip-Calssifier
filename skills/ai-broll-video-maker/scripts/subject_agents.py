#!/usr/bin/env python3
"""subject_agents.py — the TWO-AGENT SUBJECT-CONTINUITY FRAMEWORK (v6.5).

DIY videos show ONE subject EVOLVING (empty jar -> wax poured -> cured -> lit -> gifted). For the render
to be honest, each shot must look like the SAME object at its current stage. A flat keyword heuristic
can't reason about evolution or tell a hero from a "what-NOT-to-do" counter-example. So we use a team:

  AGENT 1 — SUBJECT DIRECTOR
    Reads the whole script in order and decides WHAT the subjects are: it segments the image beats into
    distinct physical subjects, orders each subject's beats, writes the evolution STAGE of each beat, and
    flags counter-examples (bad/"don't do this" shots) that must NOT inherit a good subject's identity.

  AGENT 2 — CONTINUITY SUPERVISOR
    Given the Director's map, decides for EACH image beat WHICH earlier beat's rendered image to feed in
    as the img2img reference — i.e. the best prior STATE of that same subject to evolve from. First
    appearance of a subject = a root (no ref). Counter-examples reference other counter-examples or are
    roots, never the hero. It returns a per-beat reference graph.

Backends (pluggable):
  * ANTHROPIC_API_KEY in env  -> the two agents run autonomously against the Anthropic Messages API.
  * Otherwise -> the orchestrator emits the two prompts to <project>/Project files/agent_io/ for the
    Claude Code build agent (or any LLM) to answer, and consumes the answers it writes back.
  * If neither is available at run time, the caller keeps the v6.4 heuristic baseline (buildlib).

Output: <project>/Project files/subject_plan.json  AND it stamps subject_ref_of onto manifest.json.
Run: python3 subject_agents.py <project_dir> [--model claude-sonnet-4-6]
"""
import os, sys, json, re, urllib.request

# ---------------- agent role prompts ----------------
SYSTEM_DIRECTOR = (
"You are the SUBJECT DIRECTOR for a faceless DIY candle video. You receive the video's still-image beats "
"in script order. Identify the distinct PHYSICAL subjects shown (e.g. 'the hero candle', 'the starter "
"kit', 'the wax in the jug', 'flawed example candles'). A subject is ONE object/material followed through "
"the video, even as it changes state. Assign every image beat to exactly one subject. For each beat give a "
"short 'stage' describing the subject's state at that moment, and set is_counterexample=true for any "
"'what NOT to do' / failed / bad-example shot. Group generic standalone shots that share no evolving "
"object under their own one-off subjects. Return STRICT JSON only:\n"
'{"subjects":[{"subject_id":"hero_candle","label":"the candle being made",'
'"beats":[{"id":"b006_full","stage":"finished petal-topped, lit","is_counterexample":false}]}]}')

SYSTEM_SUPERVISOR = (
"You are the CONTINUITY SUPERVISOR for a faceless DIY candle video. You receive the Subject Director's "
"map (subjects, each with ordered beats, stages, and counter-example flags). For EACH image beat decide "
"the single best img2img REFERENCE: the earlier beat (same subject) whose rendered image this beat should "
"visually continue from, so the object stays consistent as it evolves. Rules: (1) the FIRST beat of a "
"subject is a root -> ref=null. (2) Otherwise reference the most recent EARLIER beat of the SAME subject "
"whose state is the natural predecessor (usually the previous stage; use the stable establishing shot if "
"identity matters more than state). (3) A counter-example may only reference another counter-example of "
"the same subject, else null. (4) A reference MUST be an earlier beat id. Keep chains shallow where "
"possible. Return STRICT JSON only: {\"refs\":{\"b006_full\":null,\"b002_live\":\"b001_full\"}}")

def _beats_for_agents(M):
    out=[]
    for b in M["beats"]:
        if b.get("visual_mode") in ("image_full","image_live","image_split"):
            out.append({"id":b["id"],"mode":b["visual_mode"],
                        "subject":b.get("subject_text",""),"says":b.get("narration") or b.get("sentence","")})
    return out

# ---------------- LLM backend ----------------
def llm(system, user, model):
    key=os.environ.get("ANTHROPIC_API_KEY")
    if not key: return None
    body=json.dumps({"model":model,"max_tokens":8000,"system":system,
                     "messages":[{"role":"user","content":user}]}).encode()
    base=os.environ.get("ANTHROPIC_BASE_URL","https://api.anthropic.com").rstrip("/")
    req=urllib.request.Request(base+"/v1/messages",data=body,method="POST",headers={
        "x-api-key":key,"anthropic-version":"2023-06-01","content-type":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=120) as r:
            d=json.loads(r.read()); return "".join(p.get("text","") for p in d.get("content",[]))
    except Exception as e:
        print("[agents] LLM error:",e); return None

def _json(txt):
    if not txt: return None
    m=re.search(r"\{.*\}", txt, re.S)
    try: return json.loads(m.group(0)) if m else None
    except Exception: return None

# ---------------- file-handoff backend (Claude Code build agent answers) ----------------
def _io(project):
    d=os.path.join(project,"Project files","agent_io"); os.makedirs(d,exist_ok=True); return d
def emit_prompts(project, beats):
    d=_io(project)
    json.dump({"system":SYSTEM_DIRECTOR,"input":beats}, open(os.path.join(d,"director_prompt.json"),"w"), indent=2)
    json.dump({"system":SYSTEM_SUPERVISOR,"note":"answer director_response.json first"}, open(os.path.join(d,"supervisor_prompt.json"),"w"), indent=2)
    print(f"[agents] no LLM key — wrote prompts to {d}; build agent should write director_response.json + supervisor_response.json")

# ---------------- orchestration ----------------
def plan(project, model="claude-sonnet-4-6"):
    PF=os.path.join(project,"Project files"); M=json.load(open(os.path.join(PF,"manifest.json")))
    beats=_beats_for_agents(M); ids={b["id"] for b in beats}; order={b["id"]:i for i,b in enumerate(beats)}
    d=_io(project)
    # Agent 1
    subj=_json(llm(SYSTEM_DIRECTOR, json.dumps(beats), model))
    if subj is None and os.path.exists(os.path.join(d,"director_response.json")):
        subj=json.load(open(os.path.join(d,"director_response.json")))
    if subj is None:
        emit_prompts(project, beats); return None
    json.dump(subj, open(os.path.join(d,"director_response.json"),"w"), indent=2)
    # Agent 2
    refs=_json(llm(SYSTEM_SUPERVISOR, json.dumps(subj), model))
    if refs is None and os.path.exists(os.path.join(d,"supervisor_response.json")):
        refs=json.load(open(os.path.join(d,"supervisor_response.json")))
    if refs is None:
        json.dump(subj, open(os.path.join(d,"director_response.json"),"w"), indent=2)
        print("[agents] director done; supervisor pending (no LLM) — build agent should write supervisor_response.json"); return None
    refmap=refs.get("refs",refs)
    # validate: ref must be an earlier image beat
    clean={}
    for bid,rid in refmap.items():
        if bid in ids and rid in ids and order.get(rid,1e9)<order.get(bid,-1): clean[bid]=rid
    plan={"subjects":subj.get("subjects",[]),"refs":clean}
    json.dump(plan, open(os.path.join(PF,"subject_plan.json"),"w"), indent=2)
    # apply to manifest: the agent plan REPLACES any heuristic baseline (clear non-keyed links first)
    n=0
    for b in M["beats"]:
        if b.get("subject_key"): continue
        b.pop("subject_ref_of",None)
        if b["id"] in clean: b["subject_ref_of"]=clean[b["id"]]; n+=1
    json.dump(M, open(os.path.join(PF,"manifest.json"),"w"), indent=2)
    print(f"[agents] subject_plan.json written: {len(plan['subjects'])} subjects, {n} reference links applied")
    return plan

if __name__=="__main__":
    proj=sys.argv[1].rstrip("/")
    model=sys.argv[sys.argv.index("--model")+1] if "--model" in sys.argv else "claude-sonnet-4-6"
    plan(proj, model)
