# Build Your Own Autonomous Posting Engine

**A complete, plain-English setup guide.**

This guide walks you through building a system that posts to your social accounts
automatically, on a schedule, from a Notion calendar — without you touching an app at
posting time. You write and approve content in Notion. The system does the rest.

You do **not** need to know how to code. You need to be able to create accounts, copy
and paste, and talk to Claude.

**Time required:** about 30 minutes of clicking, then one big copy-paste.

---

## Table of contents

1. [What you are actually building](#1-what-you-are-actually-building)
2. [What it costs](#2-what-it-costs)
3. [Part 1 — Create your accounts (the clicking part)](#3-part-1--create-your-accounts-the-clicking-part)
4. [Part 2 — The master prompt (the one big paste)](#4-part-2--the-master-prompt-the-one-big-paste)
5. [Part 3 — Set up your Notion calendar](#5-part-3--set-up-your-notion-calendar)
6. [Part 4 — Your reel library (storing your own videos)](#6-part-4--your-reel-library-storing-your-own-videos)
7. [Part 5 — Using it day to day](#7-part-5--using-it-day-to-day)
8. [Part 6 — When something breaks](#8-part-6--when-something-breaks)
9. [Appendix — How it works under the hood](#9-appendix--how-it-works-under-the-hood)

---

## 1. What you are actually building

Five pieces that pass work down a line:

```
   NOTION                SUPABASE                  UPLOAD-POST         YOUR ACCOUNTS
   (your calendar)       (the engine)              (the delivery)      (where it lands)

   You write a post  ->  A robot checks every  ->  Hands the post  ->  Instagram
   and mark it           10-15 min for posts       to each network     TikTok
   "Approved"            that are approved                             YouTube
                         AND due right now                             LinkedIn, X...
```

**In plain words:**

- **Notion** is your writing desk and calendar. You draft posts, attach the video or
  image, pick the platforms, pick a date and time, and flip a switch to `Approved`.
- **Supabase** is the engine room. It is a free database that can also run small
  programs on a timer. It holds every post, stores your videos, and wakes up every 15
  minutes to ask: *is anything approved and due?*
- **Upload-Post** is the delivery service. It is one company that has already done the
  painful work of connecting to Instagram, TikTok, YouTube and 10+ others. You connect
  your accounts to it once; after that your engine only has to talk to Upload-Post.
- **Claude** is your builder and your assistant. It builds all of this for you, and
  afterwards you talk to it to upload reels, schedule posts, and check what's failing.

### The one rule that makes this safe

**Nothing ever posts by itself unless you explicitly approved it.**

A post only goes out when two things are true at the same time:

1. Its status is `Approved`, and
2. Its scheduled time has already passed.

If either is missing, it sits still. There is no way for a draft to escape. This is
deliberate — it is the single most important design decision in the whole system, and
you should not let anyone talk you out of it.

---

## 2. What it costs

| Thing | Cost | Notes |
|---|---|---|
| Supabase | **Free** to start | The free tier is genuinely enough. Paid is ~$25/mo if you outgrow it. |
| Upload-Post | **Free tier available** | Paid plans (roughly $9–$29/mo) raise your monthly post limits. |
| Notion | **Free** | The free personal plan is fine. |
| Claude | Your existing plan | You need the Supabase connector, covered in Part 1. |

You can build and test the entire thing for **$0**.

---

## 3. Part 1 — Create your accounts (the clicking part)

Do these four things **before** you paste anything into Claude. Keep a scratch note open
— you are going to collect five values along the way.

> **Scratch note template** — fill this in as you go:
> ```
> SUPABASE_PROJECT_URL   = https://xxxxxxxx.supabase.co
> UPLOADPOST_API_KEY     = ..........
> UPLOADPOST_PROFILE     = ..........   (the username you choose in step 2)
> NOTION_TOKEN           = ntn_.........
> NOTION_DATABASE_ID     = ..........
> ```
> Treat the API key and the Notion token like passwords. Don't paste them into a public
> chat, a GitHub issue, or anywhere they'd be stored in the clear.

### Step 1 — Supabase (the engine room)

1. Go to **supabase.com** and sign up (GitHub login is quickest).
2. Click **New project**. Give it any name — `posting-engine` is fine.
3. Pick a database password. **Save it in your password manager.** You will rarely need
   it, but you cannot recover it later.
4. Pick the region closest to you. Click **Create new project** and wait ~2 minutes.
5. Once it's up, go to **Project Settings → API**. Copy the **Project URL** into your
   scratch note.

### Step 2 — Upload-Post (the delivery service)

1. Go to **upload-post.com** and create an account.
2. Find the **API key** in your dashboard settings. Copy it into your scratch note.
3. Create a **profile**. A profile is just a named bundle of connected social accounts —
   think of it as "the accounts for this one brand". Name it something simple and
   lowercase, like your brand name. Write that name in your scratch note as
   `UPLOADPOST_PROFILE`.
4. Connect your social accounts to that profile. Upload-Post gives you a connect link,
   and you click through each network's normal login-and-approve screen.

> **Important:** the connect link expires after **48 hours**. If you come back later and
> it's dead, just generate a new one — nothing is lost.

> **Also important:** only connect accounts you actually intend to post to. The engine
> checks which platforms are genuinely linked before each post and skips the rest, so a
> half-connected account is a silent no-post rather than an error.

### Step 3 — Notion (your calendar)

1. Go to **notion.so/my-integrations** and click **New integration**.
2. Name it `Posting Engine`. Give it **Read** and **Update** content capabilities.
3. Click **Submit**, then copy the **Internal Integration Token** (starts with `ntn_`)
   into your scratch note.
4. Create a new page in Notion, and inside it add a **Table** database. Name it
   `Content Calendar`. Leave it empty for now — Part 3 sets up the columns.
5. Open that database, click the **`...`** menu in the top right → **Connections** →
   **Connect to** → pick `Posting Engine`.

   > If you skip this step nothing will work. The integration can only see databases you
   > have explicitly connected it to. This is the single most commonly missed step in
   > the whole guide.

6. Get the database ID: open the database as a full page and look at the URL.
   ```
   https://notion.so/myworkspace/8f2c1a4b9d3e4f5a6b7c8d9e0f1a2b3c?v=...
                                 └──────── this part is your database ID ────────┘
   ```
   Copy it into your scratch note.

### Step 4 — Connect Claude to your Supabase

Claude needs permission to build inside your Supabase project.

1. In Claude, open your **connector / integration settings**.
2. Add the **Supabase** connector and authorise it.
3. Confirm it worked by asking Claude:
   > `List my Supabase projects.`

   If it names your project, you're ready. If it doesn't, fix this before continuing —
   every step from here on depends on it.

---

## 4. Part 2 — The master prompt (the one big paste)

This is the moment everything gets built. Fill in the five values from your scratch note
at the top, then paste the **whole thing** into Claude as a single message.

It will take Claude several minutes and a lot of steps. Let it work. If it stops partway
and asks a question, answer it and say `continue`.

> **Before you paste:** replace every `<PLACEHOLDER>` below. If you leave one in, Claude
> will stop and ask you for it anyway — no harm done, just slower.

````text
I want you to build an autonomous social media posting engine inside my Supabase project.
Use the Supabase tools to do the work directly. Here are my details:

  SUPABASE_PROJECT_URL = <PASTE YOUR PROJECT URL>
  UPLOADPOST_API_KEY   = <PASTE YOUR UPLOAD-POST API KEY>
  UPLOADPOST_PROFILE   = <PASTE YOUR UPLOAD-POST PROFILE NAME>
  NOTION_TOKEN         = <PASTE YOUR NOTION TOKEN>
  NOTION_DATABASE_ID   = <PASTE YOUR NOTION DATABASE ID>

Build all of the following. Explain each step to me in plain English as you go, and tell
me clearly when you are finished.

=== 1. SECRETS ===
Store these four secrets in Supabase Vault. Generate the two cron secrets yourself as
long random strings and tell me what they are at the end:
  - UPLOADPOST_API_KEY   (the value above)
  - NOTION_TOKEN         (the value above)
  - PUBLISH_CRON_SECRET  (you generate)
  - CLEANUP_CRON_SECRET  (you generate)

Create a SECURITY DEFINER function `public.get_publisher_secret(_name text) returns text`
with `search_path` set to empty, which reads `decrypted_secret` from
`vault.decrypted_secrets` by name. Every function below reads its secrets through this,
so no API key is ever hardcoded into a function.

=== 2. TABLES ===
Create `public.social_posts` — the single source of truth for every post:
  id uuid primary key default gen_random_uuid()
  title text, caption text
  platform text not null           -- comma-separated, e.g. 'instagram,tiktok'
  publisher_profile text not null default '<UPLOADPOST_PROFILE>'
  status text not null default 'draft'   -- draft|approved|queued|posted|failed|rejected
  scheduled_for timestamptz
  posted_at timestamptz, created_at timestamptz not null default now()
  approved_at timestamptz, approved_by uuid, rejected_at timestamptz, review_note text
  media_url text                   -- PUBLIC https URL(s), comma-separated for carousels
  media_content_type text          -- e.g. 'video/mp4' or 'image/png'
  media_storage_path text, media_sha256 text, media_bytes bigint
  media_stored_at timestamptz, media_deleted_at timestamptz, media_error text
  source_media_url text
  external_id text, permalink text, error text
  notion_page_id text
  audience text, pillar text

Add a partial unique index on notion_page_id where it is not null. This is essential —
without it the Notion importer creates duplicate rows on every single run.

Create `public.social_post_metrics`: id, post_id (fk to social_posts), captured_at
default now(), and bigint columns views, likes, comments, shares, saves.

Create `public.reel_library` — my personal video library:
  id uuid primary key default gen_random_uuid()
  title text not null
  storage_path text not null, public_url text not null
  content_type text not null, bytes bigint, duration_seconds numeric
  sha256 text not null unique      -- so re-uploading the same file dedupes
  tags text[] default '{}', source text not null default 'uploaded', notes text
  times_posted int not null default 0, last_posted_at timestamptz
  created_at timestamptz not null default now()

Turn on RLS for all three tables. Reads are for admins only; all writing happens through
the service role inside the edge functions. Do not create any policy that lets the
anonymous role read or write these tables.

=== 3. STORAGE — TWO SEPARATE BUCKETS. THIS MATTERS. ===
Create bucket `social` — public, file size limit 524288000 (500 MB), allowed types:
image/png, image/jpeg, image/webp, image/gif, video/mp4, video/quicktime, video/webm.
This is scratch space for one-off post media. It gets auto-cleaned a week after posting.

Create bucket `reels` — public, file size limit 524288000 (500 MB), allowed types:
video/mp4, video/quicktime, video/webm, image/png, image/jpeg.
This is my permanent library. NOTHING may ever auto-delete from this bucket.

Set the size limits exactly as written. A default Supabase bucket caps at ~25-50 MB,
which silently rejects almost every real reel. Please double-check the limits actually
saved by reading the bucket config back after you create them.

=== 4. EDGE FUNCTIONS ===

(a) `media-intake` — turns a file into a public URL.
  Auth: require header `x-media-secret` matching CLEANUP_CRON_SECRET, else 403.
  POST only. Accepts either multipart/form-data with a `file` field, or JSON `{url}`.
  For JSON, only allow https:// sources, and handle one redirect safely.
  Reject anything that isn't a supported image or video type.
  SHA-256 the bytes, store to `social` at uploads/YYYY-MM-DD/<sha256>.<ext>, upsert off.
  Return: ok, bucket, path, public_url, bytes, content_type, kind, sha256.
  Content-addressing means uploading the same file twice reuses one stored copy.

(b) `library-intake` — same idea, but for my permanent library.
  Auth: same `x-media-secret` header.
  Accepts a file or an https URL, plus `title`, optional `tags` array, optional `notes`,
  and optional `source` ('uploaded' or 'generated', default 'uploaded').
  Store to the `reels` bucket at library/<sha256>.<ext>.
  Then insert a `reel_library` row. If a row with that sha256 already exists, update its
  title/tags instead of erroring, and say so in the response.
  Return the reel_library row including its public_url.

(c) `auto-publish` — the heart of the system.
  Auth: require header `x-publish-secret` matching PUBLISH_CRON_SECRET, else 403.
  Steps:
   1. GET https://api.upload-post.com/api/uploadposts/users with header
      `Authorization: Apikey <UPLOADPOST_API_KEY>` to list profiles and their connected
      social accounts.
   2. Select up to 10 rows from social_posts where status = 'approved'
      AND scheduled_for <= now().
   3. For each row: find its profile by publisher_profile. Work out which of the wanted
      platforms are actually connected on that profile; skip the rest and report them.
      If the profile doesn't exist or no wanted platform is connected, record a clear
      reason and move on — do not fail the whole run.
   4. CLAIM the row before posting: update it to status='queued' with a WHERE clause that
      still requires status='approved'. If that update affects zero rows, another run
      already took it — skip. This is what stops a post going out twice.
   5. Choose the endpoint by media type:
        media_content_type starts with 'video/'  -> POST /api/upload        (field: video)
        any other media                          -> POST /api/upload_photos (field: photos[])
        no media at all                          -> POST /api/upload_text
      Send as multipart form: `user` = the profile, `title` = the caption, and one
      `platform[]` entry per platform. Media is passed as its public URL string.
   6. On success set status='posted', posted_at, external_id and permalink from the
      response, and clear error. On failure set status='failed' and store the error text.
   7. If the row has a notion_page_id, PATCH that Notion page's Status property to
      'Posted'. Make this best-effort — a Notion hiccup must never fail a post that
      already went out successfully.
  Return a JSON summary: when it ran, how long it took, available profiles, how many
  posts it considered, and a per-post result.

(d) `notion-sync` — pulls my Notion calendar into the database.
  Auth: require header `x-sync-secret` matching PUBLISH_CRON_SECRET, else 403.
  FIRST, before writing any code: read my Notion database's real property schema via the
  Notion API and map to the property names that actually exist. Do not assume my column
  names — show me the mapping you chose and let me correct it.
  Then, for each Notion page whose Status is 'Approved' and which has a scheduled date:
    - Upsert into social_posts keyed on notion_page_id.
    - Map: caption text -> caption, title -> title, platform multi-select -> comma-joined
      platform, profile -> publisher_profile (default my profile), date -> scheduled_for,
      pillar/audience if those properties exist.
    - If the page has an attached file or a media URL, push it through media-intake to
      get a public URL, then set media_url AND media_content_type from what intake
      returns. Setting media_content_type correctly is mandatory: auto-publish decides
      video-vs-photo purely from that column, so a reel with a blank content type gets
      sent to the photo endpoint and fails.
    - Set status='approved' only for pages actually marked Approved.
    - NEVER modify a row that is already status='posted'. Once something is published,
      Notion edits must not resurrect or repost it.
  Return a summary of what it created, updated and skipped.

(e) `cleanup-media` — keeps storage tidy.
  Auth: header `x-cleanup-secret` matching CLEANUP_CRON_SECRET.
  Find social_posts that are 'posted' or 'failed', older than 7 days, whose
  media_deleted_at is null AND whose media_url starts with the public URL prefix of the
  `social` bucket. Delete those files and stamp media_deleted_at.
  The bucket-prefix condition is critical: it is what guarantees this sweep can never
  touch anything in my `reels` library.

=== 5. DATABASE HOUSEKEEPING FUNCTIONS ===
`public.prune_old_social_posts()` — delete rejected rows after 30 days, failed rows after
30 days, and posted rows after 1 year but only when their media is already cleaned up.

`public.run_social_recovery_watchdog()` — flag posts stuck in 'queued' for more than 15
minutes past their scheduled time, and recent failures, so problems surface instead of
sitting silently. Write these into a simple `ops_alerts` table (create it if needed) and
avoid raising a duplicate alert for something already flagged and unresolved.

=== 6. THE TIMERS (pg_cron + pg_net) ===
Enable the pg_cron and pg_net extensions, then schedule:
  every 15 min  -> POST to auto-publish  with the X-Publish-Secret header
  every 10 min  -> POST to notion-sync   with the X-Sync-Secret header
  daily 09:00   -> POST to cleanup-media with the X-Cleanup-Secret header
  daily 09:30   -> select public.prune_old_social_posts();
  every 10 min  -> select public.run_social_recovery_watchdog();
Read each secret inside the cron command straight from vault.decrypted_secrets so no
secret is ever written into the job definition in plain text.

=== 7. WHEN YOU ARE DONE ===
Verify and report back to me:
  - Confirm both buckets exist WITH the 500 MB limits actually applied.
  - Confirm all cron jobs are listed and active.
  - Confirm the partial unique index on notion_page_id exists.
  - Run auto-publish once manually and show me it returns a clean result with zero posts
    considered (an empty run is the correct result for an empty calendar).
  - Give me the Notion property setup I need to create, matching what notion-sync expects.
  - Give me the two cron secrets you generated, so I can save them.
Do not post anything to my real social accounts as a test without asking me first.
````

### What to expect

Claude will work through this for a while. Along the way it will show you the Notion
property mapping it picked — **read that bit** and correct it if your column names differ.

When it finishes, it hands you back your two generated cron secrets. Save them in your
password manager. You will need them if you ever want to trigger something manually.

---

## 5. Part 3 — Set up your Notion calendar

Your `Content Calendar` database needs these columns. Create them exactly — the names
have to match what `notion-sync` expects (or tell Claude your names and let it adapt).

| Column name | Type | What it's for |
|---|---|---|
| **Name** | Title | Short internal label. Not posted. |
| **Caption** | Text | The actual caption that gets published. |
| **Status** | Select | `Draft`, `Approved`, `Posted`, `Rejected` |
| **Scheduled** | Date | **Include the time**, not just the date. |
| **Platform** | Multi-select | `instagram`, `tiktok`, `youtube`, `linkedin`, `facebook`, `twitter`, `threads` |
| **Media** | Files & media *or* URL | The video or image to post. |
| **Profile** | Text | Your Upload-Post profile name. Leave blank for the default. |
| **Pillar** | Select | Optional. Your content categories. |
| **Audience** | Text | Optional. Who it's aimed at. |

> **Platform names must be lowercase and spelled exactly as above.** They are passed
> straight through to Upload-Post. `Instagram` or `IG` will not match and will be
> silently skipped — the post still goes out, just not to that network.

> **X is still called `twitter`.** Upload-Post never renamed its platform code, so
> writing `x` matches nothing. Same trap for YouTube Shorts: the platform is `youtube`,
> and whether it posts as a Short is decided by the video's own aspect ratio and length,
> not by the platform name.

> **The Scheduled date must include a time.** A date with no time is treated as midnight,
> which usually means "post immediately at the next check".

Once the columns exist, paste this to Claude:

```text
Read my Notion content calendar's property schema and confirm my notion-sync function
maps to it correctly. Then create one test row: caption "testing my posting engine",
platform instagram, scheduled 10 minutes from now, status Draft. Walk me through what
will happen to it, but do not approve it — I want to approve it myself.
```

---

## 6. Part 4 — Your reel library (storing your own videos)

This is the part that makes the system yours rather than a content treadmill. You get a
permanent, searchable library of your own videos that you can post and re-post whenever
you like.

### Why it needed a separate bucket

The engine automatically deletes post media **7 days after publishing**. That's correct
behaviour for one-off images — otherwise storage fills with junk forever.

But it's completely wrong for a reel you spent hours making and want to re-post next
quarter.

So your videos live in a **separate bucket** (`reels`) that the cleanup job is
structurally incapable of touching. The cleanup only looks at files whose URL starts with
the `social` bucket's address. A reel in the `reels` bucket doesn't match that pattern, so
it can never be selected for deletion. It isn't a setting someone can flip off by mistake
— it's a property of how the query is written.

```
   social bucket   ->  scratch space   ->  auto-deleted 7 days after posting
   reels bucket    ->  your library    ->  never auto-deleted, post it as often as you like
```

### Getting reels in

**Option A — hand a file to Claude:**

```text
Add this video to my reel library. Title it "gym transformation hook v2" and tag it
fitness, hook, high-performer. Then give me the public URL it's stored at.
```

**Option B — from a link you already have:**

```text
Pull the video at <URL> into my reel library, title "podcast clip - pricing rant",
tags podcast, pricing. Confirm the file size and that the public URL loads.
```

**Option C — bulk, at the start:**

```text
I'm going to give you 10 videos to load into my reel library. For each one, store it,
title it from the filename, tag it 'backlog', and then show me the finished library as a
table with title, size, duration and public URL.
```

Uploading the same file twice is safe. Files are identified by a fingerprint of their
contents (a SHA-256 hash), so a duplicate updates the existing entry instead of creating a
second copy and a second storage charge.

### Posting from the library

```text
Show me my reel library, then schedule the "gym transformation hook v2" reel to Instagram
and TikTok for Friday at 6pm, with this caption:

<your caption here>

Leave it as Draft — I'll approve it in Notion.
```

Or let it choose:

```text
Look at my reel library for anything tagged 'hook' that I haven't posted in the last 60
days, and draft me three posts from them for next week. Draft status only.
```

### Keeping track

```text
Show me my reel library sorted by how many times each one has been posted, so I can see
what I'm over-using and what I've never touched.
```

### Removing a reel

Deleting a reel has to remove **both** the stored file and its library entry. Drop only
the row and you keep paying to store an invisible file; drop only the file and you keep a
library entry pointing at a dead URL that fails at publish time. Ask for both:

```text
Delete "gym transformation hook v2" from my reel library — remove the stored file and
the library row, and confirm both are gone.
```

Note that Supabase deliberately blocks deleting storage files straight from the database
for exactly this reason, so this has to go through the library function. If your Claude
reports that a direct delete was rejected, that's the safety net working, not a bug.

---

## 7. Part 5 — Using it day to day

Once it's built, your actual routine is small.

### The loop

1. **Write** in Notion. Fill in the caption, attach the media, pick your platforms and a
   date/time. Leave Status as `Draft`.
2. **Approve** when you're happy — flip Status to `Approved`.
3. **Forget about it.** Within 10 minutes the post is imported. At its scheduled time it
   goes out. Status flips to `Posted` on its own.

That's it. There is no step 4.

### Useful things to say to Claude

**Check on things:**
```text
What's scheduled to go out in the next 7 days, and what's failed recently?
```

**Bulk scheduling:**
```text
Here are 5 captions. Spread them across the next two weeks, Tue/Thu/Sat at 6pm, going to
Instagram and TikTok, pulling media from my reel library. Everything stays as Draft until
I approve it in Notion.
```

**Stop something:**
```text
Cancel the post scheduled for Friday — set it back to Draft.
```

**Emergency stop everything:**
```text
Pause my posting engine right now — disable the auto-publish cron job. Don't delete
anything, I want to turn it back on later.
```

> Worth doing once, early: run that pause command and then turn it back on, so you know
> how to stop the machine before you need to stop the machine.

**Performance:**
```text
Show me everything I posted in the last 30 days with its permalink, grouped by platform.
```

---

## 8. Part 6 — When something breaks

Most problems are one of these six. Each has a plain cause.

### "No connected platform"

**Means:** you asked to post to a network that isn't linked to that Upload-Post profile.

**Fix:** open Upload-Post, generate a fresh connect link, and connect the missing account.
Then re-approve the post. Remember connect links expire after 48 hours.

### A post is stuck on "queued"

**Means:** the engine claimed the post and then something went wrong mid-flight. `queued`
is a temporary state that should last seconds.

**Fix:**
```text
Show me any posts stuck in queued, with their error messages, and tell me what went wrong.
```
To retry, set it back to `approved` and it'll be picked up on the next run.

### A video posted as a photo, or failed with a media error

**Means:** `media_content_type` wasn't set to something starting with `video/`. The engine
picks the video endpoint purely from that field — it does not guess from the file
extension.

**Fix:**
```text
Find any posts where the media is a video but media_content_type isn't set to a video
type, and correct them.
```

### An upload was rejected

**Means:** the file is bigger than the bucket's size limit, or its type isn't allowed.

**Fix:**
```text
Show me the actual file size limit and allowed types on my social and reels buckets, and
raise them to 500 MB if they're lower.
```

This is worth checking early — Supabase buckets often default to a much smaller cap than
you asked for, and the failure only shows up when you upload your first real reel.

### A function returns 403

**Means:** wrong secret in the request header. Almost always a manual call, not the cron.

**Fix:**
```text
Check that my cron jobs are using the right secrets from the vault and fix any mismatch.
```

### Nothing is posting at all

Work down this list:

```text
Diagnose my posting engine end to end:
1. Are the cron jobs active and when did each last run?
2. Are there rows that are approved with a scheduled time in the past?
3. Does my Upload-Post profile have connected accounts?
4. Run notion-sync and auto-publish manually and show me the raw responses.
Tell me exactly which link in the chain is broken.
```

That last prompt is the single most useful one in this document. When in doubt, paste it.

### The failure that hides

One thing to know about: if your Notion calendar stops importing, **nothing errors**. The
engine keeps running perfectly and posting nothing, because an empty queue and a broken
importer look identical from the outside.

So check in occasionally:

```text
When was the most recent row created in social_posts? If it's more than a few days old,
tell me why the Notion sync isn't bringing anything in.
```

---

## 9. Appendix — How it works under the hood

For when you or someone helping you needs the real mechanics.

### The publish cycle, precisely

```
every 15 minutes
   |
   v
pg_cron fires -> POST /functions/v1/auto-publish  (X-Publish-Secret header)
   |
   v
fetch connected accounts from Upload-Post for this post's profile
   |
   v
SELECT * FROM social_posts
  WHERE status = 'approved' AND scheduled_for <= now()  LIMIT 10
   |
   v
for each post:
   UPDATE ... SET status='queued' WHERE id=? AND status='approved'
   |                                          ^^^^^^^^^^^^^^^^^^^^
   |                                          zero rows updated = another
   |                                          run already claimed it -> skip
   v
   pick endpoint:  video/*  -> /api/upload
                   other    -> /api/upload_photos
                   none     -> /api/upload_text
   |
   v
   success -> status='posted', save permalink, flip Notion page to 'Posted'
   failure -> status='failed', save the error text
```

### Why the claim step exists

Two cron runs could overlap. Without claiming, both would see the same approved post and
both would publish it — a duplicate on your real account, which you cannot un-see.

The claim is a single atomic update that only succeeds if the row is *still* approved.
Exactly one run can win. The loser skips. This is the standard fix for this class of bug
and it's worth not letting anyone "simplify" it away.

### Why media is a public URL and not a file

Upload-Post fetches your media by URL rather than you streaming bytes to it. That's why
`media-intake` exists: it takes a file or a link, stores it in Supabase Storage, and hands
back a **public HTTPS URL** that Upload-Post can reach.

Consequences worth knowing:
- The media bucket must be **public**. A private bucket produces a URL that returns 403
  when Upload-Post tries to fetch it, and the post fails with a confusing error.
- Multiple URLs separated by commas in `media_url` become a **carousel**.
- Files are named by their content hash, so the same file uploaded twice is stored once.

### Post statuses

| Status | Meaning |
|---|---|
| `draft` | Being written. Will never post. |
| `approved` | Cleared to publish. Goes out once its scheduled time passes. |
| `queued` | Claimed by a run, being sent right now. Should last seconds. |
| `posted` | Live. `permalink` holds the URL. |
| `failed` | Something went wrong. `error` holds the reason. |
| `rejected` | You said no. Deleted after 30 days. |

### Retention

| What | Kept for |
|---|---|
| Media in the `social` bucket | 7 days after posting, then deleted |
| **Media in the `reels` bucket** | **Forever — never auto-deleted** |
| Rejected / failed posts | 30 days |
| Posted post records | 1 year |

### The security model

- Every secret lives in **Supabase Vault**, read at runtime through one
  `SECURITY DEFINER` function. No API key is ever written into a function's source or into
  a cron job definition.
- Every edge function requires a **shared secret header**. A stranger who finds your
  function URL gets a 403.
- Tables are **RLS-protected**, readable only by admins. All writes go through the service
  role inside the functions.
- The **approval gate** is the last line: even a bug that creates a hundred rows can't
  publish any of them, because none of them are `approved`.

---

## One last thing

Build it, then post one real thing through it end to end before you trust it with a
month's content. Watch a single post go from Notion → `Approved` → live, and confirm the
permalink comes back. Ten minutes of paranoia now saves you an embarrassing week later.
