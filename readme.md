## DESCRIPTION

- Summarized daily test log status/update for AI-optimized servers,
- Managed firmware upgrades/downgrades such as BIOS, BMC, and drivers,
- Integrated third-party utilities (e.g., IPMI tools) to debug and manage remote servers.

> Tools: Python, Flask, JavaScript, Bootstrap, HTML, CSS, Nginx, Redis


## PROJECT STRUCTURE
```
.
├── main
│   ├── __init__.py
│   ├── core.py
│   ├── extensions.py
│   ├── firmware_info.py
│   ├── ftu_helper.py
│   ├── cburn_helper.py
│   ├── rburn_helper.py
│   ├── tools.py
│   └── search.py
├── templates
│   ├── base.html
│   ├── index.html
│   ├── cburn_log.html
│   ├── ftu_log.html
│   ├── rburn_log.html
│   ├── tools.html
│   ├── construction.html
│   ├── input_form.html
│   ├── ip_lookup.html
│   ├── nodata.html
│   ├── unauthorized.html
│   └── update_commands.html
├── static
│   ├── css
│   ├── js
│   └── images
├── instance
│   └── database.db
├── models
│   └── models.py
├── config.py
├── app.py
```

## Application Showcase

### Home - Live (IMG)

![Home Page](media/home_page.jpg)

### Tools - User Authentication (IMG)

![Tools - Auth](media/user_auth.jpg)

![Tools - Auth](media/user_login.jpg)

### Tools - IP LOOKUP (IMG)

![Tools - IP_lookup](media/tool_1.jpg)

### Tools - ADDONS (IMG)

![Tools - Addons](media/tool_2.jpg)

---

### Live Page Demo (VIDEO)

https://github.com/user-attachments/assets/260d0923-0091-49bb-bc7c-d186702a135a

### Tools Page Demo - Test Server Info Lookup (VIDEO)

https://github.com/user-attachments/assets/5e4ce1ac-4748-46b9-b98a-a03caffea614

### Tools Page Demo - Custom Firmware Uploading and Updating (VIDEO)

https://github.com/user-attachments/assets/462366e0-694d-4b59-8580-d7f2093f0ef6

### Tools Page Demo - Error Handling and File Validation (VIDEO)

https://github.com/user-attachments/assets/eb851169-3e22-4446-9310-69a0277e4b71

### Tools Page Demo - 3rd Party Tools Integration and Usage (VIDEO)

https://github.com/user-attachments/assets/a7b574ba-7bf5-408e-9354-4887f43a4125

---
