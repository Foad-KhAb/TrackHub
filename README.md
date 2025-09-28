# TrackHub

### How to create the DB & user (psql)

```bash
# enter psql (adjust password method for your setup)
psql -U postgres

-- inside psql:
CREATE DATABASE myproject;
CREATE USER myprojectuser WITH PASSWORD 'yourStrongPassword';
GRANT ALL PRIVILEGES ON DATABASE myproject TO myprojectuser;
```
