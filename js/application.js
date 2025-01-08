// Wait till the browser is ready to render the game (avoids glitches)
window.onload = function () {
  const gameManager = new GameManager(
    4,
    KeyboardInputManager,
    HTMLActuator,
    LocalStorageManager
  );

  // Initialize OllamaManager with the game manager
  new OllamaManager(gameManager);

  // Initialize the input manager after the DOM is ready
  gameManager.initInputManager(KeyboardInputManager);
};
