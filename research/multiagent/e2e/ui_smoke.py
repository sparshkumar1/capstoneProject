import sys, glob, json
from playwright.sync_api import sync_playwright
tag = sys.argv[1]
exe = (glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome") or glob.glob("/opt/pw-browsers/chromium/**/chrome", recursive=True))[0]
errs, logs = [], []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe, args=["--no-sandbox", "--use-fake-ui-for-media-stream", "--use-fake-device-for-media-stream"])
    pg = b.new_page(viewport={"width": 1280, "height": 900})
    pg.on("console", lambda m: logs.append((m.type, m.text[:200])) if m.type in ("error", "warning") else None)
    pg.on("pageerror", lambda e: errs.append(str(e)[:300]))
    pg.goto("http://127.0.0.1:3000/", wait_until="networkidle")
    pg.screenshot(path=f"{sys.argv[2]}/ui_{tag}_1_login.png")
    pg.fill("input[placeholder='Arjun Mehta']", "Audit Probe"); pg.fill("input[placeholder='arjun@college.edu']", f"probe_{tag}@example.com")
    btns = [t for t in pg.locator("button").all_inner_texts()]
    print("buttons on login:", btns)
    for label in ("Start", "Continue", "Begin", "Next", "Login"):
        loc = pg.get_by_role("button", name=label)
        if loc.count():
            loc.first.click(); break
    pg.wait_for_timeout(1500); pg.screenshot(path=f"{sys.argv[2]}/ui_{tag}_2_after_login.png")
    print("after login buttons:", pg.locator("button").all_inner_texts()[:25])
    print("headings:", pg.locator("h1,h2,h3").all_inner_texts()[:8])
    pg.get_by_text("Array Algorithms").first.click(); pg.get_by_text("Demo Interview").first.click()
    pg.get_by_role("button", name="Begin Interview").click()
    pg.wait_for_timeout(6000); pg.screenshot(path=f"{sys.argv[2]}/ui_{tag}_3_room.png", full_page=True)
    body = pg.inner_text("body"); print("room text sample:", body[:500].replace(chr(10)," | "))
    print("question visible:", "two indices" in body or "Explain your logic" in body)
    b.close()
print("page errors:", errs); print("console errors/warnings:", logs[:8])
