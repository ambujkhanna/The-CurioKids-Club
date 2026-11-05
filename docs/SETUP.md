# The CurioKids Club: one-time setup (about 30 minutes, no cost)

This is the same process as AInation Studio, so you can reuse most of what you already have.

## 1. Create the YouTube channel

1. Go to YouTube, then your profile picture → **Settings** → **Add or manage your channel(s)** → **Create a channel**.
   Name it **The CurioKids Club**. This creates a Brand Account under the same Google login.
2. Set the handle to **@CurioKidsClub**.
   - **If that handle is taken:** pick another one. Then in Git Bash, inside this repo, run this (replace `NEWHANDLE`):
     ```bash
     sed -i 's/@CurioKidsClub/@NEWHANDLE/g' episodes/*/episode.json episodes/README.md
     ```
3. In YouTube Studio for the new channel, go to **Settings → Channel → Advanced settings → Audience** and choose
   **"Yes, set this channel as made for kids"**. Save.

**What "Made for Kids" means:** YouTube's law-based rules for children's content (COPPA) apply:
- comments are turned off
- no personalised ads (so earnings per view are lower)
- no notification bell and no mini-player on these videos
- the uploader also marks every video as Made for Kids

This is required for content aimed at children. Don't switch it off.

## 2. Put the code on GitHub

1. Create a new **private** repository, for example `curio-kids-automation`. Don't add a README.
2. Unzip this bundle into a folder.
3. In Git Bash, from inside that folder, run:
   ```bash
   git init -b main
   ```
   ```bash
   git add . && git commit -m "The CurioKids Club pipeline + 75 episodes"
   ```
   ```bash
   git remote add origin https://github.com/ambujkhanna/curio-kids-automation.git
   ```
   ```bash
   git push -u origin main
   ```
4. Open the repo's **Settings → Actions → General**. Under **Workflow permissions**, choose **Read and write permissions** and save. This lets the run save `state.json`.

## 3. Give the workflow permission to upload (reuse your Google project)

You can use the **same** Google Cloud project, "AInation Automation". It's already In production, so no new app is needed.

1. Open https://developers.google.com/oauthplayground.
2. Click the gear icon, tick **Use your own OAuth credentials**, and paste the **same** Client ID and Client secret you used for AInation.
3. In Step 1, scope:
   ```text
   https://www.googleapis.com/auth/youtube.upload
   ```
   Click **Authorize APIs**. When asked which channel, **choose The CurioKids Club**.
4. In Step 2, click **Exchange authorization code for tokens** and copy the **Refresh token**.
5. In the new repo, go to **Settings → Secrets and variables → Actions → New repository secret**, three times:
   - `YT_CLIENT_ID`: same as AInation
   - `YT_CLIENT_SECRET`: same as AInation
   - `YT_REFRESH_TOKEN`: the **new** token for The CurioKids Club

Notes:
- **Quota:** both channels share the project's free 10,000 units a day. Two uploads use about 3,200.
- **Privacy page:** add one line to `privacy.html` in the `ambujkhanna.github.io` repo saying the tool is also used for The CurioKids Club channel.

## 4. First runs

1. **Test without uploading:** Actions → **Daily Curio Kids Short** → **Run workflow**, tick **dry_run**.
   After about 15 minutes, download the MP4 from the run's **Artifacts** and watch it. Listen to Leo's voice especially. If you want a different voice, see "Changing voices" in `README.md`.
2. **Real run:** run the workflow again with dry_run unticked. The video arrives in YouTube Studio for The CurioKids Club as **Private**, scheduled for 16:00–19:00 IST.

Your Google project isn't audited, so every upload is Private. As with AInation, open Studio each day and set the new video to **Public** or **Schedule** it.

## 4b. Custom thumbnails

Each run designs a thumbnail and uploads it with the video. YouTube only accepts custom thumbnails from **verified** channels.
Verify each channel once at https://www.youtube.com/verify (a phone code). Until then the run still succeeds and the run summary says `Thumbnail: not set`.
The thumbnail JPG is also in the run's Artifacts if you want to add it by hand.

## 5. Running two channels from one GitHub account

- **AInation Studio** runs at 14:45 IST and posts at 17:00–20:00. **The CurioKids Club** runs at 14:10 IST and posts at 16:00–19:00.
- **GitHub's free minutes:** private repos get 2,000 minutes a month in total, shared by both repos. Each run takes about 15 minutes, so two channels use about 900 minutes a month, which is fine.
- **When episodes run out:** the run stays green and says "No ready episode left in the backlog". Add more episode files.

## 6. Keeping the channel healthy (kids' content rules)

- **Facts:** keep them accurate and gentle. Avoid anything scary, unsafe experiments, brands and copyrighted characters or songs.
- **Variety:** YouTube rewards it and limits mass-produced, repetitive content. Mix topics, poems and casts, as the 75 included episodes do.
- **AI disclosure:** the voices are AI-generated and the upload marks the video as altered or synthetic content.
- **Check before posting:** spot-check each video in Studio before you set it to Public. That daily click is your quality check.
