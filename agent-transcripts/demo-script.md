# 2–3 Minute Video Demo Script — The Lenny Growth Assistant

**Presenter:** Full-Stack Engineer / Product Developer  
**Camera:** Camera ON (face visible in bottom corner), screen shared.  
**Target Duration:** 2 minutes 30 seconds  

---

## [0:00 – 0:25] Introduction & Hook
*(Camera full-screen or corner webcam on)*

> **Speaker:**  
> "Hi everyone! Welcome to the demo of **The Lenny Growth Assistant**.  
> If you're a product manager or founder, you know that *Lenny's Podcast* contains some of the highest-signal tactical growth advice in tech. But general LLMs often hallucinate generic advice and quote guests out of context.  
> We built a production-grade, locally runnable full-stack application that grounds every answer directly in real transcript evidence—powered by local models with Ollama, backed by PostgreSQL, and featuring a side-by-side Artifact Viewer."

---

## [0:25 – 1:05] Grounded Question Answering & Citations
*(Screen sharing: Browser showing `http://localhost:5173`)*

> **Speaker:**  
> "Here is our web application. Notice the clean, dark SaaS interface. Down here in the footer, our active provider is running on **Ollama with `llama3.2:3b`**—completely private and free, with zero cloud API keys required.  
> Let's test a tactical growth question:  
> *'What does Elena Verna recommend about PLG loops and fixing retention before acquisition?'*  
> *(Presses Enter — live response streams in)*  
> Notice two things:  
> First, look at the answer: Elena's core distinction between self-serve checkout and virality loops is explained with precision.  
> Second, look right below the answer: our **Grounded Citations Shelf**. If I expand this, we see the exact source title, chunk index, and direct excerpt from the podcast transcript. If the transcript doesn't support a claim, the agent refuses to fabricate."

---

## [1:05 – 1:45] The Ship 30 for 30 Essay Skill
*(Clicks the 'Ship 30 Essay Skill' button in the toolbar)*

> **Speaker:**  
> "Now let's demonstrate our specialized writing skill: the **Ship 30 for 30 essay engine**.  
> I'll click the 'Ship 30 Essay' action and ask:  
> *'Write an essay on why Brian Chesky eliminated traditional product management at Airbnb.'*  
> *(Sends query)*  
> The agent orchestrates a multi-step retrieval tool call, gathers Brian Chesky's Config interview transcripts, and generates a structured ~1,250-word essay with a compelling hook headline, clear subheadings, and grounded principles."

---

## [1:45 – 2:15] Side-by-Side Artifact Viewer
*(Artifact Viewer slides open beside the chat)*

> **Speaker:**  
> "As soon as the essay or visual artifact is created, our **Artifact Viewer** opens automatically beside the chat on desktop.  
> We can read the full formatted piece, copy it to clipboard with one click, or download it as Markdown or sandboxed HTML.  
> If an HTML preview is generated, it renders inside a safe, sandboxed iframe so untrusted code can never compromise the main application."

---

## [2:15 – 2:30] Architecture & Conclusion
*(Briefly show terminal with passing backend tests and PostgreSQL schema)*

> **Speaker:**  
> "Under the hood, we have:  
> - A FastAPI backend with PostgreSQL Full-Text Search.  
> - Session isolation and persistence across reloads.  
> - A flexible provider abstraction supporting Ollama, Anthropic Claude, and OpenAI.  
> - 100% passing automated test suite.  
> Thank you so much for watching!"
