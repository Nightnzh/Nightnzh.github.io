#!/usr/bin/env python3
# 由單一份中英文案產生 index.html：
# 中文預先渲染進 HTML（無 JS 也讀得到、對 SEO 友善），英文放在 JS 字典；
# 切換時 JS 從 DOM 收割中文、從字典取英文，兩邊互換 —— 文案不重複維護。
import html, json, pathlib

C = {
  "kicker":      ("Agent Workflows · Android", "Agent Workflows · Android"),
  "name":        ("許証皓", "Kevin Hsu"),
  "nameAlt":     ("Kevin Hsu · Android / App Engineer", "許証皓 · Android / App Engineer"),
  "tagline":     ("我把自己的開發流程做成 agent 工作流——讓領域規則變成可被審查、可被重複執行的東西。",
                  "I turn my own development process into agent workflows — so domain rules become something reviewable and repeatable."),
  "taglineSub":  ("重點不是「用 AI 寫得比較快」。而是把真正能抓到 bug 的判斷——硬體事件監聽器的歸屬、付款階段的轉換、產品線之間的隔離——從一個人的經驗，變成整個團隊每次改動都會跑到的檢查。",
                  "Not “using AI to write code faster”. The point is to take the judgement that actually catches bugs — who owns a hardware event listener, how payment stages hand over, where product lines must stay isolated — and move it out of one engineer’s head into a check that runs on every change."),
  "flowLabel":   ("Review Workflow", "Review Workflow"),
  "n1":          ("diff", "diff"),
  "n2":          ("分派", "dispatch"),
  "n3a":         ("通用正確性與死碼", "Correctness & dead code"),
  "n3b":         ("硬體事件生命週期", "Hardware event lifecycle"),
  "n3c":         ("flavor 洩漏與相容性", "Flavor leaks & compatibility"),
  "n4":          ("對抗式驗證", "adversarial verify"),
  "n5":          ("結論 + 檔案:行號", "verdict + file:line"),
  "flowFanout":  ("FAN-OUT", "FAN-OUT"),
  "flowVerify":  ("VERIFY", "VERIFY"),
  "flowCaption": ("一支 MR 進來，先依領域拆成數條並行審查，每條的 findings 再交給獨立的驗證者嘗試推翻——只有被推翻不了的才進結論。落地在一個每天出貨到門市的 Android 產線上，不是玩具專案。",
                  "A merge request fans out into parallel reviews by domain; each finding then goes to independent verifiers whose job is to refute it — only what survives reaches the verdict. Running against an Android product line that ships to real stores, not a toy repo."),
  "p1t": ("規則要能被執行，不只被記錄", "Rules must execute, not just be documented"),
  "p1b": ("寫在文件裡的 review 準則會被遺忘。編碼成 skill 與 subagent 之後，它每次改動都會跑，而且會指到具體的檔案與行號。",
          "Review conventions written in a doc get forgotten. Encoded as skills and subagents, they run on every change — and point at a specific file and line."),
  "p2t": ("先重現，再修", "Reproduce first, then fix"),
  "p2b": ("bugfix 的定義是「寫一個會失敗的測試讓它通過」。agent 也一樣：先讓它產出能重現問題的證據，再談解法。",
          "A bugfix means writing a failing test and making it pass. Agents are held to the same bar: produce evidence that reproduces the problem before proposing a fix."),
  "p3t": ("不信任單一結論", "Never trust a single verdict"),
  "p3b": ("單一 agent 的判斷會有自信但錯誤的時候。用獨立的驗證者去推翻它，推翻不掉的才留下。",
          "One agent can be confidently wrong. Independent verifiers try to refute each finding; only what cannot be refuted survives."),
  "contactLabel":   ("Contact", "Contact"),
  "locationLabel":  ("Location", "Location"),
  "location":       ("桃園，台灣", "Taoyuan, Taiwan"),
  "availability":   ("可配合台北／新北・對遠端工作有興趣", "Open to Taipei / New Taipei & remote"),
  "eduLabel":  ("Education", "Education"),
  "eduSchool": ("國立虎尾科技大學", "National Formosa University"),
  "eduDept":   ("資訊工程系", "B.E., Computer Science & Information Engineering"),
  "eduPeriod": ("2015 — 2019", "2015 — 2019"),
  "expLabel":  ("Experience", "Experience"),
  "expIntro":  ("上面那套工作流不是憑空設計的——它長在下面這條產線上：真的錢、真的硬體、真的已出貨機台。",
                "That workflow was not designed in the abstract — it grew on the product line below: real money, real hardware, real units already in the field."),
  "j1role":   ("Android 軟體工程師", "Android Software Engineer"),
  "j1org":    ("鴻智互動 Cashier Tech", "Cashier Tech"),
  "j1period": ("2022.08 — 現在", "Aug 2022 — Present"),
  "j1place":  ("新北市", "New Taipei City"),
  "j2role":   ("Software Engineer (Android)", "Software Engineer (Android)"),
  "j2org":    ("臻鼎科技集團", "Zhen Ding Tech Group"),
  "j2period": ("2020.03 — 2021.09", "Mar 2020 — Sep 2021"),
  "j2place":  ("桃園市", "Taoyuan"),
  "skillsLabel": ("Skills", "Skills"),
  "ctaLabel":    ("Open to Opportunities", "Open to Opportunities"),
  "ctaBody":     ("目前會考慮了解新的機會：Android／行動端，或把 agent 工作流真正做進團隊開發流程的題目。架構與取捨很樂意當面聊。",
                  "Open to new opportunities: Android / mobile, or work on getting agent workflows genuinely into a team’s development process. Happy to walk through architecture and trade-offs."),
}

J1 = [
 ("把 code review 的領域規則工具化：硬體事件 observer 生命週期、付款階段轉換、kiosk／pos／cubbies 三條產品線的隔離檢查",
  "Encoded review domain rules into tooling: hardware-event observer lifecycles, payment stage transitions, and isolation checks across three product lines (kiosk / pos / cubbies)"),
 ("主導付款模組架構重構，將 Java MVP 漸進遷移至 Kotlin MVVM，降低耦合並提升可測試性",
  "Led the re-architecture of the payment module, migrating Java MVP to Kotlin MVVM incrementally, cutting coupling and making it testable"),
 ("導入 MockK + Robolectric 單元測試框架，補強付款、會員點數、優惠券等核心邏輯覆蓋率，並接入 GitLab CI 自動化驗證",
  "Introduced MockK + Robolectric unit testing on payment, loyalty-point and coupon logic, wired into GitLab CI"),
 ("整合多元支付方案與紙鈔機、硬幣機等現金硬體，處理多階段找零與退券流程",
  "Integrated multiple payment providers plus bill acceptors and coin hoppers, covering multi-stage change-return and refund flows"),
 ("主導 AGP 8.13.2 + Kotlin 2.0 升級工程，建置 Jetpack Compose 設計系統與可重用元件庫",
  "Led the AGP 8.13.2 + Kotlin 2.0 upgrade and built a Jetpack Compose design system with a reusable component library"),
 ("整合 USB / Serial / TCP 周邊硬體，並維護 LAN NSD 設備探索與離線容錯背景同步",
  "Integrated USB / serial / TCP peripherals and maintained LAN NSD device discovery with fault-tolerant background sync"),
]
J2 = [
 ("將舊有 Eclipse 專案翻新為 Android Studio 專案，並開發 SDK 模組",
  "Modernised a legacy Eclipse project into Android Studio and developed SDK modules"),
 ("導入 MVVM 架構，建立程式碼架構規範，降低長期維護成本",
  "Introduced MVVM, establishing code structure conventions and lowering maintenance cost"),
 ("開發與維護供公司內部使用的 App，提升公司作業效率",
  "Built and maintained internal apps that improved operational efficiency company-wide"),
]
SKILLS = [
 ("Agent / AI", "Claude Code skills 與 subagent・MCP server・多階段 agent 工作流設計・review 自動化・結構化輸出與驗證",
               "Claude Code skills & subagents · MCP servers · multi-stage agent workflow design · review automation · structured output and verification"),
 ("Languages", "Kotlin・Java・Python・TypeScript・Dart", "Kotlin · Java · Python · TypeScript · Dart"),
 ("Android",   "Jetpack Compose・MVVM（ViewModel / LiveData / Coroutines / Flow）・Room・CameraX・多模組 Gradle・product flavors・AGP 8・Kotlin 2.0・Kotlin KMP・Flutter",
               "Jetpack Compose · MVVM (ViewModel / LiveData / Coroutines / Flow) · Room · CameraX · multi-module Gradle · product flavors · AGP 8 · Kotlin 2.0 · Kotlin KMP · Flutter"),
 ("Testing / CI", "JUnit・MockK・Robolectric・GitLab CI・detekt / checkstyle / lint", "JUnit · MockK · Robolectric · GitLab CI · detekt / checkstyle / lint"),
 ("Hardware",  "USB / Serial / TCP・紙鈔機・硬幣機・熱感發票與標籤印表機・條碼掃描器・LAN NSD 設備探索",
               "USB / serial / TCP · bill acceptors · coin hoppers · thermal receipt and label printers · barcode scanners · LAN NSD device discovery"),
 ("Backend",   "Spring Boot・REST API・WebSocket（STOMP）", "Spring Boot · REST API · WebSocket (STOMP)"),
]

EN = {k: v[1] for k, v in C.items()}
for i, (zh, en) in enumerate(J1): EN[f"j1p{i}"] = en
for i, (zh, en) in enumerate(J2): EN[f"j2p{i}"] = en
for i, (k, zh, en) in enumerate(SKILLS): EN[f"sk{i}v"] = en

def t(key):
    """輸出中文（HTML 轉義）與 i18n key"""
    return f'data-i="{key}">{html.escape(C[key][0])}'

def bullets(items, prefix):
    out = []
    for i, (zh, _) in enumerate(items):
        out.append(f'<li><span class="dash">—</span><span data-i="{prefix}p{i}">{html.escape(zh)}</span></li>')
    return "\n            ".join(out)

def skillrows():
    out = []
    for i, (k, zh, _) in enumerate(SKILLS):
        out.append(f'<div class="srow"><div class="skey mono">{html.escape(k)}</div>'
                   f'<div class="sval" data-i="sk{i}v">{html.escape(zh)}</div></div>')
    return "\n          ".join(out)

DOC = f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>許証皓 Kevin Hsu — Android / App Engineer</title>
<meta name="description" content="Android / App Engineer。把開發流程做成 agent 工作流，讓領域規則變成可被審查、可被重複執行的東西。餐飲 POS 與硬體整合，5 年以上經驗。">
<meta property="og:type" content="profile">
<meta property="og:title" content="許証皓 Kevin Hsu — Android / App Engineer">
<meta property="og:description" content="把開發流程做成 agent 工作流，讓領域規則變成可被審查、可被重複執行的東西。">
<meta property="og:image" content="https://nightnzh.github.io/avatar.jpg">
<meta name="twitter:card" content="summary">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><text y='25' font-size='26'>%F0%9F%AA%AA</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Noto+Sans+TC:wght@400;500;700&display=swap">
<style>
  :root {{
    --bg:#f7f8fa; --ink:#101319; --muted:#666d79; --dim:#9aa1ad;
    --rule:#e3e6eb; --hair:#eceef2; --accent:#2f3fd4; --card:#fff;
  }}
  *,*::before,*::after {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--ink);
    font-family:'Archivo','Noto Sans TC','PingFang TC',system-ui,-apple-system,sans-serif;
    -webkit-font-smoothing:antialiased; }}
  .mono {{ font-family:'JetBrains Mono',ui-monospace,SFMono-Regular,monospace; }}
  a {{ color:var(--accent); text-decoration:none; border-bottom:1px solid rgba(47,63,212,.3); }}
  a:hover {{ color:#1b28a0; border-bottom-color:#1b28a0; }}
  .wrap {{ max-width:1120px; margin:0 auto; padding:0 64px 88px; }}

  .top {{ display:flex; justify-content:space-between; align-items:center; gap:32px; padding:52px 0 26px; }}
  .id {{ display:flex; align-items:center; gap:26px; }}
  .id img {{ width:120px; height:120px; border-radius:50%; display:block;
    border:1px solid #dcdfe5; flex-shrink:0; object-fit:cover; }}
  .idtext {{ display:flex; flex-direction:column; gap:8px; }}
  .kicker {{ font-size:11px; letter-spacing:.16em; text-transform:uppercase; color:var(--accent); }}
  h1 {{ margin:0; font-size:38px; font-weight:700; letter-spacing:-.02em; line-height:1.06; }}
  .sub {{ font-size:16px; color:var(--muted); }}

  .lang {{ display:flex; border:1px solid #dcdfe5; border-radius:2px; overflow:hidden; flex-shrink:0; }}
  .lang button {{ font:inherit; font-size:12.5px; padding:7px 15px; border:0; cursor:pointer;
    background:transparent; color:var(--muted); font-weight:500; }}
  .lang button[aria-pressed="true"] {{ background:var(--accent); color:#fff; font-weight:600; }}

  .bar {{ height:2px; background:var(--ink); }}
  .tagline {{ margin:0; padding:30px 0 8px; font-size:26px; line-height:1.42;
    letter-spacing:-.01em; max-width:860px; text-wrap:pretty; }}
  .taglinesub {{ margin:0; padding:0 0 34px; font-size:16px; line-height:1.7;
    color:var(--muted); max-width:760px; text-wrap:pretty; }}

  .flow {{ border:1px solid var(--rule); background:var(--card); border-radius:3px; padding:26px 30px 22px; }}
  .flow > .label {{ font-size:10px; letter-spacing:.15em; text-transform:uppercase;
    color:var(--dim); padding-bottom:18px; }}
  .flowscroll {{ overflow-x:auto; }}
  .flow svg {{ display:block; min-width:660px; width:100%; }}
  .flowcap {{ margin:16px 0 0; font-size:13.5px; line-height:1.65; color:var(--muted); text-wrap:pretty; }}

  .principles {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:28px; padding:40px 0 4px; }}
  .principles > div {{ display:flex; flex-direction:column; gap:9px; padding-top:16px; border-top:2px solid var(--ink); }}
  .pno {{ font-size:11px; color:var(--accent); }}
  .ptitle {{ font-size:17px; font-weight:600; letter-spacing:-.01em; line-height:1.35; }}
  .pbody {{ margin:0; font-size:14px; line-height:1.66; color:#4d5461; text-wrap:pretty; }}

  .split {{ height:1px; background:var(--rule); margin:44px 0 0; }}
  .cols {{ display:grid; grid-template-columns:268px minmax(0,1fr); gap:56px; padding-top:40px; }}
  .rail {{ display:flex; flex-direction:column; gap:30px; }}
  .block {{ display:flex; flex-direction:column; gap:9px; }}
  .blabel {{ font-size:10px; letter-spacing:.15em; text-transform:uppercase; color:var(--dim); }}
  .rail a, .rail div {{ font-size:14px; }}
  /* column flex 會把 <a> 拉成滿寬，底線就會超出文字 —— 收回成內容寬度 */
  .rail a {{ align-self:flex-start; }}
  .rail .small {{ font-size:13px; line-height:1.5; color:var(--muted); }}
  .rail .strong {{ font-size:14px; font-weight:600; line-height:1.45; }}
  .rail .period {{ font-size:12px; color:var(--dim); }}

  .main {{ display:flex; flex-direction:column; gap:42px; }}
  .seclabel {{ font-size:10px; letter-spacing:.15em; text-transform:uppercase; color:var(--accent); }}
  .section {{ display:flex; flex-direction:column; gap:20px; }}
  .intro {{ margin:0; font-size:14.5px; line-height:1.7; color:var(--muted); text-wrap:pretty; }}
  .job {{ display:flex; flex-direction:column; gap:11px; padding-bottom:26px; border-bottom:1px solid var(--rule); }}
  .jobhead {{ display:flex; justify-content:space-between; align-items:baseline; gap:20px; }}
  .jrole {{ font-size:19px; font-weight:600; letter-spacing:-.01em; }}
  .jorg {{ font-size:14.5px; color:var(--muted); }}
  .jmeta {{ font-size:12px; color:var(--dim); text-align:right; white-space:nowrap; line-height:1.6; }}
  .job ul {{ list-style:none; margin:2px 0 0; padding:0; display:flex; flex-direction:column; gap:7px; }}
  .job li {{ display:grid; grid-template-columns:16px minmax(0,1fr); gap:4px;
    font-size:14.5px; line-height:1.62; color:#2a2f38; }}
  .dash {{ color:var(--accent); }}
  .job li span:last-child {{ text-wrap:pretty; }}

  .srow {{ display:grid; grid-template-columns:132px minmax(0,1fr); gap:20px;
    padding:11px 0; border-top:1px solid var(--hair); }}
  .skey {{ font-size:12px; letter-spacing:.02em; }}
  .sval {{ font-size:14px; line-height:1.6; color:#4d5461; text-wrap:pretty; }}

  .cta {{ display:flex; flex-direction:column; gap:10px; padding:24px 26px;
    background:var(--ink); color:#f2f3f6; border-radius:2px; }}
  .cta .seclabel {{ color:#8f9bf5; }}
  .cta p {{ margin:0; font-size:15px; line-height:1.66; color:#d3d6de; text-wrap:pretty; }}
  .cta a {{ font-size:15px; font-weight:600; color:#a9b3f8;
    border-bottom-color:rgba(169,179,248,.4); margin-top:4px; align-self:flex-start; }}

  @media (max-width:920px) {{
    .wrap {{ padding:0 28px 64px; }}
    .top {{ flex-direction:column; align-items:flex-start; gap:20px; padding:36px 0 22px; }}
    .id {{ gap:18px; }}
    .id img {{ width:88px; height:88px; }}
    h1 {{ font-size:30px; }}
    .tagline {{ font-size:21px; padding-top:24px; }}
    .flow {{ padding:20px 18px 18px; }}
    .principles {{ grid-template-columns:1fr; gap:22px; padding-top:32px; }}
    .cols {{ grid-template-columns:1fr; gap:36px; padding-top:32px; }}
    .jobhead {{ flex-direction:column; gap:6px; }}
    .jmeta {{ text-align:left; }}
    .srow {{ grid-template-columns:1fr; gap:3px; padding:10px 0; }}
  }}
  @media print {{
    @page {{ size:A4; margin:13mm 14mm; }}
    :root {{ --bg:#fff; --card:#fff; }}
    body {{ background:#fff; font-size:11px; }}
    .wrap {{ max-width:none; padding:0; }}
    .lang {{ display:none; }}          /* 切換鈕在紙上沒有意義 */
    /* A4 的 CSS 寬度約 794px < 920px，手機斷點會一起套用進來；
       以下幾條把被覆寫掉的桌機排版拉回來，否則縱向空間浪費很大。 */
    .top {{ flex-direction:row; align-items:center; padding:0 0 14px; }}
    .id img {{ width:84px; height:84px; }}
    h1 {{ font-size:25px; }}
    .sub {{ font-size:12.5px; }}
    .kicker {{ font-size:9px; }}
    .tagline {{ font-size:16px; padding:16px 0 6px; max-width:none; }}
    .taglinesub {{ font-size:11px; line-height:1.6; padding-bottom:16px; max-width:none; }}
    .flow {{ padding:14px 16px 12px; break-inside:avoid; }}
    .flowscroll {{ overflow:visible; }}
    .flow svg {{ min-width:0; }}
    .flowcap {{ font-size:10px; margin-top:10px; }}
    .principles {{ grid-template-columns:repeat(3,minmax(0,1fr)); gap:16px; padding:20px 0 0; break-inside:avoid; }}
    .ptitle {{ font-size:12.5px; }}
    .pbody {{ font-size:10px; line-height:1.55; }}
    .split {{ margin:20px 0 0; }}
    /* A4 內容寬度放不下 268px 側欄 + 主欄，改為單欄、側欄橫排 */
    .cols {{ grid-template-columns:1fr; gap:18px; padding-top:18px; }}
    .rail {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:18px; align-items:start; }}
    .rail .small, .rail .period {{ font-size:9.5px; }}
    .rail a, .rail div {{ font-size:10.5px; }}
    .main {{ gap:20px; }}
    .job {{ break-inside:avoid; padding-bottom:14px; }}
    .jobhead {{ flex-direction:row; align-items:baseline; }}
    .jmeta {{ text-align:right; }}
    .jrole {{ font-size:14px; }}
    .jorg, .intro {{ font-size:11px; }}
    .job li {{ font-size:10.5px; line-height:1.5; }}
    .srow {{ grid-template-columns:120px minmax(0,1fr); gap:16px; padding:6px 0; break-inside:avoid; }}
    .sval {{ font-size:10.5px; line-height:1.5; }}
    .cta {{ padding:14px 16px; break-inside:avoid; }}
    .cta p, .cta a {{ font-size:11px; }}
    a {{ border-bottom:none; }}
  }}
  @media (max-width:480px) {{
    .wrap {{ padding:0 20px 56px; }}
    h1 {{ font-size:26px; }}
    .tagline {{ font-size:19px; }}
  }}
</style>
</head>
<body>
<div class="wrap">

  <header class="top">
    <div class="id">
      <img src="avatar.jpg" alt="許証皓 Kevin Hsu" width="120" height="120">
      <div class="idtext">
        <div class="kicker mono" {t('kicker')}</div>
        <h1 {t('name')}</h1>
        <div class="sub" {t('nameAlt')}</div>
      </div>
    </div>
    <div class="lang" role="group" aria-label="Language">
      <button type="button" id="btn-zh" aria-pressed="true">中文</button>
      <button type="button" id="btn-en" aria-pressed="false">EN</button>
    </div>
  </header>

  <div class="bar"></div>

  <p class="tagline" {t('tagline')}</p>
  <p class="taglinesub" {t('taglineSub')}</p>

  <section class="flow">
    <div class="label mono" {t('flowLabel')}</div>
    <div class="flowscroll">
    <svg viewBox="0 0 940 212" role="img" aria-label="review workflow" fill="none" xmlns="http://www.w3.org/2000/svg">
      <g stroke="var(--accent)" stroke-width="1.25" stroke-linecap="round">
        <path d="M108 106 H142"/>
        <path d="M136 101 l7 5 -7 5" fill="var(--accent)" stroke="none"/>
        <path d="M232 106 H258 M258 106 V38 H286 M258 106 H286 M258 106 V174 H286"/>
        <path d="M280 33 l7 5 -7 5" fill="var(--accent)" stroke="none"/>
        <path d="M280 101 l7 5 -7 5" fill="var(--accent)" stroke="none"/>
        <path d="M280 169 l7 5 -7 5" fill="var(--accent)" stroke="none"/>
        <path d="M540 38 H568 V106 M540 106 H568 M540 174 H568 V106 M568 106 H594"/>
        <path d="M588 101 l7 5 -7 5" fill="var(--accent)" stroke="none"/>
        <path d="M714 106 H752"/>
        <path d="M746 101 l7 5 -7 5" fill="var(--accent)" stroke="none"/>
      </g>
      <rect x="2" y="86" width="106" height="40" rx="2" stroke="#c9ced7" stroke-width="1.25" fill="var(--bg)"/>
      <text x="55" y="111" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="12" fill="var(--ink)" {t('n1')}</text>
      <rect x="142" y="86" width="90" height="40" rx="2" stroke="#101319" stroke-width="1.5" fill="#101319"/>
      <text x="187" y="111" text-anchor="middle" font-size="13" font-weight="600" fill="#fff" {t('n2')}</text>
      <rect x="286" y="18" width="254" height="40" rx="2" stroke="#c9ced7" stroke-width="1.25" fill="#fff"/>
      <text x="303" y="43" font-size="13" fill="var(--ink)" {t('n3a')}</text>
      <rect x="286" y="86" width="254" height="40" rx="2" stroke="#c9ced7" stroke-width="1.25" fill="#fff"/>
      <text x="303" y="111" font-size="13" fill="var(--ink)" {t('n3b')}</text>
      <rect x="286" y="154" width="254" height="40" rx="2" stroke="#c9ced7" stroke-width="1.25" fill="#fff"/>
      <text x="303" y="179" font-size="13" fill="var(--ink)" {t('n3c')}</text>
      <rect x="594" y="86" width="120" height="40" rx="2" stroke="var(--accent)" stroke-width="1.5" fill="#fff"/>
      <text x="654" y="111" text-anchor="middle" font-size="13" font-weight="600" fill="var(--accent)" {t('n4')}</text>
      <rect x="752" y="86" width="186" height="40" rx="2" stroke="#c9ced7" stroke-width="1.25" fill="var(--bg)"/>
      <text x="845" y="111" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="12" fill="var(--ink)" {t('n5')}</text>
      <text x="286" y="10" font-family="JetBrains Mono, monospace" font-size="10" letter-spacing="1.4" fill="var(--dim)" {t('flowFanout')}</text>
      <text x="594" y="76" font-family="JetBrains Mono, monospace" font-size="10" letter-spacing="1.4" fill="var(--dim)" {t('flowVerify')}</text>
    </svg>
    </div>
    <p class="flowcap" {t('flowCaption')}</p>
  </section>

  <section class="principles">
    <div><div class="pno mono">01</div><div class="ptitle" {t('p1t')}</div><p class="pbody" {t('p1b')}</p></div>
    <div><div class="pno mono">02</div><div class="ptitle" {t('p2t')}</div><p class="pbody" {t('p2b')}</p></div>
    <div><div class="pno mono">03</div><div class="ptitle" {t('p3t')}</div><p class="pbody" {t('p3b')}</p></div>
  </section>

  <div class="split"></div>

  <div class="cols">
    <aside class="rail">
      <div class="block">
        <div class="blabel mono" {t('contactLabel')}</div>
        <a href="mailto:nzh.xuu@gmail.com">nzh.xuu@gmail.com</a>
        <a href="https://github.com/Nightnzh">github.com/Nightnzh</a>
        <a href="https://www.linkedin.com/in/%E8%A8%BC%E7%9A%93-%E8%A8%B1-b586ab238/">LinkedIn</a>
      </div>
      <div class="block">
        <div class="blabel mono" {t('locationLabel')}</div>
        <div {t('location')}</div>
        <div class="small" {t('availability')}</div>
      </div>
      <div class="block">
        <div class="blabel mono" {t('eduLabel')}</div>
        <div class="strong" {t('eduSchool')}</div>
        <div class="small" {t('eduDept')}</div>
        <div class="period mono" {t('eduPeriod')}</div>
      </div>
    </aside>

    <main class="main">
      <section class="section">
        <div class="seclabel mono" {t('expLabel')}</div>
        <p class="intro" {t('expIntro')}</p>

        <article class="job">
          <div class="jobhead">
            <div style="display:flex;flex-direction:column;gap:3px">
              <div class="jrole" {t('j1role')}</div>
              <div class="jorg" {t('j1org')}</div>
            </div>
            <div class="jmeta mono"><span {t('j1period')}</span><br><span {t('j1place')}</span></div>
          </div>
          <ul>
            {bullets(J1, 'j1')}
          </ul>
        </article>

        <article class="job">
          <div class="jobhead">
            <div style="display:flex;flex-direction:column;gap:3px">
              <div class="jrole" {t('j2role')}</div>
              <div class="jorg" {t('j2org')}</div>
            </div>
            <div class="jmeta mono"><span {t('j2period')}</span><br><span {t('j2place')}</span></div>
          </div>
          <ul>
            {bullets(J2, 'j2')}
          </ul>
        </article>
      </section>

      <section class="section">
        <div class="seclabel mono" {t('skillsLabel')}</div>
        <div>
          {skillrows()}
        </div>
      </section>

      <section class="cta">
        <div class="seclabel mono" {t('ctaLabel')}</div>
        <p {t('ctaBody')}</p>
        <a href="mailto:nzh.xuu@gmail.com">nzh.xuu@gmail.com</a>
      </section>
    </main>
  </div>
</div>

<script>
// 中文已在 HTML 內；載入時把它收割成 zh 字典，英文取自 EN。
(function () {{
  var EN = {json.dumps(EN, ensure_ascii=False)};
  var nodes = document.querySelectorAll('[data-i]');
  var ZH = {{}};
  nodes.forEach(function (el) {{ ZH[el.getAttribute('data-i')] = el.textContent; }});

  var btnZh = document.getElementById('btn-zh');
  var btnEn = document.getElementById('btn-en');

  function apply(lang) {{
    var dict = lang === 'en' ? EN : ZH;
    nodes.forEach(function (el) {{
      var k = el.getAttribute('data-i');
      if (dict[k] != null) el.textContent = dict[k];
    }});
    document.documentElement.lang = lang === 'en' ? 'en' : 'zh-Hant';
    btnZh.setAttribute('aria-pressed', String(lang !== 'en'));
    btnEn.setAttribute('aria-pressed', String(lang === 'en'));
    try {{ localStorage.setItem('lang', lang); }} catch (e) {{}}
  }}

  btnZh.addEventListener('click', function () {{ apply('zh'); }});
  btnEn.addEventListener('click', function () {{ apply('en'); }});

  var saved = null;
  try {{ saved = localStorage.getItem('lang'); }} catch (e) {{}}
  if (saved === 'en') apply('en');
  else if (!saved) {{
    // 只有在瀏覽器明確表示非中文時才切英文；讀不到語系就維持預先渲染的中文
    var nav = navigator.language || '';
    if (nav && nav.slice(0, 2) !== 'zh') apply('en');
  }}
}})();
</script>
</body>
</html>
"""

out = pathlib.Path(__file__).parent / "index.html"
out.write_text(DOC, encoding="utf-8")
print(f"index.html 已產生：{len(DOC)} chars / i18n keys = {len(EN)}")
