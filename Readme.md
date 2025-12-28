Directory Structure:

tango-orchestrator
├── Dockerfile (i.e. Dockerfile for creating the image)
├── Readme.md 
├── data (i.e. directory storing runtime data)
│   ├── local_storage (i.e. temporary .csv stores here)
│   └── runtime (i.e. temporary chrome profiles generated stores here)
├── requirements.txt (i.e. python dependencies)
├── src
│   ├── config 
│   │   └── settings.py (i.e. all configs including text message, resource paths, max workers to be used etc)
│   ├── core
│   │   ├── driver.py (i.e. creates chrome driver)
│   │   ├── login.py (i.e. script to login to Tango)
│   │   ├── otp.py (i.e. script to fetch OTP sent by tango to the email ID)
│   │   └── profiles.py (i.e. script to clone chrome profiles, close chrome drivers etc)
│   ├── main.py (i.e. main file which starts the orchestrator)
│   ├── pipeline 
│   │   └── runner.py (i.e. pipeline of scripts specifying the sequence of execution)
│   ├── resources
│   │   ├── ProfileDP.jpg (i.e. image used in profile DP)
│   │   └── RateCard.png (i.e. image having coin price list)
│   ├── storage
│   │   └── local_storage.py (i.e. scrip to perform CRUD operation on temporary database stored in data folder)
│   ├── utils
│   │   ├── interaction_utils.py
│   │   ├── logger.py
│   │   └── metrics.py 
│   └── workflows
│       ├── collectors
│       │   └── customer_collector.py (i.e. script to collect customers, including broadcasters and senders)
│       └── senders
│           └── message_sender.py (i.e. script to message text and image to customer)
└── tango_orchestrator.sh (i.e. script performing docker cleanup, build and run)
