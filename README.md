# ZNexora Tech: automatic cybersecurity news site

ZNexora Tech runs itself. Robots collect information and write drafts; **you only approve or reject**.

| Content | How often | Where it comes from |
|---|---|---|
| **Latest news** | Every 6 hours | Security news feeds (The Hacker News, BleepingComputer, SecurityWeek, Krebs on Security, The Record, CISA) |
| **Exploited vulnerabilities** | Every 6 hours | CISA Known Exploited Vulnerabilities + NVD scores |
| **Weekly recap** (news, ransomware, web defacement) | Every Monday, 09:00 Japan time | Everything collected during the week + ransomware.live statistics |
| **Theory or practical article** | Every Thursday, 09:00 Japan time | The next topic in `topics.json` |

Every draft arrives as a **pull request** in the GitHub app. **Merge** = publish and share automatically. **Close** = reject.

## What it costs

| Item | Cost |
|---|---|
| Hosting (GitHub Pages), robots (GitHub Actions), data sources, social sharing | Free |
| AI writing (optional, recommended) | About $2–8 per month with a small model |
| Your own domain, e.g. znexoratech.com (optional) | About $10 per year |

### With AI vs without AI

| | With an AI key | Free (no AI key) |
|---|---|---|
| Latest news | Each top story becomes a short brief in our own words, linking to the original | One "news roundup" post listing headlines with links |
| Exploited vulnerabilities | Full written briefing | Structured briefing from official data |
| Weekly recap | Written introduction and tailored advice, plus all data | All data, tables and headlines with standard advice |
| Theory / practical | Full first draft for you to check | An outline for you to fill in |

You can start free and add AI later. Nothing else changes.

---

## Part 1: Put the site online (about 30 minutes, one time)

### 1. Create a GitHub account
Sign up free at https://github.com. Install the **GitHub mobile app** and sign in: this is where you approve posts.

### 2. Create a repository
**+** (top right) > **New repository** > name it `znexora-tech` > **Public** > **Create repository**.

### 3. Upload the project
Easiest, no command line: install **GitHub Desktop** (https://desktop.github.com).
1. **File > Clone repository** > choose `znexora-tech`.
2. Unzip this project and copy **everything** into that folder, including the hidden `.github` folder.
   - Mac: press `Cmd + Shift + .` in Finder to see hidden folders.
   - Windows: File Explorer > **View > Show > Hidden items**.
3. Type a summary ("First upload") > **Commit to main** > **Push origin**.

### 4. Edit your settings
On GitHub open `site.json` > pencil icon, and set:
- `"url"`: `https://YOUR-USERNAME.github.io/znexora-tech`
- `"contact_email"`: your email

Also put your email in `content/pages/about.md`. Click **Commit changes**.

### 5. Turn on the website
**Settings > Pages > Source: GitHub Actions**.

### 6. Allow the robots to create drafts
**Settings > Actions > General > Workflow permissions**:
- choose **Read and write permissions**
- tick **Allow GitHub Actions to create and approve pull requests**
- **Save**

### 7. Publish for the first time
**Actions** tab > **Publish site** > **Run workflow**. After 1–2 minutes your site is live at your `url`.

### 8. Start the robots
**Actions** tab > **Latest news and exploited vulnerabilities** > **Run workflow**. Drafts appear in **Pull requests** within a few minutes.

You can also run **Weekly recap** and **Weekly theory or practical article** by hand to see them straight away. (The first recap will be thin, because the robots need a week to collect news. From the second week it is full.)

From now on everything runs by itself.

---

## Part 2: Your daily routine (a few minutes)

1. A notification arrives in the GitHub app.
2. Open the pull request > **Files changed** to read the post.
3. Use the checklist in the pull request.
4. **Merge pull request** to publish (shared automatically within ~2 minutes), or **Close pull request** to reject.
5. To fix something first: **Files changed** > file menu (…) > **Edit file** > commit > merge.

Turn on notifications: on the repository page tap **Watch > All activity**.

**Too many drafts?** In `site.json`, lower `max_drafts_per_run`, or set `"enabled": false` for any robot.

---

## Part 3: Upgrades

Secrets go in **Settings > Secrets and variables > Actions > New repository secret**. Use the exact names. Never put keys in files.

### AI writing
1. Create an account at https://console.anthropic.com, add a little credit, set a **monthly spend limit**, and create an API key.
2. Add secret `ANTHROPIC_API_KEY`.

### Better vulnerability scores
Free key from https://nvd.nist.gov/developers/request-an-api-key → secret `NVD_API_KEY`.

### Automatic social sharing (free)
- **Telegram channel:** in Telegram talk to `@BotFather` > `/newbot` > token → `TELEGRAM_BOT_TOKEN`. Create a public channel, add the bot as admin, use `@yourchannel` → `TELEGRAM_CHAT_ID`.
- **Discord:** Server Settings > Integrations > Webhooks > New > Copy URL → `DISCORD_WEBHOOK_URL`.
- **Bluesky:** Settings > Privacy and security > App passwords → `BLUESKY_HANDLE` and `BLUESKY_APP_PASSWORD`.
- **Mastodon:** Preferences > Development > New application (`write:statuses`) → `MASTODON_INSTANCE` (e.g. `infosec.exchange`) and `MASTODON_TOKEN`.

### Email newsletter
Your feed is `https://YOUR-SITE/feed.xml`. Use a newsletter service with **RSS-to-email** (Buttondown, MailerLite, Brevo, Kit; check the free plan includes it). Put the signup page link in `site.json` → `"newsletter_url"`.

### Your own domain
Buy one (Cloudflare Registrar or Porkbun), set `"custom_domain": "znexoratech.com"` in `site.json`, add the DNS records from GitHub's "managing a custom domain for GitHub Pages" guide, then tick **Enforce HTTPS** in **Settings > Pages**.

---

## Customising content

### Choose your news sources
Edit the `feeds` list in `site.json`. Any RSS or Atom feed works, for example a national CERT in your region.

### Plan your theory and practical articles
Edit `topics.json`. The robot takes the next unused topic every Thursday:
```json
{"title": "How to detect brute-force logins in Linux auth logs", "type": "practical", "level": "Intermediate", "notes": "Use journalctl and grep examples"}
```
`type` is `theory` or `practical`. `notes` is optional guidance for the AI.

### Write posts yourself
Copy a file from `templates/` (news, weekly-recap, theory, practical) into `content/posts/`, give it a new file name, edit it, and commit. It publishes automatically.

## Graphics on every page

Every post automatically gets an original ZNexora Tech graphic in your logo's style, with its own design for each content type: broadcast rings for news, a weekly grid for recaps, the CVSS score for exploited vulnerabilities, a node network for theory, and a terminal window for practical guides. Section pages get banners too. These graphics also appear when a post is shared on social media.

**To use your own photo for a post instead:**
1. Upload the photo into `assets/images/` (ideally 1200 x 630 pixels, JPG or PNG).
2. In the post's top section, add:
   ```
   image: my-photo.jpg
   image_alt: Short description of the photo
   ```

Only use photos you took or made yourself, or have a licence to use. Do not copy photos from news websites.

## Your logo and brand files
Your logo is already built in. The site uses these files in `assets/`:

| File | Used for |
|---|---|
| `logo.png` | Header on every page |
| `favicon-32.png` | Browser tab icon |
| `apple-touch-icon.png`, `icon-512.png` | Phone home-screen icon (the "Z") |
| `og-image.jpg` | Preview picture when a link is shared on social media or chat apps |

Your original logo is kept in `brand/`. To change the logo later, replace these files with new ones of the same names and sizes.

The site colors come from the logo: deep-space navy, electric blue, cyan and silver. The header always stays dark so the logo's glow looks right in both light and dark mode.

## Good to know
- **News is never copied.** AI briefs are short and in our own words, and every news post links to the original publisher.
- **Ransomware figures** come from criminal leak sites and are often unverified. The recap shows trends only and never names victims.
- **Check practical commands** on a test machine before approving. A wrong command can break someone's server.
- **Add your own voice.** A sentence of your own opinion or experience in some posts helps Google rank you.
- **GitHub pauses scheduled robots after 60 days without commits.** Approving posts counts as activity. To restart: **Actions** > the workflow > **Enable workflow**.
- **Something failed?** Open **Actions**, click the red run, read the message. The usual fix is Part 1, step 6.

## Project layout
```
site.json                   Settings: name, address, news sources, robot limits
topics.json                 Queue of theory and practical article ideas
templates/                  Starter files for writing posts yourself
content/posts/              Published posts
content/pages/              About and Privacy pages
assets/                     Logo, icons, design, search, dark mode, copy buttons
brand/                      Your original logo file
scripts/news_drafts.py      Latest news robot (also records weekly data)
scripts/cve_drafts.py       Exploited vulnerability robot
scripts/weekly_recap.py     Weekly recap robot
scripts/article_draft.py    Theory and practical article robot
scripts/build.py            Builds the website
scripts/share.py            Shares approved posts
.github/workflows/          The schedules
data/                       Robot memory (created automatically)
```
