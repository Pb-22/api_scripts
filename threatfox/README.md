

# Script Explanation: `get_threatfox.py`

This script automates the process of fetching, cleaning, and exporting Indicators of Compromise (IOCs) from the [ThreatFox API](https://threatfox.abuse.ch/), focusing on recent IOCs for a user-specified number of days (7 or less). It outputs the results as JSON and CSV files, and further separates IP and domain IOCs into their own CSVs.

---

## **Getting Started**

### **1. Obtain a Free API Key**

1. Visit [https://auth.abuse.ch](https://auth.abuse.ch)
2. Register for a free account and follow the instructions to generate your ThreatFox API key.

---

### **2. Set Your API Key as an Environment Variable**

Before running the script, set your API key in your shell session:

```bash
export THREATFOX_API_KEY='your_actual_key_here'
```

**Tip:**
To avoid having to set this every time, you can add the above line to your `~/.bashrc` or `~/.zshrc` file for automatic loading in every terminal session.

---

### **3. Install Required Python Packages**

Make sure you have the dependencies installed. You can do this with pip:

```bash
pip install pandas tqdm urllib3 requests
```

---

## **Usage**

```bash
python get_threatfox.py DAYS [-v]
```

* `DAYS`: Number of past days (1–7) to fetch IOCs for (required).
* `-v` or `--verbose`: Optional flag for verbose logging.

**Example:**

```bash
export THREATFOX_API_KEY='your_actual_key_here'
python get_threatfox.py 7 -v
```

---

## **Key Steps and Functionality**

### 1. **Imports and Setup**

* **Standard Libraries:** Handles HTTP requests, JSON, CSV, system arguments, and date/time.
* **Third-party Libraries:** Uses `pandas` for data manipulation and `tqdm` for progress bars.
* **Argument Parsing:** Uses `argparse` to accept:

  * `days` (required): Number of days of IOCs to fetch.
  * `-v`/`--verbose` (optional): Enables verbose logging.

---

### 2. **Helper Functions**

* **`get_week_number()`**: Returns the current ISO week number (used for output filenames).
* **`clean_ioc(ioc)`**: Cleans IOCs by:

  * Extracting the domain from URLs (removing protocol and port).
  * Removing port numbers from IP addresses.
  * Returning the cleaned value.
* **`is_ip(ioc)`**: Checks if a string is an IPv4 address.
* **`is_domain(ioc)`**: Checks if a string is a domain (not an IP, but contains a dot).

---

### 3. **Argument Parsing and Logging**

* Parses command-line arguments.
* If `-v` is set, enables verbose output via the `log()` function.

---

### 4. **ThreatFox API Request**

* Uses `urllib3` to POST a request to the ThreatFox API for IOCs from the past `N` days.
* Saves the raw JSON response to a file named `wk<week_number>.json`.

---

### 5. **Data Processing**

* Loads the JSON data.
* Checks for the presence of the `'data'` key and ensures it contains results.
* Converts the data to a pandas DataFrame for easier manipulation.
* Cleans the `ioc` column using `clean_ioc()`.

---

### 6. **CSV Output**

* Writes the cleaned data to a CSV file named `wk<week_number>.csv`.
* Uses the first dictionary's keys as column headers.
* Each IOC is written as a row.

---

### 7. **IP and Domain Extraction**

* Filters the DataFrame to separate IP and domain IOCs.
* Writes each to their own CSV files:

  * `wk<week_number>_ip.csv` (column: `ip`)
  * `wk<week_number>_domain.csv` (column: `domain`)

---

## **Summary Table of Outputs**

| File Name         | Content                        |
| ----------------- | ------------------------------ |
| `wkXX.json`       | Raw JSON API response          |
| `wkXX.csv`        | Cleaned, tabular IOC data      |
| `wkXX_ip.csv`     | Only IP addresses (column: ip) |
| `wkXX_domain.csv` | Only domains (column: domain)  |

---

## **Troubleshooting**

* If you see the error
  `Error: ThreatFox API key not found.`
  Make sure you have set the `THREATFOX_API_KEY` environment variable as shown above.

* If you see
  `No data found in the API response.`
  The API did not return any IOCs for your specified number of days.


