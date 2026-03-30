# Personal Ops Assistant

Fully automated AI personal assistant system with dual-AI architecture:
- **Claude** (Primary): Daily planning, execution guidance, proactive schedule management
- - **Grok** (Secondary): Unfiltered pressure advisor, blind spot detection, reality checks
 
  - ## Architecture
 
  - ```
    Morning Check --> Claude --> Plan the day --> SMS
    Midday Check  --> Grok   --> Urgent actions --> SMS/Call
    Evening Review --> Both   --> Daily log
    ```

    ## Features

    - Google Calendar + Microsoft Outlook integration
    - - Automated morning/midday/evening loops via APScheduler
      - - SMS and voice call notifications via Twilio
        - - Structured JSON responses from both AI agents
          - - Daily logging for review and pattern tracking
            - - Docker containerized for easy deployment
             
              - ## Project Structure
             
              - ```
                personal-ops-assistant/
                |-- src/
                |   |-- main.py              # Entry point (CLI)
                |   |-- config.py            # Environment config (Pydantic)
                |   |-- calendar_service.py  # Google + Outlook calendar
                |   |-- claude_agent.py      # Claude primary agent
                |   |-- grok_agent.py        # Grok pressure agent
                |   |-- twilio_service.py    # SMS + voice notifications
                |   |-- scheduler.py         # APScheduler orchestrator
                |-- .env.example             # Environment template
                |-- requirements.txt         # Python dependencies
                |-- Dockerfile               # Container build
                |-- .github/workflows/       # CI/CD pipeline
                ```

                ## Quick Start

                ### 1. Clone and install

                ```bash
                git clone https://github.com/curt117-design/personal-ops-assistant.git
                cd personal-ops-assistant
                pip install -r requirements.txt
                ```

                ### 2. Configure environment

                ```bash
                cp .env.example .env
                # Edit .env with your API keys
                ```

                ### 3. Get your API keys

                **Anthropic (Claude):**
                1. Go to https://console.anthropic.com
                2. 2. Create an API key
                   3. 3. Add to .env as ANTHROPIC_API_KEY
                     
                      4. **xAI (Grok):**
                      5. 1. Go to https://console.x.ai
                         2. 2. Create an API key
                            3. 3. Add to .env as XAI_API_KEY
                              
                               4. **Google Calendar:**
                               5. 1. Go to https://console.cloud.google.com
                                  2. 2. Enable Google Calendar API
                                     3. 3. Create OAuth2 credentials (Desktop app)
                                        4. 4. Download as credentials.json in project root
                                           5. 5. First run will open browser for auth
                                             
                                              6. **Twilio:**
                                              7. 1. Sign up at https://twilio.com
                                                 2. 2. Get Account SID, Auth Token, and a phone number
                                                    3. 3. Add to .env
                                                      
                                                       4. ### 4. Run
                                                      
                                                       5. ```bash
                                                          # Test a single morning loop
                                                          cd src
                                                          python main.py --test morning

                                                          # Ask a one-off question
                                                          python main.py --ask "What should I focus on today?"

                                                          # Start the full scheduler (runs continuously)
                                                          python main.py
                                                          ```

                                                          ### 5. Docker deployment

                                                          ```bash
                                                          docker build -t personal-ops-assistant .
                                                          docker run -d --env-file .env personal-ops-assistant
                                                          ```

                                                          ## Daily Loop Schedule

                                                          | Time | Loop | Agent | Action |
                                                          |------|------|-------|--------|
                                                          | 0600 | Morning | Claude | Plan the day, send SMS brief |
                                                          | 1200 | Midday | Both | Check alignment, Grok critiques |
                                                          | 1900 | Evening | Both | Review day, log results |

                                                          ## Cost Estimate (Monthly)

                                                          - Hosting: $20-50 (small VM or container)
                                                          - - Twilio: ~$1-5 (100 SMS/calls)
                                                            - - Claude API: ~$5-10
                                                              - - Grok API: ~$5-10
                                                                - - Total: ~$30-75/month
                                                                 
                                                                  - ## Configuration
                                                                 
                                                                  - All settings are in `.env`. Key options:
                                                                 
                                                                  - - `MORNING_HOUR` / `MIDDAY_HOUR` / `EVENING_HOUR` - loop times
                                                                    - - `USER_TIMEZONE` - your timezone (e.g., America/Chicago)
                                                                      - - `USER_NAME` - personalization for prompts
                                                                       
                                                                        - ## License
                                                                       
                                                                        - MIT
