# How it works: the video factory in plain words

**For:** anyone, no technical background needed. **Same file in both repos.** Last updated 2026-11-23 09:15 (IST).
The diagrams below are drawn by GitHub automatically when you open this file on github.com.

---

## 1. The big picture

Think of it as a small **factory that runs by itself every day**. The factory building is **GitHub** (a free service that stores the project and runs jobs on a timetable). Each "job" is a recipe that turns a written script into a finished video and posts it.

```mermaid
flowchart LR
    A["📝 Scripts<br/>(episode files in the repo)"] --> B["🎙️ Voices<br/>(free AI voices)"]
    B --> C["🎨 Animation<br/>(characters, boards, pictures)"]
    C --> D["🎬 Finishing<br/>(captions, music, intro/outro)"]
    D --> E["✅ Quality checks"]
    E --> F["📤 Publish<br/>YouTube · Facebook · Instagram"]
    F --> G["📊 Learn<br/>(views, searches, comments)"]
    G -.->|"ideas for new topics"| A
```

Nobody has to press a button: GitHub starts each job at a fixed time. The owner only adds new content, flips switches, and (until Google approves the API audit) makes uploaded videos public in YouTube Studio.

---

## 2. A day in the factory (times in India, IST)

```mermaid
timeline
    title The CurioKids Club + AInation Studio: daily schedule (IST)
    03.11 : Spanish kids Short made, posts 05.30-07.30 (evening in Mexico)
    07.17 : Trend check, opens a Trend alert if a hot topic fits
    08.47 Monday : Weekly topic report (what people search for)
    11.41 : Automatic trend Short made, posts 12.00-14.00
    14.10 and 21.10 : English or Hindi kids Short (alternate days), posts 17.00-20.00 or 09.00-11.00
    14.53 : AInation daily Short, posts 17.00-20.00
    17.30 : Analytics collected for both channels, incl. views by country
    Friday night : Weekly art run on Kaggle, new pictures and icons for the coming week
    Weekend : Long videos (kids Saturday 10.00, AInation Sunday 10.07)
```

---

## 3. Where topics come from

```mermaid
flowchart TB
    subgraph Sources["Free sources the factory reads"]
      GT["🔥 Google Trends<br/>today's rising searches<br/>India · USA · Mexico"]
      YS["🔎 YouTube search suggestions<br/>what people type"]
      YT["📈 YouTube trending charts<br/>Education · Science · Animals"]
      CM["💬 Comments on our videos<br/>topics viewers ask for"]
      AN["📊 Our own analytics<br/>which videos people watch"]
    end
    Sources --> F{"Fits the channel?<br/>kid-safe? not made yet?"}
    F -->|"weekly"| R["📋 Topic report<br/>(GitHub issue with tick boxes)"]
    F -->|"daily, if hot"| TA["🚨 Trend alert<br/>(GitHub issue, emailed)"]
    F -->|"daily, first match"| TS["🤖 Automatic trend Short"]
    R --> O["👤 Owner picks topics → new scripts"]
```

**"Fits the channel"** means: kids = science, nature, body, space, weather, festivals (never anything on the block list); AInation = AI, apps, phones, chips. Sport, celebrities and news are ignored.

---

## 4. How one Short is made (step by step)

```mermaid
sequenceDiagram
    autonumber
    participant Clock as ⏰ GitHub timetable
    participant Q as 📚 Episode queue
    participant V as 🎙️ Voice maker
    participant A as 🎨 Animator
    participant Fin as 🎬 Finisher
    participant QC as ✅ Checker
    participant YT as 📺 YouTube / FB / IG
    participant Log as 🗂️ Records

    Clock->>Q: "Time for today's Short"
    Q->>Q: Pick the next episode not yet posted (English, Hindi or Spanish queue)
    Q->>QC: Check the script file (lines, pictures, lengths, translations)
    Q->>V: Lines + who says them
    V->>V: Speak each line (Kokoro or Chatterbox voices) and time every word
    V->>A: Audio + word timings
    A->>A: Draw every frame: Mia & Leo, room picture, board with icons that pop on their word
    A->>Fin: ~1,500 picture frames
    Fin->>Fin: Add captions, music, sound effects, end card, then join into an MP4
    Fin->>QC: Finished video
    QC->>QC: Length, sound, picture size, then an AI listens to it and compares with the script
    QC->>YT: Upload in the time slot, thumbnail, playlist, subtitles, translated titles
    YT->>Log: Link + status saved (so it is never posted twice)
```

What each step uses:

| Step | What does the work | Free / open? |
|---|---|---|
| Voices | **Kokoro** (English, Hindi, Spanish voices) and **Chatterbox** (more expressive English) | yes, open licences (Apache 2.0, MIT) |
| Characters, boards, animation | our own drawing code (**Skia** graphics library). Steady camera; the speaker gets a golden spotlight and steps forward; a board stays until the next picture appears | yes |
| Background pictures, picture boards, 3D icons | made on a free **Kaggle** GPU with **FLUX.1-schnell** (image AI) + **rembg** (cut-outs): by hand so far, and from now on by the **weekly art run** (it makes only what upcoming episodes are missing); extra icons from **Microsoft Fluent Emoji 3D** | yes (Apache 2.0, MIT) |
| Real photos (AInation) | **NASA** and **Openverse** (free-licence photos, credited) | yes |
| Music | composed by our code for each episode | yes |
| Captions, joining, sound | **FFmpeg** | yes |
| Listening check | **faster-whisper** (speech-to-text AI) | yes (MIT) |
| Upload | **YouTube Data API**, **Meta** (Facebook/Instagram) | free with limits |

---

## 5. How the automatic trend Short is written

```mermaid
flowchart TB
    T["1️⃣ Topic<br/>first relevant search of the day"] --> W["2️⃣ Facts<br/>matching Wikipedia article<br/>(Simple English for kids)"]
    W --> AI["3️⃣ Script<br/>free AI model <b>Qwen 2.5</b><br/>runs inside GitHub via <b>Ollama</b><br/>told: use ONLY these facts"]
    AI --> C1{"4️⃣ Format check<br/>same rules as our own scripts"}
    C1 -->|"problems"| AI
    C1 -->|"ok"| C2{"5️⃣ Fact check<br/>numbers must be in Wikipedia<br/>+ AI looks for contradictions"}
    C2 -->|"doubt"| AI
    C2 -->|"still wrong"| NEXT["Drop topic,<br/>try the next one (max 4)"]
    NEXT --> W
    C2 -->|"ok"| MAKE["6️⃣ Make the video<br/>(same steps as section 4)"]
    MAKE --> P["7️⃣ Publish 12:00-14:00 IST<br/>own queue, never the same topic twice"]
```

No paid AI service is used: the AI model is downloaded free and runs on GitHub's computer for a few minutes.

---

## 6. Learning and improving

```mermaid
flowchart LR
    YTA["📊 YouTube Analytics<br/>(read-only)"] --> GB["Growth brief<br/>best / weakest videos<br/>+ views by country"]
    GB --> RANK["Topics ranked by<br/>what works for us (★/▼)"]
    RANK --> RAD
    GB --> SUM["Shown in each daily run's summary"]
    RAD["📋 Weekly topic report"] --> OWN["👤 Owner ticks topics"]
    OWN --> NEW["New scripts in the queue"]
    TRN["🚨 Trend alerts"] --> OWN
```

---

## 7. Safety nets (why a bad video doesn't go out)

- Every script is **checked before anything is drawn**; a broken script stops the run with a list of problems.
- Pictures that can't be drawn (e.g. combined emoji 🦸‍♂️) are replaced by plain ones.
- Kids channel: a **block list** of words and topics that are never used.
- Finished video is **checked** (length, sound, size) and an AI **listens** to it.
- Automatic scripts: facts **only from Wikipedia**, numbers verified, contradictions checked; if unsure, the topic is skipped.
- Every upload is **recorded**, so nothing is posted twice.
- Every feature has an **on/off switch** (see `CONFIGURATION.md`).

---

## 8. What the owner does

| Task | How often |
|---|---|
| Push the bundles (code updates) | when a new bundle arrives |
| Make uploaded videos public in YouTube Studio | daily, until Google approves the API audit |
| Tick topics in the weekly report / react to trend alerts | weekly / as they come |
| Change switches (variables) | rarely: list in `CONFIGURATION.md` |
| Check the weekly art run's new pictures (Artifacts) | weekly, until automatic install (`ART_AUTO_COMMIT=on`) is trusted |

Open tasks: `docs/TODO.md`. Plans: `docs/PRIVATE_CODE_PLAN.md`, `docs/PINTEREST_PLAN.md`. More detail: `CONFIGURATION.md` (all switches), `docs/AUTOMATION_KAGGLE.md`, `docs/TREND_SHORTS.md`, `docs/SPANISH.md`, `docs/RADAR_AND_ALERTS.md`, `docs/HD_ART.md`.
