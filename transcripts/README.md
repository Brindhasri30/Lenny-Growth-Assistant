# Transcript Sources and Licensing

This document records the provenance, licensing, and access constraints for all transcript data ingested into The Lenny Growth Assistant knowledge base.

---

## 1. Provenance and Attribution

All interview content is based on public episodes of **Lenny's Podcast**, hosted by **Lenny Rachitsky**.
- Official Site: [https://www.lennyspodcast.com](https://www.lennyspodcast.com)
- Substack Newsletter: [https://www.lennysnewsletter.com](https://www.lennysnewsletter.com)
- YouTube Channel: [https://www.youtube.com/@LennysPodcast](https://www.youtube.com/@LennysPodcast)

### Seed Episodes Included in Repository:
1. **Episode: Elena Verna on Product-Led Growth (PLG), B2B Freemium, and Growth Loops**
   - Guest: Elena Verna (Head of Growth at Amplitude, Lovable, Dropbox advisor)
   - Topics: Product-led growth loops, freemium conversion, monetization metrics, virality.
   - File: `transcripts/elena_verna_growth.txt`

2. **Episode: Brian Chesky on Founder Mode, Product Design, and Scaling Airbnb**
   - Guest: Brian Chesky (CEO & Co-founder of Airbnb)
   - Topics: Founder-led product reviews, unbundling product management, brand marketing vs. performance marketing.
   - File: `transcripts/brian_chesky_airbnb.txt`

3. **Episode: Shreyas Doshi on Product Management Principles, High-Leverage Thinking, and the LNO Framework**
   - Guest: Shreyas Doshi (ex-Stripe, Twitter, Google Product Lead)
   - Topics: LNO Framework (Leverage, Neutral, Overhead), product sense, avoiding vanity metrics.
   - File: `transcripts/shreyas_doshi_product.txt`

---

## 2. Licensing and Fair Use Constraints

1. **Educational & Demonstration Fair Use:**
   - The transcripts included in this project are excerpts and structured summaries curated strictly for educational demonstration, technical evaluation, and testing retrieval-augmented generation (RAG) within the take-home assignment.
   - No commercial redistribution or resale of full copyrighted audio recordings or proprietary subscription transcripts is permitted.

2. **No Hallucinated Citations:**
   - In accordance with project instructions, the AI agent retrieves quotes and claims strictly from stored transcript chunks.
   - If a user asks about an episode or topic not in the knowledge base, the agent explicitly states that no transcript evidence exists rather than fabricating statements.

---

## 3. How to Ingest Additional Episodes

To ingest a new transcript file (.txt, .md, .json, or .html):
```bash
cd D:\lenny-growth-assistant\backend
venv\Scripts\python.exe -m app.ingest "..\transcripts\new_episode.txt" --title "Guest Name on Topic" --url "https://lennyspodcast.com/guest-name"
```
Or use the REST endpoint:
```http
POST /api/knowledge/ingest
Content-Type: application/json

{
  "file_path": "transcripts/new_episode.txt",
  "title": "Guest Name on Topic",
  "source_url": "https://lennyspodcast.com/guest-name",
  "source_type": "podcast"
}
```
