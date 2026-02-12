# Book Recommendation Agent: Product Specification
*Last updated: 12th February 2025*  
*Version: 1.0 - Initial Specification*

## Overview

A personalized book recommendation system built primarily as a learning vehicle for developing sophisticated agentic systems. The project follows a phased approach, starting with a single conversational agent and evolving toward a multi-agent architecture inspired by the MACRS (Multi-Agent Conversational Recommendation System) framework.

### Primary Goals
1. **Learning objective**: Develop fluency in building, orchestrating, and evaluating agent systems
2. **Product objective**: Create a personalized book recommendation experience that feels like exploring a library rather than interrogating a librarian
3. **Personal objective**: Build confidence as an excellent maker of technology through hands-on implementation

---

## Core Concept

**What we're building:**  
A conversational agent that helps users discover their next book by understanding their preferences through dialogue, remembering context across sessions, and eventually providing a rich exploratory interface.

**What makes it different from ChatGPT/Claude:**
- **Persistent memory**: Tracks reading history, preferences, and past interactions
- **Personalization**: Integrates actual consumption data (Kindle, Goodreads)
- **Exploratory interface** (future): Moves beyond linear chat toward spatial/visual book discovery
- **Focused purpose**: Optimized specifically for book recommendations, not general conversation

**Success metric:**  
User "checks out" a recommended book — they save it and genuinely want to read it.

---

## Target User

**Primary user (Phase 1):** Myself — using the system to learn agent architecture while solving a real personal need.

**Secondary users (Phase 1.5):** Friends who love reading and are willing to test early versions.

**Future users:** Book lovers who want personalized recommendations that go deeper than algorithmic suggestions.

### User Needs & Behaviors

The agent should handle three distinct recommendation modes:

1. **Taste-matching**: "I loved *Piranesi*, what's similar but not too similar?"  
   → Pattern-matching on reading history and preferences

2. **Mood-tracking**: "I want something light but intellectually stimulating"  
   → Inferring intent from current conversation, reading between the lines

3. **Meta-cognition**: "I've DNF'd three books in a row, maybe I'm in a slump"  
   → Noticing patterns across sessions and intervening intelligently

---

## Product Philosophy & Values

1. **Personalized over popular**: Recommend books that fit the user and where they are in their life, not just what's trending
2. **Exploration over efficiency**: Create the feeling of wandering through a bookshop — delightful discovery, not just fast answers
3. **End choice paralysis**: Guide users to a decision without overwhelming them
4. **Learning-first**: Every architectural decision should maximize learning about agent systems

---

## Phased Development Plan

### Phase 1: Single Conversational Agent
**Timeline:** Next 2 weeks  
**Goal:** Learn conversation design and agent steering

**What we're building:**
- Single LLM agent with well-crafted prompt
- Chat interface (Streamlit is fine)
- No external data sources — relies purely on LLM's knowledge of books
- Manual logging of sessions and outcomes

**What we're learning:**
- Can we steer a conversation toward a decision?
- What makes a good recommendation dialogue?
- When should we ask vs. recommend?
- How many questions are too many?

**Success criteria:**
- Run 10-20 test sessions
- Achieve >60% "checkout" rate (user saves the recommended book)
- Develop clear intuition about conversation flow patterns

**Evaluation approach:**
- Manual qualitative assessment
- Track: turns to recommendation, hit rate, reasons for success/failure
- Document patterns in conversation flow

---

### Phase 1.5: Hardcoded Manager + Worker Agents
**Timeline:** TBD after Phase 1 learnings  
**Goal:** Learn multi-agent orchestration basics

**What we're building:**
- **Manager agent**: Simple rule-based dispatcher
  - Logic: "If < 3 preferences collected → ask. If ≥ 3 preferences → recommend."
- **Memory worker**: Returns user reading history when called
- **Retrieval worker**: Searches book corpus (uses 2M Goodreads dataset)
- **Conversation worker**: Conducts dialogue

**What we're learning:**
- How to pass context between agents
- What retrieval actually needs
- How to structure agent communication
- Where the handoffs get messy

**Success criteria:**
- System can successfully route between workers
- Recommendations improve with access to user history
- Clear understanding of multi-agent communication patterns

---

### Phase 2: LLM-Based Planner (MACRS-Inspired)
**Timeline:** TBD  
**Goal:** Sophisticated multi-agent orchestration

**What we're building:**
- **Planner agent** (manager): Reasons about which worker to call and why
  - Memory module: Tracks conversation state
  - Profiling module: Builds user preference model
  - Planning module: Decides optimal next action
- **Three specialized workers:**
  - Ask responder: Gathers user preferences through questions
  - Chat responder: Handles conversational elements
  - Recommendation responder: Generates book suggestions
  
**Planning logic** (from MACRS paper):
> "The planner agent utilizes multi-step reasoning to select responses across multiple dimensions, such as informativeness and engagement. For example, when available user preferences are insufficient, the planner agent reasons which candidate response can potentially yield a higher user information gain."

**What we're learning:**
- How to implement sophisticated agent reasoning
- Trade-off evaluation across competing objectives
- Long-term memory and state management
- Full multi-agent system architecture

---

### Phase 3: Rich Interface (Future)
**Goal:** Move beyond chat toward exploratory experience

**Potential interface ideas:**
- **Dynamic bookshelf**: Shelves that populate/shift based on conversation
- **Rich book pages**: Detailed descriptions, author context, thematic connections
- **Visual exploration**: Map/grid of book covers that evolve as preferences are refined
- **Generative elements**: AI-generated summaries, thematic illustrations

**Note:** Interface development happens *after* agent architecture is solid. Don't build the wrapper before the engine works.

---

## Technical Architecture

### Current Stack (Phase 1)

**Interface:**
- Streamlit for rapid prototyping
- Simple chat UI
- Manual session logging

**Agent:**
- Single LLM call (Claude/GPT)
- Prompt engineering as primary tool
- No external tools or data sources

**Data:**
- None yet — pure LLM knowledge

---

### Future Stack (Phase 1.5+)

**Data sources:**
- **User reading history**: Goodreads export, Kindle data
- **Book corpus**: 2M book Goodreads dataset (2017)
- **Potential APIs**: Amazon, OpenLibrary, Google Books (for metadata enrichment)

**Agent framework:**
- Multi-agent orchestration (manager + workers)
- Memory modules for context persistence
- Retrieval system for book search

**Evaluation infrastructure:**
- Logging database for checkouts, skips, denials
- Session transcripts
- User feedback collection

---

## Data & Memory Strategy

### What Makes a Good Recommendation?

**Primary metric:** User consumes the book and derives joy from it.

**Secondary considerations:**
- Did we expand the user's repertoire?
- Did we match their current mood/needs?
- Did we help them discover something unexpected?

### Recommendation Approaches

1. **Based on explicit preferences**: User states what they want
2. **Based on reading history**: Pattern-match against past consumption
3. **Based on collected signals**: Implicit preferences from skips, saves, ratings
4. **Cross-media correlation**: (Future) Articles, podcasts, other content they consume

**Important constraint:** Stay personal, avoid groupthink from collaborative filtering

### Memory Requirements

**Minimum viable (Phase 1):**
- Nothing — just LLM knowledge

**Phase 1.5 onwards:**
- User's reading history with ratings
- User's preferences and wish list
- Conversation history across sessions
- Explicit feedback (saves, skips, denials with reasons)

**Future:**
- Cross-session patterns (reading slumps, genre phases)
- Consumption history beyond books
- Long-term preference evolution

---

## Evaluation Framework

### Success Metrics (Prioritized)

**Primary metric: Checkout rate**
- Did the user save the recommended book?
- This is the core success signal

**Secondary metrics:**

1. **User engagement**
   - Completion rate: % of conversations that end with a checkout
   - Return rate: How often users come back
   - Session duration: Time spent in conversation

2. **Recommendation quality**
   - Acceptance rate: % of books saved
   - Activation rate: % of saved books actually started
   - Satisfaction rate: % of started books finished + rated well

3. **Efficiency**
   - Turns to recommendation
   - Time to checkout
   - (Note: May conflict with "exploration journey" philosophy)

4. **Accuracy**
   - Do recommended books exist?
   - Is metadata correct?
   - Do descriptions match reality?

### Technical Metrics

- Response latency
- Cost per session
- Token usage
- Error rates

---

### Evaluation Approach by Phase

**Phase 1: Manual qualitative evaluation**
- Run 10-20 sessions with self and friends
- Track: turns to rec, hit rate, why it worked/failed
- Look for patterns: too many questions? Recommends too quickly?
- Document findings in structured format (see Session Notes Framework below)

**Phase 1.5: Synthetic evaluation harness**
- Create 5-10 user personas with known preferences
  - Example: "loves literary fiction, hates sci-fi, currently in a reading slump"
- Have agent converse with another LLM playing the persona
- Evaluate: does recommendation fit the persona?
- Run hundreds of conversations to test prompt/architecture changes

**Phase 2+: Real usage data**
- Checkout logging becomes primary eval dataset
- Build proprietary conversational recommendation corpus
- A/B test architectural changes
- Long-term: track activation and satisfaction rates

---

### Session Notes Framework

After each test session, capture:

**Setup:**
- What mood/intent did the user start with?
- Any specific constraints or preferences mentioned upfront?

**Flow:**
- How many turns before recommendation?
- What questions did the agent ask?
- What was the conversation arc?

**Outcome:**
- Did user save a book?
- Would they actually read it? (1-5 scale)
- If multiple books suggested, which was chosen and why?

**Hypothesis:**
- Why did this work/fail?
- What would you change in the next iteration?
- Any surprising behaviors or insights?

---

## Feedback Collection

### During Conversation
- Track all suggested books
- Log user reactions: saved, skipped, denied
- Capture *why* for denials:
  - Wrong genre/vibe
  - Already read
  - Not in the mood right now
  - Just didn't sound interesting

### After Conversation
- Immediate: Did you save a book? (boolean)
- Immediate: How excited are you to read it? (1-5 scale)

### On Return Visit
- Did you start the book we recommended?
- Are you still reading it?
- Would you like to rate it now?

### Post-Reading (Long-term)
- Did you finish it?
- Rating (1-5 stars)
- Short feedback on what worked/didn't work

---

## Data Assets

### Available Now
- Personal Kindle reading history (exported)
- Goodreads data (request submitted)

### In Progress
- 2M book Goodreads dataset (2017) — currently downloading

### Future Considerations
- Web scraping: Amazon, library systems, publisher sites
- API integrations: Google Books, OpenLibrary, Goodreads API (if available)
- Cost analysis needed for hosting comprehensive book database

---

## Open Questions & Future Exploration

### Interface Ideas to Test
- What if chat isn't the primary interface?
- Can we create beautiful, generative book pages?
- How do we capture the serendipity of physical bookstores?
- What role does visual design play in recommendation acceptance?

### Agent Architecture Questions
- How much context should memory retain?
- What's the right balance between asking and recommending?
- How do we handle reading slumps or taste evolution?
- When should the system proactively intervene?

### Technical Deep Dives
- Context management strategies for long conversations
- Minimal agent interfaces that still feel rich
- Model selection: when to use different models for different tasks
- Memory: what to retain, what to forget, how to surface

---

## Non-Goals (For Now)

- ❌ Building for a company or commercial launch
- ❌ Collaborative filtering or social features
- ❌ Creating groupthink through "users like you" recommendations
- ❌ Optimizing for engagement metrics over recommendation quality
- ❌ Fancy UI before the agent architecture is solid

---

## Success Criteria for Overall Project

**Learning objectives met:**
- Deep understanding of agent orchestration
- Fluency in multi-agent system design
- Practical experience with evaluation methodologies
- Confidence in building agentic systems

**Product objectives met:**
- System successfully recommends books users want to read
- Checkout rate >60% across diverse users
- Users return for multiple sessions
- Recommendations improve with accumulated context

**Personal objectives met:**
- Tangible proof of agent-building capability
- Something to share that demonstrates technical depth
- Foundation for future, more ambitious agent projects
- Growth in leadership, development, and impact

---

## Notes for Collaborators & Coding Agents

### When Building
- **Start simple**: Single agent, basic prompt, manual testing
- **Log everything**: Every session teaches us something
- **Iterate fast**: Don't get stuck perfecting before shipping
- **Focus on learning**: The goal is understanding, not perfection

### When Evaluating
- **Primary signal**: Did they checkout the book?
- **Secondary signals**: Conversation flow, user satisfaction, return rate
- **Qualitative > Quantitative** in early phases: Understand *why* things work before measuring *how much*

### When Stuck
- Go back to the core question: "What's the moment of magic for the user?"
- Simplify: Can we test this assumption with less complexity?
- Ask: Is this teaching us about agents, or just about book data?

---

## Current Status

**What's done:**
- ✅ Core concept defined
- ✅ Phased development plan established
- ✅ Evaluation framework designed
- ✅ Kindle data exported
- ✅ Goodreads data requested
- ✅ 2M book dataset downloading

**Next immediate steps:**
1. Build Phase 1 single-agent system
2. Run initial test sessions (target: 10-20)
3. Document learnings using Session Notes Framework
4. Review findings and refine approach before Phase 1.5

**Timeline:**
- Phase 1: Next 2 weeks
- Review & iterate: 1 week
- Phase 1.5: TBD based on learnings

---