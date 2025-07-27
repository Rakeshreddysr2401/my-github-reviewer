# my-github-reviewer
Used to review PR's with the help of git workflows. 


START
  ↓
┌─────────────────┐
│  get_next_chunk │
└─────────────────┘
          ↓
    [Check if done?]
          ↓
      [If done] → END
          ↓
    [Has guidelines_store?]
          ↓
    [Yes] → retrieve_guidelines
    [No]  → reviewer_agent
          ↓
┌─────────────────────┐
│ retrieve_guidelines │ (optional)
└─────────────────────┘
          ↓
┌─────────────────┐
│ reviewer_agent  │ ← (generates review comments)
└─────────────────┘
          ↓
    [retry_count == 0 AND has guidelines_store?]
          ↓
    [Yes] → retrieve_guidelines (get guidelines after first review)
    [No]  → feedback_agent
          ↓
┌─────────────────┐
│ feedback_agent  │ ← (evaluates review quality)
└─────────────────┘
          ↓
    [Check satisfaction & retry logic]
          ↓
    [retry_count == 1 AND has guidelines_store?] → retrieve_guidelines
    [satisfied OR retry_count > MAX_RETRIES?] → format_comments
    [not satisfied AND retry_count <= MAX_RETRIES?] → reviewer_agent
          ↓
┌─────────────────┐
│ format_comments │ ← (converts to GitHub comment format)
└─────────────────┘
          ↓
    [Loop back to get_next_chunk for next chunk/file]
          ↓
    [Process until all files/chunks done] → END