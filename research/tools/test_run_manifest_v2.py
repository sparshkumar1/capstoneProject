"""Synthetic/local tests for research/tools/run_manifest_v2.py (temporary git repositories only).

Run:  python research/tools/test_run_manifest_v2.py      (or: python -m pytest research/tools/test_run_manifest_v2.py)
Nothing here touches the project repository, any frozen artifact, or any experiment data.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_manifest_v2 as rm                                    # noqa: E402
from run_manifest_v2 import Manifest, ManifestError, sha256_file, verify_completed   # noqa: E402


class World:
    """A temporary git repository with a registered protocol (annotated tag) in the real manifest format."""

    def __init__(self, extra_manifest_keys=()):
        self.tmp = Path(tempfile.mkdtemp(prefix="rmv2_test_")).resolve()
        self.repo = self.tmp / "repo"
        (self.repo / "research" / "analysis").mkdir(parents=True)
        (self.repo / "prereg").mkdir()
        (self.repo / "code").mkdir()
        self.g("init", "-q")
        self.g("config", "user.email", "t@t")
        self.g("config", "user.name", "t")
        self.w("prereg/PROTOCOL.md", b"protocol v1\n")
        self.w("code/run.py", b"print('run')\n")
        self.w("code/helper.py", b"X = 1\n")
        self.w("code/cfg.json", b'{"a": 1}\n')
        self.w("data.csv", b"a,b\n1,2\n")
        files = {r: sha256_file(self.repo / r) for r in ("code/run.py", "code/helper.py", "code/cfg.json")}
        for alias in extra_manifest_keys:                       # alias spellings of an already declared file
            files[alias] = files["code/run.py"]
        self.w("prereg/protocol_manifest.json", json.dumps({"protocol": "prereg/PROTOCOL.md", "files": files},
                                                            indent=1).encode())
        self.g("add", "-A")
        self.g("commit", "-q", "-m", "protocol")
        ps = sha256_file(self.repo / "prereg/PROTOCOL.md")
        ms = sha256_file(self.repo / "prereg/protocol_manifest.json")
        self.g("tag", "-a", "prereg/T/v1", "-m", "protocol sha256 %s manifest sha256 %s" % (ps, ms))
        self.g("commit", "-q", "--allow-empty", "-m", "later")

    def g(self, *a):
        return subprocess.run(["git", "-C", str(self.repo), *a], capture_output=True, text=True, check=True)

    def w(self, rel, data: bytes):
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    def analysis(self, name):
        return self.repo / "research" / "analysis" / name

    def mk(self, out, **kw):
        base = dict(protocol_tag="prereg/T/v1", protocol_path=self.repo / "prereg/PROTOCOL.md",
                    protocol_manifest_path=self.repo / "prereg/protocol_manifest.json",
                    dependencies=[self.repo / "code/run.py", self.repo / "code/helper.py", self.repo / "code/cfg.json"],
                    code_roots=[self.repo / "code"], inputs=[self.repo / "data.csv"], repo=self.repo,
                    allowed_roots=[self.repo / "research" / "analysis"])
        base.update(kw)
        return Manifest("t", self.analysis(out), self.repo / "code/run.py", **base)

    def status(self, out):
        p = self.analysis(out) / "manifest_t.json"
        return json.loads(p.read_text())["status"] if p.exists() else None

    def completed_run(self, out, name="out.txt"):
        with self.mk(out) as m:
            (m.out_dir / name).write_text("ok")
            m.set_gate("G", True)
            assert m.finish([m.out_dir / name]) == "completed"
        return self.analysis(out) / "manifest_t.json"


def raises(fn, needle=None, exc=ManifestError):
    try:
        fn()
    except exc as e:
        assert needle is None or needle in str(e), "wrong error: %s" % e
        return
    raise AssertionError("expected %s" % exc.__name__)


# ---- baseline ---------------------------------------------------------------------------------------
def test_happy_path_and_write_once():
    w = World()
    try:
        w.completed_run("r1")
        raises(lambda: w.mk("r1"), "already exists")                      # no check-then-create
        assert w.status("r1") == "completed"
    finally:
        shutil.rmtree(w.tmp, ignore_errors=True)


def test_exception_in_with_block_is_aborted():
    w = World()
    try:
        try:
            with w.mk("r1"):
                raise ValueError("boom")
        except ValueError:
            pass
        assert w.status("r1") == "aborted"
    finally:
        shutil.rmtree(w.tmp, ignore_errors=True)


# ---- repair 2: protocol manifest is authoritative ----------------------------------------------------
def test_omitted_dependency_is_refused():
    w = World()
    try:
        deps = [w.repo / "code/run.py", w.repo / "code/cfg.json"]                    # helper.py omitted
        raises(lambda: w.mk("r1", dependencies=deps), "missing")
        assert w.status("r1") == "aborted"                                            # explicit state, not 'started'
        raises(lambda: w.mk("r2", dependencies=deps + [w.repo / "code/helper.py", w.repo / "data.csv"]), "extra")
        raises(lambda: w.mk("r3", dependencies=[]), "missing")
    finally:
        shutil.rmtree(w.tmp, ignore_errors=True)


def test_dependency_hash_must_equal_protocol_manifest_and_tag():
    w = World()
    try:
        w.w("code/helper.py", b"X = 2\n")                                            # edited after registration
        raises(lambda: w.mk("r1"), "helper.py")
    finally:
        shutil.rmtree(w.tmp, ignore_errors=True)


def test_code_root_coverage_and_entrypoint_declared():
    w = World()
    try:
        raises(lambda: w.mk("r1", code_roots=[w.repo / "prereg"]), "not covered by a code root")
        w.w("code/other.py", b"y=1\n")
        w.g("add", "-A")
        w.g("commit", "-q", "-m", "x")
        # entrypoint that is not a declared dependency
        raises(lambda: Manifest("t", w.analysis("r2"), w.repo / "code/other.py", protocol_tag="prereg/T/v1",
                                protocol_path=w.repo / "prereg/PROTOCOL.md",
                                protocol_manifest_path=w.repo / "prereg/protocol_manifest.json",
                                dependencies=[w.repo / "code/run.py", w.repo / "code/helper.py", w.repo / "code/cfg.json"],
                                code_roots=[w.repo / "code"], repo=w.repo,
                                allowed_roots=[w.repo / "research" / "analysis"]), "not a declared dependency")
    finally:
        shutil.rmtree(w.tmp, ignore_errors=True)


def test_protocol_edited_untracked_code_and_prefix_digest_refused():
    w = World()
    try:
        w.w("code/extra.py", b"z=1\n")                                                # untracked under a code root
        raises(lambda: w.mk("r1"), "modified/untracked")
        (w.repo / "code/extra.py").unlink()
        raises(lambda: w.mk("r2", expected_digests={"data.csv": sha256_file(w.repo / "data.csv")[:8]}), "expected")
        w.w("prereg/PROTOCOL.md", b"protocol v1 EDITED\n")
        raises(lambda: w.mk("r3"), "differs from its content")
    finally:
        shutil.rmtree(w.tmp, ignore_errors=True)


# ---- repair 3: outputs must be run-scoped regular files ----------------------------------------------------
def test_output_outside_run_directory_refused():
    w = World()
    try:
        m = w.mk("r1")
        m.set_gate("G", True)
        (w.repo / "elsewhere.txt").write_text("x")
        raises(lambda: m.finish([w.repo / "elsewhere.txt"]), "outside this run")
        assert w.status("r1") == "aborted"
    finally:
        shutil.rmtree(w.tmp, ignore_errors=True)


def test_preexisting_repository_file_and_other_run_output_refused():
    w = World()
    try:
        first = w.completed_run("r1")                                                 # a previous run's real output
        m = w.mk("r2")
        m.set_gate("G", True)
        raises(lambda: m.finish([w.analysis("r1") / "out.txt"]), "outside this run")
        assert w.status("r2") == "aborted"
        m = w.mk("r3")
        m.set_gate("G", True)
        raises(lambda: m.finish([w.repo / "code/run.py"]), "outside this run")        # pre-existing tracked file
        m = w.mk("r4")
        m.set_gate("G", True)
        raises(lambda: m.finish([m.out_dir / "missing.txt"]), "does not exist")
        m = w.mk("r5")
        m.set_gate("G", True)
        raises(lambda: m.finish([m.out_dir]), "outside this run")                              # a directory
        m = w.mk("r6")
        m.set_gate("G", True)
        raises(lambda: m.finish([m.out_dir / ".run.lock"]), "manifest/lock/hidden")
        del first
    finally:
        shutil.rmtree(w.tmp, ignore_errors=True)


def test_hardlink_to_preexisting_file_refused():
    w = World()
    try:
        m = w.mk("r1")
        m.set_gate("G", True)
        link = m.out_dir / "hard.txt"
        try:
            os.link(w.repo / "data.csv", link)
        except (OSError, NotImplementedError):
            print("  (hardlinks unavailable; skipped)")
            return
        raises(lambda: m.finish([link]), "single-link")
    finally:
        shutil.rmtree(w.tmp, ignore_errors=True)


def test_symlink_output_refused():
    w = World()
    try:
        m = w.mk("r1")
        m.set_gate("G", True)
        link = m.out_dir / "sym.txt"
        try:
            os.symlink(w.repo / "data.csv", link)
        except (OSError, NotImplementedError):
            print("  (symlinks unavailable; skipped)")
            return
        raises(lambda: m.finish([link]), None)
    finally:
        shutil.rmtree(w.tmp, ignore_errors=True)


# ---- repair 4: upstream revalidation -----------------------------------------------------------------------
def test_upstream_altered_manifest_or_output_detected():
    w = World()
    try:
        up = w.completed_run("up")
        rel = str(up.relative_to(w.repo)).replace("\\", "/")
        good = sha256_file(up)
        # wrong expected hash at link time
        raises(lambda: verify_completed(up, w.repo, expected_sha256="0" * 64), "SHA-256")
        # downstream links, then the upstream OUTPUT changes before finish -> downstream is 'failed'
        with w.mk("down1") as m:
            m.link_upstream(up, expected_sha256=good)
            (w.analysis("up") / "out.txt").write_text("CHANGED")
            (m.out_dir / "o.txt").write_text("x")
            m.set_gate("G", True)
            assert m.finish([m.out_dir / "o.txt"]) == "failed"
            assert any("UPSTREAM INVALID AT FINISH" in f for f in m.d["failures"])
        raises(lambda: verify_completed(up, w.repo), "upstream output changed")
        (w.analysis("up") / "out.txt").write_text("ok")                                # restore
        verify_completed(up, w.repo, expected_sha256=good)
        # upstream MANIFEST changes after linking
        with w.mk("down2") as m:
            m.link_upstream(up, expected_sha256=good)
            d = json.loads(up.read_text())
            d["deviations"] = ["edited after link"]
            up.write_text(json.dumps(d, indent=2))
            (m.out_dir / "o.txt").write_text("x")
            m.set_gate("G", True)
            assert m.finish([m.out_dir / "o.txt"]) == "failed"
        raises(lambda: verify_completed(up, w.repo, expected_sha256=good), "SHA-256")
        del rel
    finally:
        shutil.rmtree(w.tmp, ignore_errors=True)


def test_upstream_unchanged_stays_valid_and_incomplete_upstream_refused():
    w = World()
    try:
        up = w.completed_run("up")
        with w.mk("down") as m:
            m.link_upstream(up, expected_sha256=sha256_file(up))
            (m.out_dir / "o.txt").write_text("x")
            m.set_gate("G", True)
            assert m.finish([m.out_dir / "o.txt"]) == "completed"
            assert m.d["upstream"][0]["revalidated_at_finish"] is True
        try:
            with w.mk("bad"):
                raise ValueError("x")
        except ValueError:
            pass
        raises(lambda: verify_completed(w.analysis("bad") / "manifest_t.json", w.repo), "not a completed v2 run")
    finally:
        shutil.rmtree(w.tmp, ignore_errors=True)


# ---- repair 5: initialisation / abort safety ---------------------------------------------------------------
def test_initialisation_failure_leaves_no_ambiguous_run():
    w = World()
    try:
        w.w("prereg/PROTOCOL.md", b"protocol v1 EDITED\n")
        raises(lambda: w.mk("r1"))
        assert w.status("r1") == "aborted"                                            # manifest was written first
        w.w("prereg/PROTOCOL.md", b"protocol v1\n")
        # a failure before ANY manifest can be written: directory is removed
        real = Manifest._write

        def boom(self):
            raise OSError("disk full (simulated)")
        Manifest._write = boom
        try:
            raises(lambda: w.mk("r2"), None, exc=OSError)
        finally:
            Manifest._write = real
        assert not w.analysis("r2").exists() or (w.analysis("r2") / "INIT_FAILED_DO_NOT_USE.txt").exists()
        assert w.status("r2") in (None, "aborted")                                     # never 'started'/'completed'
        # removal itself fails -> explicit marker
        real_rmtree = rm.shutil.rmtree
        Manifest._write = boom

        def bad_rmtree(*a, **k):
            raise OSError("cannot remove (simulated)")
        rm.shutil.rmtree = bad_rmtree
        try:
            raises(lambda: w.mk("r3"), None, exc=OSError)
        finally:
            rm.shutil.rmtree = real_rmtree
            Manifest._write = real
        assert (w.analysis("r3") / "INIT_FAILED_DO_NOT_USE.txt").exists()
        assert w.status("r3") is None
    finally:
        shutil.rmtree(w.tmp, ignore_errors=True)


def test_abort_with_malformed_partial_output_does_not_raise():
    w = World()
    try:
        m = w.mk("r1")
        m.abort("test", partial_outputs=[object(), "\0bad", "C:/definitely/not/in/repo.txt", w.repo / "data.csv"])
        d = json.loads((w.analysis("r1") / "manifest_t.json").read_text())
        assert d["status"] == "aborted" and len(d["outputs_partial"]) == 4
        assert any("error" in e for e in d["outputs_partial"])
        m.abort("second call is a no-op")                                             # idempotent
    finally:
        shutil.rmtree(w.tmp, ignore_errors=True)


def test_abort_when_manifest_unwritable_still_marks_run():
    w = World()
    try:
        m = w.mk("r1")
        real = Manifest._write
        Manifest._write = lambda self: (_ for _ in ()).throw(OSError("simulated"))
        try:
            m.abort("cannot write")                                                   # must not raise
        finally:
            Manifest._write = real
        assert (w.analysis("r1") / "ABORTED_MANIFEST_UNWRITABLE.txt").exists()
    finally:
        shutil.rmtree(w.tmp, ignore_errors=True)


def test_selftest_mode_only_under_temp():
    w = World()
    try:
        raises(lambda: Manifest("t", rm.DEFAULT_REPO / "research" / "analysis" / "x", w.repo / "code/run.py",
                                selftest=True, protocol_tag="prereg/T/v1", protocol_path=w.repo / "prereg/PROTOCOL.md",
                                protocol_manifest_path=w.repo / "prereg/protocol_manifest.json", dependencies=[],
                                repo=w.repo), "system temp")
    finally:
        shutil.rmtree(w.tmp, ignore_errors=True)


def test_keyset_mismatch_stops():
    w = World()
    try:
        with w.mk("r1") as m:
            m.assert_keyset("k", {1, 2}, {1, 2})
            raises(lambda: m.assert_keyset("k2", {1}, {1, 2}), "key-set mismatch")
    finally:
        shutil.rmtree(w.tmp, ignore_errors=True)


# ---- final repair 2: recursive verification of completed manifests ------------------------------------------
def _chain(w):
    """a <- b <- c : three completed v2 runs, each linking the previous one."""
    a = w.completed_run("a", "a.txt")
    runs = {"a": a}
    prev = a
    for name in ("b", "c"):
        with w.mk(name) as m:
            m.link_upstream(prev, expected_sha256=sha256_file(prev))
            (m.out_dir / (name + ".txt")).write_text(name)
            m.set_gate("G", True)
            assert m.finish([m.out_dir / (name + ".txt")]) == "completed"
        prev = w.analysis(name) / "manifest_t.json"
        runs[name] = prev
    return runs


def test_verify_completed_downstream_detects_direct_upstream_mutation_after_completion():
    w = World()
    try:
        r = _chain(w)
        verify_completed(r["c"], w.repo, expected_sha256=sha256_file(r["c"]))       # intact chain verifies
        (w.analysis("b") / "b.txt").write_text("MUTATED after c completed")           # b's output changed
        raises(lambda: verify_completed(r["c"], w.repo), "upstream output changed")
    finally:
        shutil.rmtree(w.tmp, ignore_errors=True)


def test_verify_completed_downstream_detects_nested_upstream_mutation():
    w = World()
    try:
        r = _chain(w)
        (w.analysis("a") / "a.txt").write_text("MUTATED")                             # two levels up
        raises(lambda: verify_completed(r["c"], w.repo), "upstream output changed")
        (w.analysis("a") / "a.txt").write_text("ok")                                   # exact restore: chain verifies again
        verify_completed(r["c"], w.repo)
        d = json.loads(r["a"].read_text())                                            # nested MANIFEST mutation
        d["deviations"] = ["edited"]
        r["a"].write_text(json.dumps(d, indent=2))
        raises(lambda: verify_completed(r["c"], w.repo), "upstream manifest changed")
    finally:
        shutil.rmtree(w.tmp, ignore_errors=True)


def test_finish_of_downstream_revalidates_nested_chain():
    w = World()
    try:
        r = _chain(w)
        with w.mk("d") as m:
            m.link_upstream(r["c"], expected_sha256=sha256_file(r["c"]))
            (w.analysis("a") / "a.txt").write_text("MUTATED")                         # nested change before finish
            (m.out_dir / "d.txt").write_text("d")
            m.set_gate("G", True)
            assert m.finish([m.out_dir / "d.txt"]) == "failed"
            assert any("UPSTREAM INVALID AT FINISH" in f for f in m.d["failures"])
    finally:
        shutil.rmtree(w.tmp, ignore_errors=True)


def test_upstream_cycle_fails_closed_and_terminates():
    w = World()
    try:
        # A real cycle needs a hash fixed point, so make every manifest hash identical for this mechanism test.
        real = rm.sha256_bytes
        rm.sha256_bytes = lambda b: "f" * 64
        try:
            ra = {"manifest_path": "research/analysis/x/manifest_t.json", "manifest_sha256": "f" * 64, "outputs": []}
            rb = {"manifest_path": "research/analysis/y/manifest_t.json", "manifest_sha256": "f" * 64, "outputs": []}
            for name, up in (("x", rb), ("y", ra)):
                d = w.analysis(name)
                d.mkdir(parents=True)
                (d / "manifest_t.json").write_text(json.dumps(
                    {"manifest_version": rm.SCHEMA, "status": "completed", "failures": [], "selftest": False,
                     "gate": {"name": "G", "passed": True}, "outputs": [], "upstream": [up]}))
            raises(lambda: verify_completed(w.analysis("x") / "manifest_t.json", w.repo), "cycle")
        finally:
            rm.sha256_bytes = real
    finally:
        shutil.rmtree(w.tmp, ignore_errors=True)


def test_diamond_chain_is_not_mistaken_for_a_cycle():
    w = World()
    try:
        a = w.completed_run("a", "a.txt")
        for name in ("b1", "b2"):
            with w.mk(name) as m:
                m.link_upstream(a, expected_sha256=sha256_file(a))
                (m.out_dir / "o.txt").write_text(name)
                m.set_gate("G", True)
                m.finish([m.out_dir / "o.txt"])
        with w.mk("d") as m:
            for name in ("b1", "b2"):
                p = w.analysis(name) / "manifest_t.json"
                m.link_upstream(p, expected_sha256=sha256_file(p))
            (m.out_dir / "o.txt").write_text("d")
            m.set_gate("G", True)
            assert m.finish([m.out_dir / "o.txt"]) == "completed"
        verify_completed(w.analysis("d") / "manifest_t.json", w.repo)
    finally:
        shutil.rmtree(w.tmp, ignore_errors=True)


# ---- final repair 3: normalised dependency aliases are refused, not collapsed --------------------------------
def test_duplicate_normalised_dependency_aliases_fail_closed():
    for alias in ("code\\run.py", "./code/run.py", "code/x/../run.py", "code//run.py", ".\\code\\run.py"):
        w = World(extra_manifest_keys=[alias])
        try:
            raises(lambda: w.mk("r1"), "same logical path twice")
            assert w.status("r1") == "aborted"
        finally:
            shutil.rmtree(w.tmp, ignore_errors=True)
    w = World(extra_manifest_keys=["../outside.py"])                                  # escaping key is refused too
    try:
        raises(lambda: w.mk("r2"), "not repository-relative")
    finally:
        shutil.rmtree(w.tmp, ignore_errors=True)


if __name__ == "__main__":
    tests =[(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    failed = 0
    for n, f in tests:
        try:
            f()
            print("PASS", n)
        except Exception as e:                                                        # noqa: BLE001
            failed += 1
            print("FAIL", n, "->", type(e).__name__, e)
    print("%d tests, %d failed" % (len(tests), failed))
    sys.exit(1 if failed else 0)
