# 📊 Custom BI Tool

A lightweight, Power BI-style business intelligence dashboard built with **Python**, **Streamlit**, and **Plotly**. Upload any Excel file and instantly explore your data through interactive charts, KPI metrics, and visual insights — no configuration required.

---

## 🚀 Features

- 📁 **Excel File Upload** — Supports `.xlsx` and `.xls` formats
- 📈 **Auto KPI Metrics** — Automatically calculates and displays sum & average for all numeric columns
- 🎛️ **Interactive Charts** — Bar, Line, Pie, and Scatter plots with dynamic axis selection
- 📊 **Distribution Histogram** — Visualize the data spread for any numeric column
- 🔍 **Data Preview Table** — Inspect the first 100 rows of your dataset at a glance
- ⬇️ **CSV Export** — Download your processed data with a single click

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| [Streamlit](https://streamlit.io) | Web application framework |
| [Pandas](https://pandas.pydata.org) | Data manipulation and analysis |
| [Plotly Express](https://plotly.com/python/plotly-express/) | Interactive chart rendering |
| [OpenPyXL](https://openpyxl.readthedocs.io) | Excel file reading and parsing |

---

## ⚙️ Installation & Setup

Follow the steps below to install Python and run the dashboard on your local machine.

---

### Step 1 — Download Python

1. Visit the official Python website: [https://python.org/downloads](https://python.org/downloads)
2. Click the **"Download Python 3.x.x"** button
3. The installer (`.exe` file) will begin downloading automatically

---

### Step 2 — Install Python

1. Open the downloaded `.exe` installer
2. ⚠️ **Important:** Before proceeding, make sure to check the box that says **"Add Python to PATH"** at the bottom of the installer window — this step is critical
3. Click **"Install Now"** and wait for the installation to complete
4. Click **"Close"** once finished

---

### Step 3 — Verify the Installation

1. Press the **Windows key**, type `cmd`, and press **Enter** to open Command Prompt
2. Run the following command:

```
python --version
```

If the output shows `Python 3.x.x`, the installation was successful. ✅

---

### Step 4 — Install Required Libraries

In Command Prompt, run each of the following commands one by one:

```
pip install streamlit
pip install pandas
pip install plotly
pip install openpyxl
```

---

### Step 5 — Create the Dashboard File

1. Right-click on your Desktop → **New** → **Text Document**
2. Rename the file to `dashboard.py`
3. Open it with Notepad, paste the full dashboard source code, and save the file

---

### Step 6 — Launch the Dashboard

In Command Prompt, run the following commands:

```
cd Desktop
streamlit run dashboard.py
```

Your browser will automatically open at `http://localhost:8501` with the dashboard ready to use. 🎉

---

## 🖥️ Run from GitHub

To clone and run the project directly from GitHub:

```bash
git clone https://github.com/YOUR_USERNAME/custom-bi-tool.git
cd custom-bi-tool
pip install -r requirements.txt
streamlit run app.py
```

---

## 📂 Project Structure

```
custom-bi-tool/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

---

## 📌 How to Use

1. Launch the application using `streamlit run app.py`
2. Click **Browse files** and upload an Excel file (`.xlsx` or `.xls`)
3. Review the auto-generated KPI metric cards displayed at the top
4. Select the X-axis, Y-axis, and preferred chart type to generate a visualization
5. Use the histogram panel to explore the distribution of any numeric column
6. Scroll down to preview your raw data in the interactive table
7. Click **⬇️ CSV Download** to export the data to your local machine

---

## 🗺️ Roadmap

- [ ] Multi-sheet Excel support
- [ ] Date-range filtering
- [ ] Custom color themes
- [ ] Save and load dashboard configurations
- [ ] One-click deployment to Streamlit Cloud

---

## 🤝 Contributing

Contributions are welcome! If you have a feature request or found a bug, please open an issue before submitting a pull request so we can discuss the proposed changes.

---

## 📄 License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).
