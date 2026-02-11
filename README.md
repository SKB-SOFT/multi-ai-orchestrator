# Many Minds - Multi-AI Orchestrator

This project is a multi-AI orchestrator that allows you to query multiple AI models simultaneously, compare their responses, and get a synthesized, high-quality answer. It's designed for research, experimentation, and building robust AI-powered applications.

## Core Features

- **Parallel AI Queries**: Send a single query to multiple providers (Groq, Gemini, Mistral, etc.) at once.
- **Smart Judge**: Automatically scores and ranks responses based on quality, not just speed.
- **Memory Context**: The system remembers past conversations to provide better follow-up answers.
- **Easy Setup**: Get up and running with a single `docker-compose up` command.
- **Live Stats**: A real-time dashboard shows system health and performance.

## Quick Start for Contributors

Getting started is easy. Follow these 5 steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/multi-ai-orchestrator.git
    cd multi-ai-orchestrator
    ```

2.  **Create your environment file:**
    Copy the example environment file:
    ```bash
    cp .env.example .env
    ```

3.  **Add your API keys:**
    Open the `.env` file and add your API keys for the AI providers you want to use (e.g., `GROQ_API_KEY`, `GEMINI_API_KEY`).

4.  **Build and run the containers:**
    ```bash
    docker-compose up --build
    ```

5.  **Open the web interface:**
    Navigate to `http://localhost:3000` in your browser. You should see the "Many Minds" chat interface, ready to take your queries.

That's it! You're now running the full stack locally.

## How to Contribute

We welcome contributions! Here's how you can help:

-   **Test the system**: Ask complex questions and see how the different models respond.
-   **Improve the judge**: The logic in `server/app/judge.py` can always be improved.
-   **Add new providers**: Create a new provider class in the `server/providers` directory.
-   **Enhance the UI**: The frontend is a Next.js app located in the `client` directory.

We're excited to see what you build with Many Minds!
