Butterfly Livestorm Q&A
=======================

An easy-to-use app that automatically suggest answers to Livestorm event questions using a PDF "knowledge base" and Mistral's document understanding.

* * * * *

Prerequisites
-------------

-   **Python 3.8+** installed

-   **Livestorm API token** & **Session ID**

-   **Mistral API key**

* * * * *

1\. Clone & Install
-------------------

1.  **Clone this repository:**

    ```
    git clone https://github.com/faresharrazi/butterfly-ls.git
    cd butterfly-ls
    ```

2.  **Install required packages:**

    ```
    pip install streamlit requests mistralai python-dotenv streamlit-autorefresh
    ```

* * * * *

2\. Configure
-------------

Create a file named `.env` in the project folder with the following three lines:

```
MISTRAL_API_KEY=<your-mistral-api-key>
LIVESTORM_API_TOKEN=<your-livestorm-api-token>
LIVESTORM_SESSION_ID=<your-livestorm-session-id>
```

Replace the placeholders with your actual keys and Session ID.

* * * * *

3\. Run the App
---------------

Start the Streamlit server:

```
streamlit run butterfly_ui.py
```

Then:

1.  Open your browser to **http://localhost:8501**

2.  **Connect**: you can update your Livestorm API Key and/or your session ID from the UI

3.  **Upload** your PDF knowledge base

4.  Watch new questions appear and see Butterfly's answers automatically!

* * * * *

*Enjoy automated, live Q&A---no setup headaches, just butterflies 🦋!*
