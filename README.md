# Baikal-Manager

A web-based, self-hosted app for managing Baikal CalDAV/CardDAV contacts and calendars.

## Features

- User-friendly web interface for managing Baikal contacts and calendars
- Support for multiple users with individual Baikal server connections
- Calendar management with day, week, and month views
- Contact management with search and grouping capabilities
- CSV import/export functionality
- Light/Dark mode support
- Responsive design for desktop and mobile devices
- Secure data encryption
- Automatic session management

## Requirements

- A running Baikal server instance (accessible via network)
- Dockge for container deployment
- Docker and Docker Compose
- Debian 12 (recommended) or other compatible Linux distribution

## Installation

1. In Dockge:
   Use the docker-compose file to create your stack

2. Create a `.env` file and adjust your settings (or copy and modify `.env.example`):

   ```env
   #######################
   # Required Settings
   #######################

   # The directory on your host machine where all data will be stored
   # This directory will be created automatically if it doesn't exist
   HOST_DATA_DIR=/path/to/your/data/directory

   # The URL of your Baikal server
   # Example: http://192.168.1.100:5232 or https://dav.yourdomain.com
   BAIKAL_URL=http://your-baikal-server:5232

   # A secure key for session encryption
   # Use a random string of 32 characters or more
   APP_SECRET_KEY=generate_a_secure_key

   #######################
   # Optional Settings
   #######################

   # Authentication type for Baikal server
   # Values: 'basic' or 'digest'
   BAIKAL_AUTH_TYPE=basic

   # Application name displayed in the UI
   # Default: Baikal-Manager
   APP_NAME=Baikal-Manager

   # Debug mode for development
   # Values: 0 (disabled) or 1 (enabled)
   # Warning: Never enable in production
   FLASK_DEBUG=0

   # Application logging level
   # Values: DEBUG, INFO, WARNING, ERROR
   # Recommended: INFO for production, DEBUG for development
   LOG_LEVEL=INFO

   # Time in minutes before automatic logout due to inactivity
   # Minimum: 1, Recommended: 10
   DEFAULT_INACTIVITY_TIMEOUT=10

   # Default UI theme
   # Values: 'light' or 'dark'
   DEFAULT_MODE=light

   #####################################################################
   # Advanced Settings - Do not change unless you modify the Dockerfile
   #####################################################################

   # Container internal data directory
   DATA_DIR=/data

   # Container internal log directory
   LOG_PATH=/data/logs

   # Container internal encryption key path
   ENCRYPTION_KEY_PATH=/data/encryption.key
   ```

   Generate a secure key:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

   Sample settings for accessing your Baikal server calendars and contacts:
   ```
   If you connect to your calendars/contacts using URLs like:
   http://192.168.111.111:5232/dav.php/addressbooks/user/default/
   http://192.168.111.111:5232/dav.php/calendars/user/default/

   Then your BAIKAL_URL should be:
   BAIKAL_URL=http://192.168.111.111:5232/dav.php

   The application will handle the specific paths for calendars and contacts automatically.
   ```

3. Create a `docker-compose.yml` file:
   ```yaml
   version: '3.8'

   services:
     baikal-manager:
       build:
         context: https://github.com/BuggyPasta/Baikal-Manager.git
         dockerfile: Dockerfile
       container_name: baikal-manager
       user: "1000:1000"
       ports:
         - "3000:3000"
       volumes:
         - ${HOST_DATA_DIR}:/data
       env_file:
         - .env
       environment:
         - TZ=Europe/London
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
         interval: 30s
         timeout: 30s
         retries: 3
         start_period: 5s
       restart: unless-stopped
       security_opt:
         - no-new-privileges:true
       cap_drop:
         - ALL
       cap_add:
         - NET_BIND_SERVICE
       labels:
         - "com.centurylinklabs.watchtower.enable=false"
   ```

   Note: 
   - The volume mount uses the `HOST_DATA_DIR` variable from your `.env` file
   - All required directories are created automatically on first launch
   - The timezone is set to Europe/London by default
   - Security features are enabled by default
   - Container runs with minimal required privileges for directory management
   - The application runs as a non-root user for security

4. Click "Deploy" and wait until everything is pulled from the GitHub repo.

5. Access the application at `http://localhost:3000`

## Configuration

The application runs on port 3000 by default and is accessible only within your LAN.

Data Storage:
- All data is stored in the directory specified by `HOST_DATA_DIR` (created automatically)
- The following subdirectories are created automatically on first launch:
  * `logs/` - Application logs
  * `users/` - User data and credentials (encrypted)
- User data and credentials are encrypted
- Encryption keys are stored in `HOST_DATA_DIR/encryption.key`

Security Features:
- Automatic session timeout (configurable)
- Encrypted data storage
- Secure password hashing
- HTTPS support (when configured)
- Container security features:
  * Minimal required capabilities only (CHOWN, DAC_OVERRIDE, FOWNER, NET_BIND_SERVICE)
  * Non-root user execution
  * Restricted file system access

## Usage

1. Create a user account with your name and credentials
2. Configure your Baikal server connection in Settings:
   - Enter your Baikal server URL
   - Provide your Baikal username and password
   - Test the connection before saving
3. Configure application settings:
   - Set your preferred theme (light/dark)
   - Adjust auto-logout timeout
   - Configure default calendar view
4. Start managing your contacts and calendar

## Development

- Frontend: Vue.js 3 + Vite + Tailwind CSS
- Backend: Flask + Python 3.11
- Database: File-based with encryption
- Container: Docker with multi-stage build

## Deployment

1. **Environment Setup**:
   - Set all required environment variables in `.env`
   - Ensure `HOST_DATA_DIR` has correct permissions
   - Set `FLASK_DEBUG=0` for production
   - Configure a strong `APP_SECRET_KEY`

2. **Security**:
   - Use HTTPS in production
   - Set appropriate file permissions
   - Review security headers in configuration
   - Keep encryption keys secure
   - Container security is pre-configured

3. **Logging**:
   - Configure `LOG_LEVEL` appropriately
   - Monitor `app.log` for issues
   - Set up log rotation if needed

4. **Monitoring**:
   - Use the `/health` endpoint
   - Monitor container status
   - Check resource usage
   - Review logs regularly

## Maintenance

1. Update the application:
   ```bash
   # Pull latest code and rebuild
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

2. View logs:
   ```bash
   docker-compose logs -f
   ```

3. Backup data:
   - Regularly backup the `HOST_DATA_DIR` directory
   - Include encryption keys in backups
   - Store backups securely

## Troubleshooting

1. Common Issues:
   - Connection errors: Verify Baikal server URL and credentials
   - Session issues: Check `APP_SECRET_KEY` configuration
   - Encryption errors: Verify encryption key permissions
   - Timezone issues: Check TZ environment variable in docker-compose.yml

2. Debug Steps:
   - Check application logs in `HOST_DATA_DIR/logs/app.log`
   - Verify environment variables are set correctly
   - Ensure all required directories exist
   - Check container health status

3. Support:
   - Review the issues section on GitHub
   - Check logs for specific error messages
   - Verify your configuration against the example

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors
BuggyPasta, with lots of help from A.I. because BuggyPasta is otherwise WORTHLESS in programming

## Acknowledgments
Vectors and icons by various artists in PD License via SVG Repo

## Future development
None planned, which is why you see in the docker compose the 2 last lines instructing Watchtower to not bother checking for any updates. If you are not running Watchtower, feel free to remove them.

## VERY IMPORTANT NOTE. NO, SERIOUSLY.
This app is designed to work ONLY ON A LOCAL environment and is NOT secured in any way to work exposed to the Internet. As it will contain sensitive personal data, remember that you use it at your own risk. I STRONGLY recommend that you DO NOT EXPOSE it publically.