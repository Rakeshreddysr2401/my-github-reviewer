# 🤖 My GitHub Reviewer

> An AI-powered GitHub Action to **review pull requests** and **chat interactively** with developers right inside the PR discussion thread using GitHub Workflows.

[![GitHub Action](https://img.shields.io/badge/GitHub-Action-blue?logo=github)](https://github.com/marketplace/actions)
[![OpenAI](https://img.shields.io/badge/Powered%20by-OpenAI-green?logo=openai)](https://openai.com)


## ✨ Features

- ✅ **AI-powered PR reviews** - Get instant, intelligent code review comments
- ✅ **Interactive Q&A** - Ask follow-up questions in PR comments and get AI responses
- ✅ **Reply to review comments** - Bot automatically responds to replies on its review comments
- ✅ **Suggested code fixes** - Receive actionable improvement suggestions
- ✅ **Vector store support** - Enhanced context understanding with Redis-based memory
- ✅ **Configurable LLM provider** - Support for OpenAI and other providers
- ✅ **File filtering** - Exclude specific files from review (e.g., docs, configs)
- ✅ **Performance optimized** - Cached dependencies and efficient processing

## 🚀 Quick Start

### 1. Create Workflow File

Create `.github/workflows/code-reviewer.yml` in your repository:

```yaml
name: "PR Review with Reply on Bot-2"

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]

permissions: write-all

jobs:
  review-pr:
    if: |
      (github.event.issue.pull_request && (github.event.comment.in_reply_to_id != null || contains(github.event.comment.body, '/git-reply'))) ||
      (github.event_name == 'pull_request_review_comment')

    runs-on: ubuntu-latest

    steps:
      - name: Set Mode
        id: set_mode
        run: |
          if [[ "${{ github.event_name }}" == "pull_request_review_comment" ]]; then
            echo "mode=reply" >> $GITHUB_OUTPUT
            echo "Mode: Reply to review comment"
          else
            echo "mode=review" >> $GITHUB_OUTPUT
            echo "Mode: Manual review triggered"
          fi

      - name: Log PR Info
        run: |
          echo "Event: ${{ github.event_name }}"
          echo "Mode: ${{ steps.set_mode.outputs.mode }}"
          echo "PR Number: ${{ github.event.issue.number || github.event.pull_request.number }}"
          echo "Repository: ${{ github.repository }}"
          echo "Comment: ${{ github.event.comment.body }}"

      - name: Checkout Repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Cache pip dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install --cache-dir ~/.cache/pip -r requirements.txt || true

      - name: Run GitHub Reviewer Action
        uses: Rakeshreddysr2401/my-github-reviewer@ReviewReplyPromptConcise
        with:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          PULL_NUMBER: ${{ github.event.issue.number || github.event.pull_request.number }}
          REPOSITORY: ${{ github.repository }}
          EXCLUDE: "*.md,*.txt,package-lock.json,*.yml,*.yaml"
          USE_VECTORSTORE: "true"
          MAX_LOOP: "2"
          MODE: ${{ steps.set_mode.outputs.mode }}
          REDIS_PASSWORD: ${{ secrets.REDIS_PASSWORD }}
          REDIS_HOST: ${{ secrets.REDIS_HOST }}
```

### 2. Add GitHub Secrets

Navigate to **Settings → Secrets and variables → Actions** and add:

| Secret Name | Description | Required |
|-------------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | ✅ Yes |
| `GITHUB_TOKEN` | Automatically provided by GitHub | ✅ Auto-generated |
| `REDIS_PASSWORD` | Redis password for vector store | ⚡ Optional |
| `REDIS_HOST` | Redis host URL for vector store | ⚡ Optional |

## 📖 Usage

### 🔍 Get AI Code Review

Comment on any pull request with:

```
/git-review
```

The bot will analyze the PR changes and provide detailed feedback including:
- Code quality suggestions
- Potential bugs or issues
- Best practice recommendations
- Performance improvements

### 💬 Interactive Chat & Replies

The bot now supports two types of interactions:

#### Manual Reply Trigger
```
/git-reply
```

#### Automatic Reply Mode
- The bot automatically responds when you **reply to its review comments**
- Just click "Reply" on any bot comment and ask your question
- No special commands needed - natural conversation flow!

**Example interactions:**
```
Developer: "Can you explain why this approach is better?"
Bot: "This approach is better because..."

Developer: "What about performance implications?"
Bot: "Regarding performance..."
```

### 🎯 Advanced Features

#### Vector Store Memory
When Redis credentials are provided, the bot uses vector store for:
- Better context understanding across conversations
- Memory of previous discussions in the PR
- More coherent and contextual responses

#### Loop Control
The `MAX_LOOP` parameter controls how many iterations the bot can perform for complex analysis (default: 2).

## ⚙️ Configuration Options

### Basic Configuration (Legacy Support)

For simpler setups, you can still use the basic version:

```yaml
name: "PR Review with GPT on Comment"

on:
  issue_comment:
    types: [created]

permissions: write-all

jobs:
  review-pr:
    if: |
      github.event.issue.pull_request &&
      contains(github.event.comment.body, '/git-review')
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run GitHub Reviewer Action
        uses: Rakeshreddysr2401/my-github-reviewer@dev-llm-config
        with:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          PULL_NUMBER: ${{ github.event.issue.number }}
          REPOSITORY: ${{ github.repository }}
          EXCLUDE: "*.md,*.txt,package-lock.json,*.yml,*.yaml"
          PROVIDER: "openai"
          MODEL_NAME: "gpt-4o"
          TEMPERATURE: "0.7"
```

### Available Parameters

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `PROVIDER` | LLM provider to use | `openai` | `openai`, `anthropic` |
| `MODEL_NAME` | Specific model name | `gpt-4o` | `gpt-4o`, `gpt-3.5-turbo` |
| `TEMPERATURE` | Response creativity level | `0.7` | `0.0` (focused) to `1.0` (creative) |
| `EXCLUDE` | Files to exclude from review | `""` | `"*.md,*.json,dist/*"` |
| `USE_VECTORSTORE` | Enable Redis vector store | `false` | `true`, `false` |
| `MAX_LOOP` | Maximum analysis iterations | `2` | `1`, `2`, `3` |
| `MODE` | Operation mode | `review` | `review`, `reply` |

## 📸 Screenshots

### AI Code Review in Action
<img width="2880" height="1800" alt="AI PR Review" src="https://github.com/user-attachments/assets/e9c1f4b5-32ce-42e9-a82c-6e166b1c008d" />

### Interactive Chat & Reply Example
<img width="1440" height="900" alt="AI Chat in PR" src="https://github.com/user-attachments/assets/f76887e3-463e-43bd-9146-2f602c2ead02" />

## 🏗️ Architecture

The action supports two main workflows:

1. **Review Mode**: Triggered by `/git-review` or `/git-reply` comments
2. **Reply Mode**: Automatically triggered when developers reply to bot comments

The bot intelligently switches between modes based on the GitHub event type and comment context.

## 🛡️ Security & Best Practices

- **API Key Security**: Store your OpenAI API key in GitHub Secrets, never in code
- **Permissions**: The action uses `write-all` permissions to comment on PRs
- **Rate Limiting**: Be mindful of API usage limits with your LLM provider
- **Cost Management**: Monitor API usage, especially with larger repositories
- **Redis Security**: Use strong passwords and secure Redis instances for vector store

## 🚀 Performance Optimizations

- **Dependency Caching**: Pip dependencies are cached for faster workflow runs
- **Python 3.10**: Optimized Python version for better performance
- **Vector Store**: Redis-based context memory for improved response quality
- **Loop Control**: Configurable iteration limits to prevent infinite loops

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.


## 🙏 Acknowledgments

- Built with ❤️ using GitHub Actions
- Powered by OpenAI's GPT models
- Enhanced with Redis vector store technology
- Inspired by the need for better code review automation

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/Rakeshreddysr2401/my-github-reviewer/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/Rakeshreddysr2401/my-github-reviewer/discussions)
- 📧 **Email**: rakeshreddysr24@gmail.com

---

<div align="center">
  <strong>⭐ Star this repository if you found it helpful!</strong>
</div>
