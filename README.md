# Introduction  

Gemini Chemistry Chatbot demonstrate how to quickly build and deploy a chatbot powered with Gemini
and specialized to answer questions about name of chemistry compounds. 
When a SMILES code is entered, the chatbot will return a JSON with the SMILES code, the  IUPAC name
and the name of the compound.

The user interface is developed using Streamlit.  

The application is deployed with App Engine.

![](images/gemini_chatbot.png)


# Deployment using Google Cloud SDK


To init the Google Cloud SDK, run the command:

```~/google-cloud-sdk/bin/gcloud init```

See the list of projects with:

```~/google-cloud-sdk/bin/gcloud projects list```

Check what project is set:

```~/google-cloud-sdk/bin/gcloud config get-value project```


To set the current project, run:

```~/google-cloud-sdk/bin/gcloud config set project <PROJECT_NUMBER>```


To deploy  the application, run the command:

```~/google-cloud-sdk/bin/gcloud app deploy app.yaml --project <PROJECT_ID>```

# Start app

To start the application, run from the root:

```streamlit run --server.port 8080 --server.enableCORS false --server.enableXsrfProtection=false --server.enableWebsocketCompression=false app.py```

On local, if you want to test the app, just run:

```streamlit run app.py```