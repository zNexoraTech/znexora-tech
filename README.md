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

Facebook and Instagram are covered further below.
- **Telegram channel:** in Telegram talk to `@BotFather` > `/newbot` > token → `TELEGRAM_BOT_TOKEN`. Create a public channel, add the bot as admin, use `@yourchannel` → `TELEGRAM_CHAT_ID`.
- **Discord:** Server Settings > Integrations > Webhooks > New > Copy URL → `DISCORD_WEBHOOK_URL`.
- **Bluesky:** Settings > Privacy and security > App passwords → `BLUESKY_HANDLE` and `BLUESKY_APP_PASSWORD`.
- **Mastodon:** Preferences > Development > New application (`write:statuses`) → `MASTODON_INSTANCE` (e.g. `infosec.exchange`) and `MASTODON_TOKEN`.

### Facebook and Instagram auto-posting

When you approve a post, it is shared to your **Facebook Page** (with a link preview) and your **Instagram** (the post's graphic with a caption and hashtags). Free.

### What you need first
- A **Facebook Page** for ZNexora Tech. (Meta does not allow automatic posting to personal profiles, only to Pages.)
- An **Instagram professional account** (Business or Creator), linked to that Page.
  - Instagram app > Settings > **Account type and tools** > **Switch to professional account**.
  - Facebook Page > Settings > **Linked accounts** > Instagram > **Connect**.

### Get your keys (about 20 minutes, one time)
Meta changes these screens often. If something looks different, send a screenshot.

1. Go to https://developers.facebook.com, log in, and click **My Apps** > **Create App**.
2. Name it `ZNexora Tech Publisher`. When asked for a use case, choose the ones for **managing your Page** and **Instagram content publishing**. Finish creating the app.
3. Open **Tools** > **Graph API Explorer**. On the right, choose your app, then **User Token**.
4. Under **Permissions**, add: `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`, `instagram_basic`, `instagram_content_publish`, `business_management`.
5. Click **Generate Access Token** and approve everything, selecting your ZNexora Tech Page and Instagram account.
6. Make it long-lasting: open **Tools** > **Access Token Debugger**, paste the token, click **Debug**, then **Extend Access Token** at the bottom. Copy the new token.
7. Back in the Graph API Explorer, paste the extended token into the token box, type `me/accounts` in the address box and click **Submit**. Find your Page in the result and copy:
   - its `id` → this is your **FACEBOOK_PAGE_ID**
   - its `access_token` → this is your **FACEBOOK_PAGE_TOKEN** (a Page token made this way does not expire)
8. Type `YOUR-PAGE-ID?fields=instagram_business_account` (with your real Page id) and click **Submit**. Copy the `id` inside `instagram_business_account` → this is your **INSTAGRAM_ACCOUNT_ID**.
9. In your GitHub repository: **Settings > Secrets and variables > Actions > New repository secret**, and add the three secrets with those exact names.

The app can stay in **development mode**: you are posting only to your own Page, as its admin.

**Never paste these tokens anywhere else**: not in files, emails or chats (including this one). Anyone with the Page token can post as your Page.

### Keeping ZNexora Tech secure

**Your accounts (most important)**
1. **GitHub:** turn on two-factor authentication: profile picture > **Settings > Password and authentication**. Use an authenticator app or passkey, and save the recovery codes somewhere safe offline.
2. **Email:** turn on 2-Step Verification for the email linked to GitHub and Facebook. Whoever controls your email can reset everything else.
3. **Facebook and Instagram:** turn on two-factor authentication in **Accounts Center > Password and security**.

**Your repository**
4. **Only merge drafts from `github-actions[bot]` or yourself.** Your repository is public, so strangers can open pull requests too. Never merge one you didn't expect.
5. **Turn on GitHub's free security alerts:** repository **Settings**, look for the security section (called **Advanced Security** or **Code security**), and enable **Dependabot alerts**, **Secret scanning** and **Push protection**. These warn you about outdated components and block accidental key leaks.
6. **Check nobody else has access:** **Settings > Collaborators** should be empty unless you added someone on purpose.
7. **Keys only as GitHub Secrets.** Secrets are encrypted and hidden even in a public repository.

**Your website (already done for you)**
- HTTPS on every page, no tracking cookies, no ads.
- Posts cannot contain hidden scripts: raw HTML in posts is blocked.
- Every page carries browser security rules (a Content Security Policy) that only allow your own scripts and images, plus Google Fonts.
- Your contact email is public on the About page; a separate address for the site reduces spam to your personal inbox.

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

## Weekly articles from Word and PowerPoint

### Publishing a weekly article (every week, about 3 minutes)

1. Name your files the same, for example `Zero Trust Explained.docx` and `Zero Trust Explained.pptx`.
2. On github.com open the **inbox** folder, then the section folder (**theory**, **practical**, **news** or **weekly-recap**).
3. Inside the section folder: **Add file > Upload files**, drag in both files, **Commit changes**.
4. Within about 5 minutes you get a draft in **Pull requests**: "Draft: <your title>". Check it under **Files changed**.
5. **Merge pull request**. The robot then:
   - publishes the article on the website (text, pictures, tables, slide gallery, PDF download; slide 1 becomes the cover),
   - posts it to your **Facebook Page**, **Instagram**, **Blogger blog** and **LinkedIn** (once connected below),
   - sends you a **Share kit** notification for **WhatsApp** and **TikTok** (see below).

How your Word file becomes the article: the first **Heading 1** is the title, the first paragraph is the summary, other headings become sections. Pictures in PNG or JPG format come through; drawings made with Word's shape tools may not, so insert diagrams as pictures.

### Cheat sheets and infographics

Upload a PNG or JPG (for example `Linux Hardening Cheat Sheet.png`) into **inbox > cheatsheets**. After you approve the draft, the site shows it in full on its own page with a **Download** button, under the new **Cheat sheets** menu item. It is shared as a full **photo post on Facebook**, in **Instagram's 4:5 shape** (the whole sheet on a navy background), to **Blogger** and **LinkedIn**, and the share kit includes it for **TikTok** and **WhatsApp**. The file name becomes the title. To add a description, upload a Word file with the same name next to the picture.

### WhatsApp Channel and TikTok: the share kit

WhatsApp Channels and TikTok do not offer automatic posting for small publishers (TikTok requires an app review, WhatsApp Channels have no posting API). So after each article, GitHub sends you a notification titled **"Share kit: <title>"** containing:

- a **WhatsApp message**, ready to copy and paste into your channel,
- the **slide pictures** in order and a **TikTok caption** with hashtags, ready for a TikTok photo post.

It takes about a minute on your phone. Close the issue when done.

### Connect your Blogger blog (one time, about 20 minutes)

Google changes these screens from time to time. If anything looks different, send a screenshot.

1. Go to https://console.cloud.google.com and create a project named `ZNexora Publisher`.
2. **APIs & Services > Library**: search **Blogger API v3** and click **Enable**.
3. **Google Auth Platform** (or **OAuth consent screen**): choose **External**, app name `ZNexora Publisher`, your email as support and developer contact. Under **Audience**, click **Publish app** so it is **In production**.
   - Important: if it stays in "Testing", Google stops the connection after 7 days. "Unverified" is fine because only you use it.
4. **Clients** (or **Credentials > Create credentials > OAuth client ID**): type **Web application**. Under **Authorized redirect URIs** add `https://developers.google.com/oauthplayground`. Create, then copy the **Client ID** and **Client secret**.
5. Open https://developers.google.com/oauthplayground
   - Click the **gear icon** (top right), tick **Use your own OAuth credentials**, paste the Client ID and secret.
   - In **Step 1**, type `https://www.googleapis.com/auth/blogger` in the box and click **Authorize APIs**. Sign in with the Google account that owns your blog. If you see "Google hasn't verified this app", click **Advanced > Go to ZNexora Publisher**, then **Continue**.
   - In **Step 2**, click **Exchange authorization code for tokens** and copy the **Refresh token**.
6. In GitHub: **Settings > Secrets and variables > Actions > New repository secret**, add:
   - `BLOGGER_CLIENT_ID`, `BLOGGER_CLIENT_SECRET`, `BLOGGER_REFRESH_TOKEN`

The robot finds your blog from the **Blog** link in `site.json`. By default it sends **theory, practical and weekly-recap** articles (not every news item), as the full article with a link back to the website. To send only a summary with a link instead, add to `site.json`: `"blogger": {"mode": "summary"}`.

### Connect LinkedIn (one time, about 15 minutes)

**Posting to your personal profile** (available to everyone):
1. Go to https://www.linkedin.com/developers/apps and click **Create app**. Name it `ZNexora Publisher` and link it to your ZNexora Tech LinkedIn page.
2. In the app's **Products** tab, request **Share on LinkedIn** and **Sign In with LinkedIn using OpenID Connect** (both are approved instantly).
3. Open the **OAuth token generator** (Docs and tools > OAuth Token Tools), choose your app, tick `openid`, `profile` and `w_member_social`, and generate a token.
4. In GitHub add the secret `LINKEDIN_TOKEN` with that token.

LinkedIn tokens last **60 days**. Put a reminder in your calendar to generate a new one and update the secret every 2 months; the robot's log says "token expired" when it is time.

**Posting as your company page** requires LinkedIn's **Community Management API** product, which LinkedIn approves only after verifying your business. If you get approval, generate the token with `w_organization_social` instead and add the secret `LINKEDIN_AUTHOR` with the value `urn:li:organization:<your page number>` (the number in your page's admin address). Until then, posting to your profile and resharing to the page takes one tap.

## Website security (built in)

- **Strict browser security rules (Content Security Policy):** only the site's own scripts, styles and fonts may load; images only from the site and your Blogger blog. No inline code is allowed.
- **No third-party tracking or fonts:** fonts are hosted on the site itself, so visitors' browsers contact no one else.
- **No hidden code in posts:** raw HTML in articles is blocked when the site is built.
- **Anti-clickjacking:** if another website tries to show ZNexora Tech inside a frame, the page hides itself.
- **security.txt:** `/.well-known/security.txt` tells security researchers how to report a problem (uses `contact_email`, or `security_contact` if you add it to `site.json`).
- **HTTPS everywhere:** GitHub Pages serves the site over HTTPS. Make sure **Settings > Pages > Enforce HTTPS** is ticked.

GitHub Pages does not let sites set their own server security headers, so online header scanners will show some as "missing". The protections above cover the important ones; if you later move to your own domain, a free Cloudflare account can add the remaining headers.

## Your Blogger blog

The site reads your Blogger blog automatically (from the "Blog" link in the `social` section of `site.json`) and shows your newest blog posts, with their images, on the home page and on a **Blog** page in the menu. Each one links to the full post on your blog. The site refreshes every 6 hours, so new blog posts appear without any action from you.

## Design and social links

The site uses a white, professional design with a color for each section (blue for news, violet for the weekly recap, rose for exploited vulnerabilities, magenta for theory, teal for practical guides). Your cover photo is the home page banner (`assets/cover.jpg`), the flat logo is in the header (`assets/logo-light.png`), and dark mode switches to the glowing logo automatically. Every post ends with a "Thank you for reading!" card with share and subscribe buttons.

Your social channels appear in the footer, on the home page ("Join the ZNexora community"), on the About page and in the thank-you card after every post. They come from the `social` section of `site.json`, shown in the order written there (only full `https://` links). Known names get matching icons: Facebook, Instagram, TikTok, YouTube, WhatsApp, Telegram, Blog, LinkedIn.

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
