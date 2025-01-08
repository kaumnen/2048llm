class OllamaManager {
  constructor(gameManager) {
    console.log("OllamaManager constructor called"); // Log constructor call
    this.gameManager = gameManager;
    this.isRunning = false;
    this.moveMap = {
      0: 0, // up
      1: 1, // right
      2: 2, // down
      3: 3, // left
    };
    this.endpoint = "http://localhost:11434";
    this.moveHistory = [];
    this.maxRepeatedMoves = 5;
    this.selectedModel = "";
    this.moveInProgress = false;
    this.lastMove = null; // Track the last move

    // Initialize button and set initial text
    this.bindEvents(); // Bind events first
    this.initializeModels(); // Then initialize models
  }

  async initializeModels() {
    console.log("initializeModels called"); // Log initializeModels call
    const select = document.querySelector(".llm-select");
    const urlInput = document.querySelector(".endpoint-url");

    // Set the fixed localhost URL
    urlInput.value = this.endpoint;
    urlInput.disabled = true;

    try {
      // Fetch available models from Ollama
      console.log("Fetching models from Ollama..."); // Log before fetch
      const response = await fetch(`${this.endpoint}/api/tags`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("Ollama models:", data); // Log the response

      // Clear existing options
      select.innerHTML = "";

      // Add models to dropdown
      data.models.forEach((model) => {
        const option = document.createElement("option");
        option.value = model.name;
        option.textContent = model.name;
        select.appendChild(option);
      });

      // If no models found, add a message
      if (data.models.length === 0) {
        const option = document.createElement("option");
        option.value = "";
        option.textContent = "No models found";
        select.appendChild(option);
      }

      // Set the last selected model
      this.selectedModel = localStorage.getItem("lastSelectedModel") || "";
      if (this.selectedModel) {
        select.value = this.selectedModel;
      }

      select.addEventListener("change", () => {
        this.selectedModel = select.value;
        localStorage.setItem("lastSelectedModel", this.selectedModel);
      });
    } catch (error) {
      console.error("Error fetching models:", error);
      const option = document.createElement("option");
      option.value = "";
      option.textContent = "Error loading models";
      select.innerHTML = "";
      select.appendChild(option);
    }
  }

  async getMove(gameState) {
    const select = document.querySelector(".llm-select");
    const selectedModel = select.value;

    if (!selectedModel) {
      throw new Error("No model selected");
    }

    const prompt = `You are playing 2048. Here's the current game state:
Grid:
${JSON.stringify(gameState.grid, null, 2)}
Score: ${gameState.score}

Based on this grid state, respond with only a single number representing your next move:
0 for up
1 for right
2 for down
3 for left

Respond with ONLY the number, no other text.`;

    try {
      const response = await fetch(`${this.endpoint}/api/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: selectedModel,
          prompt: prompt,
          stream: false,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const move = parseInt(data.response.trim());
      return isNaN(move) || move < 0 || move > 3 ? 0 : move;
    } catch (error) {
      console.error("Error getting move:", error);
      throw error;
    }
  }

  async runLLMMove() {
    if (this.moveInProgress) {
      return;
    }

    this.moveInProgress = true;

    while (this.isRunning && !this.gameManager.over) {
      try {
        const gameState = this.getGameState();
        const move = await this.getMove(gameState);

        console.log("LLM response:", move);

        if (move !== undefined) {
          const mapped = this.moveMap[move];
          console.log("Making move:", mapped);
          this.gameManager.move(mapped);
          this.updateMoveHistory(move);
        }
      } catch (error) {
        console.error("Error during move:", error);
        this.isRunning = false;
        this.llmButton.textContent = "Start LLM";
        break;
      }

      await new Promise((resolve) => setTimeout(resolve, 500));
    }

    this.moveInProgress = false;
  }

  updateMoveHistory(move) {
    const repeatedMovesCounter = document.querySelector(
      ".repeated-moves-counter"
    );

    if (move === this.lastMove) {
      this.moveHistory.push(move);
    } else {
      this.moveHistory = [move];
    }

    this.lastMove = move;
    repeatedMovesCounter.textContent = Math.max(0, this.moveHistory.length - 1);

    if (this.moveHistory.length === this.maxRepeatedMoves) {
      console.log("LLM is stuck, restarting game.");
      this.gameManager.restart();
      this.moveHistory = [];
      this.lastMove = null;
      repeatedMovesCounter.textContent = 0;

      // Continue playing if LLM is still running
      if (this.isRunning) {
        this.runLLMMove();
      }
    }
  }

  bindEvents() {
    console.log("bindEvents called"); // Log bindEvents call
    this.llmButton = document.querySelector(".llm-button");
    this.llmButton.addEventListener("click", () => this.toggleLLM());
    this.llmButton.textContent = "Start LLM";
  }

  toggleLLM() {
    this.isRunning = !this.isRunning;
    this.llmButton.textContent = this.isRunning ? "Stop LLM" : "Start LLM";

    if (this.isRunning) {
      this.runLLMMove();
    }
  }

  getGameState() {
    const grid = this.gameManager.grid;
    const state = {
      grid: grid.cells.map((row) => row.map((cell) => (cell ? cell.value : 0))),
      score: this.gameManager.score,
    };
    return state;
  }
}
