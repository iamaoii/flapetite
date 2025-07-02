# 🦆 Flapetite
Flapetite is a food-themed twist on Flappy Bird! Fly through kitchen obstacles across 4 different world - Normal, Happy, Sad, and Angry. Dodge forks, ice, popsicles, and more as you test your reflexes in this tasty arcade challenge!

## 💻 Required Software

### ![Python](https://img.shields.io/badge/Python%20-3776AB?style=flat&logo=python&logoColor=white)
Installing Python
1. Open Windows PowerShell and execute:
```powershell
winget install -e --id Python.Python
```
2. During installation, ensure you check the `Add to PATH` option for a smooth workflow.
3. Verify installation by opening command prompt and running:
```powershell
python --version
```

### ![VS Code](https://img.shields.io/badge/VS%20Code-007ACC?style=flat&logo=visualstudiocode&logoColor=white)
Installing Visual Studio Code
1. Open Windows PowerShell and execute:
```powershell
winget install -e --id Microsoft.VisualStudioCode
```
2. Verify installation by opening VS Code from the Start menu

### ![Git](https://img.shields.io/badge/Git-F05032?style=flat&logo=git&logoColor=white)
Installing Git
1. Download Git from https://git-scm.com/download/win
2. Install with default options
3. Verify installation:
```powershell
git --version
```

---

## 🛠️ How to Run Locally

### Installation Steps

1. **Clone the Repository:**
```bash
git clone https://github.com/iamaoii/flapetite.git
cd flapetite
```

2. **Create Virtual Environment:**

Follow these steps to ensure your Python environment is correctly configured:

1. After installing Python and VS Code:
   - Open VS Code
   - Open the Git Repository (Flapetite)
   - Open the terminal in VS Code (**Ctrl+`**)

2. Create a virtual environment:
```bash
python -m venv venv
```
   - You'll notice a `.venv` folder is created in your project directory

3. Activate the virtual environment:
   - On Windows:
```bash
.\venv\Scripts\activate
```
   - On macOS/Linux:
```bash
source venv/bin/activate
```
   - Your terminal prompt should change to indicate the active environment

3. **Install requirements.txt**
```bash
pip install -r requirements.txt
```
   - Wait for the Python packages to install completely

4. **When you're done working in the virtual environment, you can deactivate it:**
```bash
deactivate
```

5. **Run the game**
```bash
python main.py
```
