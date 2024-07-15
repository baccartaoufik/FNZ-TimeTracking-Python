# FNZ-TimeTracking-Python
# added a config.py file in the root directory of the python project where i specified both configs (dev and prod)
# for developement exec these commands in WINDOWS : $env:FLASK_ENV="development" 
#                                                 : $env:SECRET_KEY="secret"
#  OR : set FLASK_ENV=development
#     : set SECRET_KEY=secret

# docker run -d -p 8081:8081 -e FLASK_ENV=production -e PORT=8081 your-flask-app-image:latest
#Test
