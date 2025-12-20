Project Directory Structure:

tango-orchestrator/
│
├── app/
│   ├── main.py
│   │
│   ├── config/
│   │   └── settings.py
│   │
│   ├── core/
│   │   ├── logging.py
│   │   ├── driver.py
│   │   ├── otp.py
│   │   ├── login.py
│   │   └── profiles.py
│   │
│   ├── collectors/
│   │   └── customer_collector.py
│   │
│   ├── senders/
│   │   └── message_sender.py
│   │
│   ├── storage/
│   │   └── csv_store.py
│   │
│   └── utils/
│       └── memory.py
│
├── runtime/
│   ├── profiles/
│   ├── output/
│   └── logs/
│
├── resources/
│   └── RateCard.png
│
├── requirements.txt
└── tango_orchestrator.sh
