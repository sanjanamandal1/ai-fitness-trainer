flowchart LR
    subgraph Client_Browser["Client: Browser"]
        UI["HTML5 / JS Dashboard"]
        CAM["Webcam Capture"]
    end

    subgraph Backend["Flask Backend (Python)"]
        API["WebSocket & REST Endpoints"]
        PROC["Real-time Processing Engine"]
        SESS["Session & Workout Manager"]
    end

    subgraph ML_Models["ML / Computer Vision"]
        POSE["Pose Detector"]
        FORM["Form Analyzer"]
        FATIGUE["Fatigue Detector"]
    end

    subgraph Storage["Data Analytics (Logical)"]
        STATS["Workout Stats"]
    end

    CAM -->|"Video Frames"| API
    UI -->|"UI Control"| API

    API --> PROC
    PROC --> POSE
    POSE --> FORM
    POSE --> FATIGUE
    FORM --> PROC
    FATIGUE --> PROC

    PROC -->|"Feedback Overlay, Scores"| API
    API -->|"JSON, Images"| UI

    PROC --> SESS
    SESS --> STATS
    STATS --> UI
