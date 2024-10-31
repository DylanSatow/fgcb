from fastapi import FastAPI
import pyautogui
import time

app = FastAPI()

# Define a delay to ensure commands are not issued too quickly
command_delay = 0.1

@app.post("/press_up")
async def press_up():
    pyautogui.press('up')
    time.sleep(command_delay)  # Delay for stability
    return {"status": "up arrow pressed"}

@app.post("/press_down")
async def press_down():
    pyautogui.press('down')
    time.sleep(command_delay)  # Delay for stability
    return {"status": "down arrow pressed"}

@app.post("/click")
async def click():
    pyautogui.click()
    time.sleep(command_delay)

@app.get("/status")
async def status():
    return {"status": "running"}